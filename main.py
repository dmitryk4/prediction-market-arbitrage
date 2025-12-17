import json
from typing import Any

from pipeline import run_pipeline, opportunities_to_dicts


def main() -> None:
    """
    Simple CLI entry point for the MVP.

    - Runs the arbitrage detection pipeline.
    - Prints JSON output of detected opportunities (if any).
    - Requires Kalshi and Polymarket API keys set in the environment or
      `config.py`.
    """
    opportunities = run_pipeline()

    data: Any = opportunities_to_dicts(opportunities)
    print(json.dumps(data, indent=2, default=str))


if __name__ == "__main__":
    main()


