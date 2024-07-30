from decimal import Decimal, ROUND_HALF_UP

def round_to_integer(value: float) -> int:
    """
    Python rounds half values to the nearest even number, which is not desirable when
    stepping upwards from positions 0.5 -> 1.5 -> 2.5 on an Arc as it causes
    steppiness. This helper function always rounds half values up.

    Args:
        value (float): The input

    Returns:
        int: The rounded integer.
    """
    return int(Decimal(value).to_integral_value(rounding=ROUND_HALF_UP))