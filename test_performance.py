#!/usr/bin/env python3
"""
Performance test script for the LiteLLM MCP server.

This script benchmarks the server's response times and throughput
to help identify performance bottlenecks and optimize settings.
"""

import asyncio
import time
import statistics
from typing import List, Dict, Any
from server_litellm.server import _handle_completion, _handle_list_models
from performance_config import performance_monitor

# Test configurations
TEST_CONFIGS = [
    {
        "name": "Simple Query",
        "model": "gpt-4o",
        "messages": [{"role": "user", "content": "What is 2 + 2?"}],
        "temperature": 0.1,
        "max_tokens": 50
    },
    {
        "name": "Complex Query",
        "model": "gpt-4o",
        "messages": [{"role": "user", "content": "Explain quantum computing in detail."}],
        "temperature": 0.7,
        "max_tokens": 500
    },
    {
        "name": "Claude Simple",
        "model": "anthropic.claude-3-7-sonnet-20250219-v1:0",
        "messages": [{"role": "user", "content": "What is the capital of France?"}],
        "temperature": 0.1,
        "max_tokens": 50
    },
    {
        "name": "Claude Complex",
        "model": "anthropic.claude-3-7-sonnet-20250219-v1:0",
        "messages": [{"role": "user", "content": "Write a detailed analysis of climate change impacts."}],
        "temperature": 0.7,
        "max_tokens": 800
    }
]

async def run_single_test(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run a single performance test.
    
    Args:
        config: Test configuration
        
    Returns:
        Test results including timing and response data
    """
    start_time = time.time()
    
    try:
        arguments = {
            "model": config["model"],
            "messages": config["messages"],
            "temperature": config["temperature"],
            "max_tokens": config["max_tokens"]
        }
        
        result = await _handle_completion(arguments)
        end_time = time.time()
        
        duration = end_time - start_time
        response_text = result[0].text
        response_length = len(response_text)
        
        # Record performance metrics
        performance_monitor.record_request(duration)
        
        return {
            "success": True,
            "duration": duration,
            "response_length": response_length,
            "response_preview": response_text[:100] + "..." if len(response_text) > 100 else response_text,
            "error": None
        }
        
    except Exception as e:
        end_time = time.time()
        duration = end_time - start_time
        
        return {
            "success": False,
            "duration": duration,
            "response_length": 0,
            "response_preview": "",
            "error": str(e)
        }

async def run_performance_suite(iterations: int = 5) -> Dict[str, Any]:
    """
    Run a complete performance test suite.
    
    Args:
        iterations: Number of iterations per test configuration
        
    Returns:
        Comprehensive performance results
    """
    print(f"🚀 Starting Performance Test Suite ({iterations} iterations per test)")
    print("=" * 80)
    
    all_results = {}
    total_tests = len(TEST_CONFIGS) * iterations
    
    for i, config in enumerate(TEST_CONFIGS):
        print(f"\n📊 Testing: {config['name']} ({config['model']})")
        print("-" * 60)
        
        test_results = []
        
        for j in range(iterations):
            print(f"  Iteration {j+1}/{iterations}...", end=" ")
            
            result = await run_single_test(config)
            test_results.append(result)
            
            if result["success"]:
                print(f"✅ {result['duration']:.2f}s ({result['response_length']} chars)")
            else:
                print(f"❌ {result['duration']:.2f}s - {result['error']}")
        
        # Calculate statistics for this test
        successful_results = [r for r in test_results if r["success"]]
        
        if successful_results:
            durations = [r["duration"] for r in successful_results]
            response_lengths = [r["response_length"] for r in successful_results]
            
            all_results[config["name"]] = {
                "model": config["model"],
                "total_tests": iterations,
                "successful_tests": len(successful_results),
                "success_rate": len(successful_results) / iterations * 100,
                "avg_duration": statistics.mean(durations),
                "min_duration": min(durations),
                "max_duration": max(durations),
                "std_duration": statistics.stdev(durations) if len(durations) > 1 else 0,
                "avg_response_length": statistics.mean(response_lengths),
                "total_duration": sum(durations),
                "errors": [r["error"] for r in test_results if not r["success"]]
            }
        else:
            all_results[config["name"]] = {
                "model": config["model"],
                "total_tests": iterations,
                "successful_tests": 0,
                "success_rate": 0,
                "avg_duration": 0,
                "min_duration": 0,
                "max_duration": 0,
                "std_duration": 0,
                "avg_response_length": 0,
                "total_duration": 0,
                "errors": [r["error"] for r in test_results]
            }
    
    return all_results

def print_performance_report(results: Dict[str, Any]):
    """
    Print a comprehensive performance report.
    
    Args:
        results: Performance test results
    """
    print("\n" + "=" * 80)
    print("📈 PERFORMANCE TEST REPORT")
    print("=" * 80)
    
    # Overall statistics
    total_tests = sum(r["total_tests"] for r in results.values())
    total_successful = sum(r["successful_tests"] for r in results.values())
    overall_success_rate = (total_successful / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\n🎯 Overall Results:")
    print(f"   Total Tests: {total_tests}")
    print(f"   Successful: {total_successful}")
    print(f"   Success Rate: {overall_success_rate:.1f}%")
    print(f"   Average Response Time: {performance_monitor.get_average_response_time():.2f}s")
    print(f"   Slow Requests (>5s): {performance_monitor.slow_requests} ({performance_monitor.get_slow_request_percentage():.1f}%)")
    
    # Per-test results
    print(f"\n📊 Detailed Results:")
    print("-" * 80)
    print(f"{'Test Name':<20} {'Model':<35} {'Avg Time':<10} {'Success':<8} {'Rate':<6}")
    print("-" * 80)
    
    for test_name, result in results.items():
        model_display = result["model"][:34] + "..." if len(result["model"]) > 35 else result["model"]
        print(f"{test_name:<20} {model_display:<35} {result['avg_duration']:<10.2f} {result['successful_tests']:<8} {result['success_rate']:<6.1f}%")
    
    # Performance recommendations
    print(f"\n💡 Performance Recommendations:")
    
    avg_response_time = performance_monitor.get_average_response_time()
    if avg_response_time > 10.0:
        print("   ⚠️  Average response time is high (>10s). Consider:")
        print("      - Reducing max_tokens for faster responses")
        print("      - Using streaming for better perceived performance")
        print("      - Checking network connectivity to the proxy")
    
    if performance_monitor.get_slow_request_percentage() > 20:
        print("   ⚠️  High percentage of slow requests. Consider:")
        print("      - Increasing HTTP timeout settings")
        print("      - Optimizing connection pool settings")
        print("      - Monitoring proxy server performance")
    
    if overall_success_rate < 95:
        print("   ⚠️  Success rate is below 95%. Consider:")
        print("      - Checking API key validity")
        print("      - Verifying proxy server status")
        print("      - Reviewing error logs for patterns")
    
    if avg_response_time < 3.0 and overall_success_rate > 95:
        print("   ✅ Performance is excellent! Current settings are optimal.")

async def main():
    """Main function to run the performance test suite."""
    print("🔧 LiteLLM MCP Server Performance Test")
    print("=" * 50)
    
    # Test model listing first
    try:
        print("Testing model listing...")
        models_result = await _handle_list_models()
        print(f"✅ Available models: {models_result[0].text}")
    except Exception as e:
        print(f"❌ Error listing models: {e}")
        return
    
    # Run performance tests
    iterations = 3  # Adjust based on your needs
    results = await run_performance_suite(iterations)
    
    # Print report
    print_performance_report(results)
    
    print(f"\n🏁 Performance test completed!")
    print(f"   Total requests: {performance_monitor.request_count}")
    print(f"   Total time: {performance_monitor.total_response_time:.2f}s")

if __name__ == "__main__":
    asyncio.run(main()) 