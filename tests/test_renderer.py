"""Tests for velocity_previewer.renderer context building."""

from datetime import datetime

from velocity_previewer.renderer import build_render_context


class TestBuildRenderContext:
    def test_adds_format_date_tool(self):
        context = build_render_context({})
        assert callable(context["format_date"])

    def test_format_date_ddmmyyyy(self):
        context = build_render_context({})
        result = context["format_date"]("DDMMYYYY")
        assert result == datetime.now().strftime("%d%m%Y")

    def test_format_date_strftime_passthrough(self):
        context = build_render_context({})
        assert context["format_date"]("%Y") == datetime.now().strftime("%Y")

    def test_adds_default_user_when_absent(self):
        context = build_render_context({})
        assert context["user"]["name"] == "Anonymous"
        assert context["user"]["skills"] == []

    def test_keeps_existing_user(self):
        context = build_render_context({"user": {"name": "Ada"}})
        assert context["user"] == {"name": "Ada"}

    def test_preserves_other_keys(self):
        context = build_render_context({"greeting": "hi"})
        assert context["greeting"] == "hi"

    def test_does_not_mutate_input(self):
        original = {"greeting": "hi"}
        build_render_context(original)
        assert original == {"greeting": "hi"}
