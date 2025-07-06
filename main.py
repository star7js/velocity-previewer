import sys
import os
from typing import Optional, Dict, Any
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QTextEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QFileDialog,
    QAction,
    QLabel,
    QSplitter,
    QMessageBox,
    QToolBar,
    QProgressBar,
    QTabWidget,
    QTextBrowser,
)
from PyQt5.QtCore import Qt, QSize, QTimer, QSettings, QThread, pyqtSignal
from PyQt5.QtGui import QIcon, QKeySequence, QFont, QColor
from datetime import datetime

# Import our modules
from utils import (
    APP_NAME,
    DEFAULT_WINDOW_WIDTH,
    DEFAULT_WINDOW_HEIGHT,
    TEMPLATE_FILE_FILTER,
    JSON_FILE_FILTER,
    TEXT_FILE_FILTER,
    HTML_FILE_FILTER,
    AUTO_SAVE_INTERVAL,
    validate_template_syntax,
    validate_json_data,
    render_template,
    create_html_export,
    format_error_message,
)
from syntax_highlighters import (
    VelocitySyntaxHighlighter,
    JSONSyntaxHighlighter,
    OutputSyntaxHighlighter,
)

DEFAULT_FONT = "Menlo"  # macOS native monospace font


class TemplateRenderer(QThread):
    """Background thread for template rendering."""

    rendered = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, template_str: str, context_data: Dict[str, Any]):
        super().__init__()
        self.template_str = template_str
        self.context_data = context_data

    def run(self):
        """Render the template in background thread."""
        success, result = render_template(self.template_str, self.context_data)
        if success:
            self.rendered.emit(result)
        else:
            self.error.emit(result)


class VelocityTemplatePreviewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self._current_template_file_path: Optional[str] = None
        self._current_data_file_path: Optional[str] = None
        self._settings = QSettings("VelocityTemplatePreviewer", "Settings")
        self._auto_save_timer = QTimer()
        self._renderer_thread: Optional[TemplateRenderer] = None
        self._dark_mode = True  # Default to dark mode

        self._load_settings()
        self.initUI()
        self._setup_auto_save()

    def _load_settings(self):
        """Load application settings."""
        self._recent_files = self._settings.value("recent_files", [])
        self._window_geometry = self._settings.value("window_geometry")
        self._splitter_sizes = self._settings.value("splitter_sizes")

    def _save_settings(self):
        """Save application settings."""
        self._settings.setValue("recent_files", self._recent_files[:10])  # Keep last 10
        self._settings.setValue("window_geometry", self.saveGeometry())
        self._settings.setValue("splitter_sizes", self.mainSplitter.saveState())

    def _setup_auto_save(self):
        """Setup auto-save functionality."""
        self._auto_save_timer.timeout.connect(self._auto_save)
        self._auto_save_timer.start(AUTO_SAVE_INTERVAL)

    def _auto_save(self):
        """Auto-save current template if modified."""
        if (
            self._current_template_file_path
            and self.templateEditor.document().isModified()
        ):
            self._save_template_to_path(self._current_template_file_path, silent=True)

    def initUI(self):
        self.setWindowTitle(APP_NAME)

        # Restore window geometry or use defaults
        if self._window_geometry:
            self.restoreGeometry(self._window_geometry)
        else:
            self.setGeometry(100, 100, DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)

        self._create_widgets()
        self._create_layouts()
        self._create_menu_bar()
        self._create_toolbar()
        self._create_status_bar()
        self._connect_signals()
        self._apply_styling()

        self.statusBar().showMessage("Ready")

    def _create_widgets(self):
        """Create and configure UI widgets."""
        # Template editor with syntax highlighting
        self.templateEditor = QTextEdit()
        self.templateEditor.setPlaceholderText(
            "Enter your Velocity Template (.vm) code here..."
        )
        self.templateEditor.setAcceptRichText(False)
        self.templateEditor.setFont(QFont(DEFAULT_FONT, 11))
        self.templateHighlighter = VelocitySyntaxHighlighter(
            self.templateEditor.document()
        )
        # Explicit palette for text color
        pal = self.templateEditor.palette()
        pal.setColor(self.templateEditor.backgroundRole(), QColor("#ffffff"))
        pal.setColor(self.templateEditor.foregroundRole(), QColor("#222222"))
        self.templateEditor.setPalette(pal)
        self.templateEditor.setStyleSheet("color: #222; background: #fff;")

        # Data editor with JSON syntax highlighting
        self.dataEditor = QTextEdit()
        self.dataEditor.setPlaceholderText(
            'Enter JSON data for the template here...\nExample: {"name": "World", "items": [1, 2, 3]}'
        )
        self.dataEditor.setAcceptRichText(False)
        self.dataEditor.setFont(QFont(DEFAULT_FONT, 11))
        self.jsonHighlighter = JSONSyntaxHighlighter(self.dataEditor.document())
        pal = self.dataEditor.palette()
        pal.setColor(self.dataEditor.backgroundRole(), QColor("#ffffff"))
        pal.setColor(self.dataEditor.foregroundRole(), QColor("#222222"))
        self.dataEditor.setPalette(pal)
        self.dataEditor.setStyleSheet("color: #222; background: #fff;")

        # Output viewer with better formatting
        self.outputViewer = QTextBrowser()
        self.outputViewer.setPlaceholderText("Rendered output will appear here.")
        self.outputViewer.setFont(QFont(DEFAULT_FONT, 11))
        self.outputViewer.setOpenExternalLinks(True)
        self.outputHighlighter = OutputSyntaxHighlighter(self.outputViewer.document())
        pal = self.outputViewer.palette()
        pal.setColor(self.outputViewer.backgroundRole(), QColor("#ffffff"))
        pal.setColor(self.outputViewer.foregroundRole(), QColor("#222222"))
        self.outputViewer.setPalette(pal)
        self.outputViewer.setStyleSheet("color: #222; background: #fff;")

        # Buttons with better styling
        self.renderButton = QPushButton("Render Template")
        self.renderButton.setIcon(
            self._get_stock_icon(QApplication.style().SP_MediaPlay)
        )
        self.renderButton.setMinimumHeight(40)

        self.clearDataButton = QPushButton("Clear Data")
        self.clearDataButton.setIcon(
            self._get_stock_icon(QApplication.style().SP_DialogResetButton)
        )

        # Progress bar for rendering
        self.progressBar = QProgressBar()
        self.progressBar.setVisible(False)

    def _create_layouts(self):
        """Create the main layout with improved organization."""
        # Main horizontal splitter
        self.mainSplitter = QSplitter(Qt.Horizontal)

        # Left pane with tabs for template and data
        leftPaneWidget = QWidget()
        leftLayout = QVBoxLayout(leftPaneWidget)

        # Create tab widget for template and data
        self.tabWidget = QTabWidget()

        # Template tab
        templateTab = QWidget()
        templateLayout = QVBoxLayout(templateTab)
        templateLabel = QLabel("Velocity Template Editor (.vm):")
        templateLabel.setStyleSheet(
            "font-weight: bold; font-size: 12px; margin-bottom: 5px;"
        )
        templateLayout.addWidget(templateLabel)
        templateLayout.addWidget(self.templateEditor)
        self.tabWidget.addTab(templateTab, "Template")

        # Data tab
        dataTab = QWidget()
        dataLayout = QVBoxLayout(dataTab)
        dataLabel = QLabel("Template Data (JSON):")
        dataLabel.setStyleSheet(
            "font-weight: bold; font-size: 12px; margin-bottom: 5px;"
        )
        dataLayout.addWidget(dataLabel)
        dataLayout.addWidget(self.dataEditor)

        # Data buttons
        dataButtonsLayout = QHBoxLayout()
        dataButtonsLayout.addWidget(self.clearDataButton)
        dataButtonsLayout.addStretch()
        dataLayout.addLayout(dataButtonsLayout)
        self.tabWidget.addTab(dataTab, "Data")

        leftLayout.addWidget(self.tabWidget)

        # Right pane for output
        rightPaneWidget = QWidget()
        rightLayout = QVBoxLayout(rightPaneWidget)

        outputLabel = QLabel("Rendered Output:")
        outputLabel.setStyleSheet(
            "font-weight: bold; font-size: 12px; margin-bottom: 5px;"
        )
        rightLayout.addWidget(outputLabel)
        rightLayout.addWidget(self.outputViewer)

        # Output controls
        outputControlsLayout = QHBoxLayout()
        outputControlsLayout.addWidget(self.renderButton)
        outputControlsLayout.addWidget(self.progressBar)
        outputControlsLayout.addStretch()
        rightLayout.addLayout(outputControlsLayout)

        self.mainSplitter.addWidget(leftPaneWidget)
        self.mainSplitter.addWidget(rightPaneWidget)

        # Restore splitter sizes or use defaults
        if self._splitter_sizes:
            self.mainSplitter.restoreState(self._splitter_sizes)
        else:
            self.mainSplitter.setSizes(
                [int(DEFAULT_WINDOW_WIDTH * 0.6), int(DEFAULT_WINDOW_WIDTH * 0.4)]
            )

        centralWidget = QWidget()
        centralLayout = QVBoxLayout(centralWidget)
        centralLayout.addWidget(self.mainSplitter)
        self.setCentralWidget(centralWidget)

    def _create_status_bar(self):
        """Create an enhanced status bar."""
        statusBar = self.statusBar()
        statusBar.setStyleSheet("QStatusBar { border-top: 1px solid #ccc; }")

        # Add a permanent message area
        self.statusLabel = QLabel("Ready")
        statusBar.addPermanentWidget(self.statusLabel)

    def _apply_styling(self):
        """Apply modern styling to the application."""
        if self._dark_mode:
            self.setStyleSheet(
                """
                QMainWindow {
                    background-color: #23272e;
                }
                QTabWidget::pane {
                    border: 1px solid #444;
                    background-color: #181a20;
                }
                QTabBar::tab {
                    background-color: #23272e;
                    color: #eee;
                    padding: 8px 16px;
                    margin-right: 2px;
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                }
                QTabBar::tab:selected {
                    background-color: #181a20;
                    border-bottom: 2px solid #2980b9;
                }
                QPushButton {
                    background-color: #2980b9;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #3498db;
                }
                QPushButton:pressed {
                    background-color: #21618c;
                }
                QTextEdit, QTextBrowser {
                    border: 1px solid #444;
                    border-radius: 4px;
                    padding: 8px;
                    background-color: #181a20;
                    color: #eee;
                    selection-background-color: #2980b9;
                    selection-color: #fff;
                }
                QLabel {
                    color: #eee;
                }
                QStatusBar {
                    background: #23272e;
                    color: #eee;
                }
            """
            )
        else:
            self.setStyleSheet(
                """
                QMainWindow {
                    background-color: #f5f5f5;
                }
                QTabWidget::pane {
                    border: 1px solid #ccc;
                    background-color: white;
                }
                QTabBar::tab {
                    background-color: #e0e0e0;
                    color: #222;
                    padding: 8px 16px;
                    margin-right: 2px;
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                }
                QTabBar::tab:selected {
                    background-color: white;
                    border-bottom: 2px solid #2980b9;
                }
                QPushButton {
                    background-color: #2980b9;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #3498db;
                }
                QPushButton:pressed {
                    background-color: #21618c;
                }
                QTextEdit, QTextBrowser {
                    border: 1px solid #ccc;
                    border-radius: 4px;
                    padding: 8px;
                    background-color: white;
                    color: #222;
                    selection-background-color: #2980b9;
                    selection-color: #fff;
                }
                QLabel {
                    color: #2c3e50;
                }
                QStatusBar {
                    background: #f5f5f5;
                    color: #222;
                }
            """
            )

    def _get_stock_icon(self, standard_icon_enum) -> QIcon:
        return self.style().standardIcon(standard_icon_enum)

    def _create_menu_bar(self):
        menuBar = self.menuBar()

        # File menu
        fileMenu = menuBar.addMenu("&File")

        self.openTemplateAction = QAction(
            self._get_stock_icon(QApplication.style().SP_DialogOpenButton),
            "&Open Template...",
            self,
        )
        self.openTemplateAction.setShortcut(QKeySequence.Open)
        fileMenu.addAction(self.openTemplateAction)

        self.openDataAction = QAction(
            self._get_stock_icon(QApplication.style().SP_FileLinkIcon),
            "Open D&ata File...",
            self,
        )
        fileMenu.addAction(self.openDataAction)

        # Recent files submenu
        self.recentFilesMenu = fileMenu.addMenu("&Recent Files")
        self._update_recent_files_menu()

        fileMenu.addSeparator()

        self.saveTemplateAction = QAction(
            self._get_stock_icon(QApplication.style().SP_DialogSaveButton),
            "&Save Template",
            self,
        )
        self.saveTemplateAction.setShortcut(QKeySequence.Save)
        fileMenu.addAction(self.saveTemplateAction)

        self.saveTemplateAsAction = QAction("Save Template &As...", self)
        self.saveTemplateAsAction.setShortcut(QKeySequence.SaveAs)
        fileMenu.addAction(self.saveTemplateAsAction)

        self.saveOutputAction = QAction(
            self._get_stock_icon(QApplication.style().SP_DialogSaveButton),
            "Save &Output As...",
            self,
        )
        fileMenu.addAction(self.saveOutputAction)

        fileMenu.addSeparator()
        exitAction = QAction(
            self._get_stock_icon(QApplication.style().SP_DialogCloseButton),
            "E&xit",
            self,
        )
        exitAction.setShortcut(QKeySequence.Quit)
        exitAction.triggered.connect(self.close)
        fileMenu.addAction(exitAction)

        # Edit menu
        editMenu = menuBar.addMenu("&Edit")
        self.renderAction = QAction(
            self._get_stock_icon(QApplication.style().SP_MediaPlay), "&Render", self
        )
        self.renderAction.setShortcut("F5")
        editMenu.addAction(self.renderAction)

        clearMenu = editMenu.addMenu("&Clear")
        self.clearTemplateAction = QAction("Clear Template", self)
        clearMenu.addAction(self.clearTemplateAction)
        self.clearDataActionMenu = QAction("Clear Data", self)
        clearMenu.addAction(self.clearDataActionMenu)
        self.clearOutputAction = QAction("Clear Output", self)
        clearMenu.addAction(self.clearOutputAction)

        # Tools menu
        toolsMenu = menuBar.addMenu("&Tools")
        self.validateTemplateAction = QAction("&Validate Template", self)
        self.validateTemplateAction.setShortcut("Ctrl+Shift+V")
        toolsMenu.addAction(self.validateTemplateAction)

        self.validateDataAction = QAction("Validate &Data", self)
        self.validateDataAction.setShortcut("Ctrl+Shift+D")
        toolsMenu.addAction(self.validateDataAction)

        toolsMenu.addSeparator()
        self.exportHtmlAction = QAction("Export as &HTML", self)
        toolsMenu.addAction(self.exportHtmlAction)

        # Dark mode toggle
        self.toggleDarkModeAction = QAction("Toggle &Dark Mode", self)
        self.toggleDarkModeAction.setCheckable(True)
        self.toggleDarkModeAction.setChecked(self._dark_mode)
        self.toggleDarkModeAction.triggered.connect(self.toggle_dark_mode)
        toolsMenu.addSeparator()
        toolsMenu.addAction(self.toggleDarkModeAction)

        # Help menu
        helpMenu = menuBar.addMenu("&Help")
        aboutAction = QAction("&About", self)
        aboutAction.triggered.connect(self._show_about)
        helpMenu.addAction(aboutAction)

    def _create_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(16, 16))  # Smaller icons for toolbar
        self.addToolBar(toolbar)

        toolbar.addAction(self.openTemplateAction)
        toolbar.addAction(self.saveTemplateAction)
        toolbar.addSeparator()
        toolbar.addAction(self.renderAction)

    def _connect_signals(self):
        # File actions
        self.openTemplateAction.triggered.connect(self.open_template_file)
        self.openDataAction.triggered.connect(self.open_data_file)
        self.saveTemplateAction.triggered.connect(self.save_template_file)
        self.saveTemplateAsAction.triggered.connect(self.save_template_file_as)
        self.saveOutputAction.triggered.connect(self.save_output_file)

        # Edit actions
        self.renderAction.triggered.connect(self.render_template)
        self.renderButton.clicked.connect(self.render_template)

        # Clear actions
        self.clearDataButton.clicked.connect(self.clear_data_editor)
        self.clearTemplateAction.triggered.connect(self.clear_template_editor)
        self.clearDataActionMenu.triggered.connect(self.clear_data_editor)
        self.clearOutputAction.triggered.connect(self.clear_output_viewer)

        # Tools actions
        self.validateTemplateAction.triggered.connect(self.validate_template)
        self.validateDataAction.triggered.connect(self.validate_data)
        self.exportHtmlAction.triggered.connect(self.export_as_html)

    def _update_window_title(self):
        title = APP_NAME
        if self._current_template_file_path:
            title = f"{self._current_template_file_path} - {APP_NAME}"
        self.setWindowTitle(title)

    def open_template_file(self):
        fileName, _ = QFileDialog.getOpenFileName(
            self,
            "Open Template File",
            self._current_template_file_path or "",
            TEMPLATE_FILE_FILTER,
        )
        if fileName:
            try:
                with open(fileName, "r", encoding="utf-8") as file:
                    self.templateEditor.setText(file.read())
                self._current_template_file_path = fileName
                self._update_window_title()
                self._add_to_recent_files(fileName)
                self.statusBar().showMessage(f"Template '{fileName}' loaded.", 5000)
            except IOError as e:
                QMessageBox.critical(
                    self, "Error Opening File", f"Could not open template file:\n{e}"
                )
                self.statusBar().showMessage(f"Error opening template: {e}", 5000)

    def open_data_file(self):
        fileName, _ = QFileDialog.getOpenFileName(
            self, "Open Data File", self._current_data_file_path or "", JSON_FILE_FILTER
        )
        if fileName:
            try:
                with open(fileName, "r", encoding="utf-8") as file:
                    self.dataEditor.setText(file.read())
                self._current_data_file_path = fileName
                self.statusBar().showMessage(f"Data file '{fileName}' loaded.", 5000)
            except IOError as e:
                QMessageBox.critical(
                    self, "Error Opening File", f"Could not open data file:\n{e}"
                )
                self.statusBar().showMessage(f"Error opening data file: {e}", 5000)

    def _save_template_to_path(self, file_path: str, silent: bool = False) -> bool:
        if not file_path:
            return False
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(self.templateEditor.toPlainText())
            self._current_template_file_path = file_path
            self._update_window_title()
            if not silent:
                self.statusBar().showMessage(f"Template saved to '{file_path}'.", 5000)
            return True
        except IOError as e:
            QMessageBox.critical(
                self, "Error Saving File", f"Could not save template file:\n{e}"
            )
            self.statusBar().showMessage(f"Error saving template: {e}", 5000)
            return False

    def save_template_file(self):
        if self._current_template_file_path:
            self._save_template_to_path(self._current_template_file_path)
        else:
            self.save_template_file_as()

    def save_template_file_as(self):
        fileName, _ = QFileDialog.getSaveFileName(
            self,
            "Save Template File As",
            self._current_template_file_path or "",
            TEMPLATE_FILE_FILTER,
        )
        if fileName:
            self._save_template_to_path(fileName)

    def save_output_file(self):
        if not self.outputViewer.toPlainText().strip():
            QMessageBox.information(self, "Empty Output", "There is no output to save.")
            return

        fileName, _ = QFileDialog.getSaveFileName(
            self, "Save Rendered Output As", "", TEXT_FILE_FILTER
        )
        if fileName:
            try:
                with open(fileName, "w", encoding="utf-8") as file:
                    file.write(self.outputViewer.toPlainText())
                self.statusBar().showMessage(f"Output saved to '{fileName}'.", 5000)
            except IOError as e:
                QMessageBox.critical(
                    self, "Error Saving File", f"Could not save output file:\n{e}"
                )
                self.statusBar().showMessage(f"Error saving output: {e}", 5000)

    def clear_data_editor(self):
        self.dataEditor.clear()
        self.statusBar().showMessage("Data editor cleared.", 3000)

    def render_template(self):
        """Render the template with the provided data."""
        template_str = self.templateEditor.toPlainText()
        data_str = self.dataEditor.toPlainText()
        if not template_str.strip():
            self.outputViewer.setText("Template is empty. Nothing to render.")
            self.statusBar().showMessage("Render attempted with empty template.", 3000)
            return
        # Validate JSON data
        is_valid, error_message, context_data = validate_json_data(data_str)
        if not is_valid:
            self.outputViewer.setText(
                format_error_message(error_message, "JSON Data Error")
            )
            self.statusBar().showMessage("JSON Data Error.", 5000)
            return
        if context_data is None:
            context_data = {}

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
        # Show progress and disable render button
        self.progressBar.setVisible(True)
        self.progressBar.setRange(0, 0)  # Indeterminate progress
        self.renderButton.setEnabled(False)
        self.statusLabel.setText("Rendering template...")
        # Create and start renderer thread
        self._renderer_thread = TemplateRenderer(template_str, context_data)
        self._renderer_thread.rendered.connect(self._on_template_rendered)
        self._renderer_thread.error.connect(self._on_template_error)
        self._renderer_thread.finished.connect(self._on_render_finished)
        self._renderer_thread.start()

    def _on_template_rendered(self, rendered_text: str):
        """Handle successful template rendering."""
        self.outputViewer.setText(rendered_text)
        self.statusLabel.setText("Template rendered successfully")
        self.statusBar().showMessage("Template rendered successfully.", 3000)

    def _on_template_error(self, error_message: str):
        """Handle template rendering error."""
        self.outputViewer.setText(error_message)
        self.statusLabel.setText("Rendering failed")
        self.statusBar().showMessage("Template Rendering Error.", 5000)

    def _on_render_finished(self):
        """Handle render thread completion."""
        self.progressBar.setVisible(False)
        self.renderButton.setEnabled(True)
        self._renderer_thread = None

    def validate_template(self):
        """Validate the current template syntax."""
        template_str = self.templateEditor.toPlainText()
        is_valid, error_message = validate_template_syntax(template_str)

        if is_valid:
            QMessageBox.information(self, "Validation", "Template syntax is valid!")
        else:
            QMessageBox.critical(
                self, "Validation Error", f"Template syntax error:\n{error_message}"
            )

    def validate_data(self):
        """Validate the current JSON data."""
        data_str = self.dataEditor.toPlainText()
        is_valid, error_message, _ = validate_json_data(data_str)

        if is_valid:
            QMessageBox.information(self, "Validation", "JSON data is valid!")
        else:
            QMessageBox.critical(
                self, "Validation Error", f"JSON syntax error:\n{error_message}"
            )

    def export_as_html(self):
        """Export the rendered output as HTML."""
        if not self.outputViewer.toPlainText().strip():
            QMessageBox.information(self, "Export", "There is no output to export.")
            return

        fileName, _ = QFileDialog.getSaveFileName(
            self, "Export as HTML", "", HTML_FILE_FILTER
        )
        if fileName:
            try:
                html_content = create_html_export(self.outputViewer.toPlainText())
                with open(fileName, "w", encoding="utf-8") as file:
                    file.write(html_content)
                self.statusBar().showMessage(f"HTML exported to '{fileName}'.", 5000)
            except IOError as e:
                QMessageBox.critical(
                    self, "Export Error", f"Could not export HTML file:\n{e}"
                )

    def clear_template_editor(self):
        """Clear the template editor."""
        self.templateEditor.clear()
        self.statusBar().showMessage("Template editor cleared.", 3000)

    def clear_output_viewer(self):
        """Clear the output viewer."""
        self.outputViewer.clear()
        self.statusBar().showMessage("Output viewer cleared.", 3000)

    def _update_recent_files_menu(self):
        """Update the recent files menu."""
        self.recentFilesMenu.clear()

        if not self._recent_files:
            noRecentAction = QAction("No recent files", self)
            noRecentAction.setEnabled(False)
            self.recentFilesMenu.addAction(noRecentAction)
            return

        for file_path in self._recent_files:
            if os.path.exists(file_path):
                action = QAction(os.path.basename(file_path), self)
                action.setData(file_path)
                action.triggered.connect(
                    lambda checked, path=file_path: self._open_recent_file(path)
                )
                self.recentFilesMenu.addAction(action)

        self.recentFilesMenu.addSeparator()
        clearRecentAction = QAction("Clear Recent Files", self)
        clearRecentAction.triggered.connect(self._clear_recent_files)
        self.recentFilesMenu.addAction(clearRecentAction)

    def _open_recent_file(self, file_path: str):
        """Open a file from the recent files list."""
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                self.templateEditor.setText(file.read())
            self._current_template_file_path = file_path
            self._update_window_title()
            self._add_to_recent_files(file_path)
            self.statusBar().showMessage(f"Recent file '{file_path}' loaded.", 5000)
        except IOError as e:
            QMessageBox.critical(
                self, "Error Opening File", f"Could not open recent file:\n{e}"
            )

    def _add_to_recent_files(self, file_path: str):
        """Add a file to the recent files list."""
        if file_path in self._recent_files:
            self._recent_files.remove(file_path)
        self._recent_files.insert(0, file_path)
        self._recent_files = self._recent_files[:10]  # Keep only last 10
        self._update_recent_files_menu()

    def _clear_recent_files(self):
        """Clear the recent files list."""
        self._recent_files.clear()
        self._update_recent_files_menu()

    def _show_about(self):
        """Show the about dialog."""
        QMessageBox.about(
            self,
            "About Velocity Template Previewer",
            """<h3>Velocity Template Previewer</h3>
            <p>Version 1.0</p>
            <p>A modern PyQt5 application for previewing and rendering Velocity templates.</p>
            <p>Features:</p>
            <ul>
                <li>Syntax highlighting for Velocity templates and JSON data</li>
                <li>Real-time template validation</li>
                <li>Background rendering for better performance</li>
                <li>Auto-save functionality</li>
                <li>Recent files support</li>
                <li>Export to HTML</li>
            </ul>
            <p>Built with PyQt5 and Airspeed.</p>""",
        )

    def closeEvent(self, event):
        """Handle application close event."""
        self._save_settings()
        event.accept()

    def toggle_dark_mode(self):
        self._dark_mode = not self._dark_mode
        self.toggleDarkModeAction.setChecked(self._dark_mode)
        self._apply_styling()


def main():
    app = QApplication(sys.argv)
    # You can set a style here if you want, e.g., "Fusion"
    # app.setStyle("Fusion")
    mainWin = VelocityTemplatePreviewer()
    mainWin.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
