# Local Setup & Operations

This guide shows two paths:

1) **Minimal demo (no external services)** — fastest way to run locally.  
2) **Full stack (Docker)** — adds Kafka + Postgres + Grafana for observability and persistence.

---

## 1) Minimal Demo

**Prereqs:** Python 3.11+

```bash
python -m venv .venv && source .venv/bin/activate   # (Windows: .venv\Scripts\activate)
pip install -U pip wheel
pip install fastapi uvicorn[standard] pydantic numpy pandas scikit-learn websockets
uvicorn app.main:api --reload --port 8080
```

Test order submit:

```bash
curl -X POST http://localhost:8080/orders -H "Content-Type: application/json" -d '{
  "symbol": "AAPL", "side": "BUY", "qty": 3700, "price": 138.91
}'
```

Open the dashboard (if bundled): `http://localhost:8080/dashboard`

---

## 2) Full Stack (Docker)

**Prereqs:** Docker Desktop

Create a `docker-compose.yml` like below (feel free to copy/paste):

```yaml
version: "3.9"
services:
  api:
    build: .
    command: uvicorn app.main:api --host 0.0.0.0 --port 8080
    ports: ["8080:8080"]
    environment:
      - APP_ENV=local
      - KAFKA_BROKERS=redpanda:9092
      - POSTGRES_HOST=postgres
      - POSTGRES_DB=sors
      - POSTGRES_USER=sors
      - POSTGRES_PASSWORD=sors
    depends_on: [redpanda, postgres]

  redpanda:
    image: redpandadata/redpanda:latest
    command:
      - redpanda start --overprovisioned --smp 1 --memory 512M --reserve-memory 0M --check=false
    ports: ["9092:9092"]

  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: sors
      POSTGRES_USER: sors
      POSTGRES_PASSWORD: sors
    ports: ["5432:5432"]
    volumes:
      - pgdata:/var/lib/postgresql/data

  grafana:
    image: grafana/grafana:latest
    ports: ["3000:3000"]
    environment:
      - GF_AUTH_ANONYMOUS_ENABLED=true

volumes:
  pgdata:
```

Then:

```bash
docker compose up --build
```

Submit traffic with `curl` or a load generator. Visit:
- API: `http://localhost:8080`
- Grafana: `http://localhost:3000` (configure Prometheus if you wire it in)

---

## Environment Variables

Create `.env` if needed:

```
APP_ENV=local
KAFKA_BROKERS=redpanda:9092
POSTGRES_HOST=localhost
POSTGRES_DB=sors
POSTGRES_USER=sors
POSTGRES_PASSWORD=sors
```

---

## Useful Commands

```bash
# Run tests
pytest -q

# Format & lint (if configured)
ruff check .
black .
```

---

## Troubleshooting

- **Port already in use**: change `--port` or stop the conflicting process.  
- **Pip install slow**: use `pip install -r requirements.txt`.  
- **WS not updating**: confirm the WebSocket endpoint is reachable from the browser (CORS/origin).  

---

## Production Hardening (Checklist)

- Graceful shutdown & draining
- Per‑route SLAs; latency budgets per stage
- Retry budgets; circuit‑breakers per venue
- Replayable event log & audit trail
- Canary deploys; shadow traffic
- SLOs for P50/P95/P99; autoscaling
