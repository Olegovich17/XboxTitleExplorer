# -*- coding: utf-8 -*-
"""Configuration management module."""
import logging
import os
import sys
import threading
from pathlib import Path
from typing import Optional

import configparser

logger = logging.getLogger(__name__)


class Config:
    """Application configuration manager."""
    
    _instance: Optional['Config'] = None
    _lock = threading.Lock()
    
    def __new__(cls) -> 'Config':
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self) -> None:
        if hasattr(self, '_initialized') and self._initialized:
            return
        self._initialized = True
        
        self._config = configparser.ConfigParser(interpolation=None)
        self._config_path: Path = APP_BASE_PATH / "config.ini"
        
        self._default_config = {
            'General': {
                'language': 'en',
            },
            'TeraCopy': {
                'exe_path': r'%LOCALAPPDATA%\Programs\TeraCopy\TeraCopy.exe',
                'flags': '/NoClose',
            }
        }
        
        self._language: str = self._default_config['General']['language']
        self._teracopy_exe_path: str = self._default_config['TeraCopy']['exe_path']
        self._teracopy_flags: str = self._default_config['TeraCopy']['flags']
        
        self._load()
    
    @property
    def language(self) -> str:
        return self._language
    
    @language.setter
    def language(self, value: str) -> None:
        self._language = value
        self._save()
    
    @property
    def teracopy_exe_path(self) -> str:
        return self._teracopy_exe_path
    
    @teracopy_exe_path.setter
    def teracopy_exe_path(self, value: str) -> None:
        self._teracopy_exe_path = value
        self._save()
    
    @property
    def teracopy_flags(self) -> str:
        return self._teracopy_flags
    
    @teracopy_flags.setter
    def teracopy_flags(self, value: str) -> None:
        self._teracopy_flags = value
        self._save()
    
    @property
    def teracopy_exe_path_expanded(self) -> str:
        return os.path.expandvars(self._teracopy_exe_path)
    
    def _load(self) -> None:
        try:
            if self._config_path.exists():
                self._config.read(self._config_path, encoding='utf-8')
                if 'General' in self._config:
                    self._language = self._config['General'].get('language', 'en')
                if 'TeraCopy' in self._config:
                    self._teracopy_exe_path = self._config['TeraCopy'].get(
                        'exe_path', self._default_config['TeraCopy']['exe_path']
                    )
                    self._teracopy_flags = self._config['TeraCopy'].get(
                        'flags', self._default_config['TeraCopy']['flags']
                    )
            else:
                self._create_default()
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            self._create_default()
    
    def _create_default(self) -> None:
        try:
            self._config.read_dict(self._default_config)
            self._language = self._default_config['General']['language']
            self._teracopy_exe_path = self._default_config['TeraCopy']['exe_path']
            self._teracopy_flags = self._default_config['TeraCopy']['flags']
            self._save()
        except Exception as e:
            logger.error(f"Error creating default config: {e}")
    
    def _save(self) -> None:
        try:
            self._config_path.parent.mkdir(parents=True, exist_ok=True)
            
            if 'General' not in self._config:
                self._config['General'] = {}
            if 'TeraCopy' not in self._config:
                self._config['TeraCopy'] = {}
            
            self._config['General']['language'] = self._language
            self._config['TeraCopy']['exe_path'] = self._teracopy_exe_path
            self._config['TeraCopy']['flags'] = self._teracopy_flags
            
            with open(self._config_path, 'w', encoding='utf-8') as f:
                self._config.write(f)
        except Exception as e:
            logger.error(f"Error saving config: {e}")
    
    def update(self, exe_path: str, flags: str) -> None:
        self._teracopy_exe_path = exe_path.strip()
        self._teracopy_flags = flags.strip()
        self._save()


def get_app_base_path() -> Path:
    """Get application base directory (works for script and PyInstaller EXE)."""
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


APP_BASE_PATH = get_app_base_path()
TEMP_LIST_PATH = APP_BASE_PATH / "temp_tc_filelist.txt"

config = Config()


def cleanup_temp_file(path: Path) -> None:
    try:
        if path.exists():
            logger.info(f"Cleaning up temp file: {path}")
            path.unlink()
    except Exception as e:
        logger.error(f"Error cleaning up temp file {path}: {e}")
