from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from pipeline import run_pipeline, opportunities_to_dicts

app = FastAPI(title="Prediction Market Arbitrage Detector (MVP)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/opportunities")
def get_opportunities():
    """
    HTTP endpoint that exposes the arbitrage detection pipeline.

    - Returns a JSON list of informational arbitrage opportunities.
    - If the underlying Kalshi/Polymarket integrations are not yet
      implemented, responds with HTTP 501.
    """
    try:
        opportunities = run_pipeline()
    except NotImplementedError as e:
        raise HTTPException(status_code=501, detail=str(e))

    return opportunities_to_dicts(opportunities)


# Optional convenience for `python server.py` during development.
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)


