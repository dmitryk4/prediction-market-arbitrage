"use client";

import { useState } from "react";

type Market = {
  platform: string;
  market_id: string;
  question: string;
  resolution_time: string;
  yes_price: number;
  no_price: number;
  settlement_description?: string | null;
  underlying_entity?: string | null;
};

type Opportunity = {
  kalshi_market: Market;
  polymarket_market: Market;
  edge_bps: number;
  description: string;
  risks: string[];
};

type FetchState = "idle" | "loading" | "success" | "error";

const API_BASE = "http://localhost:8000";

function formatEdge(edgeBps: number) {
  return `${edgeBps.toFixed(1)} bps`;
}

export default function HomePage() {
  const [state, setState] = useState<FetchState>("idle");
  const [error, setError] = useState<string | null>(null);
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);

  const runDetection = async () => {
    setState("loading");
    setError(null);
    setOpportunities([]);

    try {
      const res = await fetch(`${API_BASE}/api/opportunities`);

      if (res.status === 501) {
        const body = await res.json().catch(() => null);
        const message =
          body?.detail ??
          "Backend pipeline not fully implemented yet (Kalshi/Polymarket stubs).";
        throw new Error(message);
      }

      if (!res.ok) {
        throw new Error(`Unexpected status code: ${res.status}`);
      }

      const data: Opportunity[] = await res.json();
      setOpportunities(data);
      setState("success");
    } catch (err: any) {
      setError(err?.message ?? "Unknown error");
      setState("error");
    }
  };

  return (
    <div className="app-root">
      <header className="app-header">
        <h1>Prediction Market Arbitrage Detector</h1>
        <p className="subtitle">
          LLM-assisted, deterministically validated. Informational only — no
          execution.
        </p>
      </header>

      <main className="app-main">
        <section className="panel">
          <h2>Run detection</h2>
          <p className="panel-text">
            This MVP semantically matches potentially equivalent markets across
            Kalshi and Polymarket and highlights pricing discrepancies, while
            keeping all execution and capital allocation out of scope.
          </p>
          <button
            className="primary-button"
            onClick={runDetection}
            disabled={state === "loading"}
          >
            {state === "loading" ? "Scanning markets…" : "Run detection"}
          </button>
          {state === "idle" && (
            <p className="hint">
              Start by running a scan. Current backend uses stub integrations
              for Kalshi and Polymarket.
            </p>
          )}
          {state === "error" && (
            <p className="error">
              {error ??
                "Something went wrong. Check that the backend is running on port 8000."}
            </p>
          )}
        </section>

        <section className="panel">
          <h2>Detected opportunities</h2>
          {state === "loading" && <p>Evaluating candidate markets…</p>}
          {state === "success" && opportunities.length === 0 && (
            <p>No opportunities detected under current thresholds.</p>
          )}
          {state !== "loading" &&
            state !== "idle" &&
            opportunities.length > 0 && (
              <div className="opportunity-list">
                {opportunities.map((opp, idx) => (
                  <article className="opportunity-card" key={idx}>
                    <div className="opportunity-header">
                      <span className="chip edge-chip">
                        {formatEdge(opp.edge_bps)}
                      </span>
                      <span className="chip platform-chip">
                        Kalshi ↔ Polymarket
                      </span>
                    </div>
                    <div className="market-block">
                      <h3>Kalshi</h3>
                      <p className="question">{opp.kalshi_market.question}</p>
                    </div>
                    <div className="market-block">
                      <h3>Polymarket</h3>
                      <p className="question">
                        {opp.polymarket_market.question}
                      </p>
                    </div>
                    <p className="description">{opp.description}</p>
                    {opp.risks.length > 0 && (
                      <div className="risks">
                        <h4>Key risks</h4>
                        <ul>
                          {opp.risks.map((r, rIdx) => (
                            <li key={rIdx}>{r}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </article>
                ))}
              </div>
            )}
        </section>
      </main>

      <footer className="app-footer">
        <p>
          Built as an MVP to demonstrate disciplined, LLM-assisted arbitrage
          detection between prediction markets. No trading. No order books. No
          latency games.
        </p>
      </footer>
    </div>
  );
}


