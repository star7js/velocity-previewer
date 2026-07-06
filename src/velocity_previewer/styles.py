"""Qt stylesheets for light and dark mode."""

DARK_STYLESHEET = """
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

LIGHT_STYLESHEET = """
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
