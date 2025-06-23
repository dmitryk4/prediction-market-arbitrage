import requests
import re

# ----- Kalshi API Client -----
class KalshiAPI:
    def __init__(self, base_url=None):
        base = base_url or "https://api.elections.kalshi.com"
        if not base.endswith("/trade-api/v2"):
            base = base.rstrip("/") + "/trade-api/v2"
        self.base_url = base

    def get_markets(self):
        try:
            r = requests.get(f"{self.base_url}/markets", timeout=10)
            r.raise_for_status()
            return r.json().get("markets", [])
        except Exception as e:
            print(f"[KalshiAPI] could not fetch markets: {e}")
            return []

    def get_best_bid(self, ticker):
        try:
            ob = requests.get(f"{self.base_url}/markets/{ticker}/orderbook", timeout=10).json()
            return float(ob.get("bids", [{}])[0].get("price", 0)) * 100
        except Exception:
            return 0.0

# ----- Polymarket API Client -----
class PolymarketAPI:
    def __init__(self):
        self.base_url = "https://gamma-api.polymarket.com"

    def get_markets(self):
        try:
            r = requests.get(f"{self.base_url}/markets", timeout=10)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            print(f"[PolymarketAPI] could not fetch markets: {e}")
            return []

    def get_yes_price(self, market):
        try:
            # Using liquidity as proxy for yes price, adjust if needed
            return float(market.get("liquidity", 0.0))
        except Exception:
            return 0.0

    def get_no_price(self, market):
        return max(0.0, 100 - self.get_yes_price(market))

# ----- Helpers -----
def tokenize(text):
    return re.findall(r"\w+", text.lower())

def match_markets(kalshi_markets, polymarket_markets):
    matches = []
    for km in kalshi_markets:
        outcomes = km.get("outcomes", [])
        if len(outcomes) != 2:
            continue
        tokens = set()
        for o in outcomes:
            tokens.update(tokenize(o.get("name", "")))
        for pm in polymarket_markets:
            slug_tokens = set(tokenize(pm.get("slug", "")))
            if tokens.issubset(slug_tokens):
                matches.append((km, pm))
                break
    return matches

def calculate_arbitrage(p1_m1, p2_m1, p1_m2, p2_m2, m1, m2, amount=100):
    results = []
    # m1_yes + m2_no
    total1 = p1_m1 + p2_m2
    arbitrage1 = total1 < 100
    margin1 = 100 - total1 if arbitrage1 else 0
    bet1 = (p2_m2 / total1) * amount if arbitrage1 else 0
    bet2 = (p1_m1 / total1) * amount if arbitrage1 else 0
    results.append({
        'pair': f"{m1} YES + {m2} NO",
        'total': total1,
        'profit_margin': margin1,
        'bet_leg1': bet1,
        'bet_leg2': bet2,
        'arbitrage': arbitrage1
    })

    # m1_no + m2_yes
    total2 = p2_m1 + p1_m2
    arbitrage2 = total2 < 100
    margin2 = 100 - total2 if arbitrage2 else 0
    bet1 = (p1_m2 / total2) * amount if arbitrage2 else 0
    bet2 = (p2_m1 / total2) * amount if arbitrage2 else 0
    results.append({
        'pair': f"{m1} NO + {m2} YES",
        'total': total2,
        'profit_margin': margin2,
        'bet_leg1': bet1,
        'bet_leg2': bet2,
        'arbitrage': arbitrage2
    })

    return results


def main():
    kalshi = KalshiAPI()
    polymarket = PolymarketAPI()

    kalshi_markets = kalshi.get_markets()
    polymarket_markets = polymarket.get_markets()

    print(f"Kalshi markets fetched: {len(kalshi_markets)}")
    print(f"Polymarket markets fetched: {len(polymarket_markets)}")

    matched_pairs = match_markets(kalshi_markets, polymarket_markets)
    print(f"Matched market pairs: {len(matched_pairs)}")

    if not matched_pairs:
        print("No matched market pairs found. Try loosening matching criteria or check market data.")
        return

    for km, pm in matched_pairs:
        ticker = km.get("ticker")
        slug = pm.get("slug")

        yes_k = kalshi.get_best_bid(ticker)
        no_k = max(0.0, 100 - yes_k)

        yes_p = polymarket.get_yes_price(pm)
        no_p = polymarket.get_no_price(pm)

        arbitrage_results = calculate_arbitrage(
            yes_k, no_k, yes_p, no_p, ticker, slug, amount=100
        )

        print(f"\nArbitrage scan for {ticker} ⇄ {slug}:")
        for r in arbitrage_results:
            status = "ARBITRAGE!" if r['arbitrage'] else "No arbitrage"
            print(f"  • {r['pair']}: total={r['total']:.2f}%, margin={r['profit_margin']:.2f}%, {status}")
            if r['arbitrage']:
                print(f"    Bet ${r['bet_leg1']:.2f} on leg1, ${r['bet_leg2']:.2f} on leg2")

if __name__ == "__main__":
    main()
