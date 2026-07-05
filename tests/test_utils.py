"""Tests for velocity_previewer.utils."""

from velocity_previewer.utils import (
    validate_template_syntax,
    validate_json_data,
    render_template,
    create_html_export,
    format_error_message,
    sanitize_filename,
)


class TestValidateTemplateSyntax:
    def test_valid_template(self):
        template = """
        #set($name = "World")
        Hello, $name!
        #foreach($i in [1..3])
            Item $i
        #end
        """
        is_valid, error = validate_template_syntax(template)
        assert is_valid
        assert error is None

    def test_empty_template_is_invalid(self):
        is_valid, error = validate_template_syntax("")
        assert not is_valid
        assert error == "Template is empty"

    def test_whitespace_only_template_is_invalid(self):
        is_valid, error = validate_template_syntax("   \n\t  ")
        assert not is_valid
        assert error == "Template is empty"

    def test_malformed_template_does_not_raise(self):
        # Airspeed is lenient; we only require a (bool, str-or-None) result
        # without an exception escaping.
        is_valid, error = validate_template_syntax("#foreach($x in $list\n$x\n#end")
        assert isinstance(is_valid, bool)


class TestValidateJsonData:
    def test_valid_object(self):
        is_valid, error, data = validate_json_data(
            '{"name": "John", "skills": ["Python", "JavaScript"]}'
        )
        assert is_valid
        assert error is None
        assert data == {"name": "John", "skills": ["Python", "JavaScript"]}

    def test_empty_string_returns_empty_dict(self):
        is_valid, error, data = validate_json_data("")
        assert is_valid
        assert error is None
        assert data == {}

    def test_syntax_error(self):
        is_valid, error, data = validate_json_data('{"name": "John",}')
        assert not is_valid
        assert "JSON syntax error" in error
        assert data is None

    def test_top_level_array_rejected(self):
        is_valid, error, data = validate_json_data("[1, 2, 3]")
        assert not is_valid
        assert data is None

    def test_top_level_string_rejected(self):
        is_valid, error, data = validate_json_data('"just a string"')
        assert not is_valid
        assert data is None

    def test_top_level_number_rejected(self):
        is_valid, error, data = validate_json_data("42")
        assert not is_valid
        assert data is None


class TestRenderTemplate:
    def test_basic_rendering(self):
        template = "Hello, $name!"
        success, result = render_template(template, {"name": "World"})
        assert success
        assert "Hello, World!" in result

    def test_foreach_and_method_call(self):
        template = """
        You have $skills.size() skills:
        #foreach($skill in $skills)
        - $skill
        #end
        """
        success, result = render_template(template, {"skills": ["Python", "HTML"]})
        assert success
        assert "2 skills" in result
        assert "- Python" in result
        assert "- HTML" in result

    def test_nested_object_access(self):
        template = "$user.name lives in $user.location"
        context = {"user": {"name": "Ada", "location": "London"}}
        success, result = render_template(template, context)
        assert success
        assert "Ada lives in London" in result

    def test_empty_template_fails(self):
        success, result = render_template("", {"name": "World"})
        assert not success
        assert "Template is empty" in result

    def test_missing_variable_left_verbatim(self):
        # Velocity leaves unresolvable $references as-is by default.
        success, result = render_template("Hello, $missing!", {})
        assert success
        assert "$missing" in result

    def test_empty_context(self):
        success, result = render_template("Static text only.", {})
        assert success
        assert "Static text only." in result


class TestCreateHtmlExport:
    def test_document_structure(self):
        result = create_html_export("Hello, World!", "Test Export")
        assert result.startswith("<!DOCTYPE html>")
        assert "Hello, World!" in result
        assert "Test Export" in result
        assert "Velocity Template Previewer" in result

    def test_content_is_escaped(self):
        result = create_html_export('<script>alert("xss")</script>')
        assert "<script>" not in result
        assert "&lt;script&gt;" in result

    def test_title_is_escaped(self):
        result = create_html_export("content", '<img src=x onerror="pwn()">')
        assert "<img" not in result
        assert "&lt;img" in result

    def test_default_title(self):
        result = create_html_export("content")
        assert "Velocity Template Output" in result


class TestFormatErrorMessage:
    def test_without_context(self):
        assert format_error_message("boom") == "Error: boom"

    def test_with_context(self):
        result = format_error_message("boom", "JSON Data Error")
        assert result == "JSON Data Error\n\nError: boom"


class TestSanitizeFilename:
    def test_clean_name_unchanged(self):
        assert sanitize_filename("report.html") == "report.html"

    def test_invalid_characters_replaced(self):
        assert sanitize_filename('a<b>c:d"e/f\\g|h?i*j') == "a_b_c_d_e_f_g_h_i_j"

    def test_leading_trailing_dots_and_spaces_stripped(self):
        assert sanitize_filename("  .name. ") == "name"

    def test_empty_falls_back_to_untitled(self):
        assert sanitize_filename("") == "untitled"

    def test_only_invalid_chars_falls_back_to_untitled(self):
        assert sanitize_filename(" . . ") == "untitled"
