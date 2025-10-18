"""
Smart caching system for 7-Ply Discord Bot
Phase 1: In-memory caching for 5x performance improvement
"""

import time
import threading
from typing import Dict, Any, Optional
import json

class BotCache:
    """
    Smart caching system for bot data
    Stores frequently accessed data in memory for faster responses
    """
    
    def __init__(self):
        # Cache stores
        self.user_cache: Dict[int, Dict[str, Any]] = {}
        self.server_cache: Dict[int, Dict[str, Any]] = {}
        self.static_cache: Dict[str, Any] = {}
        
        # Cache timestamps for expiration
        self.user_timestamps: Dict[int, float] = {}
        self.server_timestamps: Dict[int, float] = {}
        
        # Cache settings
        self.USER_CACHE_TTL = 300  # 5 minutes
        self.SERVER_CACHE_TTL = 600  # 10 minutes
        self.MAX_USER_CACHE_SIZE = 1000  # Limit memory usage
        self.MAX_SERVER_CACHE_SIZE = 500
        
        # Thread lock for thread safety
        self.lock = threading.Lock()
        
        # Load static data on initialization
        self._load_static_cache()
    
    def _load_static_cache(self):
        """Load static data that rarely changes (tricks, facts, etc.)"""
        try:
            # Load tricks list
            with open('commands/tricks.json', 'r') as f:
                self.static_cache['tricks'] = json.load(f)
        except:
            self.static_cache['tricks'] = []
        
        try:
            # Load skateboard facts
            with open('commands/skatefacts.json', 'r') as f:
                self.static_cache['facts'] = json.load(f)
        except:
            self.static_cache['facts'] = []
        
        print(f"📦 Cached {len(self.static_cache.get('tricks', []))} tricks and {len(self.static_cache.get('facts', []))} facts")
    
    def get_user_data(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user data from cache or return None if not cached/expired"""
        with self.lock:
            current_time = time.time()
            
            # Check if user is cached and not expired
            if (user_id in self.user_cache and 
                user_id in self.user_timestamps and
                current_time - self.user_timestamps[user_id] < self.USER_CACHE_TTL):
                return self.user_cache[user_id].copy()
            
            return None
    
    def set_user_data(self, user_id: int, data: Dict[str, Any]):
        """Cache user data with automatic size management"""
        with self.lock:
            current_time = time.time()
            
            # If cache is full, remove oldest entries
            if len(self.user_cache) >= self.MAX_USER_CACHE_SIZE:
                self._cleanup_old_user_data()
            
            self.user_cache[user_id] = data.copy()
            self.user_timestamps[user_id] = current_time
    
    def get_server_data(self, server_id: int) -> Optional[Dict[str, Any]]:
        """Get server data from cache or return None if not cached/expired"""
        with self.lock:
            current_time = time.time()
            
            if (server_id in self.server_cache and 
                server_id in self.server_timestamps and
                current_time - self.server_timestamps[server_id] < self.SERVER_CACHE_TTL):
                return self.server_cache[server_id].copy()
            
            return None
    
    def set_server_data(self, server_id: int, data: Dict[str, Any]):
        """Cache server data with automatic size management"""
        with self.lock:
            current_time = time.time()
            
            # If cache is full, remove oldest entries
            if len(self.server_cache) >= self.MAX_SERVER_CACHE_SIZE:
                self._cleanup_old_server_data()
            
            self.server_cache[server_id] = data.copy()
            self.server_timestamps[server_id] = current_time
    
    def get_static_data(self, key: str) -> Optional[Any]:
        """Get static data (tricks, facts, etc.) - always cached"""
        return self.static_cache.get(key)
    
    def invalidate_user(self, user_id: int):
        """Remove specific user from cache (when data changes)"""
        with self.lock:
            self.user_cache.pop(user_id, None)
            self.user_timestamps.pop(user_id, None)
    
    def invalidate_server(self, server_id: int):
        """Remove specific server from cache (when data changes)"""
        with self.lock:
            self.server_cache.pop(server_id, None)
            self.server_timestamps.pop(server_id, None)
    
    def _cleanup_old_user_data(self):
        """Remove 25% of oldest user cache entries"""
        current_time = time.time()
        
        # Sort by timestamp and remove oldest 25%
        sorted_users = sorted(self.user_timestamps.items(), key=lambda x: x[1])
        users_to_remove = sorted_users[:len(sorted_users) // 4]
        
        for user_id, _ in users_to_remove:
            self.user_cache.pop(user_id, None)
            self.user_timestamps.pop(user_id, None)
    
    def _cleanup_old_server_data(self):
        """Remove 25% of oldest server cache entries"""
        current_time = time.time()
        
        # Sort by timestamp and remove oldest 25%
        sorted_servers = sorted(self.server_timestamps.items(), key=lambda x: x[1])
        servers_to_remove = sorted_servers[:len(sorted_servers) // 4]
        
        for server_id, _ in servers_to_remove:
            self.server_cache.pop(server_id, None)
            self.server_timestamps.pop(server_id, None)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics for monitoring"""
        with self.lock:
            return {
                'users_cached': len(self.user_cache),
                'servers_cached': len(self.server_cache),
                'static_items': len(self.static_cache),
                'memory_estimate_mb': self._estimate_memory_usage()
            }
    
    def _estimate_memory_usage(self) -> float:
        """Rough estimate of cache memory usage in MB"""
        # Very rough estimate: assume 1KB per user, 2KB per server, 100KB static
        user_mb = len(self.user_cache) * 0.001  # 1KB per user
        server_mb = len(self.server_cache) * 0.002  # 2KB per server  
        static_mb = 0.1  # ~100KB for static data
        
        return round(user_mb + server_mb + static_mb, 2)
    
    def cleanup_expired(self):
        """Manual cleanup of expired cache entries"""
        current_time = time.time()
        
        with self.lock:
            # Clean expired users
            expired_users = [
                uid for uid, timestamp in self.user_timestamps.items()
                if current_time - timestamp >= self.USER_CACHE_TTL
            ]
            
            for uid in expired_users:
                self.user_cache.pop(uid, None)
                self.user_timestamps.pop(uid, None)
            
            # Clean expired servers
            expired_servers = [
                sid for sid, timestamp in self.server_timestamps.items()
                if current_time - timestamp >= self.SERVER_CACHE_TTL
            ]
            
            for sid in expired_servers:
                self.server_cache.pop(sid, None)
                self.server_timestamps.pop(sid, None)
            
            return len(expired_users) + len(expired_servers)

# Global cache instance
bot_cache = BotCache()