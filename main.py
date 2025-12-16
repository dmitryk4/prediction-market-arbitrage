import json
from typing import Any

from pipeline import run_pipeline, opportunities_to_dicts


def main() -> None:
    """
    Simple CLI entry point for the MVP.

    - Runs the arbitrage detection pipeline.
    - Prints JSON output of detected opportunities (if any).
    - In the current skeleton, API calls are stubbed and will raise
      NotImplementedError until implemented.
    """
    try:
        opportunities = run_pipeline()
    except NotImplementedError as e:
        print(
            "Pipeline is wired up, but one or more components "
            "are not implemented yet:"
        )
        print(f"  -> {e}")
        return

    data: Any = opportunities_to_dicts(opportunities)
    print(json.dumps(data, indent=2, default=str))


if __name__ == "__main__":
    main()


