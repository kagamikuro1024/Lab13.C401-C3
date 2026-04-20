"""
Timeout Monitoring System - Track timeout risks and optimize performance
"""

import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json

class TimeoutMonitor:
    """Monitor timeout risks and patterns"""
    
    def __init__(self, window_size_seconds: int = 3600):
        self.request_times: List[float] = []
        self.timeout_events: List[Dict] = []
        self.window_size = window_size_seconds
        self.request_count = 0
        self.timeout_count = 0
    
    def record_request_time(self, duration_ms: float, request_id: str = None):
        """Record request duration"""
        now = time.time()
        
        # Clean old entries outside window
        self.request_times = [
            t for t in self.request_times 
            if now - t < self.window_size
        ]
        
        self.request_times.append(duration_ms)
        self.request_count += 1
    
    def record_timeout_event(self, request_id: str, duration_ms: float, reason: str = "Unknown"):
        """Log timeout event for analysis"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "request_id": request_id,
            "duration_ms": duration_ms,
            "reason": reason,
            "event_type": "timeout"
        }
        self.timeout_events.append(event)
        self.timeout_count += 1
        
        # Keep last 100 timeout events
        if len(self.timeout_events) > 100:
            self.timeout_events = self.timeout_events[-100:]
    
    def get_stats(self) -> Dict:
        """Get timeout risk statistics"""
        if not self.request_times:
            return {
                "status": "no_data",
                "request_count": 0,
                "timeout_count": 0,
                "timeout_risk": "UNKNOWN"
            }
        
        sorted_times = sorted(self.request_times)
        count = len(sorted_times)
        
        # Calculate percentiles
        p50_idx = max(0, int(count * 0.50) - 1)
        p95_idx = max(0, int(count * 0.95) - 1)
        p99_idx = max(0, int(count * 0.99) - 1)
        
        p50 = sorted_times[p50_idx] if p50_idx < count else 0
        p95 = sorted_times[p95_idx] if p95_idx < count else 0
        p99 = sorted_times[p99_idx] if p99_idx < count else 0
        
        avg_time = sum(self.request_times) / count
        max_time = max(self.request_times)
        
        # Determine timeout risk level
        if p95 > 22000:  # 22 seconds (approaching 25s limit)
            timeout_risk = "HIGH"
            risk_level = 3
        elif p95 > 18000:  # 18 seconds
            timeout_risk = "MEDIUM"
            risk_level = 2
        else:
            timeout_risk = "LOW"
            risk_level = 1
        
        timeout_rate = (self.timeout_count / self.request_count * 100) if self.request_count > 0 else 0
        
        return {
            "status": "ok",
            "request_count": count,
            "total_requests": self.request_count,
            "timeout_count": self.timeout_count,
            "timeout_rate_percent": round(timeout_rate, 2),
            "avg_time_ms": round(avg_time, 2),
            "p50_time_ms": round(p50, 2),
            "p95_time_ms": round(p95, 2),
            "p99_time_ms": round(p99, 2),
            "max_time_ms": round(max_time, 2),
            "timeout_risk": timeout_risk,
            "risk_level": risk_level,
            "recommended_timeout": max(25000, int(p99 * 1.2)),  # 20% buffer
            "last_updated": datetime.now().isoformat()
        }
    
    def get_recent_timeouts(self, limit: int = 10) -> List[Dict]:
        """Get recent timeout events"""
        return self.timeout_events[-limit:]
    
    def should_alert(self) -> bool:
        """Check if timeout alert should be triggered"""
        stats = self.get_stats()
        if stats["status"] == "no_data":
            return False
        
        # Alert conditions:
        # 1. More than 5% timeout rate
        # 2. P95 latency exceeding 22s (approaching limit)
        # 3. Any timeout event in last minute
        
        if stats["timeout_rate_percent"] > 5:
            return True
        
        if stats["p95_time_ms"] > 22000:
            return True
        
        recent_timeouts = [
            e for e in self.timeout_events 
            if (datetime.now() - datetime.fromisoformat(e["timestamp"])).total_seconds() < 60
        ]
        
        if len(recent_timeouts) > 0:
            return True
        
        return False
    
    def get_alert_message(self) -> Optional[str]:
        """Generate alert message if needed"""
        if not self.should_alert():
            return None
        
        stats = self.get_stats()
        messages = []
        
        if stats["timeout_rate_percent"] > 5:
            messages.append(f"⚠️ High timeout rate: {stats['timeout_rate_percent']}%")
        
        if stats["p95_time_ms"] > 22000:
            messages.append(f"⚠️ P95 latency high: {stats['p95_time_ms']:.0f}ms (approaching 25s limit)")
        
        if stats["timeout_risk"] == "HIGH":
            messages.append(f"🚨 TIMEOUT RISK: {stats['timeout_risk']} - Immediate action needed")
        
        return " | ".join(messages) if messages else None
    
    def to_json(self) -> str:
        """Serialize to JSON"""
        return json.dumps({
            "stats": self.get_stats(),
            "recent_timeouts": self.get_recent_timeouts(5)
        }, indent=2)


# Global instance
timeout_monitor = TimeoutMonitor()
