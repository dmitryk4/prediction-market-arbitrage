#predicton-market-arbitrage
Overview
Prediction Market Arbitrage is a Python-based project that detects and capitalizes on arbitrage opportunities between prediction markets such as Kalshi and Polymarket. The algorithm identifies pricing discrepancies to secure risk-free profits by buying different outcomes at advantageous rates.

Features
Real-time Data Fetching: Connects with Kalshi and Polymarket APIs to retrieve live market data.
Arbitrage Detection: Identifies arbitrage opportunities when the combined cost of buying “yes” positions is under 100%.
Automated Trading Execution: Implements trade automation to act on identified arbitrage opportunities.
Flexible Configuration: Easily set up API keys, endpoints, and parameters using config.py.
Comprehensive Logging: Provides detailed logs to track algorithm performance and trade actions.
