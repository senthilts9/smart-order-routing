"""Exchange simulation service"""

import asyncio
import random
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import numpy as np

@dataclass
class Order:
    order_id: str
    symbol: str
    quantity: float
    order_type: str
    price: Optional[float]
    side: str
    timestamp: int

@dataclass
class OrderBook:
    bids: List[Tuple[float, float]] = field(default_factory=list)
    asks: List[Tuple[float, float]] = field(default_factory=list)
    last_update: float = field(default_factory=time.time)


class ExchangeSimulator:
    """Simulates an exchange with order books and execution logic"""
    
    def __init__(self, exchange_id: str, base_latency: float = 5.0):
        self.exchange_id = exchange_id
        self.base_latency = base_latency
        self.order_books = {}
        self.executed_orders = []
        self.liquidity_factor = random.uniform(0.7, 1.0)
        self.fee_percentage = random.uniform(0.001, 0.003)
        self.is_active = True
        self.symbols = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]
        self._initialize_order_books()
    
    def _initialize_order_books(self):
        """Initialize synthetic order books"""
        for symbol in self.symbols:
            base_price = random.uniform(100, 500)
            self.order_books[symbol] = self._generate_order_book(base_price)
    
    def _generate_order_book(self, base_price: float) -> OrderBook:
        """Generate synthetic order book"""
        spread = base_price * 0.001
        
        bids = []
        for i in range(10):
            price = base_price - spread/2 - i*0.01
            volume = random.uniform(100, 1000) * self.liquidity_factor
            bids.append((price, volume))
        
        asks = []
        for i in range(10):
            price = base_price + spread/2 + i*0.01
            volume = random.uniform(100, 1000) * self.liquidity_factor
            asks.append((price, volume))
        
        return OrderBook(bids=bids, asks=asks)
    
    async def execute_order(self, order: Order) -> Dict:
        """Simulate order execution"""
        latency = self.base_latency + random.exponential(2)
        await asyncio.sleep(latency / 1000)
        
        if order.symbol not in self.order_books:
            return {"success": False, "reason": "Symbol not supported"}
        
        book = self.order_books[order.symbol]
        
        if order.order_type == "MARKET":
            executed_price = book.asks[0][0] if order.side == "BUY" else book.bids[0][0]
            executed_quantity = min(order.quantity, 
                                   book.asks[0][1] if order.side == "BUY" else book.bids[0][1])
        else:
            return {"success": False, "reason": "Limit orders simplified"}
        
        fee = executed_quantity * executed_price * self.fee_percentage
        
        return {
            "success": True,
            "exchange_id": self.exchange_id,
            "order_id": order.order_id,
            "executed_price": executed_price,
            "executed_quantity": executed_quantity,
            "fee": fee,
            "latency_ms": latency,
            "timestamp": time.time()
        }
    
    def get_market_data(self, symbol: str) -> Dict:
        """Get current market data"""
        if symbol not in self.order_books:
            return {}
        
        book = self.order_books[symbol]
        return {
            "exchange_id": self.exchange_id,
            "symbol": symbol,
            "bid_price": book.bids[0][0] if book.bids else 0,
            "ask_price": book.asks[0][0] if book.asks else 0,
            "bid_volume": book.bids[0][1] if book.bids else 0,
            "ask_volume": book.asks[0][1] if book.asks else 0,
            "spread": book.asks[0][0] - book.bids[0][0] if book.bids and book.asks else 0,
            "timestamp": book.last_update
        }
    
    def get_exchange_status(self) -> Dict:
        """Get exchange status"""
        return {
            "exchange_id": self.exchange_id,
            "is_active": self.is_active,
            "latency_ms": self.base_latency,
            "liquidity_score": self.liquidity_factor,
            "fee_percentage": self.fee_percentage,
            "total_executed": len(self.executed_orders)
        }
