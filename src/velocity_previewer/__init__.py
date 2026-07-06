"""Velocity template previewer with syntax highlighting."""

from .main import VelocityTemplatePreviewer, main
from .utils import APP_VERSION

__version__ = APP_VERSION
__all__ = ["VelocityTemplatePreviewer", "main"]
