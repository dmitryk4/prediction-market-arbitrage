import requests

# ----- Kalshi API Client -----
class KalshiAPI:
    def __init__(self, base_url=None, page_size=100, max_pages=10000):
        base = base_url or "https://api.elections.kalshi.com"
        if not base.endswith("/trade-api/v2"):
            base = base.rstrip("/") + "/trade-api/v2"
        self.base_url = base
        self.page_size = page_size
        self.max_pages = max_pages

    def get_markets_page(self, page=1):
        """
        Fetch a single page of markets.
        """
        params = {"page": page, "limit": self.page_size}
        resp = requests.get(f"{self.base_url}/markets", params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data.get("markets", data)

    def get_all_markets(self):
        """
        Fetch *all* markets by paging, up to max_pages.
        """
        all_markets = []
        for page in range(1, self.max_pages + 1):
            page_markets = self.get_markets_page(page)
            if not page_markets:
                print(f"No more markets at page {page}, stopping.")
                break
            all_markets.extend(page_markets)
            print(f"Fetched page {page}, {len(page_markets)} markets")
        return all_markets

# ----- Standalone Execution -----
if __name__ == "__main__":
    client = KalshiAPI()
    all_markets = client.get_all_markets()
    print(f"\nTotal Kalshi markets fetched: {len(all_markets)}\n")
    for m in all_markets:
        ticker = m.get("ticker")
        title  = m.get("title") or m.get("question") or "<no title>"
        print(f" - {ticker}: {title}")
