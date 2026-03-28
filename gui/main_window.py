# -*- coding: utf-8 -*-
"""Main application window module using Qt."""
import logging
import re
import subprocess
import threading
import time
import webbrowser
from pathlib import Path
from typing import Any, Dict

from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox, QFileDialog, QFrame, QHBoxLayout,
    QLabel, QLineEdit, QMainWindow, QProgressBar,
    QPushButton, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget
)

from core.api import get_title_info_batch
from core.config import config
from gui.settings import SettingsWindow
from gui.styles import Layout, Theme, confirm_copy, show_error
from resources.locales import APP_AUTHOR, APP_TITLE, AVAILABLE_LANGUAGES, lang
from utils.file_ops import TeraCopyManager, calculate_directory_size, format_bytes
from utils.icon import find_icon

logger = logging.getLogger(__name__)

CANCEL_SCAN = threading.Event()

class ScanThread(QThread):
    """Thread for scanning directories."""
    progress = pyqtSignal(int, int)
    finished = pyqtSignal(list, object)
    error = pyqtSignal(str)
    
    def __init__(self, path: Path):
        super().__init__()
        self.path = path
    
    def run(self):
        try:
            folders = sorted(
                [f for f in self.path.iterdir() if f.is_dir()],
                key=lambda x: x.name.lower()
            )
            
            total = len(folders)
            final_data = []
            tids_to_fetch = []
            folder_tid_map = {}
            total_size = 0
            
            for idx, folder in enumerate(folders, 1):
                if CANCEL_SCAN.is_set():
                    break
                
                self.progress.emit(idx, total)
                
                name = folder.name
                is_tid = bool(re.fullmatch(r"[0-9A-F]{8}", name, re.I))
                
                try:
                    size_bytes = calculate_directory_size(folder)
                except Exception as e:
                    logger.warning(f"Error calculating size for {folder}: {e}")
                    size_bytes = 0
                
                total_size += size_bytes
                
                final_data.append({
                    'folder': folder,
                    'name': name,
                    'is_tid': is_tid,
                    'title': "",
                    'system': "",
                    'size_formatted': format_bytes(size_bytes),
                    'size_bytes': size_bytes
                })
                
                if is_tid:
                    tids_to_fetch.append(name)
                    folder_tid_map[name] = len(final_data) - 1
            
            if tids_to_fetch and not CANCEL_SCAN.is_set():
                title_infos = get_title_info_batch(tids_to_fetch)
                for tid, info in title_infos.items():
                    if tid in folder_tid_map:
                        idx = folder_tid_map[tid]
                        final_data[idx]['title'] = info.name
                        final_data[idx]['system'] = ", ".join(info.systems) if info.systems else ""
            
            self.finished.emit(final_data, total_size)
            
        except Exception as e:
            logger.exception("Error in ScanThread")
            self.error.emit(str(e))


class CopyThread(QThread):
    """Thread for copying files with TeraCopy."""
    finished = pyqtSignal(int)
    
    def __init__(self, sources: list, dest: Path):
        super().__init__()
        self.sources = sources
        self.dest = dest
    
    def run(self):
        try:
            process = TeraCopyManager.copy_folders(self.sources, self.dest)
            if process:
                while process.poll() is None:
                    time.sleep(0.5)
            self.finished.emit(process.returncode if process else -1)
        except Exception:
            logger.exception("Error in CopyThread")
            self.finished.emit(-1)


class MainWindow(QMainWindow):
    """Main application window controller."""
    
    def __init__(self):
        super().__init__()
        self.paths: Dict[str, Dict[str, Any]] = {}
        self.checked: set = set()
        self.total_size_bytes: int = 0
        self.scan_thread = None
        self.copy_thread = None
        self._setup_window()
        self._create_widgets()
    
    def _setup_window(self) -> None:
        self.setWindowTitle(f"{APP_TITLE} by {APP_AUTHOR}")
        self.setMinimumSize(1000, 650)
        
        Layout.center_window(self, 1000, 650)
        self.setStyleSheet(Theme.window_style())
        
        icon_path = find_icon()
        if icon_path:
            from PyQt6.QtGui import QIcon, QPixmap
            pixmap = QPixmap(str(icon_path))
            if not pixmap.isNull():
                self.setWindowIcon(QIcon(pixmap))
    
    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if hasattr(self, 'overlay'):
            self._update_overlay_geometry()
    
    def _create_widgets(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(12)
        
        main_layout.addLayout(self._create_top_bar())
        main_layout.addLayout(self._create_action_buttons())
        main_layout.addWidget(self._create_treeview())
        main_layout.addWidget(self._create_status_bar())
        
        self._create_overlay()
    
    def _create_top_bar(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        
        title_label = QLabel(APP_TITLE)
        title_label.setStyleSheet(Theme.title_large_style())
        layout.addWidget(title_label)
        
        path_frame = QFrame()
        path_layout = QHBoxLayout(path_frame)
        path_layout.setContentsMargins(0, 0, 0, 0)
        
        self.path_label = QLabel(lang['path_label'])
        self.path_label.setStyleSheet(Theme.muted_style())
        path_layout.addWidget(self.path_label)
        
        self.path_entry = QLineEdit()
        self.path_entry.setPlaceholderText(r"X:\Content\0000000000000000")
        self.path_entry.setStyleSheet(Theme.line_edit_style())
        self.path_entry.setFont(Theme.FONTS['mono'])
        self.path_entry.returnPressed.connect(self._load_path)
        path_layout.addWidget(self.path_entry, 1)
        
        self.browse_btn = QPushButton(lang['browse'])
        self.browse_btn.setStyleSheet(Theme.get_button_style('green'))
        self.browse_btn.clicked.connect(self._browse)
        path_layout.addWidget(self.browse_btn)
        
        layout.addWidget(path_frame, 1)
        
        self.teracopy_btn = QPushButton(lang['teracopy_settings'])
        self.teracopy_btn.setStyleSheet(Theme.get_button_style('blue'))
        self.teracopy_btn.clicked.connect(self._open_settings)
        layout.addWidget(self.teracopy_btn)
        
        return layout
    
    def _create_action_buttons(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        
        self.select_all_btn = QPushButton(lang['select_all'])
        self.select_all_btn.setStyleSheet(Theme.get_button_style('green'))
        self.select_all_btn.clicked.connect(self._select_all)
        layout.addWidget(self.select_all_btn)
        
        self.deselect_all_btn = QPushButton(lang['deselect_all'])
        self.deselect_all_btn.setStyleSheet(Theme.get_button_style('red'))
        self.deselect_all_btn.clicked.connect(self._deselect_all)
        layout.addWidget(self.deselect_all_btn)
        
        self.copy_btn = QPushButton(lang['copy_selected'])
        self.copy_btn.setStyleSheet(Theme.get_button_style('purple'))
        self.copy_btn.setEnabled(False)
        self.copy_btn.clicked.connect(self._copy_selected)
        layout.addWidget(self.copy_btn)
        
        layout.addStretch()
        
        return layout
    
    def _create_treeview(self) -> QTreeWidget:
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(['☐', lang['col_name'], lang['col_title'], lang['col_system'], lang['col_size']])
        
        header = self.tree.header()
        header_item = self.tree.headerItem()

        alignments = [
            Qt.AlignmentFlag.AlignCenter,
            Qt.AlignmentFlag.AlignCenter,
            Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter,
            Qt.AlignmentFlag.AlignCenter,
            Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter,
        ]
        for col, align in enumerate(alignments):
            header_item.setTextAlignment(col, align)

        resize_modes = [
            header.ResizeMode.Fixed,
            header.ResizeMode.Interactive,
            header.ResizeMode.Stretch,
            header.ResizeMode.Fixed,
            header.ResizeMode.Fixed,
        ]
        for col, mode in enumerate(resize_modes):
            header.setSectionResizeMode(col, mode)

        widths = {0: 30, 1: 120, 3: 80, 4: 80}
        for col, width in widths.items():
            self.tree.setColumnWidth(col, width)
        
        self.tree.setStyleSheet(Theme.tree_widget_style())
        
        self.tree.setAlternatingRowColors(True)
        self.tree.setSelectionBehavior(QTreeWidget.SelectionBehavior.SelectRows)
        self.tree.setRootIsDecorated(False)
        self.tree.setItemsExpandable(False)
        self.tree.setIndentation(0)
        
        self.tree.itemChanged.connect(self._on_item_changed)
        self.tree.itemDoubleClicked.connect(self._on_item_double_clicked)
        return self.tree
    
    def _create_status_bar(self) -> QFrame:
        status = QFrame()
        status.setStyleSheet(Theme.frame_style('bg_secondary'))
        status_layout = QHBoxLayout(status)
        status_layout.setContentsMargins(16, 8, 16, 8)
        
        self.status_label = QLabel(lang['status_hint'])
        self.status_label.setStyleSheet(Theme.muted_style())
        status_layout.addWidget(self.status_label)
        
        status_layout.addStretch()
        
        self.selected_label = QLabel(f"{lang['selected']}: 0")
        self.selected_label.setStyleSheet(Theme.accent_bold_style('accent_blue'))
        status_layout.addWidget(self.selected_label)
        
        self.selected_size_label = QLabel(f"{lang['selected_weight']}: 0 B")
        self.selected_size_label.setStyleSheet(Theme.accent_bold_style('accent_blue', 16))
        status_layout.addWidget(self.selected_size_label)
        
        self.count_label = QLabel(f"{lang['total_folders']}: 0 {lang['folders']}")
        self.count_label.setStyleSheet(Theme.muted_style() + " margin-left: 16px;")
        status_layout.addWidget(self.count_label)
        
        self.total_size_label = QLabel(f"{lang['total_weight']}: 0 B")
        self.total_size_label.setStyleSheet(Theme.muted_style() + " margin-left: 16px;")
        status_layout.addWidget(self.total_size_label)
        
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(list(AVAILABLE_LANGUAGES.values()))
        current_lang_name = AVAILABLE_LANGUAGES.get(lang.current_language, 'English')
        self.lang_combo.setCurrentText(current_lang_name)
        self.lang_combo.setStyleSheet(Theme.combo_box_style(80))
        self.lang_combo.currentTextChanged.connect(self._on_language_changed)
        status_layout.addWidget(self.lang_combo)
        
        return status
    
    def _create_overlay(self) -> None:
        self.overlay = QFrame(self)
        self.overlay.setStyleSheet(Theme.overlay_style())
        
        self.overlay_layout = QVBoxLayout(self.overlay)
        self.overlay_layout.setContentsMargins(0, 0, 0, 0)
        self.overlay_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.overlay_label = QLabel(lang['scanning'])
        self.overlay_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.overlay_label.setStyleSheet(Theme.overlay_label_style())
        self.overlay_layout.addWidget(self.overlay_label)
        
        self.overlay_progress = QProgressBar()
        self.overlay_progress.setRange(0, 100)
        self.overlay_progress.setValue(0)
        self.overlay_progress.setFixedWidth(400)
        self.overlay_progress.setStyleSheet(Theme.progress_bar_style())
        self.overlay_layout.addWidget(self.overlay_progress)
        
        self.overlay.hide()
    
    def _update_overlay_geometry(self) -> None:
        self.overlay.setGeometry(self.rect())
    
    def _block(self, text: str = None, show_progress: bool = True) -> None:
        if text is None:
            text = lang['scanning']
        self.overlay_label.setText(text)
        self.overlay_progress.setVisible(show_progress)
        self._update_overlay_geometry()
        self.overlay.show()
        self.setEnabled(False)
    
    def _unblock(self) -> None:
        self.overlay.hide()
        self.setEnabled(True)
    
    def _browse(self) -> None:
        path = QFileDialog.getExistingDirectory(self, lang['browse_title'])
        if path and path.strip():
            self.path_entry.setText(path.replace('/', '\\'))
            self._load_path()

    def _open_settings(self) -> None:
        dialog = SettingsWindow(self)
        dialog.exec()
    
    def _on_item_changed(self, item, column: int) -> None:
        if column == 0:
            iid = item.text(1)
            if item.checkState(0) == Qt.CheckState.Checked:
                self.checked.add(iid)
            else:
                self.checked.discard(iid)
            self._update_status()
    
    def _on_item_double_clicked(self, item, column: int) -> None:
        path_data = self.paths.get(item.text(1))
        if not path_data:
            return
        
        match column:
            case 1:
                path = str(path_data['path'])
                logger.info(f"Opening in Explorer: {path}")
                subprocess.Popen(['explorer', path])
            case 2:
                tid = path_data.get('tid')
                systems = path_data.get('systems', '')
                if tid:
                    systems_part = systems.split(',')[0].strip().lower() if systems else 'xbox360'
                    url = f"https://dbox.tools/titles/{systems_part}/{tid}"
                    logger.info(f"Opening URL: {url}")
                    webbrowser.open(url)
    
    def _select_all(self) -> None:
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            item.setCheckState(0, Qt.CheckState.Checked)
        self._update_status()

    def _deselect_all(self) -> None:
        for i in range(self.tree.topLevelItemCount()):
            self.tree.topLevelItem(i).setCheckState(0, Qt.CheckState.Unchecked)
        self._update_status()
    
    def _load_path(self) -> None:
        path_str = self.path_entry.text().strip()
        logger.info(f"Loading path: {path_str}")
        if not path_str:
            return
        
        CANCEL_SCAN.clear()
        
        p = Path(path_str).resolve()
        if not p.is_dir():
            logger.warning(f"Path not found or not a directory: {p}")
            show_error(self, lang['error_title'], lang.get('path_error', path=path_str.replace('/', '\\')))
            return
        
        self.tree.clear()
        self.paths.clear()
        self.checked.clear()
        self.total_size_bytes = 0
        self._update_status()
        
        self._block()
        
        logger.debug(f"Starting scan thread for: {p}")
        self.scan_thread = ScanThread(p)
        self.scan_thread.progress.connect(self._update_progress)
        self.scan_thread.finished.connect(self._scan_finished)
        self.scan_thread.error.connect(self._scan_error)
        self.scan_thread.start()
    
    def _cancel_scan(self) -> None:
        CANCEL_SCAN.set()
    
    def _update_progress(self, current: int, total: int) -> None:
        pct = int((current / total) * 100) if total else 0
        self.overlay_progress.setValue(pct)
        self.overlay_label.setText(lang.get('scanning_progress', current=current, total=total, pct=pct))
    
    def _scan_finished(self, data: list, total_size: int) -> None:
        self._unblock()
        self.total_size_bytes = total_size
        
        for item in data:
            iid = item['name']
            tree_item = QTreeWidgetItem([
                '',
                item['name'],
                item['title'],
                item['system'],
                item['size_formatted']
            ])
            tree_item.setFlags(tree_item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            tree_item.setCheckState(0, Qt.CheckState.Unchecked)
            tree_item.setTextAlignment(0, Qt.AlignmentFlag.AlignCenter)
            tree_item.setTextAlignment(1, Qt.AlignmentFlag.AlignCenter)
            tree_item.setTextAlignment(2, Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
            tree_item.setTextAlignment(3, Qt.AlignmentFlag.AlignCenter)
            tree_item.setTextAlignment(4, Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)
            self.tree.addTopLevelItem(tree_item)
            self.paths[iid] = {
                'path': item['folder'],
                'size': item['size_bytes'],
                'tid': item['name'] if item.get('is_tid') else None,
                'systems': item['system'] if item.get('is_tid') else ''
            }
        
        self.status_label.setText(lang.get('ready', path=self.path_entry.text().replace('/', '\\')))
        self._update_status()
    
    def _scan_error(self, error: str) -> None:
        logger.error(f"Scan error: {error}")
        self._unblock()
        show_error(self, lang['critical_error'], lang.get('scan_error', error=error))
    
    def _copy_selected(self) -> None:
        valid_teracopy, teracopy_path = TeraCopyManager.validate_executable()
        if not valid_teracopy:
            logger.error(f"TeraCopy executable not found: {teracopy_path}")
            show_error(self, lang['teracopy_error'], lang.get('teracopy_not_found', path=teracopy_path))
            return
        
        dest = QFileDialog.getExistingDirectory(self, lang['select_dest'])
        if not dest:
            return
        
        dest_path = Path(dest).resolve()
        
        if not dest_path.exists() or not dest_path.is_dir():
            show_error(self, lang['error_title'], lang.get('path_error', path=dest.replace('/', '\\')))
            return
        
        num = len(self.checked)
        checked_bytes = sum(
            self.paths[iid]['size']
            for iid in self.checked
            if iid in self.paths
        )
        
        msg = lang.get('copy_confirm_msg',
            count=num,
            size=format_bytes(checked_bytes),
            src=self.path_entry.text().strip().replace('/', '\\'),
            dest=dest.replace('/', '\\')
        )
        
        if not confirm_copy(self, lang['copy_confirm_title'], msg, lang['yes'], lang['no']):
            logger.info("Copy operation cancelled by user.")
            return
        
        valid_sources = []
        for iid in self.checked:
            if iid in self.paths:
                src_path = self.paths[iid]['path']
                if src_path.exists() and src_path.is_dir():
                    valid_sources.append(src_path)
        
        if not valid_sources:
            logger.warning("No valid sources for copy.")
            show_error(self, lang['error_title'], lang['teracopy_error'])
            return
        
        logger.info(f"Initiating copy of {len(valid_sources)} items ({format_bytes(checked_bytes)}) to {dest_path}")
        self._block(lang['copying'], show_progress=False)
        
        self.copy_thread = CopyThread(valid_sources, dest_path)
        self.copy_thread.finished.connect(self._copy_finished)
        self.copy_thread.start()
    
    def _copy_finished(self, exit_code: int) -> None:
        logger.info(f"Copy finished with exit code: {exit_code}")
        self._unblock()
        
        if exit_code == -1:
            show_error(self, lang['teracopy_error'], lang['teracopy_error'])
        elif exit_code != 0:
            show_error(self, lang['teracopy_error'], lang.get('teracopy_error_code', code=exit_code))
    
    def _on_language_changed(self, text: str) -> None:
        lang_code = next((code for code, name in AVAILABLE_LANGUAGES.items() if name == text), 'en')
        logger.info(f"Changing language to: {lang_code}")
        lang.set_language(lang_code)
        self._refresh_ui_text()
    
    def _refresh_ui_text(self) -> None:
        self.setWindowTitle(f"{APP_TITLE} by {APP_AUTHOR}")
        self.teracopy_btn.setText(lang['teracopy_settings'])
        self.path_label.setText(lang['path_label'])
        self.browse_btn.setText(lang['browse'])
        self.select_all_btn.setText(lang['select_all'])
        self.deselect_all_btn.setText(lang['deselect_all'])
        self.copy_btn.setText(lang['copy_selected'])
        
        headers = ['', lang['col_name'], lang['col_title'], lang['col_system'], lang['col_size']]
        header_item = self.tree.headerItem()
        for i, header in enumerate(headers):
            header_item.setText(i, header)
        
        self._update_status()
        
        if not self.paths:
            self.status_label.setText(lang['status_hint'])
    
    def _update_status(self) -> None:
        selected = len(self.checked)
        total = self.tree.topLevelItemCount()
        checked_bytes = sum(
            self.paths[iid]['size']
            for iid in self.checked
            if iid in self.paths
        )
        
        self.copy_btn.setEnabled(selected > 0)
        self.selected_label.setText(f"{lang['selected']}: {selected}")
        self.selected_size_label.setText(f"{lang['selected_weight']}: {format_bytes(checked_bytes)}")
        self.count_label.setText(f"{lang['total_folders']}: {total} {lang['folders']}")
        self.total_size_label.setText(f"{lang['total_weight']}: {format_bytes(self.total_size_bytes)}")
