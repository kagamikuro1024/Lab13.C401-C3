import requests
import json
import time
import concurrent.futures
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

BASE_URL = "http://localhost:8000"
SCENARIOS_FILE = Path(__file__).parent.parent / "data" / "stress_test_scenarios.json"

class StressTestRunner:
    def __init__(self):
        self.results = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "errors": [],
            "details": []
        }
        self.start_time = None
        self.end_time = None
    
    def load_scenarios(self) -> List[Dict]:
        """Load scenarios from JSON file"""
        if not SCENARIOS_FILE.exists():
            print(f"❌ Scenarios file not found: {SCENARIOS_FILE}")
            return []
        
        with open(SCENARIOS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get("scenarios", [])
    
    def run_single_scenario(self, scenario: Dict) -> Dict[str, Any]:
        """Run a single scenario and return result"""
        scenario_id = scenario.get("id")
        name = scenario.get("name")
        endpoint = scenario.get("endpoint")
        method = scenario.get("method", "POST")
        payload = scenario.get("payload", {})
        timeout = scenario.get("timeout", 30)
        expected_status = scenario.get("expected_status", 200)
        
        result = {
            "id": scenario_id,
            "name": name,
            "status": "FAILED",
            "actual_status": None,
            "error": None,
            "response_time_ms": 0,
            "passed": False
        }
        
        try:
            start = time.time()
            
            if method.upper() == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}", timeout=timeout)
            else:
                response = requests.post(f"{BASE_URL}{endpoint}", json=payload, timeout=timeout)
            
            elapsed = (time.time() - start) * 1000
            result["response_time_ms"] = round(elapsed, 2)
            result["actual_status"] = response.status_code
            
            # Check if status matches expected
            if response.status_code == expected_status:
                result["status"] = "PASSED ✅"
                result["passed"] = True
            else:
                result["status"] = f"FAILED (expected {expected_status}, got {response.status_code})"
                result["error"] = f"Status code mismatch"
            
        except requests.exceptions.Timeout:
            result["error"] = f"Timeout after {timeout}s"
            result["status"] = "TIMEOUT ⏱️"
        except requests.exceptions.ConnectionError as e:
            result["error"] = f"Connection error: {str(e)}"
            result["status"] = "CONNECTION_ERROR 🔌"
        except Exception as e:
            result["error"] = str(e)
            result["status"] = "ERROR ❌"
        
        return result
    
    def run_concurrent_scenario(self, scenario: Dict, concurrent_count: int = 5) -> List[Dict]:
        """Run scenario multiple times concurrently"""
        results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_count) as executor:
            futures = [executor.submit(self.run_single_scenario, scenario) for _ in range(concurrent_count)]
            for future in concurrent.futures.as_completed(futures):
                results.append(future.result())
        
        return results
    
    def run_all_scenarios(self):
        """Run all scenarios and collect results"""
        scenarios = self.load_scenarios()
        
        if not scenarios:
            print("❌ No scenarios loaded!")
            return
        
        self.start_time = datetime.now()
        print(f"\n{'='*80}")
        print(f"🚀 STRESS TEST RUNNER - Started at {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*80}\n")
        print(f"📊 Total scenarios to run: {len(scenarios)}\n")
        
        for scenario in scenarios:
            concurrent_count = scenario.get("concurrent_count")
            
            if concurrent_count:
                print(f"▶️ [{scenario['id']}] {scenario['name']} (x{concurrent_count} concurrent)...")
                results = self.run_concurrent_scenario(scenario, concurrent_count)
                for result in results:
                    self.results["details"].append(result)
                    self.results["total"] += 1
                    if result["passed"]:
                        self.results["passed"] += 1
                    else:
                        self.results["failed"] += 1
                        self.results["errors"].append({
                            "scenario": scenario['id'],
                            "error": result.get("error")
                        })
                
                # Print summary for concurrent
                passed_count = sum(1 for r in results if r["passed"])
                print(f"   └─ Results: {passed_count}/{len(results)} passed, " +
                      f"Avg time: {sum(r['response_time_ms'] for r in results) / len(results):.0f}ms\n")
            else:
                print(f"▶️ [{scenario['id']}] {scenario['name']}...", end=" ")
                result = self.run_single_scenario(scenario)
                self.results["details"].append(result)
                self.results["total"] += 1
                
                if result["passed"]:
                    self.results["passed"] += 1
                    print(f"✅ {result['response_time_ms']:.0f}ms")
                else:
                    self.results["failed"] += 1
                    self.results["errors"].append({
                        "scenario": scenario['id'],
                        "error": result.get("error")
                    })
                    print(f"❌ {result['status']}")
            
            time.sleep(0.5)  # Small delay between scenarios
        
        self.end_time = datetime.now()
        self.print_report()
    
    def print_report(self):
        """Print comprehensive report"""
        duration = (self.end_time - self.start_time).total_seconds()
        success_rate = (self.results["passed"] / self.results["total"] * 100) if self.results["total"] > 0 else 0
        
        print(f"\n{'='*80}")
        print(f"📈 TEST REPORT - Completed at {self.end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*80}\n")
        
        # Summary
        print(f"⏱️  Duration: {duration:.2f}s")
        print(f"📊 Total Scenarios: {self.results['total']}")
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"📉 Success Rate: {success_rate:.1f}%\n")
        
        # Detailed results
        if self.results["errors"]:
            print(f"{'─'*80}")
            print(f"🔴 ERROR DETAILS ({len(self.results['errors'])} errors):\n")
            for err in self.results["errors"]:
                print(f"  [{err['scenario']}] {err['error']}")
            print()
        
        # Performance stats
        print(f"{'─'*80}")
        print(f"⚡ PERFORMANCE STATS:\n")
        response_times = [d["response_time_ms"] for d in self.results["details"] if d["passed"]]
        if response_times:
            print(f"  Min response time: {min(response_times):.0f}ms")
            print(f"  Max response time: {max(response_times):.0f}ms")
            print(f"  Avg response time: {sum(response_times) / len(response_times):.0f}ms")
        
        # Status codes distribution
        print(f"\n{'─'*80}")
        print(f"🔍 STATUS CODE DISTRIBUTION:\n")
        status_counts = {}
        for detail in self.results["details"]:
            status = detail.get("actual_status", "N/A")
            status_counts[status] = status_counts.get(status, 0) + 1
        
        for status, count in sorted(status_counts.items()):
            percentage = (count / self.results["total"] * 100)
            print(f"  {status}: {count} ({percentage:.1f}%)")
        
        print(f"\n{'='*80}\n")
        
        # Recommendation
        if success_rate >= 95:
            print(f"✨ Excellent! All scenarios passing. Ready for production.\n")
        elif success_rate >= 80:
            print(f"⚠️  Some failures detected. Review error details above.\n")
        else:
            print(f"🚨 Critical issues found. Immediate investigation required.\n")

def main():
    runner = StressTestRunner()
    runner.run_all_scenarios()

if __name__ == "__main__":
    main()
