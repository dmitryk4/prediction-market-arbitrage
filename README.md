## Prediction Market Arbitrage Detector (LLM‑assisted) – MVP Skeleton

This repository contains a **Python-only skeleton** for an MVP that detects **potential arbitrage opportunities** between prediction markets (e.g., Kalshi and Polymarket), using:

- **Deterministic rules** for pre-filtering and validation
- An **LLM** for semantic candidate matching (no pricing, no trade suggestions)

At this stage, the skeleton **does not call any real APIs** and contains **no trading/execution logic**.

### High-level architecture

- **`config.py`** – Configuration and settings (API keys, thresholds, etc.).
- **`models.py`** – Core data models (normalized market schema, LLM match results, arbitrage opportunities).
- **`llm_client.py`** – LLM interface abstraction (no provider-specific implementation yet).
- **`filters.py`** – Deterministic pre-filtering and validation skeleton.
- **`arb_math.py`** – Arbitrage detection math skeleton.
- **`kalshi_api.py` / `polymarket_api.py`** – Authenticated REST clients that normalize markets for the pipeline.
- **`pipeline.py`** – Orchestrates the full flow from fetching markets to emitting opportunities.
- **`main.py`** – Simple CLI entry point that runs the pipeline and prints JSON/console output.
– **`server.py`** – FastAPI server exposing `/api/opportunities` for the frontend.

Next.js frontend is under **`next-frontend/`**:

- **`next-frontend/app/page.tsx`** – UI with a “Run detection” button and results list.
- **`next-frontend/app/layout.tsx`**, `app/globals.css`, `next.config.mjs`, etc. – Standard Next.js app router setup.

### Running the pipeline locally

Create and activate a virtual environment, then install dependencies:

```bash
pip install -r requirements.txt
```

Export API keys (or set them in `config.py`):

```bash
export KALSHI_API_KEY="your_kalshi_key"
export POLYMARKET_API_KEY="your_polymarket_key"
```

Run the pipeline:

```bash
python main.py
```

This will call both platforms' REST APIs with retries, filter to active binary markets, and print any detected arbitrage
opportunities as JSON. Exceptions include clear messages for auth/rate limit/network issues.

### Running the web app locally (backend + Next.js frontend)

1. **Start the backend API**

```bash
python -m uvicorn server:app --reload
```

This serves the FastAPI backend at `http://localhost:8000`, with the main endpoint:

- `GET /api/opportunities` – returns a JSON list of arbitrage opportunities, or HTTP 501 while the Kalshi/Polymarket integrations are still stubs.

2. **Start the Next.js frontend (development)**

In a second terminal, from the `next-frontend` directory:

```bash
npm install
npm run dev
```

By default this runs on `http://localhost:3000` and calls the backend at `http://localhost:8000/api/opportunities`.



