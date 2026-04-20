"""
Health Monitor Module — Application health and uptime tracking
"""

import time
from datetime import datetime


class HealthMonitor:
    """Monitor application health and performance"""
    
    def __init__(self):
        """Initialize health monitor"""
        self.start_time = time.time()
        self.request_count = 0
        self.error_count = 0
    
    def record_request(self, success: bool = True):
        """
        Record a request.
        
        Args:
            success: Whether request succeeded
        """
        self.request_count += 1
        if not success:
            self.error_count += 1
    
    def get_stats(self) -> dict:
        """
        Get health stats.
        
        Returns:
            Dictionary with health metrics
        """
        uptime = time.time() - self.start_time
        error_rate = (self.error_count / self.request_count * 100) if self.request_count > 0 else 0
        
        return {
            "status": "healthy" if error_rate < 5 else "degraded",
            "uptime_seconds": round(uptime, 2),
            "total_requests": self.request_count,
            "error_count": self.error_count,
            "error_rate": round(error_rate, 2)
        }
