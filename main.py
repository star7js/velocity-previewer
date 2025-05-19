import sys
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QWidget, QFileDialog, QAction, QLabel, QSplitter, QMessageBox, QToolBar
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QKeySequence

from airspeed import Template
from airspeed import TemplateError  

# --- Constants ---
APP_NAME = "Velocity Template Previewer"
DEFAULT_WINDOW_WIDTH = 1000
DEFAULT_WINDOW_HEIGHT = 700
TEMPLATE_FILE_FILTER = "Velocity Templates (*.vm);;All Files (*)"
JSON_FILE_FILTER = "JSON Files (*.json);;All Files (*)"
TEXT_FILE_FILTER = "Text Files (*.txt);;All Files (*)"


class VelocityTemplatePreviewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self._current_template_file_path: str | None = None
        self._current_data_file_path: str | None = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle(APP_NAME)
        self.setGeometry(100, 100, DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)  # x, y, w, h

        self._create_widgets()
        self._create_layouts()
        self._create_menu_bar()
        self._create_toolbar()
        self._connect_signals()

        self.statusBar().showMessage("Ready")

    def _create_widgets(self):
        self.templateEditor = QTextEdit()
        self.templateEditor.setPlaceholderText("Enter your Velocity Template (.vm) code here...")
        self.templateEditor.setAcceptRichText(False)  # Ensure plain text

        self.dataEditor = QTextEdit()
        self.dataEditor.setPlaceholderText("Enter JSON data for the template here...\nExample: {\"name\": \"World\"}")
        self.dataEditor.setAcceptRichText(False)

        self.outputViewer = QTextEdit()
        self.outputViewer.setReadOnly(True)
        self.outputViewer.setPlaceholderText("Rendered output will appear here.")
        self.outputViewer.setAcceptRichText(False)

        self.renderButton = QPushButton("Render Template")
        self.renderButton.setIcon(self._get_stock_icon(QApplication.style().SP_MediaPlay))

        self.clearDataButton = QPushButton("Clear Data")
        self.clearDataButton.setIcon(self._get_stock_icon(QApplication.style().SP_DialogResetButton))

    def _create_layouts(self):
        # Main horizontal splitter: Left (Inputs) | Right (Output)
        mainSplitter = QSplitter(Qt.Horizontal)

        # Left pane: Vertical layout for Template and Data editors
        leftPaneWidget = QWidget()
        leftLayout = QVBoxLayout(leftPaneWidget)

        templateLabel = QLabel("Velocity Template Editor (.vm):")
        dataLabel = QLabel("Template Data (JSON):")

        leftLayout.addWidget(templateLabel)
        leftLayout.addWidget(self.templateEditor, 3)  # Stretch factor for template editor
        leftLayout.addWidget(dataLabel)
        leftLayout.addWidget(self.dataEditor, 1)  # Stretch factor for data editor

        dataButtonsLayout = QHBoxLayout()
        dataButtonsLayout.addWidget(self.clearDataButton)
        dataButtonsLayout.addStretch()
        leftLayout.addLayout(dataButtonsLayout)

        mainSplitter.addWidget(leftPaneWidget)

        # Right pane: Vertical layout for Output and Render button
        rightPaneWidget = QWidget()
        rightLayout = QVBoxLayout(rightPaneWidget)

        outputLabel = QLabel("Rendered Output:")
        rightLayout.addWidget(outputLabel)
        rightLayout.addWidget(self.outputViewer, 1)  # Stretch factor
        rightLayout.addWidget(self.renderButton)

        mainSplitter.addWidget(rightPaneWidget)

        # Set initial sizes for splitter panes
        mainSplitter.setSizes([int(DEFAULT_WINDOW_WIDTH * 0.5), int(DEFAULT_WINDOW_WIDTH * 0.5)])

        centralWidget = QWidget()
        centralLayout = QVBoxLayout(centralWidget)
        centralLayout.addWidget(mainSplitter)
        self.setCentralWidget(centralWidget)

    def _get_stock_icon(self, standard_icon_enum) -> QIcon:
        return self.style().standardIcon(standard_icon_enum)

    def _create_menu_bar(self):
        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('&File')

        self.openTemplateAction = QAction(self._get_stock_icon(QApplication.style().SP_DialogOpenButton),
                                          '&Open Template...', self)
        self.openTemplateAction.setShortcut(QKeySequence.Open)
        fileMenu.addAction(self.openTemplateAction)

        self.openDataAction = QAction(self._get_stock_icon(QApplication.style().SP_FileLinkIcon), 'Open D&ata File...',
                                      self)  # No standard shortcut
        fileMenu.addAction(self.openDataAction)

        fileMenu.addSeparator()

        self.saveTemplateAction = QAction(self._get_stock_icon(QApplication.style().SP_DialogSaveButton),
                                          '&Save Template', self)
        self.saveTemplateAction.setShortcut(QKeySequence.Save)
        fileMenu.addAction(self.saveTemplateAction)

        self.saveTemplateAsAction = QAction('Save Template &As...', self)
        self.saveTemplateAsAction.setShortcut(QKeySequence.SaveAs)
        fileMenu.addAction(self.saveTemplateAsAction)

        self.saveOutputAction = QAction(self._get_stock_icon(QApplication.style().SP_DialogSaveButton),
                                        'Save &Output As...', self)
        fileMenu.addAction(self.saveOutputAction)

        fileMenu.addSeparator()
        exitAction = QAction(self._get_stock_icon(QApplication.style().SP_DialogCloseButton), 'E&xit', self)
        exitAction.setShortcut(QKeySequence.Quit)
        exitAction.triggered.connect(self.close)
        fileMenu.addAction(exitAction)

        editMenu = menuBar.addMenu('&Edit')
        self.renderAction = QAction(self._get_stock_icon(QApplication.style().SP_MediaPlay), '&Render', self)
        self.renderAction.setShortcut("F5")
        editMenu.addAction(self.renderAction)

        clearMenu = editMenu.addMenu("&Clear")
        self.clearTemplateAction = QAction("Clear Template", self)
        clearMenu.addAction(self.clearTemplateAction)
        self.clearDataActionMenu = QAction("Clear Data", self)  # Different from button
        clearMenu.addAction(self.clearDataActionMenu)
        self.clearOutputAction = QAction("Clear Output", self)
        clearMenu.addAction(self.clearOutputAction)

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
        self.renderButton.clicked.connect(self.render_template)  # Also connect the button

        # Clear actions
        self.clearDataButton.clicked.connect(self.clear_data_editor)
        self.clearTemplateAction.triggered.connect(self.templateEditor.clear)
        self.clearDataActionMenu.triggered.connect(self.clear_data_editor)
        self.clearOutputAction.triggered.connect(self.outputViewer.clear)

    def _update_window_title(self):
        title = APP_NAME
        if self._current_template_file_path:
            title = f"{self._current_template_file_path} - {APP_NAME}"
        self.setWindowTitle(title)

    def open_template_file(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Template File", self._current_template_file_path or "",
                                                  TEMPLATE_FILE_FILTER)
        if fileName:
            try:
                with open(fileName, 'r', encoding='utf-8') as file:
                    self.templateEditor.setText(file.read())
                self._current_template_file_path = fileName
                self._update_window_title()
                self.statusBar().showMessage(f"Template '{fileName}' loaded.", 5000)
            except IOError as e:
                QMessageBox.critical(self, "Error Opening File", f"Could not open template file:\n{e}")
                self.statusBar().showMessage(f"Error opening template: {e}", 5000)

    def open_data_file(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Data File", self._current_data_file_path or "",
                                                  JSON_FILE_FILTER)
        if fileName:
            try:
                with open(fileName, 'r', encoding='utf-8') as file:
                    self.dataEditor.setText(file.read())
                self._current_data_file_path = fileName
                self.statusBar().showMessage(f"Data file '{fileName}' loaded.", 5000)
            except IOError as e:
                QMessageBox.critical(self, "Error Opening File", f"Could not open data file:\n{e}")
                self.statusBar().showMessage(f"Error opening data file: {e}", 5000)

    def _save_template_to_path(self, file_path: str) -> bool:
        if not file_path:
            return False
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(self.templateEditor.toPlainText())
            self._current_template_file_path = file_path
            self._update_window_title()
            self.statusBar().showMessage(f"Template saved to '{file_path}'.", 5000)
            return True
        except IOError as e:
            QMessageBox.critical(self, "Error Saving File", f"Could not save template file:\n{e}")
            self.statusBar().showMessage(f"Error saving template: {e}", 5000)
            return False

    def save_template_file(self):
        if self._current_template_file_path:
            self._save_template_to_path(self._current_template_file_path)
        else:
            self.save_template_file_as()

    def save_template_file_as(self):
        fileName, _ = QFileDialog.getSaveFileName(self, "Save Template File As", self._current_template_file_path or "",
                                                  TEMPLATE_FILE_FILTER)
        if fileName:
            self._save_template_to_path(fileName)

    def save_output_file(self):
        if not self.outputViewer.toPlainText().strip():
            QMessageBox.information(self, "Empty Output", "There is no output to save.")
            return

        fileName, _ = QFileDialog.getSaveFileName(self, "Save Rendered Output As", "", TEXT_FILE_FILTER)
        if fileName:
            try:
                with open(fileName, 'w', encoding='utf-8') as file:
                    file.write(self.outputViewer.toPlainText())
                self.statusBar().showMessage(f"Output saved to '{fileName}'.", 5000)
            except IOError as e:
                QMessageBox.critical(self, "Error Saving File", f"Could not save output file:\n{e}")
                self.statusBar().showMessage(f"Error saving output: {e}", 5000)

    def clear_data_editor(self):
        self.dataEditor.clear()
        self.statusBar().showMessage("Data editor cleared.", 3000)

    def render_template(self):
        template_str = self.templateEditor.toPlainText()
        data_str = self.dataEditor.toPlainText()
        context_data = {}

        if not template_str.strip():
            self.outputViewer.setText("Template is empty. Nothing to render.")
            self.statusBar().showMessage("Render attempted with empty template.", 3000)
            return

        if data_str.strip():
            try:
                context_data = json.loads(data_str)
                if not isinstance(context_data, dict):
                    raise TypeError("JSON data must be an object (dictionary).")
            except json.JSONDecodeError as e:
                self.outputViewer.setText(f"JSON Data Error:\n{e}\n\nPlease check your JSON syntax.")
                self.statusBar().showMessage("JSON Data Error.", 5000)
                return
            except TypeError as e:  # Custom check for non-dict JSON
                self.outputViewer.setText(f"JSON Data Error:\n{e}")
                self.statusBar().showMessage("JSON Data Error: Must be an object.", 5000)
                return

        try:
            template = Template(template_str)
            rendered = template.merge(context_data)
            self.outputViewer.setText(rendered)
            self.statusBar().showMessage("Template rendered successfully.", 3000)
        except TemplateError as e:  # CORRECTED EXCEPTION TYPE
            self.outputViewer.setText(f"Velocity Template Rendering Error:\n{e}")
            self.statusBar().showMessage("Template Rendering Error.", 5000)
        except Exception as e:  # Catch any other unexpected errors
            self.outputViewer.setText(f"An unexpected error occurred during rendering:\n{e}")
            self.statusBar().showMessage("Unexpected Rendering Error.", 5000)
            # For debugging, you might want to print the full traceback
            # import traceback
            # traceback.print_exc()


def main():
    app = QApplication(sys.argv)
    # You can set a style here if you want, e.g., "Fusion"
    # app.setStyle("Fusion")
    mainWin = VelocityTemplatePreviewer()
    mainWin.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
