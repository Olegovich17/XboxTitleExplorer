# -*- coding: utf-8 -*-
"""Settings window module using Qt."""
import logging
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFileDialog, QWidget
)

from core.config import config
from gui.styles import Theme, Layout, CustomTitleBar
from resources.locales import lang

logger = logging.getLogger(__name__)

TERACOPY_DOWNLOAD_URL = "https://codesector.com/downloads"


class SettingsWindow(QDialog):
    """TeraCopy settings dialog window."""
    
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setFixedSize(500, 270)
        self.setModal(True)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        
        main_widget = QWidget()
        main_widget.setStyleSheet(Theme.dialog_style())
        
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        title_bar = CustomTitleBar(lang['teracopy_settings'], self, close_callback=self.close, show_close_btn=False)
        layout.addWidget(title_bar)
        
        content = QWidget()
        content.setStyleSheet(Theme.content_style())
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(15, 15, 15, 15)
        
        exe_label = QLabel(lang['teracopy_exe_label'])
        exe_label.setStyleSheet(Theme.label_style('accent_blue') + " font-weight: bold;")
        content_layout.addWidget(exe_label)
        
        path_layout = QHBoxLayout()
        
        self.exe_path_var = QLineEdit()
        self.exe_path_var.setText(config.teracopy_exe_path)
        self.exe_path_var.setStyleSheet(Theme.line_edit_style())
        path_layout.addWidget(self.exe_path_var, 1)
        
        browse_btn = QPushButton(lang['browse'])
        browse_btn.setStyleSheet(Theme.get_button_style('green'))
        browse_btn.clicked.connect(self._browse_exe)
        path_layout.addWidget(browse_btn, 0)
        
        content_layout.addLayout(path_layout)
        
        flags_label = QLabel(lang['flags_label'])
        flags_label.setStyleSheet(Theme.label_style('accent_blue') + " font-weight: bold; margin-top: 10px;")
        content_layout.addWidget(flags_label)
        
        self.flags_var = QLineEdit()
        self.flags_var.setText(config.teracopy_flags)
        self.flags_var.setStyleSheet(Theme.line_edit_style())
        content_layout.addWidget(self.flags_var)
        
        link_label = QLabel(f'<a href="{TERACOPY_DOWNLOAD_URL}">{lang["download_teracopy"]}</a>')
        link_label.setStyleSheet(Theme.label_style('accent_blue') + " margin-top: 10px;")
        link_label.setOpenExternalLinks(True)
        content_layout.addWidget(link_label)
        
        content_layout.addStretch()
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        save_btn = QPushButton(lang['save_close'])
        save_btn.setStyleSheet(Theme.get_button_style('purple'))
        save_btn.clicked.connect(self._save_and_close)
        btn_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton(lang['cancel'])
        cancel_btn.setStyleSheet(Theme.get_button_style('red'))
        cancel_btn.clicked.connect(self.close)
        btn_layout.addWidget(cancel_btn)
        
        content_layout.addLayout(btn_layout)
        
        layout.addWidget(content)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(main_widget)
        
        Layout.center_window(self, 500, 270)
    
    def _browse_exe(self) -> None:
        filename = QFileDialog.getOpenFileName(
            self,
            lang['select_exe'],
            "",
            f"{lang['exe_files']} (*.exe)"
        )
        if filename[0]:
            self.exe_path_var.setText(filename[0])
    
    def _save_and_close(self) -> None:
        logger.info(f"Saving settings: exe={self.exe_path_var.text()}, flags={self.flags_var.text()}")
        config.update(
            self.exe_path_var.text(),
            self.flags_var.text()
        )
        self.close()
