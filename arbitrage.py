#arbitrage.py
def calculate_cross_market_arbitrage(price1_market1, price2_market1, price1_market2, price2_market2, market1_name, market2_name, candidate1_name, candidate2_name):
    """
    Function to determine if an arbitrage opportunity exists by cross-referencing prices between two markets.
    :param price1_market1: Probability (as a percentage) for candidate 1 in Market 1.
    :param price2_market1: Probability (as a percentage) for candidate 2 in Market 1.
    :param price1_market2: Probability (as a percentage) for candidate 1 in Market 2.
    :param price2_market2: Probability (as a percentage) for candidate 2 in Market 2.
    :param market1_name: Name of Market 1.
    :param market2_name: Name of Market 2.
    :param candidate1_name: Name of Candidate 1.
    :param candidate2_name: Name of Candidate 2.
    :return: List of tuples with (is_arbitrage, details) for each opportunity detected.
    """
    arbitrage_opportunities = []

    # Check arbitrage for candidate 1 in Market 1 and candidate 2 in Market 2
    total_cross1 = price1_market1 + price2_market2
    if total_cross1 < 100:
        profit_margin1 = 100 - total_cross1
        arbitrage_opportunities.append((True, f"{candidate1_name} in {market1_name} with {candidate2_name} in {market2_name}: {profit_margin1:.2f}%"))

    # Check arbitrage for candidate 2 in Market 1 and candidate 1 in Market 2
    total_cross2 = price2_market1 + price1_market2
    if total_cross2 < 100:
        profit_margin2 = 100 - total_cross2
        arbitrage_opportunities.append((True, f"{candidate2_name} in {market1_name} with {candidate1_name} in {market2_name}: {profit_margin2:.2f}%"))

    return arbitrage_opportunities

# User input for market names and probabilities
market1_name = input("Enter the name of Market 1: ")
market2_name = input("Enter the name of Market 2: ")
candidate1_name = input("Enter the name of Candidate 1: ")
candidate2_name = input("Enter the name of Candidate 2: ")

price1_market1 = float(input(f"Enter the probability (as a percentage) for {candidate1_name} in {market1_name}: "))
price2_market1 = float(input(f"Enter the probability (as a percentage) for {candidate2_name} in {market1_name}: "))
price1_market2 = float(input(f"Enter the probability (as a percentage) for {candidate1_name} in {market2_name}: "))
price2_market2 = float(input(f"Enter the probability (as a percentage) for {candidate2_name} in {market2_name}: "))

# Calculate cross-market arbitrage
arbitrage_opportunities = calculate_cross_market_arbitrage(price1_market1, price2_market1, price1_market2, price2_market2, market1_name, market2_name, candidate1_name, candidate2_name)

# Display the result
if arbitrage_opportunities:
    for is_arbitrage, details in arbitrage_opportunities:
        if is_arbitrage:
            print(f"Arbitrage detected: {details}")
else:
    print("No cross-market arbitrage opportunity. Combined percentages exceed or equal 100% for all combinations.")
