"""
Syntax highlighting classes for the Velocity Template Previewer.
"""

import re
from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PyQt5.QtCore import Qt


class VelocitySyntaxHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for Velocity templates."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_formats()
        self._setup_rules()
    
    def _setup_formats(self):
        """Setup text formats for different syntax elements."""
        # Variables: $variable or ${variable}
        self.variable_format = QTextCharFormat()
        self.variable_format.setForeground(QColor("#2980b9"))  # Blue
        self.variable_format.setFontWeight(QFont.Bold)
        
        # Directives: #if, #foreach, #set, etc.
        self.directive_format = QTextCharFormat()
        self.directive_format.setForeground(QColor("#e74c3c"))  # Red
        self.directive_format.setFontWeight(QFont.Bold)
        
        # Comments: ## comment
        self.comment_format = QTextCharFormat()
        self.comment_format.setForeground(QColor("#27ae60"))  # Green
        self.comment_format.setFontItalic(True)
        
        # Strings in quotes
        self.string_format = QTextCharFormat()
        self.string_format.setForeground(QColor("#f39c12"))  # Orange
        
        # Numbers
        self.number_format = QTextCharFormat()
        self.number_format.setForeground(QColor("#8e44ad"))  # Purple
        
        # Operators
        self.operator_format = QTextCharFormat()
        self.operator_format.setForeground(QColor("#34495e"))  # Dark gray
        self.operator_format.setFontWeight(QFont.Bold)
    
    def _setup_rules(self):
        """Setup highlighting rules."""
        self.rules = []
        
        # Variables: $variable or ${variable}
        self.rules.append((r'\$\{?[a-zA-Z_][a-zA-Z0-9_]*\}?', self.variable_format))
        
        # Directives: #if, #foreach, #set, #end, etc.
        self.rules.append((r'#[a-zA-Z_][a-zA-Z0-9_]*', self.directive_format))
        
        # Comments: ## comment
        self.rules.append((r'##.*$', self.comment_format))
        
        # Strings in quotes
        self.rules.append((r'"[^"]*"', self.string_format))
        self.rules.append((r"'[^']*'", self.string_format))
        
        # Numbers
        self.rules.append((r'\b\d+\.?\d*\b', self.number_format))
        
        # Operators
        operators = r'[+\-*/%=<>!&|^~]'
        self.rules.append((operators, self.operator_format))
    
    def highlightBlock(self, text):
        """Apply highlighting to the given block of text."""
        for pattern, format in self.rules:
            for match in re.finditer(pattern, text):
                start, end = match.span()
                self.setFormat(start, end - start, format)


class JSONSyntaxHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for JSON data."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_formats()
        self._setup_rules()
    
    def _setup_formats(self):
        """Setup text formats for different JSON elements."""
        # JSON keys
        self.key_format = QTextCharFormat()
        self.key_format.setForeground(QColor("#2980b9"))  # Blue
        self.key_format.setFontWeight(QFont.Bold)
        
        # JSON strings
        self.string_format = QTextCharFormat()
        self.string_format.setForeground(QColor("#27ae60"))  # Green
        
        # JSON numbers
        self.number_format = QTextCharFormat()
        self.number_format.setForeground(QColor("#e74c3c"))  # Red
        
        # JSON booleans and null
        self.boolean_format = QTextCharFormat()
        self.boolean_format.setForeground(QColor("#f39c12"))  # Orange
        self.boolean_format.setFontWeight(QFont.Bold)
        
        # JSON punctuation (brackets, braces, colons, commas)
        self.punctuation_format = QTextCharFormat()
        self.punctuation_format.setForeground(QColor("#34495e"))  # Dark gray
        self.punctuation_format.setFontWeight(QFont.Bold)
    
    def _setup_rules(self):
        """Setup highlighting rules."""
        self.rules = []
        
        # JSON keys
        self.rules.append((r'"[^"]*"\s*:', self.key_format))
        
        # JSON strings
        self.rules.append((r'"[^"]*"', self.string_format))
        
        # JSON numbers
        self.rules.append((r'\b\d+\.?\d*\b', self.number_format))
        
        # JSON booleans and null
        self.rules.append((r'\b(true|false|null)\b', self.boolean_format))
        
        # JSON punctuation
        self.rules.append((r'[{}[\],:]', self.punctuation_format))
    
    def highlightBlock(self, text):
        """Apply highlighting to the given block of text."""
        for pattern, format in self.rules:
            for match in re.finditer(pattern, text):
                start, end = match.span()
                self.setFormat(start, end - start, format)


class OutputSyntaxHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for rendered output."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_formats()
        self._setup_rules()
    
    def _setup_formats(self):
        """Setup text formats for output highlighting."""
        # HTML tags
        self.html_tag_format = QTextCharFormat()
        self.html_tag_format.setForeground(QColor("#e74c3c"))  # Red
        self.html_tag_format.setFontWeight(QFont.Bold)
        
        # URLs
        self.url_format = QTextCharFormat()
        self.url_format.setForeground(QColor("#3498db"))  # Blue
        self.url_format.setFontUnderline(True)
        
        # Email addresses
        self.email_format = QTextCharFormat()
        self.email_format.setForeground(QColor("#9b59b6"))  # Purple
        self.email_format.setFontUnderline(True)
        
        # Numbers
        self.number_format = QTextCharFormat()
        self.number_format.setForeground(QColor("#f39c12"))  # Orange
    
    def _setup_rules(self):
        """Setup highlighting rules."""
        self.rules = []
        
        # HTML tags
        self.rules.append((r'<[^>]+>', self.html_tag_format))
        
        # URLs
        self.rules.append((r'https?://[^\s<>"]+', self.url_format))
        
        # Email addresses
        self.rules.append((r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', self.email_format))
        
        # Numbers
        self.rules.append((r'\b\d+\.?\d*\b', self.number_format))
    
    def highlightBlock(self, text):
        """Apply highlighting to the given block of text."""
        for pattern, format in self.rules:
            for match in re.finditer(pattern, text):
                start, end = match.span()
                self.setFormat(start, end - start, format) 