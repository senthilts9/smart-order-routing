"""Smart Order Routing Service"""

import asyncio
import random
import time
from typing import Dict, List
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from ml_models.routing_model import MLRoutingEngine, ExchangeFeatures
from services.exchange_service import ExchangeSimulator, Order


class SmartOrderRouter:
    """Intelligent order routing across multiple exchanges"""
    
    def __init__(self):
        self.ml_engine = MLRoutingEngine()
        self.exchanges = self._initialize_exchanges()
        self.routing_history = []
        self.total_volume_routed = 0
        self.total_orders_routed = 0
    
    def _initialize_exchanges(self) -> Dict[str, ExchangeSimulator]:
        """Initialize multiple exchange simulators"""
        exchanges = {}
        exchange_configs = [
            ("NYSE", 3.0),
            ("NASDAQ", 2.5),
            ("BATS", 4.0),
            ("IEX", 10.0),
            ("ARCA", 3.5)
        ]
        
        for exchange_id, latency in exchange_configs:
            exchanges[exchange_id] = ExchangeSimulator(exchange_id, latency)
        
        return exchanges
    
    async def route_order(self, order: Order) -> Dict:
        """Route order using ML-driven smart routing"""
        start_time = time.time()
        
        # Get exchange features
        exchange_features = []
        for ex_id, exchange in self.exchanges.items():
            if not exchange.is_active:
                continue
            
            market_data = exchange.get_market_data(order.symbol)
            if not market_data:
                continue
            
            status = exchange.get_exchange_status()
            
            features = ExchangeFeatures(
                exchange_id=ex_id,
                latency_ms=status["latency_ms"],
                liquidity_score=status["liquidity_score"],
                spread=market_data.get("spread", 0.01),
                volume_imbalance=random.uniform(-1, 1),
                historical_fill_rate=0.95,
                fee_percentage=status["fee_percentage"],
                market_impact_estimate=0.001
            )
            exchange_features.append(features)
        
        if not exchange_features:
            return {
                "order_id": order.order_id,
                "success": False,
                "reason": "No active exchanges"
            }
        
        # Get optimal routing
        allocations = self.ml_engine.calculate_optimal_routing(
            order.quantity,
            exchange_features
        )
        
        # Execute orders
        execution_tasks = []
        routing_decisions = []
        
        for ex_id, allocated_qty in allocations.items():
            if allocated_qty > 0:
                sub_order = Order(
                    order_id=f"{order.order_id}_{ex_id}",
                    symbol=order.symbol,
                    quantity=allocated_qty,
                    order_type=order.order_type,
                    price=order.price,
                    side=order.side,
                    timestamp=order.timestamp
                )
                
                execution_tasks.append(
                    self.exchanges[ex_id].execute_order(sub_order)
                )
                
                routing_decisions.append({
                    "exchange_id": ex_id,
                    "allocated_quantity": allocated_qty,
                    "confidence_score": allocations[ex_id] / order.quantity,
                    "reason": f"ML Score: {allocations[ex_id]/order.quantity:.2%}"
                })
        
        # Wait for all executions
        execution_results = await asyncio.gather(*execution_tasks)
        
        # Aggregate results
        total_executed = sum(
            r.get("executed_quantity", 0) 
            for r in execution_results 
            if r.get("success", False)
        )
        
        total_fees = sum(
            r.get("fee", 0)
            for r in execution_results
            if r.get("success", False)
        )
        
        weighted_price = sum(
            r.get("executed_price", 0) * r.get("executed_quantity", 0)
            for r in execution_results
            if r.get("success", False)
        )
        
        avg_price = weighted_price / total_executed if total_executed > 0 else 0
        
        result = {
            "order_id": order.order_id,
            "success": total_executed > 0,
            "total_executed": total_executed,
            "average_price": avg_price,
            "total_fees": total_fees,
            "execution_time_ms": (time.time() - start_time) * 1000,
            "routing_decisions": routing_decisions,
            "fill_rate": total_executed / order.quantity if order.quantity > 0 else 0
        }
        
        self.total_volume_routed += total_executed
        self.total_orders_routed += 1
        self.ml_engine.update_performance(result)
        self.routing_history.append(result)
        
        return result
    
    def get_routing_statistics(self) -> Dict:
        """Get comprehensive routing statistics"""
        if not self.routing_history:
            return {
                "message": "No routing history available",
                "total_orders": 0,
                "total_volume": 0
            }
        
        successful_orders = [r for r in self.routing_history if r["success"]]
        
        return {
            "total_orders": self.total_orders_routed,
            "total_volume": self.total_volume_routed,
            "success_rate": len(successful_orders) / len(self.routing_history),
            "avg_execution_time_ms": sum(r["execution_time_ms"] for r in self.routing_history) / len(self.routing_history),
            "exchange_statistics": {}
        }
