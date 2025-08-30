"""Smart Order Routing API - Test Version"""
import random
import time
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn
import json
import asyncio

app = FastAPI(title="Smart Order Routing API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Track statistics
stats = {
    "total_orders": 100000,  # Pre-loaded with your test results
    "total_volume": 255003751,
    "total_value": 44616137301.77,
    "success_rate": 1.0,
    "avg_latency": 34.66,
    "p50_latency": 32.17,
    "p99_latency": 77.48,
    "throughput": 1188.09
}

exchanges_data = {
    "NYSE": {"orders": 20000, "volume": 51000000, "latency": 3.0},
    "NASDAQ": {"orders": 25000, "volume": 63750000, "latency": 2.5},
    "BATS": {"orders": 30000, "volume": 76500000, "latency": 4.0},
    "IEX": {"orders": 10000, "volume": 25500000, "latency": 10.0},
    "ARCA": {"orders": 15000, "volume": 38250000, "latency": 3.5}
}

class OrderRequest(BaseModel):
    symbol: str = Field(default="AAPL")
    quantity: float = Field(default=1000, gt=0)
    order_type: str = Field(default="MARKET")
    side: str = Field(default="BUY")

@app.get("/")
async def root():
    return {
        "status": "operational",
        "stats": stats
    }

@app.post("/orders")
async def submit_order(order: OrderRequest):
    """Simulate order execution"""
    exchange = random.choice(list(exchanges_data.keys()))
    latency = random.uniform(20, 60)
    
    return {
        "order_id": f"ORD_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
        "success": True,
        "symbol": order.symbol,
        "quantity": order.quantity,
        "side": order.side,
        "executed_price": random.uniform(170, 180),
        "exchange": exchange,
        "latency_ms": latency,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/stats")
async def get_stats():
    return stats

@app.get("/exchanges")
async def get_exchanges():
    return exchanges_data

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Send random trade data
            trade = {
                "type": "trade",
                "symbol": random.choice(["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]),
                "price": random.uniform(100, 400),
                "volume": random.randint(100, 5000),
                "exchange": random.choice(list(exchanges_data.keys())),
                "timestamp": datetime.now().isoformat()
            }
            await websocket.send_json(trade)
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        pass

if __name__ == "__main__":
    print("\n" + "="*60)
    print("SMART ORDER ROUTING TEST SERVER")
    print("="*60)
    print("Starting server on http://localhost:8000")
    print("After server starts, open test.html in your browser")
    print("="*60 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")