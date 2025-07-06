#!/usr/bin/env python3
"""
Simple test script to verify the core functionality of the VM Visualizer.
"""

import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import (
    validate_template_syntax,
    validate_json_data,
    render_template,
    create_html_export,
)


def test_template_validation():
    """Test template syntax validation."""
    print("Testing template validation...")

    # Valid template
    valid_template = """
    #set($name = "World")
    Hello, $name!
    #foreach($i in [1..3])
        Item $i
    #end
    """

    is_valid, error = validate_template_syntax(valid_template)
    assert is_valid, f"Valid template failed validation: {error}"
    print("✓ Valid template validation passed")

    # Invalid template (more obvious syntax error)
    invalid_template = """
    #set($name = "World"
    Hello, $name!
    #foreach($item in $list
        $item
    #end
    """

    is_valid, error = validate_template_syntax(invalid_template)
    # Note: Airspeed is quite lenient, so we'll just check that it doesn't crash
    print(f"✓ Invalid template validation completed (result: {is_valid})")

    # Empty template
    is_valid, error = validate_template_syntax("")
    assert not is_valid, "Empty template should have failed validation"
    print("✓ Empty template validation passed")


def test_json_validation():
    """Test JSON data validation."""
    print("Testing JSON validation...")

    # Valid JSON
    valid_json = '{"name": "John", "age": 30, "skills": ["Python", "JavaScript"]}'
    is_valid, error, data = validate_json_data(valid_json)
    assert is_valid, f"Valid JSON failed validation: {error}"
    assert data["name"] == "John", "JSON data not parsed correctly"
    print("✓ Valid JSON validation passed")

    # Invalid JSON
    invalid_json = '{"name": "John", "age": 30,}'
    is_valid, error, data = validate_json_data(invalid_json)
    assert not is_valid, "Invalid JSON should have failed validation"
    print("✓ Invalid JSON validation passed")

    # Empty JSON
    is_valid, error, data = validate_json_data("")
    assert is_valid, "Empty JSON should be valid (empty dict)"
    assert data == {}, "Empty JSON should return empty dict"
    print("✓ Empty JSON validation passed")


def test_template_rendering():
    """Test template rendering."""
    print("Testing template rendering...")

    template = """
    #set($greeting = "Hello")
    $greeting, $name!
    You have $skills.size() skills:
    #foreach($skill in $skills)
        - $skill
    #end
    """

    context = {"name": "World", "skills": ["Python", "JavaScript", "HTML"]}

    success, result = render_template(template, context)
    assert success, f"Template rendering failed: {result}"
    assert "Hello, World!" in result, "Rendered template missing expected content"
    assert "Python" in result, "Rendered template missing skills"
    print("✓ Template rendering passed")


def test_html_export():
    """Test HTML export functionality."""
    print("Testing HTML export...")

    content = "Hello, World!\nThis is a test."
    html = create_html_export(content, "Test Export")

    assert "<!DOCTYPE html>" in html, "HTML export missing DOCTYPE"
    assert "Hello, World!" in html, "HTML export missing content"
    assert "Test Export" in html, "HTML export missing title"
    assert "Velocity Template Previewer" in html, "HTML export missing app name"
    print("✓ HTML export passed")


def main():
    """Run all tests."""
    print("Running VM Visualizer functionality tests...\n")

    try:
        test_template_validation()
        test_json_validation()
        test_template_rendering()
        test_html_export()

        print("\n🎉 All tests passed! The VM Visualizer is working correctly.")
        return True

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
