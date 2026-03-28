# -*- coding: utf-8 -*-
"""Localization module."""
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from core.config import config

logger = logging.getLogger(__name__)


AVAILABLE_LANGUAGES: Dict[str, str] = {
    'ru': 'Русский',
    'en': 'English',
}

APP_TITLE: str = "Xbox Title Explorer"
APP_AUTHOR: str = "Olegovich17"


def _get_lang_path() -> Path:
    """Get path to locales folder (handles PyInstaller onefile mode)."""
    if getattr(sys, 'frozen', False):
        base = Path(sys._MEIPASS) / "resources" / "locales"
    else:
        base = Path(__file__).resolve().parent
    return base


class Localizer:
    """Localization handler."""
    
    _instance: Optional['Localizer'] = None
    _strings: Dict[str, Any] = {}
    _current_lang: str = ''
    _loaded: bool = False
    
    def __new__(cls) -> 'Localizer':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self) -> None:
        if self._loaded:
            return
        self._load(config.language or 'en')
    
    def _load(self, lang_code: str) -> None:
        lang_dir = _get_lang_path()
        lang_file = lang_dir / f"{lang_code}.json"
        
        try:
            if lang_file.exists():
                with open(lang_file, "r", encoding="utf-8") as f:
                    self._strings = json.load(f)
                self._current_lang = lang_code
                self._loaded = True
            else:
                logger.warning(f"Language file not found: {lang_file}")
        except Exception as e:
            logger.error(f"Error loading language file {lang_file}: {e}")
    
    def set_language(self, lang_code: str) -> None:
        """Change the current language."""
        if lang_code != self._current_lang:
            self._load(lang_code)
            config.language = lang_code
    
    @property
    def current_language(self) -> str:
        return self._current_lang
    
    def get(self, key: str, **kwargs) -> str:
        """Get localized string with optional format params."""
        text = self._strings.get(key, key)
        if kwargs:
            return text.format(**kwargs)
        return text
    
    def __getitem__(self, key: str) -> str:
        return self.get(key)


lang = Localizer()