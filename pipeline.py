from __future__ import annotations

from dataclasses import asdict
from typing import List, Dict, Any

from arb_math import compute_arbitrage_opportunities
from config import load_config
from filters import prefilter_markets, validate_matches
from kalshi_api import fetch_open_binary_markets
from llm_client import DummyLLMClient
from models import ArbitrageOpportunity
from polymarket_api import fetch_active_markets


def run_pipeline() -> List[ArbitrageOpportunity]:
    """
    End-to-end orchestration of the arbitrage detection pipeline.

    This function is the single entry point for the MVP logic:
    1. Pull markets from both platforms (via stubbed API modules).
    2. Normalize and deterministically pre-filter candidate pairs.
    3. Use an LLM (dummy in skeleton) for semantic candidate detection.
    4. Deterministically validate candidate matches.
    5. Compute arbitrage edges for validated matches.
    6. Return a list of informational arbitrage opportunities.
    """
    config = load_config()

    # 1. Fetch markets (these will raise NotImplementedError in the skeleton).
    kalshi_markets = fetch_open_binary_markets()
    polymarket_markets = fetch_active_markets()

    # 2. Deterministic pre-filtering.
    candidate_pairs = prefilter_markets(
        kalshi_markets=kalshi_markets,
        polymarket_markets=polymarket_markets,
        max_resolution_delta=config.thresholds.max_resolution_delta,
    )

    # 3. LLM-based semantic detection (dummy client in skeleton).
    llm_client = DummyLLMClient()
    llm_results = llm_client.evaluate_pairs(candidate_pairs)

    # 4. Deterministic validation layer.
    validated = validate_matches(
        pairs=candidate_pairs,
        llm_results=llm_results,
        max_resolution_delta=config.thresholds.max_resolution_delta,
    )

    # 5. Arbitrage detection math.
    opportunities = compute_arbitrage_opportunities(
        validated_matches=validated,
        min_edge_bps=config.thresholds.min_edge_bps,
    )

    return opportunities


def opportunities_to_dicts(opportunities: List[ArbitrageOpportunity]) -> List[Dict[str, Any]]:
    """
    Convert arbitrage opportunities into JSON-serializable dictionaries.
    """

    def serialize_opportunity(opp: ArbitrageOpportunity) -> Dict[str, Any]:
        pair = opp.pair
        return {
            "kalshi_market": asdict(pair.kalshi_market),
            "polymarket_market": asdict(pair.polymarket_market),
            "edge_bps": opp.edge_bps,
            "description": opp.description,
            "risks": opp.risks,
        }

    return [serialize_opportunity(o) for o in opportunities]


