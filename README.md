# Velocity Template Previewer

This is a simple PyQt5 application for previewing and rendering Velocity templates. Velocity is a template engine used
primarily for generating dynamic web content and transforming data.

## Installation

Before running the application, make sure you have the necessary libraries installed:

```bash
pip install PyQt5 airspeed
```

## Usage

Run the application by executing the following command in your terminal:

```bash
python main.py
```
![Example Template Render](example-template.png)
- The application window will appear with a text editor, a "Render" button, and an output viewer.
- Click the "Open" option in the "File" menu to open an existing Velocity template file (with a .vm extension).
- Edit the template in the text editor.
- Click the "Render" button to render the template. The rendered output will be displayed in the output viewer.
- You can also save your edited template using the "Save" option in the "File" menu.

## Features

- Open existing Velocity template files.
- Edit and save template files.
- Render Velocity templates and display the output.
- Error handling for template rendering.
- Notes
- Ensure that you have the necessary .vm files for previewing.
- The application uses the Airspeed library for template rendering.
- Feel free to use this simple Velocity template previewer to experiment with your Velocity templates.
