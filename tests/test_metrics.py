"""
Unit tests for metrics module in TA_Chatbot backend.
Run with: python -m pytest tests/test_metrics.py -v
"""
import sys
from pathlib import Path

# Add app/backend to sys.path
BACKEND_DIR = Path(__file__).parent.parent / "app" / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from obs.metrics import (
    record_request, record_error, snapshot, percentile,
    REQUEST_LATENCIES, REQUEST_COSTS, ERRORS, TRAFFIC
)


def test_percentile_calculation():
    """Test percentile function with known values"""
    values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    p50 = percentile(values, 50)
    p95 = percentile(values, 95)
    p99 = percentile(values, 99)
    
    assert 4 <= p50 <= 6, f"P50 should be around 5, got {p50}"
    assert 8 <= p95 <= 10, f"P95 should be around 9, got {p95}"
    assert 9 <= p99 <= 10, f"P99 should be around 10, got {p99}"


def test_record_request():
    """Test recording a single request"""
    record_request(
        latency_ms=1500,
        cost_usd=0.05,
        tokens_in=100,
        tokens_out=200,
        quality_score=0.85
    )
    
    snap = snapshot()
    assert snap['traffic'] >= 1
    assert snap['latency_p50'] > 0
    assert snap['total_cost_usd'] > 0


def test_error_tracking():
    """Test error recording and breakdown"""
    record_error("timeout")
    record_error("timeout")
    record_error("validation_error")
    
    snap = snapshot()
    assert snap['error_breakdown'].get('timeout', 0) >= 1
    assert snap['error_breakdown'].get('validation_error', 0) >= 1


def test_snapshot_structure():
    """Test snapshot returns all required fields"""
    record_request(latency_ms=2000, cost_usd=0.1)
    snap = snapshot()
    
    required_fields = {
        'traffic', 'latency_p50', 'latency_p95', 'latency_p99',
        'avg_cost_usd', 'total_cost_usd', 'tokens_in_total', 'tokens_out_total',
        'error_breakdown', 'quality_avg'
    }
    
    missing = required_fields - set(snap.keys())
    assert not missing, f"Missing: {missing}"


def test_percentile_basic() -> None:
    assert percentile([100, 200, 300, 400], 50) >= 100
