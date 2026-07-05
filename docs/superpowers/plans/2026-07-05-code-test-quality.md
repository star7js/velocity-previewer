# Code & Test Quality Pass Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convert the script-style tests to a real pytest suite with broader coverage, make CI enforce pytest + mypy, and extract non-UI logic out of `main.py` into `renderer.py` and `styles.py` — with zero behavior change.

**Architecture:** `utils.py` already holds pure functions; we pin them down with pytest. The context-building logic inlined in the GUI's `render_template()` method moves to a pure `build_render_context()` in a new `renderer.py` (alongside the `TemplateRenderer` QThread), making it unit-testable without a GUI. Stylesheet strings move to `styles.py`. CI swaps the script test invocation for `pytest` and adds `mypy src/`.

**Tech Stack:** Python 3.9+, PyQt5, airspeed, pytest, mypy, black, flake8. Spec: `docs/superpowers/specs/2026-07-05-code-test-quality-design.md`.

## Global Constraints

- No behavior change anywhere. No new features.
- No GUI test framework (no pytest-qt).
- Tests use plain pytest: no `sys.path` manipulation, no prints, no `main()` wrapper. The package is importable because it is installed with `pip install -e .` (already true locally and in CI).
- Keep the mypy global config strict; use per-module overrides in `pyproject.toml` only where noted.
- Line length 88 (black + flake8 `--max-line-length=88 --extend-ignore=E203,W503`). Run `black src/ tests/` before every commit.
- Entry point `velocity_previewer.main:main` must keep working (referenced by `[project.scripts]`).

---

### Task 1: Pytest suite for utils

**Files:**
- Create: `tests/test_utils.py`
- Delete: `tests/test_functionality.py`

**Interfaces:**
- Consumes: `velocity_previewer.utils` — `validate_template_syntax(str) -> Tuple[bool, Optional[str]]`, `validate_json_data(str) -> Tuple[bool, Optional[str], Optional[Dict]]`, `render_template(str, dict) -> Tuple[bool, str]`, `create_html_export(str, str) -> str`, `format_error_message(str, str) -> str`, `sanitize_filename(str) -> str` (all exist already).
- Produces: nothing consumed by later tasks.

- [ ] **Step 1: Write the test file**

Create `tests/test_utils.py` with exactly this content:

```python
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
```

- [ ] **Step 2: Run the suite**

Run: `pytest tests/test_utils.py -v`
Expected: all tests PASS (these characterize existing behavior). If any test fails, the test's expectation is wrong — inspect the actual behavior in `src/velocity_previewer/utils.py`, fix the *test* to match real behavior, and note the surprise in the commit message. Do not change `utils.py`.

- [ ] **Step 3: Delete the old script test**

```bash
git rm tests/test_functionality.py
```

- [ ] **Step 4: Verify full suite + lint**

Run: `pytest && black --check src/ tests/ && flake8 src/ tests/ --max-line-length=88 --extend-ignore=E203,W503`
Expected: pytest collects only `tests/test_utils.py`, all pass; black and flake8 clean. (CI still references the deleted file — fixed in Task 5; that's fine because tasks land on one branch together.)

- [ ] **Step 5: Commit**

```bash
git add tests/
git commit -m "Replace script-style tests with pytest suite for utils"
```

---

### Task 2: Extract renderer.py with testable context building

**Files:**
- Create: `src/velocity_previewer/renderer.py`
- Create: `tests/test_renderer.py`
- Modify: `src/velocity_previewer/main.py` (remove `TemplateRenderer` class at lines 57–74, replace context-building block inside `render_template()` at lines 663–687, update imports)

**Interfaces:**
- Consumes: `velocity_previewer.utils.render_template(str, dict) -> Tuple[bool, str]`.
- Produces: `velocity_previewer.renderer.TemplateRenderer(template_str: str, context_data: Dict[str, Any])` — QThread with `rendered = pyqtSignal(str)` and `error = pyqtSignal(str)`; `velocity_previewer.renderer.build_render_context(context_data: Dict[str, Any]) -> Dict[str, Any]`. Task 5's CI and later mypy work rely on these being fully type-annotated.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_renderer.py`:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_renderer.py -v`
Expected: FAIL at collection with `ModuleNotFoundError: No module named 'velocity_previewer.renderer'`

- [ ] **Step 3: Create renderer.py**

Create `src/velocity_previewer/renderer.py`:

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_renderer.py -v`
Expected: all 7 PASS

- [ ] **Step 5: Rewire main.py**

In `src/velocity_previewer/main.py`:

a. Delete the whole `TemplateRenderer` class (lines 57–74, including the class docstring).

b. Delete `from datetime import datetime` (line 24 — after this change nothing in main.py uses it).

c. Remove `QThread, pyqtSignal` from the `PyQt5.QtCore` import (line 22), leaving:

```python
from PyQt5.QtCore import Qt, QSize, QTimer, QSettings
```

d. Add below the `.syntax_highlighters` import:

```python
from .renderer import TemplateRenderer, build_render_context
```

e. In `render_template()`, replace this block (currently lines 663–687):

```python
        # Add format_date function for template
        def format_date(fmt):
            # Support 'DDMMYYYY' and other strftime formats
            if fmt == "DDMMYYYY":
                return datetime.now().strftime("%d%m%Y")
            try:
                return datetime.now().strftime(fmt)
            except Exception:
                return datetime.now().strftime("%d%m%Y")

        context_data["format_date"] = format_date
        # Add dummy $user if not present (for example template)
        if "user" not in context_data:
            context_data["user"] = {
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
```

with:

```python
        context_data = build_render_context(context_data)
```

- [ ] **Step 6: Verify suite, lint, and headless launch**

Run: `pytest && black --check src/ tests/ && flake8 src/ tests/ --max-line-length=88 --extend-ignore=E203,W503`
Expected: all pass.

Run the app headless to confirm wiring (instantiates the window, renders a template through the real thread, checks output):

```bash
QT_QPA_PLATFORM=offscreen python -c "
from PyQt5.QtWidgets import QApplication
from velocity_previewer.main import VelocityTemplatePreviewer
app = QApplication([])
w = VelocityTemplatePreviewer()
w.templateEditor.setText('Hello, \$name!')
w.dataEditor.setText('{\"name\": \"World\"}')
w.render_template()
w._renderer_thread.wait()
app.processEvents()
out = w.outputViewer.toPlainText()
assert 'Hello, World!' in out, out
print('OK:', out)
"
```

Expected output ends with `OK: Hello, World!`

- [ ] **Step 7: Commit**

```bash
git add src/velocity_previewer/renderer.py src/velocity_previewer/main.py tests/test_renderer.py
git commit -m "Extract TemplateRenderer and context building into renderer module"
```

---

### Task 3: Extract stylesheets into styles.py

**Files:**
- Create: `src/velocity_previewer/styles.py`
- Modify: `src/velocity_previewer/main.py` (`_apply_styling_unsafe`, lines 275–381 in the pre-Task-2 numbering)

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces: `velocity_previewer.styles.DARK_STYLESHEET: str`, `velocity_previewer.styles.LIGHT_STYLESHEET: str`.

- [ ] **Step 1: Create styles.py**

Create `src/velocity_previewer/styles.py` containing the two stylesheet strings, moved verbatim from `main.py._apply_styling_unsafe`:

```python
"""Qt stylesheets for light and dark mode."""

DARK_STYLESHEET = """
    QMainWindow {
        background-color: #23272e;
    }
    ...  # <- the exact string currently passed to setStyleSheet() in the
         #    `if self._dark_mode:` branch of _apply_styling_unsafe.
         #    Copy it character-for-character from main.py.
"""

LIGHT_STYLESHEET = """
    QMainWindow {
        background-color: #f5f5f5;
    }
    ...  # <- the exact string from the else branch, copied verbatim.
"""
```

(The `...` above stands for the verbatim copied CSS — 50 lines per branch already in `main.py`; move, don't retype.)

- [ ] **Step 2: Rewire main.py**

Add to main.py imports:

```python
from .styles import DARK_STYLESHEET, LIGHT_STYLESHEET
```

Replace the whole `_apply_styling_unsafe` body with:

```python
    def _apply_styling_unsafe(self):
        """Apply modern styling to the application
        (unsafe version without error handling)."""
        self.setStyleSheet(
            DARK_STYLESHEET if self._dark_mode else LIGHT_STYLESHEET
        )
```

- [ ] **Step 3: Verify no behavior change**

Run: `pytest && black --check src/ tests/ && flake8 src/ tests/ --max-line-length=88 --extend-ignore=E203,W503`
Expected: all pass.

Headless check that both modes apply a non-empty stylesheet:

```bash
QT_QPA_PLATFORM=offscreen python -c "
from PyQt5.QtWidgets import QApplication
from velocity_previewer.main import VelocityTemplatePreviewer
app = QApplication([])
w = VelocityTemplatePreviewer()
dark = w.styleSheet()
w.toggle_dark_mode()
light = w.styleSheet()
assert '#23272e' in dark and '#f5f5f5' in light
print('OK')
"
```

Expected: `OK`

- [ ] **Step 4: Commit**

```bash
git add src/velocity_previewer/styles.py src/velocity_previewer/main.py
git commit -m "Extract light/dark stylesheets into styles module"
```

---

### Task 4: Make mypy pass on src/

**Files:**
- Modify: `pyproject.toml` (`[tool.mypy]` section)
- Modify: `src/velocity_previewer/syntax_highlighters.py` (add annotations)
- Modify: `src/velocity_previewer/main.py`, `src/velocity_previewer/utils.py`, `src/velocity_previewer/renderer.py` (only if mypy reports errors)

**Interfaces:**
- Consumes: modules from Tasks 2–3.
- Produces: `mypy src/` exits 0 — Task 5's CI step depends on this.

- [ ] **Step 1: Add mypy overrides to pyproject.toml**

Append after the existing `[tool.mypy]` table:

```toml
[[tool.mypy.overrides]]
module = "airspeed.*"
ignore_missing_imports = true

[[tool.mypy.overrides]]
module = "velocity_previewer.main"
disallow_untyped_defs = false
disallow_incomplete_defs = false
```

Rationale (from the spec): global strictness stays; the PyQt5-heavy UI module gets a targeted relaxation instead of watering down the global config.

- [ ] **Step 2: Run mypy and record the errors**

Run: `mypy src/`
Expected: errors in `syntax_highlighters.py` (untyped defs) and possibly a handful elsewhere. If mypy cannot find PyQt5 type information, add PyQt5-stubs to the dev extra in `pyproject.toml` (`"PyQt5-stubs>=5.15"` under `[project.optional-dependencies] dev`) and `pip install -e ".[dev]"` again.

- [ ] **Step 3: Annotate syntax_highlighters.py**

Add annotations to all three highlighter classes (identical shape in each):

```python
from typing import List, Optional, Tuple

from PyQt5.QtGui import (
    QColor,
    QFont,
    QSyntaxHighlighter,
    QTextCharFormat,
    QTextDocument,
)


class VelocitySyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, parent: Optional[QTextDocument] = None) -> None:
        super().__init__(parent)
        self._setup_formats()
        self._setup_rules()

    def _setup_formats(self) -> None: ...
    def _setup_rules(self) -> None:
        self.rules: List[Tuple[str, QTextCharFormat]] = []
        ...
    def highlightBlock(self, text: str) -> None: ...
```

(`...` = existing bodies unchanged; only signatures and the `self.rules` annotation change. Apply the same three signature changes and `rules` annotation to `JSONSyntaxHighlighter` and `OutputSyntaxHighlighter`. Note `text` in `highlightBlock` may arrive as `Optional[str]` in some stub versions — if mypy complains, use the signature the installed stubs declare.)

Fix any remaining errors mypy reports in `utils.py`/`renderer.py` by adding precise annotations — never `# type: ignore` unless the error is inside PyQt5 stub territory, and then with a specific code, e.g. `# type: ignore[attr-defined]`.

- [ ] **Step 4: Verify**

Run: `mypy src/ && pytest && black --check src/ tests/ && flake8 src/ tests/ --max-line-length=88 --extend-ignore=E203,W503`
Expected: `Success: no issues found` from mypy; everything else passes.

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml src/
git commit -m "Make mypy pass on src with targeted per-module overrides"
```

---

### Task 5: CI enforces pytest + mypy; README update

**Files:**
- Modify: `.github/workflows/ci.yml`
- Modify: `README.md` (Development section, lines 104–121)

**Interfaces:**
- Consumes: green `pytest` (Tasks 1–2) and green `mypy src/` (Task 4).
- Produces: CI pipeline other contributors rely on.

- [ ] **Step 1: Update the workflow**

In `.github/workflows/ci.yml`, replace:

```yaml
    - name: Run functionality tests
      run: |
        python tests/test_functionality.py
```

with:

```yaml
    - name: Type check with mypy
      run: |
        mypy src/

    - name: Run tests
      run: |
        pytest
```

(Keep the black, flake8, and build steps as they are.)

- [ ] **Step 2: Update README Development section**

Replace the `# Run tests` command and the project-structure listing:

```bash
# Run tests
pytest

# Type check
mypy src/
```

and in the structure listing add the two new modules:

```
├── src/velocity_previewer/    # Main package
│   ├── main.py                # Application UI and logic
│   ├── renderer.py            # Background rendering & context building
│   ├── styles.py              # Light/dark Qt stylesheets
│   ├── utils.py               # Template processing
│   └── syntax_highlighters.py # Syntax highlighting
```

- [ ] **Step 3: Validate workflow syntax locally**

Run: `python -c "import yaml, pathlib; yaml.safe_load(pathlib.Path('.github/workflows/ci.yml').read_text()); print('YAML OK')"`
Expected: `YAML OK`

- [ ] **Step 4: Commit**

```bash
git add .github/workflows/ci.yml README.md
git commit -m "Run pytest and mypy in CI; update README dev docs"
```

---

### Task 6: Final verification and push

**Files:** none (verification only)

- [ ] **Step 1: Full local gate**

Run:

```bash
pytest -v \
  && black --check src/ tests/ \
  && flake8 src/ tests/ --max-line-length=88 --extend-ignore=E203,W503 \
  && mypy src/
```

Expected: everything green.

- [ ] **Step 2: End-to-end headless render with the bundled example**

```bash
QT_QPA_PLATFORM=offscreen python -c "
from PyQt5.QtWidgets import QApplication
from velocity_previewer.main import VelocityTemplatePreviewer
app = QApplication([])
w = VelocityTemplatePreviewer()
w.templateEditor.setText(open('examples/example-template.vm').read())
w.dataEditor.setText(open('examples/example-data.json').read())
w.render_template()
w._renderer_thread.wait()
app.processEvents()
out = w.outputViewer.toPlainText()
assert out and 'Error' not in out.split(chr(10))[0], out[:200]
print('Example rendered,', len(out), 'chars')
"
```

Expected: `Example rendered, <N> chars` with no traceback.

- [ ] **Step 3: Push and watch CI**

```bash
git push origin main
gh run watch --exit-status
```

Expected: CI green on all three OS runners. If a runner fails, read the log (`gh run view --log-failed`), fix, commit, push again.
