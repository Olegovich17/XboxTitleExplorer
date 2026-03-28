# -*- coding: utf-8 -*-
"""Icon loading utilities."""
import sys
from pathlib import Path
from typing import Optional

from core.config import APP_BASE_PATH


def find_icon() -> Optional[Path]:
    """Find application icon in standard locations.
    
    Handles both development and frozen exe modes.
    Returns Path to icon or None if not found.
    """
    if getattr(sys, 'frozen', False):
        meipass = Path(sys._MEIPASS)
        if (meipass / 'resources' / 'icon.ico').exists():
            return meipass / 'resources' / 'icon.ico'
        exe_dir = Path(sys.executable).parent
        if (exe_dir / 'resources' / 'icon.ico').exists():
            return exe_dir / 'resources' / 'icon.ico'
    
    if (resources_dir := Path('resources') / 'icon.ico').exists():
        return resources_dir
    if (APP_BASE_PATH / 'resources' / 'icon.ico').exists():
        return APP_BASE_PATH / 'resources' / 'icon.ico'
    
    return None
