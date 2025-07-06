"""
Utility functions and constants for the Velocity Template Previewer.
"""

import json
from typing import Dict, Any, Optional
from airspeed import Template, TemplateError


# --- Constants ---
APP_NAME = "Velocity Template Previewer"
DEFAULT_WINDOW_WIDTH = 1200
DEFAULT_WINDOW_HEIGHT = 800
TEMPLATE_FILE_FILTER = "Velocity Templates (*.vm);;All Files (*)"
JSON_FILE_FILTER = "JSON Files (*.json);;All Files (*)"
TEXT_FILE_FILTER = "Text Files (*.txt);;All Files (*)"
HTML_FILE_FILTER = "HTML Files (*.html);;All Files (*)"

# Auto-save interval in milliseconds
AUTO_SAVE_INTERVAL = 30000  # 30 seconds


def validate_template_syntax(template_str: str) -> tuple[bool, Optional[str]]:
    """
    Validate Velocity template syntax.

    Args:
        template_str: The template string to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not template_str.strip():
        return False, "Template is empty"

    try:
        Template(template_str)
        return True, None
    except TemplateError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Unexpected error: {e}"


def validate_json_data(
    data_str: str,
) -> tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
    """
    Validate JSON data syntax and structure.

    Args:
        data_str: The JSON string to validate

    Returns:
        Tuple of (is_valid, error_message, parsed_data)
    """
    if not data_str.strip():
        return True, None, {}

    try:
        data = json.loads(data_str)
        if not isinstance(data, dict):
            return False, "JSON data should be an object (dictionary)", None
        return True, None, data
    except json.JSONDecodeError as e:
        return False, f"JSON syntax error: {e}", None
    except Exception as e:
        return False, f"Unexpected error: {e}", None


def render_template(
    template_str: str, context_data: Dict[str, Any]
) -> tuple[bool, str]:
    """
    Render a Velocity template with the given context data.

    Args:
        template_str: The template string to render
        context_data: The context data dictionary

    Returns:
        Tuple of (success, result_or_error_message)
    """
    if not template_str.strip():
        return False, "Template is empty. Nothing to render."

    try:
        template = Template(template_str)
        rendered = template.merge(context_data)
        return True, rendered
    except TemplateError as e:
        return False, f"Velocity Template Rendering Error:\n{e}"
    except Exception as e:
        return False, f"An unexpected error occurred during rendering:\n{e}"


def create_html_export(content: str, title: str = "Velocity Template Output") -> str:
    """
    Create HTML content for export.

    Args:
        content: The content to include in the HTML
        title: The HTML page title

    Returns:
        Complete HTML document as string
    """
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 20px;
            line-height: 1.6;
            background-color: #f8f9fa;
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2980b9;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}
        pre {{
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 5px;
            overflow-x: auto;
            border-left: 4px solid #3498db;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 14px;
            line-height: 1.4;
        }}
        .metadata {{
            background-color: #e8f4fd;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
            border-left: 4px solid #3498db;
        }}
        .metadata p {{
            margin: 5px 0;
            color: #2c3e50;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
        <div class="metadata">
            <p><strong>Generated:</strong> {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>Template Engine:</strong> Velocity (Airspeed)</p>
        </div>
        <pre>{content}</pre>
    </div>
</body>
</html>"""


def format_error_message(error: str, context: str = "") -> str:
    """
    Format error messages for display.

    Args:
        error: The error message
        context: Additional context information

    Returns:
        Formatted error message
    """
    if context:
        return f"{context}\n\nError: {error}"
    return f"Error: {error}"


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename for safe file operations.

    Args:
        filename: The filename to sanitize

    Returns:
        Sanitized filename
    """
    import re

    # Remove or replace invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', "_", filename)
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip(". ")
    return sanitized or "untitled"
