"""Smart Order Routing API - Complete Working Version"""

import json
import asyncio
import random
import time
from datetime import datetime
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

app = FastAPI(title="Smart Order Routing API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Track orders for analytics
order_history = []

# Simple Exchange Simulator
exchanges = {}

class SimpleExchange:
    def __init__(self, exchange_id, latency=3.0):
        self.exchange_id = exchange_id
        self.latency_ms = latency
        self.liquidity_score = random.uniform(0.7, 1.0)
        self.fee_percentage = random.uniform(0.001, 0.003)
        self.is_active = True
        self.total_executed = 0
    
    def get_exchange_status(self):
        return {
            "exchange_id": self.exchange_id,
            "is_active": self.is_active,
            "latency_ms": self.latency_ms,
            "liquidity_score": self.liquidity_score,
            "fee_percentage": self.fee_percentage,
            "total_executed": self.total_executed
        }

# Initialize exchanges
exchanges["NYSE"] = SimpleExchange("NYSE", 3.0)
exchanges["NASDAQ"] = SimpleExchange("NASDAQ", 2.5)
exchanges["BATS"] = SimpleExchange("BATS", 4.0)
exchanges["IEX"] = SimpleExchange("IEX", 10.0)
exchanges["ARCA"] = SimpleExchange("ARCA", 3.5)

class OrderRequest(BaseModel):
    symbol: str = Field(default="AAPL", example="AAPL")
    quantity: float = Field(default=1000, gt=0, example=1000)
    order_type: str = Field(default="MARKET", pattern="^(MARKET|LIMIT)$", example="MARKET")
    price: Optional[float] = Field(default=None, gt=0)
    side: str = Field(default="BUY", pattern="^(BUY|SELL)$", example="BUY")

@app.get("/")
async def root():
    return {
        "message": "Smart Order Routing Simulator API",
        "version": "1.0.0",
        "status": "online",
        "endpoints": ["/docs", "/orders", "/exchanges", "/analytics/performance"]
    }

@app.post("/orders")
async def submit_order(order_request: OrderRequest):
    """Submit and route an order"""
    
    # Pick best exchange based on simple logic
    best_exchange = None
    best_score = -1
    
    for ex_id, exchange in exchanges.items():
        score = (1 / exchange.latency_ms) + (1 / exchange.fee_percentage)
        if score > best_score:
            best_score = score
            best_exchange = exchange
    
    # Simulate execution
    await asyncio.sleep(0.01)  # 10ms delay
    
    # Generate results
    executed_price = random.uniform(150, 200)
    fee = order_request.quantity * executed_price * best_exchange.fee_percentage
    
    # Update exchange stats
    best_exchange.total_executed += 1
    
    result = {
        "order_id": f"ORD_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "success": True,
        "total_executed": order_request.quantity,
        "average_price": executed_price,
        "total_fees": fee,
        "execution_time_ms": best_exchange.latency_ms,
        "routing_decisions": [{
            "exchange_id": best_exchange.exchange_id,
            "allocated_quantity": order_request.quantity,
            "confidence_score": 1.0,
            "reason": "Best latency/fee combination"
        }],
        "fill_rate": 1.0
    }
    
    # Store in history
    order_history.append(result)
    
    return result

@app.get("/exchanges")
async def get_exchanges():
    """Get all exchange statuses"""
    return [exchange.get_exchange_status() for exchange in exchanges.values()]

@app.get("/analytics/performance")
async def get_performance():
    """Get performance analytics"""
    total_orders = len(order_history)
    
    if total_orders == 0:
        return {
            "total_orders": 0,
            "total_volume": 0,
            "success_rate": 0,
            "avg_execution_time_ms": 0,
            "exchange_statistics": {}
        }
    
    total_volume = sum(order["total_executed"] for order in order_history)
    successful = sum(1 for order in order_history if order["success"])
    avg_time = sum(order["execution_time_ms"] for order in order_history) / total_orders
    
    # Exchange statistics
    exchange_stats = {}
    for exchange in exchanges.values():
        exchange_stats[exchange.exchange_id] = {
            "total_routed": exchange.total_executed,
            "percentage": (exchange.total_executed / total_orders * 100) if total_orders > 0 else 0
        }
    
    return {
        "total_orders": total_orders,
        "total_volume": total_volume,
        "success_rate": successful / total_orders if total_orders > 0 else 0,
        "avg_execution_time_ms": avg_time,
        "exchange_statistics": exchange_stats
    }

@app.get("/market-data/{symbol}")
async def get_market_data(symbol: str):
    """Get market data for a symbol"""
    market_data = {}
    for ex_id, exchange in exchanges.items():
        base_price = random.uniform(150, 200)
        market_data[ex_id] = {
            "exchange_id": ex_id,
            "symbol": symbol,
            "bid_price": base_price - 0.5,
            "ask_price": base_price + 0.5,
            "bid_volume": random.uniform(100, 1000),
            "ask_volume": random.uniform(100, 1000),
            "spread": 1.0,
            "timestamp": time.time()
        }
    return market_data

if __name__ == "__main__":
    print("="*60)
    print("SMART ORDER ROUTING API - Starting...")
    print("="*60)
    print("Server running at: http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    print("Dashboard should connect automatically")
    print("Press CTRL+C to stop")
    print("="*60)
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")