# Velocity Template Previewer

[![CI](https://github.com/star7js/velocity-previewer/actions/workflows/ci.yml/badge.svg)](https://github.com/star7js/velocity-previewer/actions/workflows/ci.yml) [![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/) ![PyQt5](https://img.shields.io/badge/PyQt5-5.15+-41CD52?logo=qt&logoColor=white)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Desktop application for previewing and rendering Apache Velocity templates with real-time syntax highlighting and validation. Perfect for developers working with Atlassian products (Jira, Confluence), ScriptRunner, email templates, and web applications.

![Velocity Template Previewer](examples/example-template-render.png)

## What is This?

Apache Velocity is a Java-based template engine commonly used in:
- **Atlassian Products**: Jira email templates, Confluence macros, ScriptRunner scripts
- **Email Systems**: Dynamic email generation
- **Web Applications**: Server-side templating
- **Code Generation**: Template-based code scaffolding

This tool lets you preview and test your Velocity templates instantly without deploying to production.

## Features

- **Real-time Preview**: See changes as you type
- **Syntax Highlighting**: Color-coded templates and JSON data
- **Validation**: Catch errors before deployment
- **Background Rendering**: Smooth performance with large templates
- **Auto-save**: Never lose your work (saves every 30 seconds)
- **Export**: Generate static HTML from your templates
- **Dark Mode**: Easy on the eyes
- **Recent Files**: Quick access to your projects

## Installation

**Requirements:** Python 3.9+ (Windows, macOS, Linux)

```bash
git clone https://github.com/star7js/velocity-previewer.git
cd velocity-previewer
pip install -e .
velocity-previewer
```

## Quick Start

1. **Open a template**: File > Open or Ctrl+O
2. **Add your data**: Switch to Data tab, paste JSON
3. **Render**: Press F5
4. **Export** (optional): File > Export to HTML

Try the included `examples/example-template.vm` with `examples/example-data.json` to see it in action.

## Use Cases

### Atlassian/ScriptRunner Development
Test Jira email notifications, Confluence macros, or ScriptRunner templates locally before deploying:

```velocity
#if($issue.priority.name == "Critical")
  <span style="color: red;">$issue.key - $issue.summary</span>
#end
```

### Email Template Design
Preview dynamic email templates with test data:

```velocity
Hello $customer.name,

Your order #$order.id has shipped!
#foreach($item in $order.items)
  - $item.name (Qty: $item.quantity)
#end
```

### Dynamic Reports
Generate reports from JSON data without manual formatting.

## Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Render Template | F5 |
| Open Template | Ctrl+O |
| Save Template | Ctrl+S |
| Validate Template | Ctrl+Shift+V |
| Validate Data | Ctrl+Shift+D |

## Supported Velocity Syntax

- **Variables**: `$variable`, `${variable}`
- **Directives**: `#if`, `#foreach`, `#set`, `#macro`
- **Comments**: `##` (single line), `#* ... *#` (multi-line)
- **Properties**: `$object.property`, `$array[0]`
- **Methods**: `$string.substring(0, 5)`

Full Apache Velocity specification supported via Airspeed engine.

## Platform Support

- ✅ Windows 10/11
- ✅ macOS 10.15+
- ✅ Linux (Ubuntu, Fedora, Arch)

## Development

```bash
# Install dependencies
pip install -e .

# Run tests
python tests/test_functionality.py

# Project structure
├── src/velocity_previewer/    # Main package
│   ├── main.py                # Application UI and logic
│   ├── utils.py               # Template processing
│   └── syntax_highlighters.py # Syntax highlighting
├── examples/                  # Example templates and data
├── tests/                     # Test files
└── pyproject.toml            # Project configuration
```

Settings (window size, recent files) are saved to:
- **Windows**: `%APPDATA%/VelocityPreviewer`
- **macOS**: `~/Library/Application Support/VelocityPreviewer`
- **Linux**: `~/.config/VelocityPreviewer`

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Template won't render | Use `Tools > Validate Template` (Ctrl+Shift+V) to see errors |
| JSON parse errors | Use `Tools > Validate Data` (Ctrl+Shift+D) to check format |
| Slow performance | Large templates render in background automatically |
| App won't start | Ensure PyQt5 is installed: `pip install PyQt5` |

## Roadmap

- [ ] Live preview mode (render on every keystroke)
- [ ] Multiple data sets for testing
- [ ] Template snippet library
- [ ] Velocity macro autocomplete

## License

MIT License

## Built With

- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) - Cross-platform UI framework
- [Airspeed](https://github.com/purcell/airspeed) - Python implementation of Apache Velocity
