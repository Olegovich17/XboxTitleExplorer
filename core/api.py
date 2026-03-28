# -*- coding: utf-8 -*-
"""API module for fetching title information."""
import json
import logging
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional

from core.cache import get_cache

logger = logging.getLogger(__name__)

cache = get_cache()

MAX_RETRIES = 3
RETRY_DELAY = 1.0
API_TIMEOUT = 8
API_URL = "https://dbox.tools/api/title_ids/{tid}"


class TitleInfo:
    """Data class for title information."""
    
    def __init__(self, name: str = "Unknown", systems: Optional[List[str]] = None):
        self.name = name
        self.systems = systems or []
    
    def to_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "systems": self.systems}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TitleInfo':
        return cls(
            name=data.get("name", "Unknown"),
            systems=data.get("systems", [])
        )


def fetch_title(tid: str) -> Optional[TitleInfo]:
    """Fetch title info from external API with retry logic."""
    tid = tid.upper()
    url = API_URL.format(tid=tid)
    logger.debug(f"Fetching title info for {tid} from URL: {url}")
    
    for attempt in range(MAX_RETRIES):
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'XboxTitleExplorer/1.0'}
        )
        try:
            with urllib.request.urlopen(req, timeout=API_TIMEOUT) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    if isinstance(data, dict):
                        name = data.get('name', 'Unknown')
                        if name and name != 'Unknown':
                            logger.debug(f"Successfully fetched {tid}: {name}")
                            return TitleInfo.from_dict(data)
                        logger.warning(f"API returned 'Unknown' name for {tid}")
                        return None
                else:
                    logger.warning(f"API request failed for {tid} with status: {response.status}")
        except urllib.error.URLError as e:
            logger.warning(f"URL error for {tid} (attempt {attempt+1}/{MAX_RETRIES}): {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY * (attempt + 1))
                continue
        except Exception as e:
            logger.error(f"Unexpected error fetching title {tid}: {e}")
        
        break
    
    logger.warning(f"Failed to fetch valid info for {tid}")
    return None


def fetch_titles_batch(tids: List[str]) -> Dict[str, TitleInfo]:
    """Fetch multiple title infos in parallel."""
    results: Dict[str, TitleInfo] = {}
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_tid = {
            executor.submit(fetch_title, tid): tid 
            for tid in tids
        }
        
        for future in as_completed(future_to_tid):
            tid = future_to_tid[future]
            try:
                info = future.result()
                if info is not None:
                    results[tid] = info
                    cache.set(tid, info.to_dict())
                else:
                    results[tid] = TitleInfo()
            except Exception:
                logger.exception(f"Unexpected error fetching {tid} in batch")
                results[tid] = TitleInfo()
    
    return results


def get_title_info(tid: str) -> TitleInfo:
    """Get title info from cache or API."""
    tid = tid.upper()
    
    if cache.has_valid_entry(tid):
        cached_data = cache.get(tid)
        if cached_data:
            return TitleInfo.from_dict(cached_data)
    
    info = fetch_title(tid)
    if info is not None:
        cache.set(tid, info.to_dict())
    else:
        info = TitleInfo()
    return info


def get_title_info_batch(tids: List[str]) -> Dict[str, TitleInfo]:
    """Get multiple title infos efficiently."""
    tids_upper = [t.upper() for t in tids]
    
    results: Dict[str, TitleInfo] = {}
    to_fetch: List[str] = []
    
    for tid in tids_upper:
        if cache.has_valid_entry(tid):
            cached_data = cache.get(tid)
            if cached_data:
                results[tid] = TitleInfo.from_dict(cached_data)
                continue
        to_fetch.append(tid)
    
    if to_fetch:
        fetched = fetch_titles_batch(to_fetch)
        results.update(fetched)
        
        for tid in to_fetch:
            if tid not in results:
                results[tid] = TitleInfo()
    
    return results
