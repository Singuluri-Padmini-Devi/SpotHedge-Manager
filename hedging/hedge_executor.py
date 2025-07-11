# hedging/hedge_executor.py

from exchanges.bybit_api import place_order  # Assumes this is implemented
from hedging.hedge_logger import log_hedge  # For logging to DB

def execute_hedge(user_id, asset, delta_value):
    """
    Execute a hedge by placing a futures order and logging it.
    """
    try:
        symbol = "BTCUSDT"
        side = "Sell" if delta_value > 0 else "Buy"
        qty = abs(delta_value)

        # Simulate sending order
        response = place_order(symbol=symbol, side=side, qty=qty)

        print(f"📉 Executing hedge for delta {delta_value} as {side} order: {response}")

        # Log the hedge execution in DB
        log_hedge(user_id=user_id, asset=asset, delta=delta_value, action="hedge_executed")

        return True
    except Exception as e:
        print(f"❌ Failed to execute hedge: {e}")
        return False
