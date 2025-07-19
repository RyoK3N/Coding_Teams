import asyncio
import json
import os
import pickle
import time
from typing import Dict, Any, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
import logging
import hashlib
import threading
from collections import defaultdict

@dataclass
class CacheEntry:
    key: str
    value: Any
    namespace: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    access_count: int = 0
    last_accessed: datetime = field(default_factory=datetime.now)
    size_bytes: int = 0
    
    def is_expired(self) -> bool:
        return self.expires_at is not None and datetime.now() > self.expires_at
    
    def touch(self):
        self.last_accessed = datetime.now()
        self.access_count += 1
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "key": self.key,
            "namespace": self.namespace,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "access_count": self.access_count,
            "last_accessed": self.last_accessed.isoformat(),
            "size_bytes": self.size_bytes
        }

class CacheManager:
    def __init__(self, cache_dir: str = "./cache", write_cycle_minutes: int = 5, max_memory_mb: int = 100):
        self.cache_dir = Path(cache_dir)
        self.write_cycle_minutes = write_cycle_minutes
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        
        self.memory_cache: Dict[str, CacheEntry] = {}
        self.namespace_stats: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            "hit_count": 0,
            "miss_count": 0,
            "total_size": 0,
            "entry_count": 0
        })
        
        self.logger = logging.getLogger("cache_manager")
        self.write_lock = threading.Lock()
        self.running = False
        self.write_task = None
        
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.total_hits = 0
        self.total_misses = 0
        self.total_writes = 0
        self.total_reads = 0
        
    async def start(self):
        if self.running:
            return
            
        self.running = True
        await self.load_from_disk()
        self.write_task = asyncio.create_task(self._write_cycle_loop())
        self.logger.info(f"Cache manager started with {self.write_cycle_minutes}min write cycles")
        
    async def stop(self):
        if not self.running:
            return
            
        self.running = False
        
        if self.write_task:
            self.write_task.cancel()
            try:
                await self.write_task
            except asyncio.CancelledError:
                pass
                
        await self.flush_to_disk()
        self.logger.info("Cache manager stopped")
        
    async def set(self, key: str, value: Any, namespace: str = "default", ttl_seconds: Optional[int] = None):
        full_key = f"{namespace}:{key}"
        
        expires_at = None
        if ttl_seconds:
            expires_at = datetime.now() + timedelta(seconds=ttl_seconds)
            
        serialized_value = self._serialize_value(value)
        size_bytes = len(serialized_value) if isinstance(serialized_value, (str, bytes)) else 0
        
        entry = CacheEntry(
            key=full_key,
            value=value,
            namespace=namespace,
            created_at=datetime.now(),
            expires_at=expires_at,
            size_bytes=size_bytes
        )
        
        with self.write_lock:
            self.memory_cache[full_key] = entry
            self.namespace_stats[namespace]["entry_count"] += 1
            self.namespace_stats[namespace]["total_size"] += size_bytes
            
        await self._check_memory_limits()
        self.logger.debug(f"Cached {full_key} with TTL {ttl_seconds}s")
        
    async def get(self, key: str, namespace: str = "default") -> Optional[Any]:
        full_key = f"{namespace}:{key}"
        
        with self.write_lock:
            entry = self.memory_cache.get(full_key)
            
        if entry is None:
            self.total_misses += 1
            self.namespace_stats[namespace]["miss_count"] += 1
            return None
            
        if entry.is_expired():
            await self.delete(key, namespace)
            self.total_misses += 1
            self.namespace_stats[namespace]["miss_count"] += 1
            return None
            
        entry.touch()
        self.total_hits += 1
        self.namespace_stats[namespace]["hit_count"] += 1
        
        self.logger.debug(f"Cache hit for {full_key}")
        return entry.value
        
    async def delete(self, key: str, namespace: str = "default"):
        full_key = f"{namespace}:{key}"
        
        with self.write_lock:
            entry = self.memory_cache.pop(full_key, None)
            
        if entry:
            self.namespace_stats[namespace]["entry_count"] -= 1
            self.namespace_stats[namespace]["total_size"] -= entry.size_bytes
            self.logger.debug(f"Deleted cache entry {full_key}")
            
    async def clear(self, namespace: str = None):
        with self.write_lock:
            if namespace:
                keys_to_remove = [k for k in self.memory_cache.keys() if k.startswith(f"{namespace}:")]
                for key in keys_to_remove:
                    del self.memory_cache[key]
                self.namespace_stats[namespace] = {
                    "hit_count": 0,
                    "miss_count": 0,
                    "total_size": 0,
                    "entry_count": 0
                }
                self.logger.info(f"Cleared cache namespace: {namespace}")
            else:
                self.memory_cache.clear()
                self.namespace_stats.clear()
                self.logger.info("Cleared entire cache")
                
    async def get_cache_stats(self) -> Dict[str, Any]:
        total_entries = len(self.memory_cache)
        total_size = sum(entry.size_bytes for entry in self.memory_cache.values())
        
        hit_rate = (self.total_hits / (self.total_hits + self.total_misses)) * 100 if (self.total_hits + self.total_misses) > 0 else 0
        
        return {
            "total_entries": total_entries,
            "total_size_bytes": total_size,
            "total_size_mb": total_size / (1024 * 1024),
            "memory_usage_percent": (total_size / self.max_memory_bytes) * 100,
            "hit_rate_percent": hit_rate,
            "total_hits": self.total_hits,
            "total_misses": self.total_misses,
            "total_writes": self.total_writes,
            "total_reads": self.total_reads,
            "namespace_stats": dict(self.namespace_stats),
            "write_cycle_minutes": self.write_cycle_minutes,
            "running": self.running
        }
        
    async def _write_cycle_loop(self):
        while self.running:
            try:
                await asyncio.sleep(self.write_cycle_minutes * 60)
                if self.running:
                    await self.flush_to_disk()
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in write cycle: {e}")
                
    async def flush_to_disk(self):
        if not self.memory_cache:
            return
            
        try:
            cache_data = {}
            stats_data = {}
            
            with self.write_lock:
                for full_key, entry in self.memory_cache.items():
                    if not entry.is_expired():
                        cache_data[full_key] = {
                            "value": self._serialize_value(entry.value),
                            "namespace": entry.namespace,
                            "created_at": entry.created_at.isoformat(),
                            "expires_at": entry.expires_at.isoformat() if entry.expires_at else None,
                            "access_count": entry.access_count,
                            "last_accessed": entry.last_accessed.isoformat(),
                            "size_bytes": entry.size_bytes
                        }
                        
                stats_data = dict(self.namespace_stats)
                
            cache_file = self.cache_dir / "cache_data.json"
            stats_file = self.cache_dir / "cache_stats.json"
            
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
                
            with open(stats_file, 'w') as f:
                json.dump(stats_data, f, indent=2)
                
            self.total_writes += 1
            self.logger.info(f"Flushed {len(cache_data)} entries to disk")
            
        except Exception as e:
            self.logger.error(f"Error flushing cache to disk: {e}")
            
    async def load_from_disk(self):
        cache_file = self.cache_dir / "cache_data.json"
        stats_file = self.cache_dir / "cache_stats.json"
        
        try:
            if cache_file.exists():
                with open(cache_file, 'r') as f:
                    cache_data = json.load(f)
                    
                loaded_count = 0
                for full_key, entry_data in cache_data.items():
                    try:
                        expires_at = None
                        if entry_data.get("expires_at"):
                            expires_at = datetime.fromisoformat(entry_data["expires_at"])
                            
                        entry = CacheEntry(
                            key=full_key,
                            value=self._deserialize_value(entry_data["value"]),
                            namespace=entry_data["namespace"],
                            created_at=datetime.fromisoformat(entry_data["created_at"]),
                            expires_at=expires_at,
                            access_count=entry_data.get("access_count", 0),
                            last_accessed=datetime.fromisoformat(entry_data.get("last_accessed", datetime.now().isoformat())),
                            size_bytes=entry_data.get("size_bytes", 0)
                        )
                        
                        if not entry.is_expired():
                            self.memory_cache[full_key] = entry
                            loaded_count += 1
                            
                    except Exception as e:
                        self.logger.warning(f"Error loading cache entry {full_key}: {e}")
                        
                self.logger.info(f"Loaded {loaded_count} cache entries from disk")
                
            if stats_file.exists():
                with open(stats_file, 'r') as f:
                    stats_data = json.load(f)
                    self.namespace_stats.update(stats_data)
                    
            self.total_reads += 1
            
        except Exception as e:
            self.logger.error(f"Error loading cache from disk: {e}")
            
    async def _check_memory_limits(self):
        total_size = sum(entry.size_bytes for entry in self.memory_cache.values())
        
        if total_size > self.max_memory_bytes:
            await self._evict_lru_entries()
            
    async def _evict_lru_entries(self):
        if not self.memory_cache:
            return
            
        sorted_entries = sorted(
            self.memory_cache.items(),
            key=lambda x: x[1].last_accessed
        )
        
        target_size = self.max_memory_bytes * 0.8
        current_size = sum(entry.size_bytes for entry in self.memory_cache.values())
        
        evicted_count = 0
        for full_key, entry in sorted_entries:
            if current_size <= target_size:
                break
                
            with self.write_lock:
                if full_key in self.memory_cache:
                    del self.memory_cache[full_key]
                    current_size -= entry.size_bytes
                    evicted_count += 1
                    
                    self.namespace_stats[entry.namespace]["entry_count"] -= 1
                    self.namespace_stats[entry.namespace]["total_size"] -= entry.size_bytes
                    
        if evicted_count > 0:
            self.logger.info(f"Evicted {evicted_count} LRU entries to free memory")
            
    def _serialize_value(self, value: Any) -> str:
        try:
            if isinstance(value, (str, int, float, bool, type(None))):
                return json.dumps(value)
            else:
                return json.dumps(value, default=str)
        except (TypeError, ValueError):
            try:
                return pickle.dumps(value).hex()
            except Exception:
                return str(value)
                
    def _deserialize_value(self, serialized: str) -> Any:
        try:
            return json.loads(serialized)
        except (json.JSONDecodeError, TypeError):
            try:
                return pickle.loads(bytes.fromhex(serialized))
            except Exception:
                return serialized
                
    async def cleanup_expired_entries(self):
        expired_keys = []
        
        with self.write_lock:
            for full_key, entry in self.memory_cache.items():
                if entry.is_expired():
                    expired_keys.append(full_key)
                    
        for full_key in expired_keys:
            namespace = full_key.split(":", 1)[0]
            await self.delete(full_key.split(":", 1)[1], namespace)
            
        if expired_keys:
            self.logger.info(f"Cleaned up {len(expired_keys)} expired entries")
            
    async def get_namespace_entries(self, namespace: str) -> Dict[str, Any]:
        entries = {}
        
        with self.write_lock:
            for full_key, entry in self.memory_cache.items():
                if entry.namespace == namespace and not entry.is_expired():
                    key = full_key.split(":", 1)[1]
                    entries[key] = entry.to_dict()
                    
        return entries
        
    async def export_cache(self, file_path: str):
        try:
            export_data = {
                "timestamp": datetime.now().isoformat(),
                "stats": await self.get_cache_stats(),
                "entries": {}
            }
            
            with self.write_lock:
                for full_key, entry in self.memory_cache.items():
                    if not entry.is_expired():
                        export_data["entries"][full_key] = {
                            "value": self._serialize_value(entry.value),
                            "metadata": entry.to_dict()
                        }
                        
            with open(file_path, 'w') as f:
                json.dump(export_data, f, indent=2)
                
            self.logger.info(f"Cache exported to {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting cache: {e}")
            return False 