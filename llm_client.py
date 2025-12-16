from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from models import MarketPair, LLMSemanticMatch


class LLMClient(ABC):
    """
    Abstract LLM client interface.

    The concrete implementation MUST ensure that the LLM never sees
    prices or other trading-related data; it should only see semantic
    descriptions of the markets.
    """

    @abstractmethod
    def evaluate_pairs(self, pairs: List[MarketPair]) -> List[LLMSemanticMatch]:
        """
        Given a batch of pre-filtered candidate market pairs, return
        LLM-based semantic judgments.
        """
        raise NotImplementedError


class DummyLLMClient(LLMClient):
    """
    Minimal placeholder implementation used for the skeleton.

    This does NOT call any real LLM provider. It simply returns
    low-confidence, non-committal matches for all pairs.
    """

    def evaluate_pairs(self, pairs: List[MarketPair]) -> List[LLMSemanticMatch]:
        return [
            LLMSemanticMatch(
                same_event=False,
                same_outcome_semantics=False,
                confidence=0.0,
                risks=["LLM not implemented; this is a dummy result."],
            )
            for _ in pairs
        ]


