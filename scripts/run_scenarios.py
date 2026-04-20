#!/usr/bin/env python3
"""
Simple Scenario Test Runner - Test scenarios from JSON file
Usage: python run_scenarios.py <scenario_file.json>
"""

import requests
import json
import sys
import time
from pathlib import Path

BASE_URL = "http://localhost:8000"

def run_scenario(scenario):
    """Run single scenario and return result"""
    scenario_id = scenario.get("id")
    name = scenario.get("name")
    endpoint = scenario.get("endpoint")
    method = scenario.get("method", "POST")
    payload = scenario.get("payload", {})
    timeout = scenario.get("timeout_seconds", 30)
    expected_status = scenario.get("expected_status", 200)
    
    print(f"\n▶️  [{scenario_id}] {name}")
    print(f"   {method} {endpoint}")
    
    try:
        start = time.time()
        
        if method == "POST":
            response = requests.post(f"{BASE_URL}{endpoint}", json=payload, timeout=timeout)
        else:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=timeout)
        
        elapsed = round((time.time() - start) * 1000, 0)
        status = response.status_code
        
        if status == expected_status:
            print(f"   ✅ {status} (expected {expected_status}) - {elapsed}ms")
            return True
        else:
            print(f"   ❌ {status} (expected {expected_status}) - {elapsed}ms")
            print(f"      Response: {response.text[:100]}")
            return False
    
    except requests.exceptions.Timeout:
        print(f"   ⏱️  TIMEOUT - exceeded {timeout}s")
        return False
    except Exception as e:
        print(f"   ❌ ERROR - {str(e)[:60]}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python run_scenarios.py <scenario_file.json>")
        print("\nExample:")
        print("  python run_scenarios.py docs/SCENARIO_EXAMPLES.json")
        sys.exit(1)
    
    scenario_file = Path(sys.argv[1])
    
    if not scenario_file.exists():
        print(f"❌ File not found: {scenario_file}")
        sys.exit(1)
    
    print(f"\n{'='*70}")
    print(f"🎯 SCENARIO TEST RUNNER")
    print(f"{'='*70}\n")
    
    with open(scenario_file) as f:
        data = json.load(f)
    
    scenarios = data.get("scenarios", [])
    print(f"📋 Loaded {len(scenarios)} scenarios from {scenario_file}\n")
    
    results = []
    for scenario in scenarios:
        passed = run_scenario(scenario)
        results.append(passed)
        time.sleep(0.5)
    
    passed_count = sum(results)
    total_count = len(results)
    
    print(f"\n{'='*70}")
    print(f"📊 RESULTS: {passed_count}/{total_count} passed")
    print(f"{'='*70}\n")
    
    return 0 if passed_count == total_count else 1

if __name__ == "__main__":
    sys.exit(main())
