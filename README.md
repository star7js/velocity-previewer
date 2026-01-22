# Velocity Template Previewer

[![CI](https://github.com/star7js/velocity-previewer/actions/workflows/ci.yml/badge.svg)](https://github.com/star7js/velocity-previewer/actions/workflows/ci.yml)

Desktop application for previewing and rendering Velocity templates with syntax highlighting and validation.

![Velocity Template Previewer](example-template-render.png)

## Features

- Syntax highlighting for Velocity templates and JSON data
- Real-time template validation with error messages
- Background rendering for performance
- Auto-save (every 30 seconds)
- Export rendered output to HTML
- Recent files tracking
- Dark mode support

## Installation

Requires Python 3.9+

```bash
git clone https://github.com/star7js/velocity-previewer.git
cd velocity-previewer
pip install PyQt5 airspeed
python main.py
```

## Usage

1. Open a Velocity template (.vm file)
2. Add JSON data in the Data tab
3. Press F5 to render
4. Export to HTML if needed

### Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Render Template | F5 |
| Open Template | Ctrl+O |
| Save Template | Ctrl+S |
| Validate Template | Ctrl+Shift+V |
| Validate Data | Ctrl+Shift+D |

See `example-template.vm` and `example-data.json` for examples.

## Supported Velocity Features

Supports standard Velocity syntax: variables (`$var`), directives (`#if`, `#foreach`, `#set`), and comments (`##`).

## Development

Project structure:
- `main.py` - Application UI and logic
- `utils.py` - Template processing and utilities
- `syntax_highlighters.py` - Syntax highlighting

Settings (window size, recent files) are automatically saved to your system's app data directory.

## Troubleshooting

- **Template errors**: Use `Tools > Validate Template` (Ctrl+Shift+V)
- **JSON errors**: Use `Tools > Validate Data` (Ctrl+Shift+D)
- **Performance**: Large templates render in background threads

## License

MIT License

## Built With

- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) - UI framework
- [Airspeed](https://github.com/purcell/airspeed) - Velocity template engine
