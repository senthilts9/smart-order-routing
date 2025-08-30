# Smart Order Routing System (SORS)

Institutional-grade algorithmic trading platform that ingests orders via REST/FIX, routes intelligently across venues, and exposes a real-time dashboard for performance, risk, and execution quality.

> **Why this exists**  
> Handling 100k+ orders with tight SLAs requires deterministic latency, smart venue selection, and rock-solid observability. SORS demonstrates how to architect a low-latency, high-throughput router with clean separation of concerns and production-grade practices you can extend at work or in interviews.

---

## Snapshot (Performance Test)
- **Total Orders:** 100,000  
- **Notional Value:** $44.6B (≈255M shares)  
- **Throughput:** 1,188 orders/sec *(peak 1,450/s)*  
- **Avg Latency:** 34.66 ms *(P50: 32.17 ms)*  
- **P99 Latency:** 77.48 ms *(max observed: 309 ms)*  
- **VWAP:** $174.99 *(avg $2,550/order)*  

### Exchange Routing Distribution (sample)
- **NYSE:** 20% | ~3.0 ms | ~51M shares  
- **NASDAQ:** 25% | ~2.5 ms | ~63.7M shares  
- **BATS:** 30% | ~4.0 ms | ~76.5M shares  
- **IEX:** 10% | ~10.0 ms | ~25.5M shares  
- **ARCA:** 15% | ~3.5 ms | ~38.3M shares  

> _Numbers shown are from a synthetic benchmark run for demo purposes._

If you’re viewing this on GitHub, the dashboard screenshot is in `docs/`:
![Smart Order Routing System Dashboard](docs/dashboard.png)

---

## Architecture

```
Client/Order Source
        │  (REST/FIX)
        ▼
┌───────────────────────────────────────┐
│  API Gateway (FastAPI)                │
│  • Auth, validation, rate limits      │
│  • Order normalization                │
└───────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────┐
│  Risk Check (Pre-trade)               │
│  • Max notional/qty                   │
│  • Fat-finger / symbol guardrails     │
│  • Market-state checks                │
└───────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────┐
│  ML Routing Engine                    │
│  • RandomForest / rules hybrid        │
│  • Features: venue latency, depth,    │
│    slippage history, queue position   │
└───────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────┐
│  Smart Router                         │
│  • Multi-venue execution (IOC/FOK)    │
│  • Partial fills & child orders       │
│  • Retry & venue fallback             │
└───────────────────────────────────────┘
        │
        ├──► Market adapters (NYSE/NASDAQ/BATS/IEX/ARCA)
        │
        └──► Analytics & TCA (Post-trade, VWAP, slippage, fill rate)
```

**System design highlights**
- Async I/O hot path: Python `asyncio` for request/response, WebSocket push for live metrics.
- Backpressure & flow control: bounded queues per stage; shed load gracefully.
- Observability: OpenTelemetry traces, metrics, and structured logs.
- Determinism: request-scoped IDs; idempotent submit; replayable event log.
- Extensibility: clean contracts between API → Risk → Router → Venue adapters.

---

## Technology Stack

- **Language:** Python 3.11 (async/await)  
- **API:** FastAPI + Uvicorn  
- **Streaming/IPC (optional):** Kafka/Redpanda or in-process queues for local demo  
- **ML:** scikit-learn (RandomForest) for venue scoring (optional rule-based fallback)  
- **Data:** Pandas/NumPy for features & TCA  
- **Dashboard:** React or FastAPI-served HTML + WebSocket for live updates  
- **Storage (optional):** PostgreSQL for TCA / audit logs  
- **Testing:** pytest + hypothesis (property tests)  
- **Obs:** OpenTelemetry + Prometheus/Grafana (optional for local)  

---

## Quick Start (Local Demo)

```bash
# 1) Create virtual env
python -m venv .venv && source .venv/bin/activate  # (Windows: .venv\Scripts\activate)

# 2) Install deps
pip install -U pip wheel
pip install fastapi uvicorn[standard] pydantic numpy pandas scikit-learn websockets

# 3) Run API
uvicorn app.main:api --reload --port 8080

# 4) Submit a test order
curl -X POST http://localhost:8080/orders \
  -H "Content-Type: application/json" \
  -d '{"symbol":"AAPL","side":"BUY","qty":3700,"price":138.91}'
```

Open the dashboard at **http://localhost:8080/dashboard** for live metrics (if included).

---

## Load Test (Optional)

```bash
pip install locust
locust -f tools/locustfile.py --headless -u 2000 -r 200 --run-time 2m   --host http://localhost:8080
```

---

## Project Structure (reference)

```
app/
 ├─ main.py              # FastAPI wiring, routes, WS
 ├─ schemas.py           # Pydantic models
 ├─ risk/                # Pre-trade checks
 ├─ router/              # Smart routing core
 ├─ venues/              # Adapters: nyse/nasdaq/bats/iex/arca
 ├─ ml/                  # Feature/Model code (RandomForest)
 ├─ analytics/           # TCA, VWAP, slippage, latency
 └─ utils/               # logging, ids, timing
docs/
 └─ dashboard.png        # screenshot
tools/
 └─ locustfile.py        # load test
```

---

## Feature Checklist

- [x] Order ingest (REST, FIX-ready contracts)  
- [x] Pre-trade risk validation  
- [x] Venue scoring (latency, impact, historical fill)  
- [x] Multi-venue execution with partial fills  
- [x] Real-time metrics & dashboard (latency, P50/P99, VWAP, fills)  
- [x] Post-trade analytics & TCA  
- [ ] Persistence (Postgres) *(optional for demo)*  
- [ ] Kafka/Redpanda integration *(optional for demo)*  

---

## Notes & Disclaimers
- For demonstration only; **not** investment advice, exchange-certified, or production-approved.  
- Synthetic data is used to illustrate routing and analytics concepts.  

---

## Credits
Developed by **Senthil Saravanamuthu** (GitHub: `senthilts9`).  
If you build on this, a ⭐ on GitHub helps others find it!
