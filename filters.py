from datetime import timedelta
from typing import Iterable, List

from models import Market, MarketPair, LLMSemanticMatch, ValidatedMatch


def prefilter_markets(
    kalshi_markets: Iterable[Market],
    polymarket_markets: Iterable[Market],
    max_resolution_delta: timedelta,
) -> List[MarketPair]:
    """
    Deterministic pre-filtering step.

    - Binary outcomes only
    - Similar resolution windows
    - Same underlying entity (if identified)
    - Markets still open/active

    For the skeleton, we keep the logic very simple and conservative.
    """
    kalshi_filtered = [
        m for m in kalshi_markets if m.is_binary and m.is_active
    ]
    poly_filtered = [
        m for m in polymarket_markets if m.is_binary and m.is_active
    ]

    pairs: List[MarketPair] = []
    for k in kalshi_filtered:
        for p in poly_filtered:
            if abs(k.resolution_time - p.resolution_time) > max_resolution_delta:
                continue
            if k.underlying_entity and p.underlying_entity:
                if k.underlying_entity.lower() != p.underlying_entity.lower():
                    continue
            pairs.append(MarketPair(kalshi_market=k, polymarket_market=p))

    return pairs


def validate_matches(
    pairs: List[MarketPair],
    llm_results: List[LLMSemanticMatch],
    max_resolution_delta: timedelta,
) -> List[ValidatedMatch]:
    """
    Deterministic validation layer.

    Even high-confidence LLM matches are rejected unless:
    - Resolution dates align
    - Strike conditions align (not modeled yet in the skeleton)
    - Settlement rules are compatible
    - No asymmetric ambiguity exists

    For the skeleton, we mostly echo the LLM result and perform an
    additional resolution window check.
    """
    validated: List[ValidatedMatch] = []

    for pair, llm_match in zip(pairs, llm_results):
        issues: List[str] = []
        passed = True

        # Basic deterministic checks
        if abs(pair.kalshi_market.resolution_time - pair.polymarket_market.resolution_time) > max_resolution_delta:
            issues.append("Resolution times differ beyond allowed threshold.")
            passed = False

        # TODO: extend with strike condition and settlement rule comparisons.

        if not (llm_match.same_event and llm_match.same_outcome_semantics):
            issues.append("LLM did not confirm same event/outcome semantics.")
            passed = False

        validation = ValidatedMatch(
            pair=pair,
            llm_match=llm_match,
            validation_passed=passed,
            validation_issues=issues,
        )
        validated.append(validation)

    return validated


