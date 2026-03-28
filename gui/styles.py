# -*- coding: utf-8 -*-
"""GUI styles and theme definitions for Qt."""
from __future__ import annotations
from typing import Dict

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont, QPalette
from PyQt6.QtWidgets import (
    QApplication, QDialog, QHBoxLayout, QLabel, QPushButton, QWidget
)

from resources.locales import lang


class Theme:
    """Application theme configuration."""
    
    COLORS: Dict[str, str] = {
        'bg_primary': '#0d1117',
        'bg_secondary': '#161b22',
        'bg_tertiary': '#21262d',
        'bg_hover': '#30363d',
        'fg_primary': '#c9d1d9',
        'fg_muted': '#8b949e',
        'accent_blue': '#58a6ff',
        'accent_green': '#238636',
        'accent_red': '#da3633',
        'accent_purple': '#8957e5',
        'accent_green_hover': '#2ea043',
        'accent_red_hover': '#f85149',
        'accent_purple_hover': '#ab7df8',
        'accent_blue_hover': '#79aaff',
        'white': '#ffffff',
        'black': '#000000',
    }
    
    FONTS: Dict[str, QFont] = {
        'title': QFont('Segoe UI', 20, QFont.Weight.Bold),
        'header': QFont('Segoe UI', 10, QFont.Weight.Bold),
        'body': QFont('Segoe UI', 10),
        'mono': QFont('Consolas', 10),
        'mono_large': QFont('Consolas', 11),
        'link': QFont('Segoe UI', 10),
    }
    
    @staticmethod
    def button_style(color_key: str, hover_key: str = None) -> str:
        """Generate button style."""
        if hover_key is None:
            hover_key = color_key + '_hover'
        color = Theme.COLORS[color_key]
        hover = Theme.COLORS.get(hover_key, color)
        disabled_color = Theme.COLORS['bg_hover']
        return f"QPushButton {{ background-color: {color}; color: white; border: none; padding: 8px 16px; border-radius: 4px; }} QPushButton:hover {{ background-color: {hover}; }} QPushButton:disabled {{ background-color: {disabled_color}; color: {Theme.COLORS['fg_muted']}; }}"
    
    BUTTON_STYLES = {
        'green': ('accent_green', 'accent_green_hover'),
        'red': ('accent_red', 'accent_red_hover'),
        'blue': ('accent_blue', 'accent_blue_hover'),
        'purple': ('accent_purple', 'accent_purple_hover'),
    }
    
    @classmethod
    def get_button_style(cls, style_type: str) -> str:
        """Get button style by type."""
        color_key, hover_key = cls.BUTTON_STYLES.get(style_type, ('accent_blue', 'accent_blue_hover'))
        return cls.button_style(color_key, hover_key)
    
    @classmethod
    def line_edit_style(cls) -> str:
        """Get line edit style."""
        return f"QLineEdit {{ background-color: {Theme.COLORS['bg_secondary']}; color: {Theme.COLORS['white']}; border: 1px solid {Theme.COLORS['bg_hover']}; border-radius: 4px; padding: 4px; }} QLineEdit::placeholder {{ color: {Theme.COLORS['fg_muted']}; }}"
    
    @classmethod
    def combo_box_style(cls, min_width: int = 100) -> str:
        """Get combo box style."""
        return f"""
            QComboBox {{ background-color: {cls.COLORS['bg_tertiary']}; color: {cls.COLORS['fg_primary']}; border: 1px solid {cls.COLORS['bg_hover']}; border-radius: 4px; padding: 4px; min-width: {min_width}px; }}
            QComboBox:hover {{ border: 1px solid {cls.COLORS['accent_blue']}; }}
            QComboBox::drop-down {{ border: none; }}
            QComboBox QAbstractItemView {{ background-color: {cls.COLORS['bg_tertiary']}; color: {cls.COLORS['fg_primary']}; selection-background-color: {cls.COLORS['accent_blue']}; }}
        """
    
    @classmethod
    def dialog_style(cls, radius: int = 8) -> str:
        """Get dialog main widget style."""
        return f"background-color: {Theme.COLORS['bg_primary']}; border: 1px solid {Theme.COLORS['bg_hover']}; border-radius: {radius}px;"
    
    @classmethod
    def title_bar_style(cls) -> str:
        """Get title bar style."""
        return f"background-color: {Theme.COLORS['bg_secondary']}; border-bottom: 1px solid {Theme.COLORS['bg_hover']};"
    
    @classmethod
    def title_label_style(cls, font_size: int = 13) -> str:
        """Get title label style."""
        return f"color: {Theme.COLORS['fg_primary']}; font-weight: bold; font-size: {font_size}px; background: transparent; border: none;"
    
    @classmethod
    def close_button_style(cls) -> str:
        """Get close button style."""
        return f"QPushButton {{ background-color: transparent; color: {Theme.COLORS['fg_primary']}; border: none; font-size: 18px; font-weight: bold; border-radius: 4px; }} QPushButton:hover {{ background-color: {Theme.COLORS['accent_red']}; color: {Theme.COLORS['white']}; }}"
    
    @classmethod
    def content_style(cls) -> str:
        """Get content area style."""
        return "background: transparent; border: none;"
    
    @classmethod
    def label_style(cls, color: str = 'fg_primary', font_size: int = 12) -> str:
        """Get label style with configurable color and font size."""
        return f"color: {Theme.COLORS[color]}; font-size: {font_size}px; background: transparent; border: none;"
    
    @classmethod
    def window_style(cls) -> str:
        """Get main window background style."""
        return f"background-color: {Theme.COLORS['bg_primary']};"
    
    @classmethod
    def title_large_style(cls) -> str:
        """Get large title style."""
        return f"font-size: 20px; font-weight: bold; color: {Theme.COLORS['accent_blue']};"
    
    @classmethod
    def muted_style(cls) -> str:
        """Get muted text style."""
        return f"color: {Theme.COLORS['fg_muted']};"
    
    @classmethod
    def accent_bold_style(cls, color: str = 'accent_blue', margin_left: int = 0) -> str:
        """Get accent bold text style."""
        margin = f" margin-left: {margin_left}px;" if margin_left else ""
        return f"color: {Theme.COLORS[color]}; font-weight: bold;{margin}"
    
    @classmethod
    def overlay_style(cls) -> str:
        """Get overlay style."""
        return f"background-color: rgba(13, 17, 23, 240);"
    
    @classmethod
    def overlay_label_style(cls) -> str:
        """Get overlay label style."""
        return f"font-size: 18px; font-weight: bold; color: {Theme.COLORS['white']}; padding: 30px 40px; border: 3px solid {Theme.COLORS['accent_blue']}; border-radius: 8px; background-color: {Theme.COLORS['bg_primary']};"
    
    @classmethod
    def frame_style(cls, bg_key: str = 'bg_secondary') -> str:
        """Get frame background style."""
        return f"background-color: {Theme.COLORS[bg_key]};"
    
    @classmethod
    def progress_bar_style(cls) -> str:
        """Get progress bar style."""
        return f"QProgressBar {{ border: 2px solid {Theme.COLORS['accent_blue']}; border-radius: 4px; background-color: {Theme.COLORS['bg_secondary']}; text-align: center; }} QProgressBar::chunk {{ background-color: {Theme.COLORS['accent_blue']}; }}"
    
    @classmethod
    def tree_widget_style(cls) -> str:
        """Get tree widget style."""
        return f"""
            QTreeWidget {{
                background-color: {Theme.COLORS['bg_secondary']};
                color: {Theme.COLORS['white']};
                border: none;
                font-size: 12px;
            }}
            QTreeWidget::item {{
                padding: 4px 8px;
                border: none;
            }}
            QTreeWidget::item:selected {{
                background-color: {Theme.COLORS['accent_blue']};
                color: {Theme.COLORS['white']};
            }}
            QTreeWidget::item:hover {{
                background-color: {Theme.COLORS['bg_hover']};
            }}
            QHeaderView::section {{
                background-color: {Theme.COLORS['bg_tertiary']};
                color: {Theme.COLORS['fg_primary']};
                padding: 6px 8px;
                border: none;
                border-bottom: 1px solid {Theme.COLORS['bg_hover']};
                font-weight: bold;
            }}
            QScrollBar:vertical {{
                background: {Theme.COLORS['bg_primary']};
                width: 12px;
            }}
            QScrollBar::handle:vertical {{
                background: {Theme.COLORS['bg_hover']};
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {Theme.COLORS['accent_blue']};
            }}
        """
    
    @classmethod
    def apply_theme(cls, app: QApplication) -> None:
        """Apply dark theme to application."""
        palette = QPalette()
        
        palette.setColor(QPalette.ColorRole.Window, QColor(cls.COLORS['bg_primary']))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(cls.COLORS['fg_primary']))
        palette.setColor(QPalette.ColorRole.Base, QColor(cls.COLORS['bg_secondary']))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(cls.COLORS['bg_tertiary']))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(cls.COLORS['bg_secondary']))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(cls.COLORS['fg_primary']))
        palette.setColor(QPalette.ColorRole.Text, QColor(cls.COLORS['fg_primary']))
        palette.setColor(QPalette.ColorRole.Button, QColor(cls.COLORS['bg_tertiary']))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(cls.COLORS['fg_primary']))
        palette.setColor(QPalette.ColorRole.BrightText, QColor(cls.COLORS['white']))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(cls.COLORS['accent_blue']))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(cls.COLORS['white']))
        palette.setColor(QPalette.ColorRole.Link, QColor(cls.COLORS['accent_blue']))
        palette.setColor(QPalette.ColorRole.PlaceholderText, QColor(cls.COLORS['fg_muted']))
        
        app.setPalette(palette)
        app.setStyleSheet(f"""
            QMainWindow, QWidget {{ background-color: {cls.COLORS['bg_primary']}; }}
            QLabel {{ color: {cls.COLORS['fg_primary']}; }}
            QPushButton {{
                background-color: {cls.COLORS['accent_blue']};
                color: {cls.COLORS['white']};
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {cls.COLORS['accent_blue_hover']};
            }}
            QPushButton:pressed {{
                background-color: {cls.COLORS['accent_blue']};
            }}
            QLineEdit, QTextEdit {{
                background-color: {cls.COLORS['bg_secondary']};
                color: {cls.COLORS['white']};
                border: 1px solid {cls.COLORS['bg_hover']};
                border-radius: 4px;
                padding: 4px;
            }}
            QLineEdit:focus, QTextEdit:focus {{
                border: 1px solid {cls.COLORS['accent_blue']};
            }}
            QComboBox {{
                background-color: {cls.COLORS['bg_tertiary']};
                color: {cls.COLORS['fg_primary']};
                border: 1px solid {cls.COLORS['bg_hover']};
                border-radius: 4px;
                padding: 4px;
            }}
            QComboBox:hover {{
                border: 1px solid {cls.COLORS['accent_blue']};
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox QAbstractItemView {{
                background-color: {cls.COLORS['bg_tertiary']};
                color: {cls.COLORS['fg_primary']};
                selection-background-color: {cls.COLORS['accent_blue']};
            }}
            QTreeWidget, QTableWidget {{
                background-color: {cls.COLORS['bg_secondary']};
                color: {cls.COLORS['fg_primary']};
                border: none;
            }}
            QTreeWidget::item:selected, QTableWidget::item:selected {{
                background-color: {cls.COLORS['accent_blue']};
            }}
            QScrollBar:vertical {{
                background-color: {cls.COLORS['bg_primary']};
                width: 12px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {cls.COLORS['bg_hover']};
                border-radius: 6px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {cls.COLORS['accent_blue']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)


class Layout:
    """Layout constants and helpers."""
    
    @staticmethod
    def center_window(window, width: int, height: int) -> None:
        """Center window on screen using Qt's built-in method."""
        window.resize(width, height)
        qr = window.frameGeometry()
        cp = window.screen().availableGeometry().center()
        qr.moveCenter(cp)
        window.move(qr.topLeft())


class CustomTitleBar(QWidget):
    """Custom title bar with optional close button."""
    
    def __init__(self, title: str, parent: QWidget = None, close_callback=None, show_close_btn: bool = True):
        super().__init__(parent)
        self._parent = parent
        self._close_callback = close_callback
        self._drag_pos = None
        
        self.setFixedHeight(36)
        self.setStyleSheet(Theme.title_bar_style())
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 8, 0)
        layout.setSpacing(8)
        
        title_label = QLabel(title)
        title_label.setStyleSheet(Theme.title_label_style())
        title_label.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        layout.addWidget(title_label)
        
        layout.addStretch()
        
        if show_close_btn:
            close_btn = QPushButton("×")
            close_btn.setFixedSize(32, 28)
            close_btn.setStyleSheet(Theme.close_button_style())
            close_btn.clicked.connect(self._on_close)
            layout.addWidget(close_btn)
    
    def _on_close(self) -> None:
        if self._close_callback:
            self._close_callback()
        elif self._parent:
            self._parent.reject()
    
    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint()
    
    def mouseMoveEvent(self, event) -> None:
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_pos:
            if self._parent:
                self._parent.move(self._parent.pos() + event.globalPosition().toPoint() - self._drag_pos)
                self._drag_pos = event.globalPosition().toPoint()


class DialogBuilder:
    """Base dialog builder for consistent dialog styling."""
    
    DIALOG_SIZES = {
        'confirm': (520, 220),
        'info': (420, 180),
        'error': (450, 190),
        'settings': (500, 270),
    }
    
    def __init__(self, parent, title: str, dialog_type: str = 'info'):
        from PyQt6.QtWidgets import QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel
        from PyQt6.QtCore import Qt
        
        self.dialog_type = dialog_type
        width, height = self.DIALOG_SIZES.get(dialog_type, (400, 200))
        self._result = 0
        
        self.dialog = QDialog(parent)
        self.dialog.setFixedSize(width, height)
        self.dialog.setModal(True)
        self.dialog.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        
        def set_result_accept():
            self._result = QDialog.DialogCode.Accepted.value
            self.dialog.accept()
        
        def set_result_reject():
            self._result = QDialog.DialogCode.Rejected.value
            self.dialog.reject()
        
        self._accept_callback = set_result_accept
        self._reject_callback = set_result_reject
        
        self.main_widget = QWidget()
        self.main_widget.setStyleSheet(Theme.dialog_style())
        
        self.layout = QVBoxLayout(self.main_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        self.title_bar = QWidget()
        self.title_bar.setFixedHeight(36)
        self.title_bar.setStyleSheet(Theme.title_bar_style())
        self.title_bar_layout = QHBoxLayout(self.title_bar)
        self.title_bar_layout.setContentsMargins(12, 0, 8, 0)
        
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet(Theme.title_label_style())
        self.title_bar_layout.addWidget(self.title_label)
        self.title_bar_layout.addStretch()
        
        self.layout.addWidget(self.title_bar)
        
        self.content = QWidget()
        self.content.setStyleSheet(Theme.content_style())
        self.content_layout = QVBoxLayout(self.content)
        
        self.btn_layout = QHBoxLayout()
        self.btn_layout.addStretch()
        
        self.dialog_layout = QVBoxLayout(self.dialog)
        self.dialog_layout.setContentsMargins(0, 0, 0, 0)
        self.dialog_layout.addWidget(self.main_widget)
    
    def add_content_margins(self, left: int = 24, top: int = 16, right: int = 24, bottom: int = 16) -> None:
        self.content_layout.setContentsMargins(left, top, right, bottom)
    
    def add_button(self, text: str, style_type: str, callback) -> None:
        from PyQt6.QtWidgets import QPushButton
        btn = QPushButton(text)
        btn.setStyleSheet(Theme.get_button_style(style_type))
        if callback == 'accept':
            btn.clicked.connect(self._accept_callback)
        elif callback == 'reject':
            btn.clicked.connect(self._reject_callback)
        else:
            btn.clicked.connect(callback)
        self.btn_layout.addWidget(btn)
    
    def add_widget(self, widget) -> None:
        self.content_layout.addWidget(widget)
    
    def add_stretch(self) -> None:
        self.content_layout.addStretch()
    
    def add_btn_stretch(self) -> None:
        self.content_layout.addLayout(self.btn_layout)
    
    def exec(self) -> int:
        self.layout.addWidget(self.content)
        Layout.center_window(self.dialog, self.dialog.width(), self.dialog.height())
        self.dialog.exec()
        return self._result


def confirm_copy(parent, title: str, message: str, yes_text: str, no_text: str) -> bool:
    """Show styled confirmation dialog."""
    from PyQt6.QtWidgets import QLabel
    from PyQt6.QtCore import Qt
    
    dlg = DialogBuilder(parent, title, 'confirm')
    dlg.add_content_margins(24, 16, 24, 16)
    
    label = QLabel(message)
    label.setWordWrap(True)
    label.setStyleSheet(Theme.label_style())
    dlg.add_widget(label)
    dlg.add_stretch()
    
    dlg.add_button(yes_text, 'green', 'accept')
    dlg.add_button(no_text, 'red', 'reject')
    dlg.add_btn_stretch()
    
    return dlg.exec() == QDialog.DialogCode.Accepted.value


def show_info(parent, title: str, message: str) -> None:
    """Show styled information dialog."""
    from PyQt6.QtWidgets import QLabel
    
    dlg = DialogBuilder(parent, title, 'info')
    dlg.add_content_margins(24, 16, 24, 16)
    
    label = QLabel(message)
    label.setWordWrap(True)
    label.setStyleSheet(Theme.label_style())
    dlg.add_widget(label)
    dlg.add_stretch()
    
    dlg.add_button(lang['ok'], 'blue', 'accept')
    dlg.add_btn_stretch()
    
    dlg.exec()


def show_error(parent, title: str, message: str) -> None:
    """Show styled error dialog."""
    from PyQt6.QtWidgets import QLabel
    
    dlg = DialogBuilder(parent, title, 'error')
    dlg.add_content_margins(24, 16, 24, 16)
    
    label = QLabel(message)
    label.setWordWrap(True)
    label.setStyleSheet(Theme.label_style('accent_red'))
    dlg.add_widget(label)
    dlg.add_stretch()
    
    dlg.add_button(lang['ok'], 'red', 'accept')
    dlg.add_btn_stretch()
    
    dlg.exec()
