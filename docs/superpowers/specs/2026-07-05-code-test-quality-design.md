# Code & Test Quality Pass — Design

**Date:** 2026-07-05
**Scope:** Behavior-preserving quality improvements. No new features, no GUI test framework.

## Goals

1. Replace the script-style test file with a real pytest suite and broaden coverage of the non-UI logic.
2. Make CI enforce what the project already claims to enforce (pytest, mypy).
3. Reduce `main.py` (897 lines) to focused UI wiring by extracting non-UI concerns.

## Non-goals

- New user-facing features (roadmap items stay on the roadmap).
- GUI testing with pytest-qt.
- Distribution/packaging changes.

## Part 1: Pytest suite

Replace `tests/test_functionality.py` with:

- `tests/test_utils.py` — covers `validate_template_syntax`, `validate_json_data`,
  `render_template`, `create_html_export`, `format_error_message`, `sanitize_filename`.
  New cases beyond the current suite:
  - `validate_json_data` rejects non-dict top-level JSON (arrays, strings, numbers).
  - `create_html_export` escapes HTML in content and title (the code claims XSS
    protection; nothing tests it).
  - `sanitize_filename` handles invalid characters, leading/trailing dots and
    spaces, and empty input (falls back to `"untitled"`).
  - `format_error_message` with and without context.
  - Rendering edge cases: missing variables, nested object access, `#foreach`,
    empty context.
- `tests/test_renderer.py` — covers the context-building logic extracted in Part 3
  (built-in tools such as `format_date`), without any GUI.

Conventions: no `sys.path` manipulation (the package is installed with
`pip install -e .` in CI and locally), no prints, no `main()` wrapper — plain
pytest functions using the existing `[tool.pytest.ini_options]` config.

## Part 2: CI enforcement

In `.github/workflows/ci.yml`:

- Replace `python tests/test_functionality.py` with `pytest`.
- Add a mypy step (`mypy src/`). The strict config in `pyproject.toml` currently
  never runs. Fix the type errors it surfaces. If the PyQt5-heavy UI module is
  impractical under full strictness, add per-module overrides in
  `pyproject.toml` (e.g. relax `disallow_untyped_defs` for `velocity_previewer.main`)
  rather than weakening the global config.

## Part 3: main.py extraction

Split `src/velocity_previewer/main.py` into:

- `renderer.py` — `TemplateRenderer` (QThread) plus a pure
  `build_render_context(data: dict) -> dict` function holding the context
  preparation currently inlined in `render_template()` (including the nested
  `format_date` helper). The pure function is unit-testable without a GUI.
- `styles.py` — the light/dark stylesheet strings currently inside
  `_apply_styling_unsafe` (~110 lines).
- `main.py` — keeps `VelocityTemplatePreviewer` (QMainWindow) and `main()`,
  importing from the two new modules.

No behavior change. Public entry point (`velocity_previewer.main:main`) is
unchanged so `pyproject.toml` scripts entry keeps working.

## Error handling

Unchanged — existing error paths in `utils.py` and the renderer thread keep
their current semantics; tests pin them down.

## Verification

- `pytest` passes locally and in CI.
- `black --check`, `flake8`, and `mypy src/` pass.
- App launches headless (`QT_QPA_PLATFORM=offscreen`) and a render round-trip
  works, confirming the extraction didn't break wiring.
