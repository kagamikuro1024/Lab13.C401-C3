"""
Rate Limiting Module — Sliding window rate limiter
"""

import time
from collections import deque


class RateLimiter:
    """Sliding window rate limiter for API requests"""
    
    def __init__(self, max_requests=20, window_seconds=60):
        """
        Initialize rate limiter.
        
        Args:
            max_requests: Maximum requests allowed per window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.user_requests = {}  # {user_id: deque of timestamps}
    
    def check(self, user_id: str) -> bool:
        """
        Check if user exceeded rate limit.
        
        Args:
            user_id: User identifier
            
        Returns:
            True if allowed, False if exceeded
        """
        now = time.time()
        
        if user_id not in self.user_requests:
            self.user_requests[user_id] = deque()
        
        # Remove old requests outside window
        while self.user_requests[user_id] and (now - self.user_requests[user_id][0]) > self.window_seconds:
            self.user_requests[user_id].popleft()
        
        # Check if exceeded
        if len(self.user_requests[user_id]) >= self.max_requests:
            return False
        
        # Add current request
        self.user_requests[user_id].append(now)
        return True
    
    def get_remaining(self, user_id: str) -> int:
        """
        Get remaining requests for user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Number of remaining requests
        """
        if user_id not in self.user_requests:
            return self.max_requests
        
        now = time.time()
        # Remove old requests
        while self.user_requests[user_id] and (now - self.user_requests[user_id][0]) > self.window_seconds:
            self.user_requests[user_id].popleft()
        
        return self.max_requests - len(self.user_requests[user_id])
