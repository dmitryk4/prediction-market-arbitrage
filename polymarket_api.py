"""
Polymarket API integration stub.

Intentionally left unimplemented for the MVP skeleton.
"""

from typing import List

from models import Market


def fetch_active_markets() -> List[Market]:
    """
    Fetch active markets from Polymarket and normalize into `Market`.

    This is a stub function; the actual HTTP/API integration should
    be implemented later.
    """
    raise NotImplementedError("Polymarket API integration not implemented in skeleton.")


