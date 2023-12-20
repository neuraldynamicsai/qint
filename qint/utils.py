Number = float | int


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
    return int(round((x * 10**precision)))


@check_arguments([(int, "x"), (int, "precision")])
def unquantize(x: int, precision: int) -> float:
    """Unquantize a number to a given precision."""
    return float(x * 10**-precision)


@check_arguments([(int, "numerator"), (int, "denominator")])
def banker_division(numerator: int, denominator: int) -> int:
    """Perform banker's rounding on a division operation."""
    d_numerator = numerator * 2
    d_denominator = denominator * 2
    quotient = d_numerator // d_denominator
    remainder = abs(d_numerator % d_denominator)
    return (
        quotient + (quotient % 2)
        if remainder == denominator
        else quotient + (remainder > denominator)
    )
