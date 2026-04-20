# Benchmark harness

Locust-based load tests to measure throughput and latency across the hot API paths.
Primary use: establish a `development` baseline before merging `feature/async-endpoints`.

## Prerequisites

- Docker stack running (`docker compose up -d`)
- Dependencies installed (`cd backend && uv sync`)
- **DB must be empty** — `docker compose down -v && docker compose up -d` guarantees this

## Quick start

```bash
cd backend

# 1. Seed known dataset (1 workqueue, 10 processes, 100 resources, 1000 workitems)
uv run python benchmarks/seed.py --host http://localhost:8000

# 2. Smoke run — 5 users, 30 seconds
uv run locust -f benchmarks/locustfile.py \
    --host http://localhost:8000 \
    --users 5 --spawn-rate 5 --run-time 30s \
    --headless --csv results/smoke

# 3. Full baseline — 50 users, 2 minutes
uv run locust -f benchmarks/locustfile.py \
    --host http://localhost:8000 \
    --users 50 --spawn-rate 10 --run-time 2m \
    --headless --csv results/$(git rev-parse --abbrev-ref HEAD | tr '/' '-')
```

Results land in `benchmarks/results/` as CSV files (gitignored).

## Comparing two branches

Run these steps in order. Each run gets a fresh DB volume so the datasets are identical.

```bash
# ── development baseline ──────────────────────────────────────────────────────
git checkout development
docker compose down -v && docker compose up -d          # fresh DB
cd backend && uv sync
uv run python benchmarks/seed.py
uv run locust -f benchmarks/locustfile.py \
    --host http://localhost:8000 \
    --users 50 --spawn-rate 10 --run-time 2m \
    --headless --csv results/development

# ── async branch ──────────────────────────────────────────────────────────────
git checkout feature/async-endpoints
docker compose down -v && docker compose up -d          # fresh DB
cd backend && uv sync
uv run python benchmarks/seed.py
uv run locust -f benchmarks/locustfile.py \
    --host http://localhost:8000 \
    --users 50 --spawn-rate 10 --run-time 2m \
    --headless --csv results/async

# ── diff ──────────────────────────────────────────────────────────────────────
# Columns: Name, req/s, Median(ms), 95%ile(ms), 99%ile(ms)
diff <(cut -d, -f1,9,11,12,13 results/development_stats.csv) \
     <(cut -d, -f1,9,11,12,13 results/async_stats.csv)
```

## Scenarios

| Class | Weight | Tasks |
|---|---|---|
| `ReaderUser` | 7 | `GET next_item` (×5), `GET /information` (×3), `GET /resources` (×2), `GET workitem` (×2), `GET workqueues` (×1) |
| `WriterUser` | 3 | `POST add` (×5), `PUT ping` (×3) |

These endpoints cover every hot path rewritten in `feature/async-endpoints`:
- `next_item` — DB lock + read, the single hottest worker endpoint
- `information` — aggregation query (N+1 suspect, async win expected)
- `resources` — calls `update_availability()` on every request
- `add` — workitem insert
- `ping` — resource keep-alive update

## Notes

- `seed-ids.json` is gitignored — it must be regenerated after each `docker compose down -v`
- The seeder is idempotent: it aborts if the benchmark workqueue already exists
- 204 responses from `next_item` (empty queue) are treated as success — not counted as errors
