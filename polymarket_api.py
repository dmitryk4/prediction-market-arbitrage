"""
Polymarket API integration.

This module provides an authenticated HTTP client for Polymarket's REST API
and normalizes the results into the shared :class:`Market` schema. The client
includes lightweight retries, logging, and clear exceptions for common failure
cases such as authentication, rate limits, and network errors.
"""

from __future__ import annotations

import logging
import os
import time
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import httpx

from config import load_config
from models import Market


logger = logging.getLogger(__name__)


class PolymarketAPIError(RuntimeError):
    """Raised when the Polymarket API returns an unrecoverable error."""


def _require_api_key() -> str:
    config = load_config()
    api_key = os.getenv("POLYMARKET_API_KEY") or config.polymarket_api_key
    if not api_key:
        raise PolymarketAPIError(
            "Polymarket API key not configured. Set POLYMARKET_API_KEY or update config.polymarket_api_key."
        )
    return api_key


def _parse_datetime(raw: Any) -> datetime:
    if raw is None:
        raise PolymarketAPIError("Polymarket market missing resolution time")

    if isinstance(raw, (int, float)):
        return datetime.fromtimestamp(float(raw), tz=timezone.utc)

    if isinstance(raw, str):
        cleaned = raw.replace("Z", "+00:00")
        try:
            dt = datetime.fromisoformat(cleaned)
        except ValueError as exc:  # pragma: no cover - defensive
            raise PolymarketAPIError(f"Unparseable Polymarket datetime: {raw}") from exc
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)

    raise PolymarketAPIError(f"Unsupported datetime type from Polymarket: {type(raw)}")


def _is_active(market: Dict[str, Any]) -> bool:
    if market.get("resolved") or market.get("closed"):
        return False
    status = str(market.get("state") or market.get("status") or "").lower()
    active_flag = market.get("active")
    if isinstance(active_flag, bool):
        return active_flag
    return status in {"active", "open", "live"}


def _is_binary(outcomes: Any) -> bool:
    if isinstance(outcomes, Iterable) and not isinstance(outcomes, (str, bytes)):
        return len(outcomes) == 2 if isinstance(outcomes, (list, tuple)) else len(list(outcomes)) == 2
    return False


def _normalize_price(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        price = float(value)
    except (TypeError, ValueError):  # pragma: no cover - defensive
        return None
    return price / 100.0 if price > 1 else price


def _extract_binary_prices(outcomes: Sequence[str], prices: Sequence[Any]) -> Tuple[Optional[float], Optional[float]]:
    yes_index = 0
    for idx, outcome in enumerate(outcomes):
        if str(outcome).lower() in {"yes", "long", "true"}:
            yes_index = idx
            break

    yes_price = _normalize_price(prices[yes_index]) if len(prices) > yes_index else None
    no_index = 1 - yes_index
    no_price = _normalize_price(prices[no_index]) if len(prices) > no_index else None

    if yes_price is None and no_price is not None:
        yes_price = 1.0 - no_price
    elif no_price is None and yes_price is not None:
        no_price = 1.0 - yes_price

    return yes_price, no_price


def _request_json(client: httpx.Client, url: str, params: Dict[str, Any]) -> Dict[str, Any]:
    attempts = 3
    for attempt in range(1, attempts + 1):
        try:
            response = client.get(url, params=params)
            if response.status_code in {401, 403}:
                raise PolymarketAPIError("Polymarket authentication failed; check API key.")
            if response.status_code == 429:
                message = "Polymarket rate limit exceeded; try again later."
                logger.warning("Polymarket rate limited on attempt %s", attempt)
                if attempt == attempts:
                    raise PolymarketAPIError(message)
                time.sleep(attempt)
                continue
            response.raise_for_status()
            return response.json()
        except (httpx.HTTPStatusError, httpx.RequestError) as exc:
            logger.warning("Polymarket request attempt %s failed: %s", attempt, exc)
            if attempt == attempts:
                status_detail = ""
                if isinstance(exc, httpx.HTTPStatusError) and exc.response is not None:
                    status_detail = f" (status {exc.response.status_code})"
                raise PolymarketAPIError(
                    f"Failed to fetch markets from Polymarket after retries{status_detail}."
                ) from exc
            time.sleep(attempt)
    raise PolymarketAPIError("Polymarket request failed unexpectedly")


def _normalize_market(raw_market: Dict[str, Any]) -> Optional[Market]:
    outcomes_raw = raw_market.get("outcomes") or raw_market.get("outcomeNames") or []
    prices_raw = raw_market.get("outcomePrices") or raw_market.get("prices") or []
    outcomes = list(outcomes_raw) if isinstance(outcomes_raw, Iterable) and not isinstance(outcomes_raw, (str, bytes)) else []
    prices = list(prices_raw) if isinstance(prices_raw, Iterable) and not isinstance(prices_raw, (str, bytes)) else []

    if not _is_binary(outcomes):
        return None

    yes_price, no_price = _extract_binary_prices(outcomes, prices)
    if yes_price is None or no_price is None:
        logger.debug("Skipping Polymarket market missing prices: %s", raw_market.get("id"))
        return None

    resolution_time = _parse_datetime(
        raw_market.get("endDate")
        or raw_market.get("closesAt")
        or raw_market.get("expiry")
        or raw_market.get("close_time")
    )

    market = Market(
        platform="polymarket",
        market_id=str(raw_market.get("id") or raw_market.get("slug")),
        question=str(raw_market.get("question") or raw_market.get("title") or ""),
        resolution_time=resolution_time,
        yes_price=yes_price,
        no_price=no_price,
        settlement_description=raw_market.get("description"),
        underlying_entity=raw_market.get("underlying") or raw_market.get("collection") or raw_market.get("slug"),
        is_binary=True,
        is_active=_is_active(raw_market),
    )
    return market


def fetch_active_markets() -> List[Market]:
    """
    Fetch active Polymarket markets and normalize into :class:`Market` objects.

    Only binary markets that appear open/active are returned, with resolution
    times parsed into timezone-aware datetimes to align with
    :func:`filters.prefilter_markets` expectations.
    """

    api_key = _require_api_key()
    base_url = os.getenv("POLYMARKET_BASE_URL", "https://clob.polymarket.com")
    headers = {"Authorization": f"Bearer {api_key}"}

    markets: List[Market] = []
    params = {"limit": 500, "active": True}

    with httpx.Client(base_url=base_url, headers=headers, timeout=10.0) as client:
        data = _request_json(client, url=f"{base_url}/markets", params=params)
        raw_markets = data.get("markets") or data.get("data") or data.get("results") or []

        for raw in raw_markets:
            normalized = _normalize_market(raw)
            if normalized is None:
                continue
            if not normalized.is_active:
                continue
            markets.append(normalized)

    return markets

