# Velocity Template Previewer

[![CI](https://github.com/star7js/vm-visualizer/actions/workflows/ci.yml/badge.svg)](https://github.com/star7js/vm-visualizer/actions/workflows/ci.yml)

A modern, feature-rich PyQt5 application for previewing and rendering Velocity templates with real-time syntax highlighting, validation, and export capabilities.

![Velocity Template Previewer](example-template-render.png)

## Features

### 🎨 **Modern UI/UX**
- Clean, modern interface with tabbed layout
- Syntax highlighting for Velocity templates and JSON data
- Responsive design with customizable splitter panes
- Professional styling with hover effects

### ⚡ **Enhanced Functionality**
- **Real-time syntax highlighting** for Velocity templates and JSON data
- **Background rendering** for better performance
- **Auto-save functionality** (every 30 seconds)
- **Recent files support** with quick access menu
- **Template and data validation** with detailed error messages
- **Export to HTML** with professional styling

### 🔧 **Developer Tools**
- Template syntax validation (Ctrl+Shift+V)
- JSON data validation (Ctrl+Shift+D)
- Error highlighting and detailed error messages
- Progress indicators for long operations
- Settings persistence across sessions

### 📁 **File Management**
- Open/save Velocity templates (.vm files)
- Load JSON data files
- Recent files tracking
- Export rendered output to HTML
- Auto-save with silent operation

## Installation

### Prerequisites
- Python 3.9 or higher
- PyQt5
- Airspeed (Velocity template engine)

### Quick Start

1. **Clone or download the project**
   ```bash
   git clone <repository-url>
   cd vm-visualizer
   ```

2. **Install dependencies**
   ```bash
   # Using pip
   pip install PyQt5 airspeed
   
   # Or using the project's dependency management
   pip install -e .
   ```

3. **Run the application**
   ```bash
   python main.py
   ```

## Usage

### Basic Workflow

1. **Open a template**: Use `File > Open Template` or drag a `.vm` file
2. **Add data**: Switch to the "Data" tab and enter JSON data
3. **Render**: Click "Render Template" or press F5
4. **Export**: Use `Tools > Export as HTML` to save the output

### Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Open Template | Ctrl+O |
| Save Template | Ctrl+S |
| Save Template As | Ctrl+Shift+S |
| Render Template | F5 |
| Validate Template | Ctrl+Shift+V |
| Validate Data | Ctrl+Shift+D |
| Exit | Ctrl+Q |

### Example Files

The project includes example files to get you started:

- `example-template.vm` - A comprehensive Velocity template demonstrating various features
- `example-data.json` - Sample JSON data that works with the example template

## Template Features

The application supports all standard Velocity template features:

### Variables
```velocity
$variable
${variable}
```

### Directives
```velocity
#set($variable = "value")
#if($condition)
    content
#end
#foreach($item in $list)
    $item
#end
```

### Comments
```velocity
## Single line comment
#*
   Multi-line comment
*#
```

## Project Structure

```
vm-visualizer/
├── main.py                 # Main application entry point
├── utils.py               # Utility functions and constants
├── syntax_highlighters.py # Syntax highlighting classes
├── example-template.vm    # Example Velocity template
├── example-data.json      # Example JSON data
├── pyproject.toml         # Project configuration
└── README.md             # This file
```

## Development

### Code Organization

The application is organized into modular components:

- **`main.py`**: Main application window and UI logic
- **`utils.py`**: Utility functions, constants, and template processing
- **`syntax_highlighters.py`**: Syntax highlighting for different languages

### Adding Features

1. **New syntax highlighting**: Add classes to `syntax_highlighters.py`
2. **Utility functions**: Add to `utils.py`
3. **UI features**: Extend the main window class in `main.py`

### Building

The project uses modern Python packaging:

```bash
# Install in development mode
pip install -e .

# Build distribution
python -m build
```

## Configuration

### Settings

The application automatically saves and restores:
- Window geometry and position
- Splitter pane sizes
- Recent files list (last 10 files)

Settings are stored in the system's application data directory.

### Customization

You can customize the application by modifying:
- `utils.py` - Constants and styling
- `syntax_highlighters.py` - Color schemes
- `main.py` - UI layout and behavior

## Troubleshooting

### Common Issues

1. **Template not rendering**: Check for syntax errors using `Tools > Validate Template`
2. **JSON errors**: Use `Tools > Validate Data` to check JSON syntax
3. **Performance issues**: Large templates are rendered in background threads

### Error Messages

The application provides detailed error messages for:
- Template syntax errors
- JSON parsing errors
- File I/O errors
- Rendering errors

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Acknowledgments

- Built with [PyQt5](https://www.riverbankcomputing.com/software/pyqt/)
- Uses [Airspeed](https://github.com/purcell/airspeed) for Velocity template processing
- Inspired by modern code editors and IDEs

---

**Happy templating!** 🚀
