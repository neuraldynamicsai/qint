Number = float | int


def int_round(x: Number) -> int:
    """Round a number to the nearest integer."""
    if not isinstance(x, Number):
        raise TypeError(f"Expected a number, got {type(x)}")
    return int(round(x))


def quantize(x: Number, precision: int) -> int:
    """Quantize a number to a given precision."""
    if not isinstance(x, Number):
        raise TypeError(f"Expected a number, got {type(x)}")
    return int_round(x * 10**precision)


def unquantize(x: int, precision: int) -> float:
    """Unquantize a number to a given precision."""
    if not isinstance(x, int):
        raise TypeError(f"Expected a int, got {type(x)}")
    return float(x * 10**-precision)


def int_div(num: int, denom: Number) -> int:
    """
    Integer division with rounding.

    NOTE: denominator can be any number type.
    """
    if not isinstance(num, int):
        raise TypeError(f"Numerator expected a int, got {type(num)}")
    if not isinstance(denom, Number):
        raise TypeError(f"Denominator expected a Number type, got {type(denom)}")
    if denom == 0:
        raise ZeroDivisionError("Denominator cannot be zero")
    return int_round(num / denom)


def int_mul(num: int, factor: Number) -> int:
    """
    Integer multiplication with rounding.

    NOTE: factor can be any number type.
    """
    if not isinstance(num, int):
        raise TypeError(f"Numerator expected a int, got {type(num)}")
    if not isinstance(factor, Number):
        raise TypeError(f"Factor expected a Number type, got {type(factor)}")
    return int_round(num * factor)
