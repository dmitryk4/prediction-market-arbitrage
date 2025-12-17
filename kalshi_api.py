"""
Kalshi API integration.

This module provides a small authenticated client for Kalshi's REST API and
normalizes responses into the shared :class:`Market` schema. It keeps the
implementation intentionally lightweight but includes basic retries, logging,
and clear exceptions for common HTTP failures (auth, quotas, network issues).
"""

from __future__ import annotations

import logging
import os
import time
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional, Tuple

import httpx

from config import load_config
from models import Market


logger = logging.getLogger(__name__)


class KalshiAPIError(RuntimeError):
    """Raised when the Kalshi API returns an unrecoverable error."""


def _require_api_key() -> str:
    config = load_config()
    api_key = os.getenv("KALSHI_API_KEY") or config.kalshi_api_key
    if not api_key:
        raise KalshiAPIError(
            "Kalshi API key not configured. Set KALSHI_API_KEY or update config.kalshi_api_key."
        )
    return api_key


def _parse_datetime(raw: Any) -> datetime:
    if raw is None:
        raise KalshiAPIError("Kalshi market missing close time")

    if isinstance(raw, (int, float)):
        return datetime.fromtimestamp(float(raw), tz=timezone.utc)

    if isinstance(raw, str):
        cleaned = raw.replace("Z", "+00:00")
        try:
            dt = datetime.fromisoformat(cleaned)
        except ValueError as exc:  # pragma: no cover - defensive
            raise KalshiAPIError(f"Unparseable Kalshi datetime: {raw}") from exc
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)

    raise KalshiAPIError(f"Unsupported datetime type from Kalshi: {type(raw)}")


def _is_active(status: Optional[str], is_resolved: Optional[bool]) -> bool:
    if is_resolved:
        return False
    status_normalized = (status or "").lower()
    return status_normalized in {"trading", "open", "active"}


def _is_binary(market: Dict[str, Any]) -> bool:
    kind = market.get("type") or market.get("contract_type")
    if isinstance(kind, str) and kind.lower() == "binary":
        return True

    outcomes = market.get("outcomes") or market.get("contracts")
    if isinstance(outcomes, Iterable) and not isinstance(outcomes, (str, bytes)):
        return len(list(outcomes)) == 2
    return False


def _normalize_price(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        price = float(value)
    except (TypeError, ValueError):  # pragma: no cover - defensive
        return None
    return price / 100.0 if price > 1 else price


def _extract_prices(market: Dict[str, Any]) -> Tuple[Optional[float], Optional[float]]:
    yes_price = _normalize_price(
        market.get("yes_bid")
        or market.get("best_bid_yes")
        or market.get("yes_price")
        or market.get("last_price_yes")
    )
    no_price = _normalize_price(
        market.get("no_bid")
        or market.get("best_bid_no")
        or market.get("no_price")
        or market.get("last_price_no")
    )

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
                raise KalshiAPIError("Kalshi authentication failed; check API key.")
            if response.status_code == 429:
                message = "Kalshi rate limit exceeded; try again later."
                logger.warning("Kalshi rate limited on attempt %s", attempt)
                if attempt == attempts:
                    raise KalshiAPIError(message)
                time.sleep(attempt)
                continue
            response.raise_for_status()
            return response.json()
        except (httpx.HTTPStatusError, httpx.RequestError) as exc:
            logger.warning("Kalshi request attempt %s failed: %s", attempt, exc)
            if attempt == attempts:
                status_detail = ""
                if isinstance(exc, httpx.HTTPStatusError) and exc.response is not None:
                    status_detail = f" (status {exc.response.status_code})"
                raise KalshiAPIError(
                    f"Failed to fetch markets from Kalshi after retries{status_detail}."
                ) from exc
            time.sleep(attempt)
    raise KalshiAPIError("Kalshi request failed unexpectedly")


def _normalize_market(raw_market: Dict[str, Any]) -> Optional[Market]:
    status = raw_market.get("status")
    is_active = _is_active(status=status, is_resolved=raw_market.get("is_resolved"))

    resolution = _parse_datetime(
        raw_market.get("close_time")
        or raw_market.get("closes_at")
        or raw_market.get("expiration_time")
        or raw_market.get("end_date")
    )

    yes_price, no_price = _extract_prices(raw_market)
    if yes_price is None or no_price is None:
        logger.debug("Skipping Kalshi market missing prices: %s", raw_market.get("id"))
        return None

    market = Market(
        platform="kalshi",
        market_id=str(raw_market.get("id") or raw_market.get("ticker")),
        question=str(raw_market.get("title") or raw_market.get("name") or ""),
        resolution_time=resolution,
        yes_price=yes_price,
        no_price=no_price,
        settlement_description=raw_market.get("settlement_description"),
        underlying_entity=raw_market.get("underlying") or raw_market.get("ticker"),
        is_binary=_is_binary(raw_market),
        is_active=is_active,
    )
    return market


def fetch_open_binary_markets() -> List[Market]:
    """
    Fetch open Kalshi markets and normalize into :class:`Market` objects.

    Returns only binary markets that appear active according to Kalshi's status
    flag, with resolution times parsed into timezone-aware datetimes so they can
    be compared in :func:`filters.prefilter_markets`.
    """

    api_key = _require_api_key()
    base_url = os.getenv("KALSHI_BASE_URL", "https://trading-api.kalshi.com/v2")
    headers = {"Authorization": f"Bearer {api_key}"}

    markets: List[Market] = []
    params = {"status": "trading", "limit": 500}

    with httpx.Client(base_url=base_url, headers=headers, timeout=10.0) as client:
        data = _request_json(client, url=f"{base_url}/markets", params=params)
        raw_markets = data.get("markets") or data.get("data") or []

        for raw in raw_markets:
            normalized = _normalize_market(raw)
            if normalized is None:
                continue
            if not normalized.is_binary:
                continue
            if not normalized.is_active:
                continue
            markets.append(normalized)

    return markets

