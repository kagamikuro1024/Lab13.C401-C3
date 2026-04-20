"""
Timeout Test Runner - Test agent performance under heavy load scenarios
Measures response time, identifies timeout points, and logs results
"""

import requests
import json
import time
from pathlib import Path
from datetime import datetime

BASE_URL = "http://localhost:8000"
TIMEOUT_TESTS_FILE = Path(__file__).parent.parent / "data" / "test_timeout.json"
LOG_FILE = Path(__file__).parent.parent / "data" / "timeout_test_logs.jsonl"

def load_timeout_tests():
    """Load timeout test scenarios from JSON"""
    if not TIMEOUT_TESTS_FILE.exists():
        print(f"❌ Test file not found: {TIMEOUT_TESTS_FILE}")
        return []
    
    with open(TIMEOUT_TESTS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get("timeout_test_scenarios", [])

def run_timeout_test(scenario):
    """Run a single timeout test scenario"""
    test_id = scenario.get("id")
    name = scenario.get("name")
    content = scenario.get("content")
    user_id = scenario.get("user_id")
    timeout_seconds = scenario.get("timeout_seconds", 30)
    
    result = {
        "timestamp": datetime.now().isoformat(),
        "test_id": test_id,
        "name": name,
        "user_id": user_id,
        "timeout_limit": timeout_seconds,
        "status": "PENDING",
        "response_time_ms": 0,
        "http_status": None,
        "error": None,
        "response_length": 0,
        "success": False
    }
    
    print(f"\n▶️ [{test_id}] {name}")
    print(f"   Timeout limit: {timeout_seconds}s")
    print(f"   Query length: {len(content)} chars")
    print(f"   Processing...", end=" ", flush=True)
    
    try:
        start = time.time()
        
        response = requests.post(
            f"{BASE_URL}/chat",
            json={"content": content, "user_id": user_id},
            timeout=timeout_seconds
        )
        
        elapsed = (time.time() - start) * 1000
        result["response_time_ms"] = round(elapsed, 2)
        result["http_status"] = response.status_code
        result["response_length"] = len(response.text)
        
        if response.status_code == 200:
            result["status"] = "SUCCESS ✅"
            result["success"] = True
            print(f"✅ {elapsed/1000:.2f}s")
        else:
            result["status"] = f"ERROR ({response.status_code})"
            result["error"] = response.text[:200]
            print(f"❌ {elapsed/1000:.2f}s")
    
    except requests.exceptions.Timeout:
        elapsed = (time.time() - start) * 1000
        result["response_time_ms"] = round(elapsed, 2)
        result["status"] = f"TIMEOUT ⏱️ ({elapsed/1000:.2f}s > {timeout_seconds}s)"
        result["error"] = f"Request exceeded {timeout_seconds}s timeout"
        print(f"⏱️ TIMEOUT after {elapsed/1000:.2f}s")
    
    except requests.exceptions.ConnectionError as e:
        result["status"] = "CONNECTION_ERROR 🔌"
        result["error"] = str(e)
        print(f"🔌 Connection error")
    
    except Exception as e:
        result["status"] = "ERROR ❌"
        result["error"] = str(e)
        print(f"❌ Exception: {str(e)[:50]}")
    
    # Save to log file
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(json.dumps(result) + "\n")
    
    return result

def analyze_timeout_patterns(results):
    """Analyze timeout patterns and provide insights"""
    print(f"\n{'='*80}")
    print(f"📊 TIMEOUT ANALYSIS REPORT")
    print(f"{'='*80}\n")
    
    total = len(results)
    passed = sum(1 for r in results if r["success"])
    timeout_count = sum(1 for r in results if "TIMEOUT" in r["status"])
    error_count = total - passed
    
    print(f"Total Tests: {total}")
    print(f"✅ Passed: {passed}")
    print(f"⏱️ Timeouts: {timeout_count}")
    print(f"❌ Errors: {error_count}\n")
    
    if results:
        response_times = [r["response_time_ms"] for r in results if r["success"]]
        if response_times:
            print(f"Response Times:")
            print(f"  Min: {min(response_times):.0f}ms")
            print(f"  Max: {max(response_times):.0f}ms")
            print(f"  Avg: {sum(response_times)/len(response_times):.0f}ms\n")
    
    # Identify bottlenecks
    print(f"{'─'*80}")
    print(f"🔍 BOTTLENECK ANALYSIS:\n")
    
    for result in results:
        if not result["success"]:
            print(f"❌ [{result['test_id']}] {result['name']}")
            print(f"   Issue: {result['status']}")
            print(f"   Error: {result['error']}")
            print()

def main():
    print(f"{'='*80}")
    print(f"⏱️  TIMEOUT TEST RUNNER - Agent Performance Testing")
    print(f"{'='*80}\n")
    
    scenarios = load_timeout_tests()
    if not scenarios:
        print("❌ No timeout test scenarios loaded!")
        return
    
    print(f"📋 Loaded {len(scenarios)} timeout test scenarios\n")
    
    results = []
    for scenario in scenarios:
        result = run_timeout_test(scenario)
        results.append(result)
        time.sleep(1)  # Delay between tests
    
    analyze_timeout_patterns(results)
    
    print(f"{'='*80}")
    print(f"📝 Detailed logs saved to: {LOG_FILE}")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    main()
