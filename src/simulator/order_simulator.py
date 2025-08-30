"""Trading simulation utilities"""

import asyncio
import random
import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from services.exchange_service import Order
from services.routing_service import SmartOrderRouter


class TradingSimulator:
    """Simulates a trading session"""
    
    def __init__(self):
        self.router = SmartOrderRouter()
        self.simulation_results = []
    
    async def simulate_trading_session(self, num_orders: int = 100):
        """Simulate a trading session with multiple orders"""
        print(f"Starting simulation with {num_orders} orders...")
        
        symbols = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]
        order_types = ["MARKET", "LIMIT"]
        sides = ["BUY", "SELL"]
        
        tasks = []
        for i in range(num_orders):
            order = Order(
                order_id=f"SIM_{i:06d}",
                symbol=random.choice(symbols),
                quantity=random.uniform(100, 5000),
                order_type=random.choice(order_types),
                price=None,
                side=random.choice(sides),
                timestamp=int(time.time() * 1000)
            )
            
            tasks.append(self.router.route_order(order))
            
            if (i + 1) % 10 == 0:
                print(f"Submitted {i + 1}/{num_orders} orders...")
            
            await asyncio.sleep(0.05)
        
        results = await asyncio.gather(*tasks)
        self.simulation_results.extend(results)
        
        self._print_summary()
    
    def _print_summary(self):
        """Print simulation summary"""
        total = len(self.simulation_results)
        successful = sum(1 for r in self.simulation_results if r["success"])
        
        print(f"\nSimulation Summary:")
        print(f"Total Orders: {total}")
        print(f"Successful: {successful} ({successful/total*100:.2f}%)")

def run_simulation():
    """Entry point for simulation"""
    simulator = TradingSimulator()
    asyncio.run(simulator.simulate_trading_session(50))

if __name__ == "__main__":
    run_simulation()
