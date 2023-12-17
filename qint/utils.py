Number = float | int


def _int_round(x: Number) -> int:
    """Round a number to the nearest integer."""
    if not isinstance(x, Number):
        raise TypeError(f"Expected a number, got {type(x)}")
    return int(round(x))


def check_arguments(types: list[tuple[type, str]]):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for arg, (expected_type, arg_name) in zip(args, types):
                if not isinstance(arg, expected_type):
                    raise TypeError(
                        f"{arg_name} expected a {expected_type}, got {type(arg)}"
                    )

            return func(*args, **kwargs)

        return wrapper

    return decorator


@check_arguments([(Number, "x"), (int, "precision")])
def quantize(x: Number, precision: int) -> int:
    """Quantize a number to a given precision."""
    return _int_round(x * 10**precision)


@check_arguments([(int, "x"), (int, "precision")])
def unquantize(x: int, precision: int) -> float:
    """Unquantize a number to a given precision."""
    return float(x * 10**-precision)


@check_arguments([(int, "numerator"), (Number, "denominator")])
def int_div(num: int, denom: Number) -> int:
    """
    Integer division with rounding.

    NOTE: denominator can be any number type.
    """
    if denom == 0:
        raise ZeroDivisionError("Denominator cannot be zero")

    return _int_round(num / denom)


@check_arguments([(int, "numerator"), (Number, "factor")])
def int_mul(num: int, factor: Number) -> int:
    """
    Integer multiplication with rounding.

    NOTE: factor can be any number type.
    """
    return _int_round(num * factor)


@check_arguments([(int, "numerator"), (Number, "denominator"), (int, "precision")])
def int_floordiv(num: int, denom: Number, precision: int) -> int:
    """
    Floor division for quantized integers, considering precision.

    :param num: The numerator, an integer representing the quantized value.
    :param denom: The denominator, can be any number type.
    :param precision: The precision of the quantized value.
    :return: The result of the floor division as a quantized integer.
    """
    if denom == 0:
        raise ZeroDivisionError("Denominator cannot be zero")

    adjusted_num = num / (10**precision)

    return _int_round(adjusted_num / denom)
