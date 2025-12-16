from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Optional, List


Platform = Literal["kalshi", "polymarket"]


@dataclass
class Market:
    """
    Normalized market representation shared across platforms.
    """

    platform: Platform
    market_id: str
    question: str
    resolution_time: datetime
    yes_price: float  # in [0, 1]
    no_price: float  # in [0, 1]
    settlement_description: Optional[str] = None
    underlying_entity: Optional[str] = None  # e.g., "BTC", "Fed", "US election 2024"
    is_binary: bool = True
    is_active: bool = True


@dataclass
class MarketPair:
    """
    Pair of markets from different platforms being compared.
    """

    kalshi_market: Market
    polymarket_market: Market


@dataclass
class LLMSemanticMatch:
    """
    Output of the LLM-based semantic detection stage.
    The LLM NEVER sees prices.
    """

    same_event: bool
    same_outcome_semantics: bool
    confidence: float  # in [0, 1]
    risks: List[str]


@dataclass
class ValidatedMatch:
    """
    Result of deterministic validation of an LLM candidate match.
    """

    pair: MarketPair
    llm_match: LLMSemanticMatch
    validation_passed: bool
    validation_issues: List[str]


@dataclass
class ArbitrageOpportunity:
    """
    Final arbitrage opportunity description (informational only).
    """

    pair: MarketPair
    edge_bps: float  # edge in basis points
    description: str
    risks: List[str]


