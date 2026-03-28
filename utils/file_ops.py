# -*- coding: utf-8 -*-
"""File operations module (size calculation, TeraCopy integration)."""
import atexit
import logging
import os
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple

from core.config import TEMP_LIST_PATH, cleanup_temp_file, config

logger = logging.getLogger(__name__)


def calculate_directory_size(path: Path) -> int:
    """Calculate directory size using iterative approach."""
    total = 0
    stack = [path]
    
    while stack:
        current = stack.pop()
        try:
            for entry in os.scandir(current):
                try:
                    if entry.is_file():
                        total += entry.stat().st_size
                    elif entry.is_dir():
                        stack.append(Path(entry.path))
                except PermissionError:
                    logger.debug(f"Permission denied: {entry.path}")
                except OSError as e:
                    logger.debug(f"OS error accessing {entry.path}: {e}")
        except PermissionError:
            logger.debug(f"Permission denied: {current}")
        except OSError as e:
            logger.debug(f"OS error accessing {current}: {e}")
    
    return total


def format_bytes(b: int) -> str:
    """Format bytes to human-readable size."""
    if b == 0:
        return "0 B"
    b = float(b)
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if b <= 1024.0:
            formatted = f"{b:.1f}"
            if '.' in formatted:
                formatted = formatted.rstrip('0').rstrip('.')
            return f"{formatted} {unit}"
        b /= 1024.0
    formatted = f"{b:.1f}"
    if '.' in formatted:
        formatted = formatted.rstrip('0').rstrip('.')
    return f"{formatted} PB"


class TeraCopyManager:
    """TeraCopy operations manager."""
    
    @staticmethod
    def validate_executable() -> Tuple[bool, str]:
        """Check if TeraCopy executable exists."""
        exe_path = config.teracopy_exe_path_expanded
        if not Path(exe_path).is_file():
            return False, exe_path
        return True, exe_path
    
    @staticmethod
    def create_list_file(paths: List[Path]) -> bool:
        """Create TeraCopy list file with source paths."""
        try:
            if TEMP_LIST_PATH.exists():
                TEMP_LIST_PATH.unlink()
            
            with open(TEMP_LIST_PATH, 'w', encoding='utf-8') as f:
                for path in paths:
                    f.write(f"{path.resolve()}\n")
            
            return True
        except Exception as e:
            logger.error(f"Error creating list file: {e}")
            return False
    
    @classmethod
    def copy_folders(
        cls,
        source_paths: List[Path],
        dest_path: Path
    ) -> Optional[subprocess.Popen]:
        """Launch TeraCopy with source folders list."""
        valid, exe_path = cls.validate_executable()
        if not valid:
            logger.error(f"TeraCopy executable not found: {exe_path}")
            return None
        
        if not cls.create_list_file(source_paths):
            logger.error("Failed to create TeraCopy list file")
            return None
        
        flags = config.teracopy_flags.split() if config.teracopy_flags else []
        
        command = [
            exe_path,
            "Copy",
            f"*{str(TEMP_LIST_PATH.resolve())}",
            str(Path(dest_path).resolve()),
            *flags
        ]
        
        logger.info(f"Launching TeraCopy command: {' '.join(command)}")
        
        try:
            process = subprocess.Popen(command)
            return process
        except Exception as e:
            logger.exception("Failed to launch TeraCopy process")
            cleanup_temp_file(TEMP_LIST_PATH)
            return None


def cleanup_temp() -> None:
    """Cleanup temporary files."""
    cleanup_temp_file(TEMP_LIST_PATH)


atexit.register(cleanup_temp)
