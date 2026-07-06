"""Background rendering and render-context preparation."""

from datetime import datetime
from typing import Any, Dict

from PyQt5.QtCore import QThread, pyqtSignal

from .utils import render_template


def _format_date(fmt: str) -> str:
    """Format the current date. Supports 'DDMMYYYY' plus strftime formats."""
    if fmt == "DDMMYYYY":
        return datetime.now().strftime("%d%m%Y")
    try:
        return datetime.now().strftime(fmt)
    except Exception:
        return datetime.now().strftime("%d%m%Y")


def build_render_context(context_data: Dict[str, Any]) -> Dict[str, Any]:
    """Return a render context with built-in tools and defaults added.

    Adds the $format_date tool and a placeholder $user object (used by the
    bundled example template) when the data doesn't define one. The input
    dict is not modified.
    """
    context = dict(context_data)
    context["format_date"] = _format_date
    if "user" not in context:
        context["user"] = {
            "name": "Anonymous",
            "age": 0,
            "email": "",
            "location": "",
            "bio": "",
            "phone": "",
            "website": "",
            "linkedin": "",
            "skills": [],
            "experience": [],
        }
    return context


class TemplateRenderer(QThread):
    """Background thread for template rendering."""

    rendered = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, template_str: str, context_data: Dict[str, Any]) -> None:
        super().__init__()
        self.template_str = template_str
        self.context_data = context_data

    def run(self) -> None:
        """Render the template in background thread."""
        success, result = render_template(self.template_str, self.context_data)
        if success:
            self.rendered.emit(result)
        else:
            self.error.emit(result)
