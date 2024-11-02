#predicton-market-arbitrage
Overview
Prediction Market Arbitrage is a Python-based project that detects and capitalizes on arbitrage opportunities between prediction markets such as Kalshi and Polymarket. The algorithm identifies pricing discrepancies to secure risk-free profits by buying different outcomes at advantageous rates.

Features
Real-time Data Fetching: Connects with Kalshi and Polymarket APIs to retrieve live market data.
Arbitrage Detection: Identifies arbitrage opportunities when the combined cost of buying “yes” positions is under 100%.
Automated Trading Execution: Implements trade automation to act on identified arbitrage opportunities.
Flexible Configuration: Easily set up API keys, endpoints, and parameters using config.py.
Comprehensive Logging: Provides detailed logs to track algorithm performance and trade actions.
Technologies Used
Python: Core programming language.
APIs: Integration with Kalshi and Polymarket APIs.
Requests/AIOHTTP: Used for making HTTP requests.
Unit Testing: Includes test scripts for validating functionality.
Project Structure
graphql
Copy code
prediction-market-arbitrage/
├── arbitrage.py               # Main script to run the algorithm
├── api_clients.py             # API interaction module
├── config.py                  # API keys and settings
├── requirements.txt           # Dependency list
├── README.md                  # Project documentation
├── tests/                     # Unit tests
│   ├── test_arbitrage.py      # Tests for arbitrage logic
│   └── test_api_clients.py    # Tests for API functions
└── utils.py                   # Utility functions
