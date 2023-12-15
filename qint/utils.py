import numpy as np

Number = np.number | float | int


def int_round(x: Number) -> np.int64:
    """Round a number to the nearest integer."""
    if not isinstance(x, Number):
        raise TypeError(f"Expected a number, got {type(x)}")
    return np.int64(round(x))


def quantize(x: Number, precision: int) -> np.int64:
    """Quantize a number to a given precision."""
    if not isinstance(x, Number):
        raise TypeError(f"Expected a number, got {type(x)}")
    return int_round(x * 10**precision)


def unquantize(x: np.int64, precision: int) -> np.float64:
    """Unquantize a number to a given precision."""
    if not isinstance(x, np.int64):
        raise TypeError(f"Expected a np.int64, got {type(x)}")
    return np.float64(x * 10**-precision)


def int_div(num: np.int64, denom: Number) -> np.int64:
    """
    Integer division with rounding.

    NOTE: denominator can be any number type.
    """
    if not isinstance(num, np.int64):
        raise TypeError(f"Numerator expected a np.int64, got {type(num)}")
    if not isinstance(denom, Number):
        raise TypeError(f"Denominator expected a NUMBER, got {type(denom)}")
    if denom == 0:
        raise ZeroDivisionError("Denominator cannot be zero")
    return int_round(num / denom)


def int_mul(num: np.int64, factor: Number) -> np.int64:
    """
    Integer multiplication with rounding.

    NOTE: factor can be any number type.
    """
    if not isinstance(num, np.int64):
        raise TypeError(f"Numerator expected a np.int64, got {type(num)}")
    if not isinstance(factor, Number):
        raise TypeError(f"Factor expected a NUMBER, got {type(factor)}")
    return int_round(num * factor)
