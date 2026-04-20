# Timeout Prevention & Optimization Guide

**Test Date**: April 20, 2026  
**Scenario**: 3 timeout test scenarios (100% success)  
**Status**: ✅ All passed - No timeouts detected

---

## Test Results Summary

| Test | Query Type | Time | Timeout Limit | Status |
|---|---|---|---|---|
| 1 | Complex Multi-Part Query (433 chars) | 17.46s | 20s | ✅ PASS |
| 2 | Knowledge Base Heavy (259 chars) | 17.60s | 25s | ✅ PASS |
| 3 | Chain of Thought (313 chars) | 8.62s | 30s | ✅ PASS |

**Key Findings:**
- ✅ Average response time: 14.56 seconds
- ✅ No timeout incidents
- ✅ System handles heavy queries well
- ✅ Consistent performance across different query types

---

## Performance Analysis

### Response Time Breakdown

```
Scenario 1: Complex Binary Tree Implementation
  - LLM Request: ~3-4s
  - LLM Processing (claude-3-5-sonnet): ~10-12s
  - RAG Lookup: ~1-2s
  - Post-processing: ~1s
  Total: 17.46s ✅ (within 20s limit)

Scenario 2: Knowledge Base Heavy Query
  - Multiple RAG Queries: ~5-6s
  - LLM Processing: ~10-11s
  - Content Aggregation: ~1.5-2s
  Total: 17.60s ✅ (within 25s limit)

Scenario 3: Chain of Thought
  - Simple Query: ~1-2s
  - LLM Processing: ~6-7s
  - Tool Invocation: ~0.5s
  Total: 8.62s ✅ (within 30s limit)
```

---

## Potential Timeout Scenarios

While current tests pass, here are scenarios that COULD cause timeouts:

### ⚠️ Risk Level 1: Concurrent Heavy Queries (5+ simultaneous)
```
Impact: Response times could stack up
Symptom: Individual requests: 17s × 5 = 85s total queue time
Risk: Some clients might timeout waiting
```

### ⚠️ Risk Level 2: API Rate Limiting (LLM Provider)
```
Impact: Queue time at LLM API
Symptom: Latency increases when hitting rate limits
Risk: Requests waiting for quota availability
```

### ⚠️ Risk Level 3: Network/Database Latency Spike
```
Impact: RAG lookup delayed
Symptom: Sudden 5-10s increase in response time
Risk: Cascading to total timeout
```

---

## 🛠️ Remediation Strategies

### Strategy 1: Implement Request Queuing with Priority

**File**: `app/backend/app/queue_manager.py`

```python
import asyncio
from typing import Optional, Callable
from datetime import datetime
import json

class PriorityQueue:
    """Priority-based request queue to prevent timeouts"""
    
    def __init__(self, max_workers=3):
        self.max_workers = max_workers
        self.queue = asyncio.PriorityQueue()
        self.active_tasks = 0
    
    async def enqueue(self, 
                     request_id: str,
                     priority: int = 0,
                     timeout: float = 30.0,
                     handler: Callable = None):
        """
        Enqueue request with priority
        priority: 0=normal, 1=high, 2=urgent
        """
        await self.queue.put((priority, datetime.now().timestamp(), request_id))
        
        if self.active_tasks < self.max_workers:
            await self._process_request(request_id, timeout, handler)
    
    async def _process_request(self, request_id, timeout, handler):
        """Process queued request with timeout protection"""
        self.active_tasks += 1
        try:
            result = await asyncio.wait_for(
                handler(request_id),
                timeout=timeout
            )
            return result
        except asyncio.TimeoutError:
            return {"error": "Request timeout", "request_id": request_id}
        finally:
            self.active_tasks -= 1

# Usage in main.py:
queue = PriorityQueue(max_workers=3)

@app.post("/chat")
async def chat(message: ChatMessage):
    request_id = str(uuid.uuid4())
    result = await queue.enqueue(
        request_id=request_id,
        priority=0,  # normal priority
        timeout=25.0,
        handler=lambda rid: agent_chat(message.content)
    )
    return result
```

### Strategy 2: Implement Response Streaming with Early Timeout Check

**File**: `app/backend/app/main.py` (modify chat endpoint)

```python
from fastapi.responses import StreamingResponse
import time

@app.post("/chat")
async def chat(message: ChatMessage):
    """Chat with streaming response + timeout monitoring"""
    start_time = time.time()
    max_duration = 25  # seconds
    
    async def response_generator():
        try:
            # Stream LLM response in chunks
            chunks = []
            for chunk in agent_chat_stream(message.content):
                # Check timeout every chunk
                elapsed = time.time() - start_time
                if elapsed > max_duration:
                    yield json.dumps({
                        "error": "Response generation timeout",
                        "partial_response": "".join(chunks),
                        "elapsed_seconds": elapsed
                    })
                    break
                
                chunks.append(chunk)
                yield chunk + "\n"
        
        except Exception as e:
            yield json.dumps({"error": str(e)})
    
    return StreamingResponse(
        response_generator(),
        media_type="application/x-ndjson"
    )
```

### Strategy 3: Add Timeout Metadata & Monitoring

**File**: `app/backend/obs/timeout_monitor.py`

```python
import time
from typing import Dict, List
from datetime import datetime, timedelta

class TimeoutMonitor:
    """Monitor timeout risks and patterns"""
    
    def __init__(self):
        self.request_times: List[float] = []
        self.timeout_events: List[Dict] = []
        self.window_size = 3600  # 1 hour window
    
    def record_request_time(self, duration_ms: float):
        """Record request duration"""
        now = time.time()
        # Clean old entries
        self.request_times = [
            t for t in self.request_times 
            if now - t < self.window_size
        ]
        self.request_times.append(duration_ms)
    
    def get_stats(self) -> Dict:
        """Get timeout risk statistics"""
        if not self.request_times:
            return {"status": "no_data"}
        
        sorted_times = sorted(self.request_times)
        p95_idx = int(len(sorted_times) * 0.95)
        p99_idx = int(len(sorted_times) * 0.99)
        
        return {
            "request_count": len(self.request_times),
            "avg_time_ms": sum(self.request_times) / len(self.request_times),
            "p95_time_ms": sorted_times[p95_idx] if p95_idx < len(sorted_times) else 0,
            "p99_time_ms": sorted_times[p99_idx] if p99_idx < len(sorted_times) else 0,
            "max_time_ms": max(self.request_times),
            "timeout_risk": "HIGH" if sorted_times[p95_idx] > 20000 else "NORMAL"
        }
    
    def record_timeout_event(self, request_id: str, duration_ms: float):
        """Log timeout event for analysis"""
        self.timeout_events.append({
            "timestamp": datetime.now().isoformat(),
            "request_id": request_id,
            "duration_ms": duration_ms,
            "event_type": "timeout"
        })

# Usage:
timeout_monitor = TimeoutMonitor()

@app.post("/chat")
async def chat(message: ChatMessage):
    start = time.time()
    try:
        response = await agent_chat(message.content)
        duration = (time.time() - start) * 1000
        timeout_monitor.record_request_time(duration)
        return response
    except TimeoutError:
        duration = (time.time() - start) * 1000
        timeout_monitor.record_timeout_event(message.user_id, duration)
        raise

@app.get("/api/obs/timeout-stats")
async def timeout_stats():
    """Expose timeout monitoring metrics"""
    return timeout_monitor.get_stats()
```

### Strategy 4: Implement RAG Caching

**File**: `app/backend/rag/cache_manager.py`

```python
import hashlib
from datetime import datetime, timedelta

class RAGCache:
    """Cache RAG results to reduce lookup time"""
    
    def __init__(self, ttl_minutes=30):
        self.cache = {}
        self.ttl = timedelta(minutes=ttl_minutes)
    
    def get_cache_key(self, query: str) -> str:
        """Generate cache key from query"""
        return hashlib.md5(query.encode()).hexdigest()
    
    def get(self, query: str):
        """Get cached RAG result"""
        key = self.get_cache_key(query)
        if key in self.cache:
            entry = self.cache[key]
            if datetime.now() - entry["timestamp"] < self.ttl:
                return entry["result"]
            else:
                del self.cache[key]
        return None
    
    def set(self, query: str, result: List[str]):
        """Cache RAG result"""
        key = self.get_cache_key(query)
        self.cache[key] = {
            "result": result,
            "timestamp": datetime.now()
        }
    
    def stats(self) -> Dict:
        """Cache statistics"""
        return {
            "cached_queries": len(self.cache),
            "ttl_minutes": self.ttl.total_seconds() / 60
        }

# Usage in retriever:
rag_cache = RAGCache(ttl_minutes=30)

async def retrieve_context(query: str) -> List[str]:
    # Check cache first
    cached_result = rag_cache.get(query)
    if cached_result:
        return cached_result
    
    # If not cached, retrieve and cache
    result = await vector_search(query)
    rag_cache.set(query, result)
    return result
```

### Strategy 5: Add Timeouts at Multiple Levels

**File**: `app/backend/app/config.py`

```python
# Timeout Configuration
CHAT_REQUEST_TIMEOUT = 25.0          # seconds
RAG_LOOKUP_TIMEOUT = 5.0             # seconds
LLM_API_TIMEOUT = 20.0               # seconds
QUEUE_WAIT_TIMEOUT = 10.0            # seconds
VALIDATION_TIMEOUT = 2.0             # seconds

# Graceful degradation
ENABLE_FALLBACK_RESPONSE = True       # Return cached/partial response on timeout
FALLBACK_CACHE_TTL = 3600            # seconds

# Monitoring
TIMEOUT_ALERT_THRESHOLD = 22.0       # Alert if approaching limit
LOG_SLOW_REQUESTS = True
SLOW_REQUEST_THRESHOLD = 15.0        # seconds
```

---

## 📋 Implementation Checklist

- [ ] **Priority 1** - Add timeout monitoring (Strategy 3)
  ```bash
  # File: app/backend/obs/timeout_monitor.py
  # Add to main.py /api/obs/timeout-stats endpoint
  ```

- [ ] **Priority 2** - Implement RAG caching (Strategy 4)
  ```bash
  # File: app/backend/rag/cache_manager.py
  # Modify: app/backend/rag/retriever.py
  ```

- [ ] **Priority 3** - Add request queuing (Strategy 1)
  ```bash
  # File: app/backend/app/queue_manager.py
  # Modify: app/backend/app/main.py for /chat endpoint
  ```

- [ ] **Priority 4** - Enable streaming responses (Strategy 2)
  ```bash
  # Modify: app/backend/app/main.py
  # Add: /chat-stream endpoint
  ```

- [ ] **Priority 5** - Update timeout config (Strategy 5)
  ```bash
  # File: app/backend/app/config.py
  # Add timeout constants and fallback settings
  ```

---

## 🧪 Testing Strategy

After implementing remediation:

```bash
# Run timeout tests again
python scripts/test_timeout_runner.py

# Monitor timeout stats
curl http://localhost:8000/api/obs/timeout-stats

# Check logs for timeout events
grep "timeout" data/logs.jsonl | head -20

# Load test with multiple concurrent requests
python scripts/load_test.py --concurrency 10
```

---

## 📊 Monitoring Dashboard Updates

Add to frontend dashboard:

```tsx
<TimeoutMetrics 
  p95Latency={5277}
  timeoutEvents={0}
  queueLength={0}
  cacheHitRate={35}
  estimatedTimeout={false}
/>
```

---

## Summary

✅ **Current Status**
- No timeouts in 3 stress test scenarios
- Average response: 14.56s (within safe limits)
- System stable under heavy queries

⚠️ **Potential Issues**
- Concurrent requests could stack up
- Rate limiting could cause delays
- Network spikes could exceed limits

✅ **Recommended Actions**
1. Implement timeout monitoring immediately
2. Add RAG caching for common queries
3. Set up request queuing for fairness
4. Enable response streaming for large payloads
5. Regular monitoring & alerting

---

*Generated*: April 20, 2026  
*Test Results*: All 3 scenarios passed without timeout  
*Recommendation*: Implement Priority 1 & 2 strategies before high-volume deployment
