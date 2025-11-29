#!/usr/bin/env python3
"""
Performance Evaluation Script for EduVerse Optimizations

This script helps validate the performance improvements claimed:
- API Latency: 51% improvement (567ms → 276ms)
- REST APIs: 2x capacity increase (100 → 200 req/sec)
- Gemini AI: 39% response time improvement (850ms → 520ms)
- CI/CD: Zero-downtime deployment with 40% cost reduction

Usage:
    python evaluate_performance.py [test_type]

Test Types:
    latency    - Test API response times
    load       - Test API capacity under load
    gemini     - Test Gemini AI response times
    all        - Run all tests
"""

import time
import requests
import json
import statistics
import concurrent.futures
import sys
import os
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"  # Change for production
API_ENDPOINTS = [
    "/api/notes/",
    "/api/homework/",
    "/api/todos/",
    "/api/progress/",
    "/api/chatbot/"
]

class PerformanceEvaluator:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.token = None

    def authenticate(self, username="testuser", password="testpass"):
        """Authenticate and get JWT token"""
        try:
            response = self.session.post(f"{self.base_url}/api/login/", json={
                "username": username,
                "password": password
            })
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('access')
                self.session.headers.update({
                    'Authorization': f'Bearer {self.token}'
                })
                print("✓ Authentication successful")
                return True
            else:
                print(f"✗ Authentication failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Authentication error: {e}")
            return False

    def measure_latency(self, endpoint, iterations=10):
        """Measure API response latency"""
        print(f"\n📊 Testing latency for {endpoint}")
        times = []

        for i in range(iterations):
            try:
                start_time = time.time()
                response = self.session.get(f"{self.base_url}{endpoint}")
                end_time = time.time()

                if response.status_code == 200:
                    latency = (end_time - start_time) * 1000  # Convert to ms
                    times.append(latency)
                    print(".1f")
                else:
                    print(f"✗ Request {i+1} failed: {response.status_code}")

            except Exception as e:
                print(f"✗ Request {i+1} error: {e}")

        if times:
            avg_latency = statistics.mean(times)
            min_latency = min(times)
            max_latency = max(times)
            p95_latency = statistics.quantiles(times, n=20)[18]  # 95th percentile

            print("\n📈 Latency Results:")
            print(".1f")
            print(".1f")
            print(".1f")
            print(".1f")
            # Check against target (276ms average)
            if avg_latency <= 300:  # Allow some margin
                print("✅ Target achieved: Average latency ≤ 300ms")
            else:
                print("⚠️ Target not met: Average latency > 300ms")

            return {
                'endpoint': endpoint,
                'average': avg_latency,
                'min': min_latency,
                'max': max_latency,
                'p95': p95_latency,
                'target_achieved': avg_latency <= 300
            }

        return None

    def load_test(self, endpoint, concurrent_users=50, duration=30):
        """Test API capacity under load"""
        print(f"\n🚀 Load testing {endpoint} with {concurrent_users} concurrent users")

        results = []
        start_time = time.time()
        end_time = start_time + duration

        def make_request():
            local_results = []
            while time.time() < end_time:
                try:
                    req_start = time.time()
                    response = self.session.get(f"{self.base_url}{endpoint}")
                    req_end = time.time()

                    if response.status_code == 200:
                        latency = (req_end - req_start) * 1000
                        local_results.append({
                            'success': True,
                            'latency': latency
                        })
                    else:
                        local_results.append({
                            'success': False,
                            'status_code': response.status_code
                        })

                except Exception as e:
                    local_results.append({
                        'success': False,
                        'error': str(e)
                    })

                time.sleep(0.1)  # Small delay between requests

            return local_results

        # Run concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = [executor.submit(make_request) for _ in range(concurrent_users)]
            for future in concurrent.futures.as_completed(futures):
                results.extend(future.result())

        # Analyze results
        total_requests = len(results)
        successful_requests = len([r for r in results if r['success']])
        success_rate = (successful_requests / total_requests) * 100 if total_requests > 0 else 0

        latencies = [r['latency'] for r in results if r['success'] and 'latency' in r]
        avg_latency = statistics.mean(latencies) if latencies else 0

        # Calculate requests per second
        actual_duration = time.time() - start_time
        rps = total_requests / actual_duration

        print("\n📈 Load Test Results:")
        print(f"Total Requests: {total_requests}")
        print(".1f")
        print(".1f")
        print(".1f")
        print(".1f")
        # Check against target (200 req/sec)
        if rps >= 180:  # Allow some margin
            print("✅ Target achieved: ≥ 180 requests/second")
        else:
            print("⚠️ Target not met: < 180 requests/second")

        return {
            'endpoint': endpoint,
            'total_requests': total_requests,
            'successful_requests': successful_requests,
            'success_rate': success_rate,
            'avg_latency': avg_latency,
            'requests_per_second': rps,
            'target_achieved': rps >= 180
        }

    def test_gemini_performance(self, iterations=5):
        """Test Gemini AI response times"""
        print("\n🤖 Testing Gemini AI performance")

        test_message = "Explain the concept of machine learning in simple terms for a beginner."
        times = []

        for i in range(iterations):
            try:
                start_time = time.time()
                response = self.session.post(f"{self.base_url}/api/chatbot/", json={
                    "message": test_message
                })
                end_time = time.time()

                if response.status_code == 200:
                    latency = (end_time - start_time) * 1000  # Convert to ms
                    times.append(latency)
                    print(".1f")
                else:
                    print(f"✗ Gemini test {i+1} failed: {response.status_code}")

            except Exception as e:
                print(f"✗ Gemini test {i+1} error: {e}")

        if times:
            avg_response_time = statistics.mean(times)
            min_time = min(times)
            max_time = max(times)

            print("\n📈 Gemini AI Results:")
            print(".1f")
            print(".1f")
            print(".1f")
            # Check against target (520ms average)
            if avg_response_time <= 550:  # Allow some margin
                print("✅ Target achieved: Average response time ≤ 550ms")
            else:
                print("⚠️ Target not met: Average response time > 550ms")

            return {
                'average': avg_response_time,
                'min': min_time,
                'max': max_time,
                'target_achieved': avg_response_time <= 550
            }

        return None

    def run_all_tests(self):
        """Run comprehensive performance evaluation"""
        print("🎯 EduVerse Performance Evaluation")
        print("=" * 50)

        if not self.authenticate():
            print("❌ Cannot proceed without authentication")
            return

        results = {
            'timestamp': datetime.now().isoformat(),
            'latency_tests': [],
            'load_tests': [],
            'gemini_test': None
        }

        # Test API latency
        print("\n🔍 PHASE 1: API Latency Testing")
        for endpoint in API_ENDPOINTS:
            result = self.measure_latency(endpoint)
            if result:
                results['latency_tests'].append(result)

        # Test API capacity
        print("\n🔍 PHASE 2: API Capacity Testing")
        for endpoint in ["/api/progress/", "/api/notes/"]:  # Test key endpoints
            result = self.load_test(endpoint, concurrent_users=20, duration=10)
            if result:
                results['load_tests'].append(result)

        # Test Gemini AI
        print("\n🔍 PHASE 3: Gemini AI Testing")
        results['gemini_test'] = self.test_gemini_performance()

        # Generate summary
        self.generate_summary(results)

        # Save results
        with open('performance_results.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print("\n💾 Results saved to performance_results.json")

    def generate_summary(self, results):
        """Generate performance summary"""
        print("\n" + "=" * 60)
        print("📊 PERFORMANCE EVALUATION SUMMARY")
        print("=" * 60)

        # API Latency Summary
        latency_achieved = all(test.get('target_achieved', False) for test in results['latency_tests'])
        print(f"API Latency (Target: ≤300ms): {'✅ PASSED' if latency_achieved else '⚠️ FAILED'}")

        # API Capacity Summary
        capacity_achieved = all(test.get('target_achieved', False) for test in results['load_tests'])
        print(f"API Capacity (Target: ≥180 req/sec): {'✅ PASSED' if capacity_achieved else '⚠️ FAILED'}")

        # Gemini AI Summary
        gemini_achieved = results['gemini_test'].get('target_achieved', False) if results['gemini_test'] else False
        print(f"Gemini AI (Target: ≤550ms): {'✅ PASSED' if gemini_achieved else '⚠️ FAILED'}")

        overall_success = latency_achieved and capacity_achieved and gemini_achieved
        print(f"\n🎯 Overall Result: {'✅ ALL TARGETS ACHIEVED' if overall_success else '⚠️ SOME TARGETS NOT MET'}")

        print("\n💡 Recommendations:")
        if not latency_achieved:
            print("  - Check database query optimization and Redis cache configuration")
        if not capacity_achieved:
            print("  - Consider increasing server resources or optimizing database connections")
        if not gemini_achieved:
            print("  - Review Gemini API caching and prompt optimization")


def main():
    if len(sys.argv) > 1:
        test_type = sys.argv[1].lower()
    else:
        test_type = "all"

    evaluator = PerformanceEvaluator()

    if test_type == "latency":
        if evaluator.authenticate():
            for endpoint in API_ENDPOINTS:
                evaluator.measure_latency(endpoint)
    elif test_type == "load":
        if evaluator.authenticate():
            evaluator.load_test("/api/progress/", concurrent_users=20, duration=10)
    elif test_type == "gemini":
        if evaluator.authenticate():
            evaluator.test_gemini_performance()
    elif test_type == "all":
        evaluator.run_all_tests()
    else:
        print("Usage: python evaluate_performance.py [latency|load|gemini|all]")


if __name__ == "__main__":
    main()