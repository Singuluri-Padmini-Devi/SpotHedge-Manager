# risk_engine/delta_calculator.py

def calculate_delta(position_size: float, price: float) -> float:
    """
    Delta for a spot position is just 1 * position size (i.e., fully directional).
    Delta = position_size * 1 for long
    """
    return position_size * 1  # 1 delta per unit in spot
