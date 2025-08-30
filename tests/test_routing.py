"""Tests for routing service"""

import pytest
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from services.routing_service import SmartOrderRouter
from services.exchange_service import Order


@pytest.mark.asyncio
async def test_order_routing():
    """Test basic order routing"""
    router = SmartOrderRouter()
    
    order = Order(
        order_id="TEST_001",
        symbol="AAPL",
        quantity=1000,
        order_type="MARKET",
        price=None,
        side="BUY",
        timestamp=1234567890
    )
    
    result = await router.route_order(order)
    
    assert result["order_id"] == "TEST_001"
    assert "success" in result
    assert "routing_decisions" in result

if __name__ == "__main__":
    asyncio.run(test_order_routing())
    print("Tests passed!")
