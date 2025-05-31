import math

def compute_step(amount: float) -> int:
    """
    Compute a step size that’s the nearest smaller power of ten for the given amount.

    Args:
        amount (float): The expense amount.

    Returns:
        int: The step size (10^(floor(log10(amount)) - 1)), minimum 1.
    """
    if amount <= 0:
        return 1
    exponent = math.floor(math.log10(amount))
    return 10 ** max(exponent - 1, 0)