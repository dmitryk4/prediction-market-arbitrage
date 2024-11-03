# arbitrage.py

def calculate_cross_market_arbitrage(price1_market1, price2_market1, price1_market2, price2_market2):
    """
    Function to determine if an arbitrage opportunity exists by cross-referencing prices between two markets.
    :param price1_market1: Probability (as a percentage) for candidate 1 in Market 1.
    :param price2_market1: Probability (as a percentage) for candidate 2 in Market 1.
    :param price1_market2: Probability (as a percentage) for candidate 1 in Market 2.
    :param price2_market2: Probability (as a percentage) for candidate 2 in Market 2.
    :return: Tuple (is_arbitrage, profit_margin)
    """
    # Check arbitrage for candidate 1 in Market 1 and candidate 2 in Market 2
    total_cross1 = price1_market1 + price2_market2
    is_arbitrage1 = total_cross1 < 100
    profit_margin1 = 100 - total_cross1 if is_arbitrage1 else 0

    # Check arbitrage for candidate 2 in Market 1 and candidate 1 in Market 2
    total_cross2 = price2_market1 + price1_market2
    is_arbitrage2 = total_cross2 < 100
    profit_margin2 = 100 - total_cross2 if is_arbitrage2 else 0

    # Determine the best arbitrage opportunity
    if is_arbitrage1 or is_arbitrage2:
        best_margin = max(profit_margin1, profit_margin2)
        return True, best_margin
    else:
        return False, 0

# User input for hard-coded prices
price1_market1 = float(input("Enter the probability (as a percentage) for candidate 1 in Market 1: "))
price2_market1 = float(input("Enter the probability (as a percentage) for candidate 2 in Market 1: "))
price1_market2 = float(input("Enter the probability (as a percentage) for candidate 1 in Market 2: "))
price2_market2 = float(input("Enter the probability (as a percentage) for candidate 2 in Market 2: "))

# Calculate cross-market arbitrage
arbitrage, margin = calculate_cross_market_arbitrage(price1_market1, price2_market1, price1_market2, price2_market2)

# Display the result
if arbitrage:
    print(f"Cross-market arbitrage opportunity detected! Best profit margin: {margin:.2f}%")
else:
    print("No cross-market arbitrage opportunity. Combined percentages exceed or equal 100% for all combinations.")
