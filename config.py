from dataclasses import dataclass
from datetime import timedelta
from typing import Optional


@dataclass
class LLMConfig:
    provider: str = "openai"  # placeholder; implementation TBD
    model: str = "gpt-4.1-mini"
    max_candidates_per_batch: int = 20


@dataclass
class ArbitrageThresholds:
    min_edge_bps: float = 50.0  # minimum edge in basis points (0.5%)
    max_resolution_delta: timedelta = timedelta(days=1)


@dataclass
class AppConfig:
    llm: LLMConfig = LLMConfig()
    thresholds: ArbitrageThresholds = ArbitrageThresholds()
    kalshi_api_key: Optional[str] = None
    polymarket_api_key: Optional[str] = None


def load_config() -> AppConfig:
    """
    In a fuller implementation, this would load from environment variables,
    .env files, or other configuration sources. For the skeleton, we just
    return defaults.
    """
    return AppConfig()


