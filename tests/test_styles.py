"""Tests for velocity_previewer.styles."""

from velocity_previewer.styles import DARK_STYLESHEET, LIGHT_STYLESHEET


class TestOutputPaneStaysLight:
    def test_dark_mode_overrides_output_viewer(self):
        # Rendered templates carry their own light-background inline styles;
        # the preview pane must stay readable in dark mode.
        assert "QTextBrowser#outputViewer" in DARK_STYLESHEET
        override = DARK_STYLESHEET.split("QTextBrowser#outputViewer")[1]
        block = override.split("}")[0]
        assert "background-color: white" in block
        assert "color: #222" in block

    def test_dark_mode_editors_stay_dark(self):
        generic = DARK_STYLESHEET.split("QTextEdit, QTextBrowser")[1].split("}")[0]
        assert "background-color: #181a20" in generic

    def test_light_mode_has_no_output_override(self):
        assert "QTextBrowser#outputViewer" not in LIGHT_STYLESHEET
