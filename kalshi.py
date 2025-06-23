import requests
from datetime import datetime, timezone

# ----- Kalshi API Client -----
class KalshiAPI:
    def __init__(self, base_url=None):
        base = base_url or "https://api.elections.kalshi.com"
        if not base.endswith("/trade-api/v2"):
            base = base.rstrip("/") + "/trade-api/v2"
        self.base_url = base

    def get_markets(self):
        """Fetch all Kalshi markets from the elections API."""
        try:
            resp = requests.get(f"{self.base_url}/markets", timeout=10)
            resp.raise_for_status()
            return resp.json().get("markets", [])
        except Exception as e:
            print(f"[KalshiAPI] Error fetching markets: {e}")
            return []

    def get_current_markets(self):
        """Return only currently trading/open Kalshi markets, debugging raw statuses."""
        all_markets = self.get_markets()
        # Debug raw status samples
        print("\nSample Kalshi market status fields (first 5):")
        for m in all_markets[:5]:
            print(f" ticker={m.get('ticker')}, status={m.get('status')}, state={m.get('state')}, active={m.get('active')}")

        # Use both status and active flag for filtering
        current = [
            m for m in all_markets 
            if str(m.get("status", "")).lower() in ("trading", "open", "active")
            or m.get("active", False) is True
        ]
        return current

# ----- Standalone Execution -----
if __name__ == "__main__":
    client = KalshiAPI()
    current_markets = client.get_current_markets()
    print(f"\nFetched {len(current_markets)} current Kalshi markets:")
    for m in current_markets:
        ticker = m.get("ticker")
        title = m.get("title") or m.get("question") or "<no title>"
        print(f" - {ticker}: {title}")
