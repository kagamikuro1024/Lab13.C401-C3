"""
RAG Query Cache - Reduce lookup latency by caching frequently accessed results
"""

import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

class RAGCache:
    """Cache RAG retrieval results to reduce lookup time"""
    
    def __init__(self, ttl_minutes: int = 30, max_cache_size: int = 500):
        self.cache: Dict[str, Dict] = {}
        self.ttl = timedelta(minutes=ttl_minutes)
        self.max_cache_size = max_cache_size
        self.hits = 0
        self.misses = 0
        self.evictions = 0
    
    def get_cache_key(self, query: str) -> str:
        """Generate cache key from query (first 100 chars)"""
        query_normalized = query.lower().strip()[:100]
        return hashlib.md5(query_normalized.encode()).hexdigest()
    
    def get(self, query: str) -> Optional[List[str]]:
        """Get cached RAG result if available and not expired"""
        key = self.get_cache_key(query)
        
        if key in self.cache:
            entry = self.cache[key]
            if datetime.now() - entry["timestamp"] < self.ttl:
                self.hits += 1
                # Update last accessed time
                entry["last_accessed"] = datetime.now()
                entry["access_count"] += 1
                return entry["result"]
            else:
                # Expired, delete
                del self.cache[key]
                self.misses += 1
                return None
        
        self.misses += 1
        return None
    
    def set(self, query: str, result: List[str]):
        """Cache RAG retrieval result"""
        # Enforce max cache size
        if len(self.cache) >= self.max_cache_size:
            # Evict least recently used (LRU)
            self._evict_lru()
        
        key = self.get_cache_key(query)
        self.cache[key] = {
            "query": query,
            "result": result,
            "timestamp": datetime.now(),
            "last_accessed": datetime.now(),
            "access_count": 1,
            "size_bytes": len(json.dumps(result))
        }
    
    def _evict_lru(self):
        """Remove least recently used entry"""
        if not self.cache:
            return
        
        lru_key = min(
            self.cache.keys(),
            key=lambda k: self.cache[k]["last_accessed"]
        )
        del self.cache[lru_key]
        self.evictions += 1
    
    def clear(self):
        """Clear all cache entries"""
        self.cache.clear()
    
    def stats(self) -> Dict:
        """Get cache statistics"""
        total_accesses = self.hits + self.misses
        hit_rate = (self.hits / total_accesses * 100) if total_accesses > 0 else 0
        
        total_size = sum(
            entry.get("size_bytes", 0) 
            for entry in self.cache.values()
        )
        
        return {
            "cached_queries": len(self.cache),
            "max_cache_size": self.max_cache_size,
            "cache_utilization_percent": round(len(self.cache) / self.max_cache_size * 100, 2),
            "hits": self.hits,
            "misses": self.misses,
            "total_accesses": total_accesses,
            "hit_rate_percent": round(hit_rate, 2),
            "evictions": self.evictions,
            "total_cache_size_kb": round(total_size / 1024, 2),
            "ttl_minutes": self.ttl.total_seconds() / 60
        }
    
    def get_hot_queries(self, limit: int = 10) -> List[Dict]:
        """Get most frequently accessed queries"""
        sorted_entries = sorted(
            self.cache.items(),
            key=lambda x: x[1]["access_count"],
            reverse=True
        )
        
        return [
            {
                "query": entry[1]["query"][:80] + "..." if len(entry[1]["query"]) > 80 else entry[1]["query"],
                "access_count": entry[1]["access_count"],
                "size_kb": round(entry[1].get("size_bytes", 0) / 1024, 2),
                "last_accessed": entry[1]["last_accessed"].isoformat()
            }
            for entry in sorted_entries[:limit]
        ]
    
    def to_json(self) -> str:
        """Serialize cache stats to JSON"""
        return json.dumps({
            "stats": self.stats(),
            "hot_queries": self.get_hot_queries(5)
        }, indent=2)


# Global instance
rag_cache = RAGCache(ttl_minutes=30, max_cache_size=500)
