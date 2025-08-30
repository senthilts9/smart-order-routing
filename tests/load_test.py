"""
Smart Order Routing - Load Testing & Performance Analysis
Generates high volume of orders to test system performance
"""

import asyncio
import aiohttp
import time
import random
import json
from datetime import datetime
import statistics
import numpy as np

class LoadTester:
    def __init__(self, api_url="http://localhost:8000"):
        self.api_url = api_url
        self.results = []
        self.errors = []
        self.start_time = None
        self.end_time = None
        
    async def submit_order(self, session, order_num):
        """Submit a single order and measure performance"""
        order = {
            "symbol": random.choice(["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "META", "NVDA", "AMD"]),
            "quantity": random.randint(100, 5000),
            "order_type": "MARKET",
            "side": random.choice(["BUY", "SELL"])
        }
        
        start = time.time()
        try:
            async with session.post(f"{self.api_url}/orders", json=order) as response:
                result = await response.json()
                end = time.time()
                
                self.results.append({
                    "order_num": order_num,
                    "latency": (end - start) * 1000,  # Convert to ms
                    "exchange": result["routing_decisions"][0]["exchange_id"],
                    "success": result["success"],
                    "executed_qty": result["total_executed"],
                    "price": result["average_price"],
                    "api_time": result["execution_time_ms"]
                })
                
                if order_num % 100 == 0:
                    print(f"✓ Completed {order_num} orders...")
                    
        except Exception as e:
            self.errors.append({"order_num": order_num, "error": str(e)})
    
    async def run_load_test(self, num_orders=1000, concurrent=10):
        """Run load test with specified number of orders"""
        print(f"\n{'='*60}")
        print(f"SMART ORDER ROUTING - LOAD TEST")
        print(f"{'='*60}")
        print(f"Orders to submit: {num_orders}")
        print(f"Concurrent requests: {concurrent}")
        print(f"API URL: {self.api_url}")
        print(f"{'='*60}\n")
        
        self.start_time = time.time()
        
        async with aiohttp.ClientSession() as session:
            # Create batches for concurrent execution
            for i in range(0, num_orders, concurrent):
                batch = []
                for j in range(min(concurrent, num_orders - i)):
                    batch.append(self.submit_order(session, i + j + 1))
                await asyncio.gather(*batch)
        
        self.end_time = time.time()
        self.print_results(num_orders)
    
    def print_results(self, num_orders):
        """Print comprehensive performance analysis"""
        total_time = self.end_time - self.start_time
        successful = len([r for r in self.results if r["success"]])
        
        print(f"\n{'='*60}")
        print(f"PERFORMANCE RESULTS")
        print(f"{'='*60}")
        
        # Overall Statistics
        print(f"\n📊 OVERALL STATISTICS:")
        print(f"  Total Orders: {num_orders}")
        print(f"  Successful: {successful} ({successful/num_orders*100:.2f}%)")
        print(f"  Failed: {len(self.errors)} ({len(self.errors)/num_orders*100:.2f}%)")
        print(f"  Total Time: {total_time:.2f} seconds")
        print(f"  Throughput: {num_orders/total_time:.2f} orders/second")
        
        if self.results:
            latencies = [r["latency"] for r in self.results]
            api_times = [r["api_time"] for r in self.results]
            
            # Latency Analysis
            print(f"\n⚡ LATENCY ANALYSIS (Client-side):")
            print(f"  Min: {min(latencies):.2f}ms")
            print(f"  Max: {max(latencies):.2f}ms")
            print(f"  Avg: {statistics.mean(latencies):.2f}ms")
            print(f"  Median: {statistics.median(latencies):.2f}ms")
            print(f"  95th percentile: {np.percentile(latencies, 95):.2f}ms")
            print(f"  99th percentile: {np.percentile(latencies, 99):.2f}ms")
            
            # API Execution Time
            print(f"\n⏱️ API EXECUTION TIME (Server-side):")
            print(f"  Min: {min(api_times):.2f}ms")
            print(f"  Max: {max(api_times):.2f}ms")
            print(f"  Avg: {statistics.mean(api_times):.2f}ms")
            
            # Exchange Distribution
            print(f"\n🏢 EXCHANGE DISTRIBUTION:")
            exchange_counts = {}
            for r in self.results:
                ex = r["exchange"]
                exchange_counts[ex] = exchange_counts.get(ex, 0) + 1
            
            for exchange, count in sorted(exchange_counts.items(), key=lambda x: x[1], reverse=True):
                percentage = count / len(self.results) * 100
                print(f"  {exchange}: {count} orders ({percentage:.2f}%)")
            
            # Volume Statistics
            volumes = [r["executed_qty"] for r in self.results]
            prices = [r["price"] for r in self.results]
            total_value = sum(v * p for v, p in zip(volumes, prices))
            
            print(f"\n💰 VOLUME STATISTICS:")
            print(f"  Total Volume: {sum(volumes):,.0f} shares")
            print(f"  Total Value: ${total_value:,.2f}")
            print(f"  Avg Order Size: {statistics.mean(volumes):,.0f} shares")
            print(f"  Avg Price: ${statistics.mean(prices):.2f}")
        
        # Save detailed results
        self.save_results()
    
    def save_results(self):
        """Save detailed results to JSON file"""
        filename = f"load_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report = {
            "summary": {
                "total_orders": len(self.results) + len(self.errors),
                "successful": len(self.results),
                "failed": len(self.errors),
                "total_time": self.end_time - self.start_time,
                "throughput": len(self.results) / (self.end_time - self.start_time)
            },
            "results": self.results[:100],  # Save first 100 for review
            "errors": self.errors
        }
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📁 Detailed results saved to: {filename}")

async def stress_test():
    """Run different load test scenarios"""
    tester = LoadTester()
    
    print("\n🚀 STARTING LOAD TEST SCENARIOS\n")
    
    # Scenario 1: Warm-up
    print("Scenario 1: Warm-up (100 orders)")
    await tester.run_load_test(num_orders=100, concurrent=5)
    await asyncio.sleep(2)
    
    # Scenario 2: Normal Load
    print("\nScenario 2: Normal Load (1,000 orders)")
    tester = LoadTester()  # Reset
    await tester.run_load_test(num_orders=1000, concurrent=10)
    await asyncio.sleep(2)
    
    # Scenario 3: High Load
    print("\nScenario 3: High Load (10,000 orders)")
    tester = LoadTester()  # Reset
    await tester.run_load_test(num_orders=10000, concurrent=20)

async def continuous_test(duration_seconds=60):
    """Run continuous load test for specified duration"""
    tester = LoadTester()
    print(f"\n🔄 CONTINUOUS LOAD TEST ({duration_seconds} seconds)")
    
    order_num = 0
    start = time.time()
    
    async with aiohttp.ClientSession() as session:
        while time.time() - start < duration_seconds:
            order_num += 1
            await tester.submit_order(session, order_num)
            
            if order_num % 50 == 0:
                elapsed = time.time() - start
                rate = order_num / elapsed
                print(f"  Orders: {order_num} | Rate: {rate:.1f}/sec | Time: {elapsed:.1f}s")
    
    tester.end_time = time.time()
    tester.start_time = start
    tester.print_results(order_num)

if __name__ == "__main__":
    import sys
    
    print("="*60)
    print("SMART ORDER ROUTING - PERFORMANCE TESTER")
    print("="*60)
    print("\nSelect test type:")
    print("1. Quick Test (100 orders)")
    print("2. Standard Test (1,000 orders)")
    print("3. Heavy Load Test (10,000 orders)")
    print("4. Extreme Load Test (100,000 orders)")
    print("5. Continuous Test (60 seconds)")
    print("6. Full Stress Test (all scenarios)")
    
    choice = input("\nEnter choice (1-6): ").strip()
    
    if choice == "1":
        asyncio.run(LoadTester().run_load_test(100, 5))
    elif choice == "2":
        asyncio.run(LoadTester().run_load_test(1000, 10))
    elif choice == "3":
        asyncio.run(LoadTester().run_load_test(10000, 20))
    elif choice == "4":
        print("\n⚠️ WARNING: This will submit 100,000 orders!")
        confirm = input("Continue? (y/n): ")
        if confirm.lower() == 'y':
            asyncio.run(LoadTester().run_load_test(100000, 50))
    elif choice == "5":
        asyncio.run(continuous_test(60))
    elif choice == "6":
        asyncio.run(stress_test())
    else:
        print("Invalid choice. Running standard test...")
        asyncio.run(LoadTester().run_load_test(1000, 10))