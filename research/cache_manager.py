"""
Cache Manager for NotebookLM Clone
Handles caching of research results, slide images, and other expensive operations.
"""

import os
import hashlib
import pickle
import json
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path
import asyncio
from datetime import datetime, timedelta

class CacheManager:
    """Manages various types of caching for the video generation pipeline."""
    
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        # Cache subdirectories
        self.research_cache_dir = self.cache_dir / "research"
        self.raster_cache_dir = self.cache_dir / "raster"
        self.llm_cache_dir = self.cache_dir / "llm"
        
        for dir_path in [self.research_cache_dir, self.raster_cache_dir, self.llm_cache_dir]:
            dir_path.mkdir(exist_ok=True)
        
        # Cache expiration times (in hours)
        self.research_ttl = 24  # Research results valid for 24 hours
        self.raster_ttl = 168   # Raster images valid for 1 week
        self.llm_ttl = 12       # LLM responses valid for 12 hours
    
    def _get_cache_key(self, prefix: str, data: Any) -> str:
        """Generate a cache key from data."""
        if isinstance(data, (dict, list)):
            data_str = json.dumps(data, sort_keys=True)
        else:
            data_str = str(data)
        
        hash_obj = hashlib.md5(data_str.encode())
        return f"{prefix}_{hash_obj.hexdigest()}"
    
    def _is_cache_valid(self, cache_file: Path, ttl_hours: int) -> bool:
        """Check if cache file is still valid based on TTL."""
        if not cache_file.exists():
            return False
        
        file_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
        return file_age < timedelta(hours=ttl_hours)
    
    # Research Cache
    def get_research_cache(self, query: str, search_type: str = "web") -> Optional[Dict[str, Any]]:
        """Get cached research results."""
        cache_key = self._get_cache_key(f"research_{search_type}", query)
        cache_file = self.research_cache_dir / f"{cache_key}.pkl"
        
        if self._is_cache_valid(cache_file, self.research_ttl):
            try:
                with open(cache_file, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                print(f"⚠️ Failed to load research cache: {e}")
        
        return None
    
    def set_research_cache(self, query: str, results: Dict[str, Any], search_type: str = "web") -> None:
        """Cache research results."""
        cache_key = self._get_cache_key(f"research_{search_type}", query)
        cache_file = self.research_cache_dir / f"{cache_key}.pkl"
        
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(results, f)
        except Exception as e:
            print(f"⚠️ Failed to save research cache: {e}")
    
    # Raster Cache
    def get_raster_cache(self, slide_data: Dict[str, Any], question_id: str) -> Optional[str]:
        """Get cached raster image path."""
        cache_key = self._get_cache_key("raster", slide_data)
        cache_file = self.raster_cache_dir / f"{cache_key}.png"
        
        if self._is_cache_valid(cache_file, self.raster_ttl):
            return str(cache_file)
        
        return None
    
    def set_raster_cache(self, slide_data: Dict[str, Any], image_path: str, question_id: str) -> str:
        """Cache raster image and return cached path."""
        cache_key = self._get_cache_key("raster", slide_data)
        cache_file = self.raster_cache_dir / f"{cache_key}.png"
        
        try:
            # Copy image to cache
            import shutil
            shutil.copy2(image_path, cache_file)
            return str(cache_file)
        except Exception as e:
            print(f"⚠️ Failed to save raster cache: {e}")
            return image_path
    
    # LLM Cache
    def get_llm_cache(self, prompt: str, model: str = "gpt-4") -> Optional[Dict[str, Any]]:
        """Get cached LLM response."""
        cache_key = self._get_cache_key(f"llm_{model}", prompt)
        cache_file = self.llm_cache_dir / f"{cache_key}.pkl"
        
        if self._is_cache_valid(cache_file, self.llm_ttl):
            try:
                with open(cache_file, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                print(f"⚠️ Failed to load LLM cache: {e}")
        
        return None
    
    def set_llm_cache(self, prompt: str, response: Dict[str, Any], model: str = "gpt-4") -> None:
        """Cache LLM response."""
        cache_key = self._get_cache_key(f"llm_{model}", prompt)
        cache_file = self.llm_cache_dir / f"{cache_key}.pkl"
        
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(response, f)
        except Exception as e:
            print(f"⚠️ Failed to save LLM cache: {e}")
    
    # Cache Statistics
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        stats = {
            "research_cache": {"files": 0, "size_mb": 0},
            "raster_cache": {"files": 0, "size_mb": 0},
            "llm_cache": {"files": 0, "size_mb": 0}
        }
        
        for cache_type, cache_dir in [
            ("research_cache", self.research_cache_dir),
            ("raster_cache", self.raster_cache_dir),
            ("llm_cache", self.llm_cache_dir)
        ]:
            files = list(cache_dir.glob("*"))
            stats[cache_type]["files"] = len(files)
            stats[cache_type]["size_mb"] = sum(f.stat().st_size for f in files) / (1024 * 1024)
        
        return stats
    
    def clear_cache(self, cache_type: Optional[str] = None) -> None:
        """Clear cache files."""
        if cache_type == "research" or cache_type is None:
            for f in self.research_cache_dir.glob("*"):
                f.unlink()
        
        if cache_type == "raster" or cache_type is None:
            for f in self.raster_cache_dir.glob("*"):
                f.unlink()
        
        if cache_type == "llm" or cache_type is None:
            for f in self.llm_cache_dir.glob("*"):
                f.unlink()
    
    def cleanup_expired(self) -> None:
        """Remove expired cache files."""
        for cache_dir, ttl in [
            (self.research_cache_dir, self.research_ttl),
            (self.raster_cache_dir, self.raster_ttl),
            (self.llm_cache_dir, self.llm_ttl)
        ]:
            for f in cache_dir.glob("*"):
                if not self._is_cache_valid(f, ttl):
                    f.unlink()

# Global cache manager instance
cache_manager = CacheManager()
