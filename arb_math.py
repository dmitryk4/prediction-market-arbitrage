from typing import List

from models import ValidatedMatch, ArbitrageOpportunity


def compute_arbitrage_opportunities(
    validated_matches: List[ValidatedMatch],
    min_edge_bps: float,
) -> List[ArbitrageOpportunity]:
    """
    Compute informational arbitrage opportunities from validated matches.

    For a pair of binary markets (prices as probabilities in [0,1]),
    typical conditions involve:
    - Cross-market buy-low / sell-high type discrepancies
    - Ensuring no obvious mispricing after fees (not modeled here)

    The skeleton keeps the math trivial and mostly illustrative.
    """
    opportunities: List[ArbitrageOpportunity] = []

    for match in validated_matches:
        if not match.validation_passed:
            continue

        k = match.pair.kalshi_market
        p = match.pair.polymarket_market

        # Simple illustrative "edge": difference in implied probabilities.
        edge = abs(k.yes_price - p.yes_price)
        edge_bps = edge * 10_000.0

        if edge_bps < min_edge_bps:
            continue

        description = (
            "Detected price discrepancy between Kalshi and Polymarket "
            f"for markets '{k.question}' and '{p.question}'. "
            "This is an informational signal only; no trading logic is implemented."
        )

        risks = list(match.llm_match.risks) + list(match.validation_issues)

        opportunities.append(
            ArbitrageOpportunity(
                pair=match.pair,
                edge_bps=edge_bps,
                description=description,
                risks=risks,
            )
        )

    return opportunities


