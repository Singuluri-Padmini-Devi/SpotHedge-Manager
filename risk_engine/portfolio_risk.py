# risk_engine/portfolio_risk.py

import math
import numpy as np

def calculate_var(position_value, volatility, confidence=0.95):
    z_score = 1.65 if confidence == 0.95 else 2.33  # 95% or 99%
    return position_value * volatility * z_score

def max_drawdown(prices):
    peak = prices[0]
    max_dd = 0.0
    for price in prices:
        if price > peak:
            peak = price
        drawdown = (peak - price) / peak
        max_dd = max(max_dd, drawdown)
    return max_dd

def correlation_matrix(asset_returns):
    return np.corrcoef(asset_returns)
def calculate_portfolio_risk(position_size, spot_price):
    # Simulate portfolio risk metrics
    var = round(position_size * spot_price * 0.11, 2)  # Example: 11% VaR
    drawdown = round(5 + (position_size % 3), 2)        # Simulated drawdown %

    return var, drawdown


# Dummy usage example (to be used in actual implementation later)
if __name__ == "__main__":
    prices = [100, 98, 96, 99, 101, 95]
    print("Max Drawdown:", max_drawdown(prices))

    returns = [[0.01, -0.02, 0.03], [-0.01, 0.01, -0.02]]
    print("Correlation Matrix:\n", correlation_matrix(returns))

    var = calculate_var(10000, 0.02)  # e.g. 2% daily vol
    print("VaR (95%):", var)
