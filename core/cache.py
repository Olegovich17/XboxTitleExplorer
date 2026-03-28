# -*- coding: utf-8 -*-
"""Caching module for title information."""
import json
import logging
import threading
from pathlib import Path
from typing import Any, Dict, Optional

from core.config import APP_BASE_PATH

logger = logging.getLogger(__name__)

DEFAULT_CACHE = {
    "C0DE9999": {
        "name": "XeX Menu",
        "systems": ["XBOX360"]
    }
}



class Cache:
    """Cache manager for game titles."""
    
    _instance: Optional['Cache'] = None
    _lock = threading.Lock()
    _cache_path: Optional[Path] = None
    
    def __new__(cls, cache_path: Optional[Path] = None) -> 'Cache':
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    if cache_path:
                        cls._cache_path = cache_path
        elif cache_path and cls._cache_path is None:
            cls._cache_path = cache_path
        return cls._instance
    
    def __init__(self, cache_path: Optional[Path] = None) -> None:
        if hasattr(self, '_initialized') and self._initialized:
            return
        self._initialized = True
        
        self._cache: Dict[str, Dict[str, Any]] = {}
        if cache_path and Cache._cache_path is None:
            Cache._cache_path = cache_path
        self._save_pending = False
        self._save_lock = threading.Lock()
        self._load()
    
    def _load(self) -> None:
        try:
            if self._cache_path and self._cache_path.exists():
                with open(self._cache_path, "r", encoding="utf-8") as f:
                    self._cache = json.load(f)
            else:
                self._cache = DEFAULT_CACHE.copy()
                self._save()
        except Exception as e:
            logger.error(f"Error loading cache: {e}")
            self._cache = {}
    
    def _save(self) -> None:
        try:
            if self._cache_path is None:
                return
            self._cache_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self._cache_path, "w", encoding="utf-8") as f:
                json.dump(self._cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving cache: {e}")
    
    def _schedule_save(self) -> None:
        with self._save_lock:
            if not self._save_pending:
                self._save_pending = True
                threading.Timer(2.0, self._delayed_save).start()
    
    def _delayed_save(self) -> None:
        with self._save_lock:
            self._save()
            self._save_pending = False
    
    def get(self, tid: str) -> Optional[Dict[str, Any]]:
        tid = tid.upper()
        data = self._cache.get(tid)
        if data:
            logger.debug(f"Cache HIT for {tid}")
        else:
            logger.debug(f"Cache MISS for {tid}")
        return data
    
    def set(self, tid: str, data: Dict[str, Any]) -> None:
        tid = tid.upper()
        self._cache[tid] = data
        self._schedule_save()
    
    def has_valid_entry(self, tid: str) -> bool:
        tid = tid.upper()
        cached = self._cache.get(tid)
        if not isinstance(cached, dict):
            return False
        if "systems" not in cached:
            return False
        return cached.get("name") != "Unknown"
    
    def clear(self) -> None:
        self._cache = {}
        self._save()
    
    @property
    def size(self) -> int:
        return len(self._cache)


def get_cache() -> Cache:
    """Get the singleton cache instance."""
    return Cache(APP_BASE_PATH / "title_cache.json")


cache = get_cache()
