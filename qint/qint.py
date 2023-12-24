from decimal import Decimal
from fractions import Fraction
from functools import total_ordering, wraps
from typing import NamedTuple, Optional, Self

import qint.utils as ut

from .exceptions import QIntPrecisionError, QIntTypeError
from .utils import Number


def check_operand(valid_types: tuple[type, ...], operation: str):
    """
    Decorator for checking the type of the operand in QInt operations. The
    operand must be of one of the types in `valid_types`.
    """

    def decorator(method):
        @wraps(method)
        def wrapper(self: QInt, other):
            if not isinstance(other, (QInt, *valid_types)):
                raise QIntTypeError(other, operation)

            if isinstance(other, QInt) and self.precision != other.precision:
                raise QIntPrecisionError(self.precision, other.precision)

            return method(self, other)

        return wrapper

    return decorator


def scale_safe(operation: str):
    """
    Scale a QInt to a given precision. This is useful when we want to perform
    operations on QInts with different precisions. We scale both QInts to the
    same precision, perform the operation, and then scale the result back to the
    original precision.
    """

    def decorator(method):
        @wraps(method)
        def wrapper(self: QInt, other):
            if not isinstance(other, QInt):
                raise QIntTypeError(other, operation)

            max_precision = max(self.precision, other.precision)

            def scale(q: QInt) -> QInt:
                precision_difference = max_precision - q.precision

                if precision_difference == 0:
                    return q  # Precision stays the same

                scaled_value = ut.scale(q.value, precision_difference)
                return QInt(scaled_value, max_precision)

            return method(scale(self), scale(other))

        return wrapper

    return decorator


@total_ordering
class QInt(NamedTuple):
    """
    Class for representing quantized integers. The value is stored as an
    integer, but the true value is calculated by dividing the integer by
    10^precision. This allows for exact arithmetic on the quantized integers.

    NOTE: You can access the true value via the `true_value` property.

    QInts are comparable to other QInts with the same precision.

    QInts are immutable.

    :param value: quantized value
    :param precision: precision of the quantized value
    """

    value: int
    precision: int

    @classmethod
    def create(cls, value: Number, precision: int) -> Self:
        """
        Create a QInt from a float with a given precision. Use this when the
        value we are passing in is NOT already quantized.
        """
        if not isinstance(value, Number):
            raise ValueError(f"Value must be a Number, not {type(value)}")

        return cls(ut.quantize(value, precision), precision)

    def scale(self, targ: int) -> Self:
        """
        Scale the precision of the QInt to the given target.
        """
        if targ is None or targ == self.precision:
            return self

        value = ut.scale(self.value, targ - self.precision)
        return QInt(value, targ)

    def to_fraction(self) -> Fraction:
        """
        Convert the QInt instance to a Fraction object.
        """
        return Fraction(self.value, 10**self.precision)

    def to_decimal(self) -> Decimal:
        """
        Convert the QInt instance to a Decimal object without loss of precision.
        """
        return Decimal(self.value) / Decimal(10**self.precision)

    def __float__(self) -> float:
        return ut.unquantize(self.value, self.precision)

    def __int__(self) -> int:
        return int(round(self.__float__()))

    def __add__(self, other: Self | int) -> Self:
        if isinstance(other, QInt):
            return QInt(self.value + other.value, self.precision)
        else:
            return QInt(self.value + other, self.precision)

    def add(self, other: Self, targ: Optional[int] = None) -> Self:
        return self.__add__(other).scale(targ)

    def __sub__(self, other: Self | int) -> Self:
        if isinstance(other, QInt):
            return QInt(self.value - other.value, self.precision)
        else:
            return QInt(self.value - other, self.precision)

    def sub(self, other: Self, targ: Optional[int] = None) -> Self:
        return self.__sub__(other).scale(targ)

    def __mul__(self, other: Self | int | Fraction) -> Self:
        if isinstance(other, QInt):
            return QInt(self.value * other.value, self.precision + other.precision)
        elif isinstance(other, Fraction):
            value = ut.banker_division(self.value * other.numerator, other.denominator)
            return QInt(value, self.precision)
        else:
            return QInt(self.value * other, self.precision)

    def mul(self, other: Self, targ: int) -> Self:
        return self.__mul__(other).scale(targ)

    def __truediv__(self, other: Self | int | Fraction) -> Self:
        if isinstance(other, QInt):
            value = ut.banker_division(self.value, other.value)
            return QInt(value, self.precision - other.precision)
        elif isinstance(other, Fraction):
            value = ut.banker_division(self.value * other.denominator, other.numerator)
            return QInt(value, self.precision)
        else:
            value = ut.banker_division(self.value, other)
            return QInt(value, self.precision)

    def div(self, other: Self, targ: Optional[int] = None) -> Self:
        # for div we scale upfront to avoid precision loss
        div_prec = other.precision + targ if targ is not None else None
        return self.scale(div_prec).__truediv__(other)

    def __floordiv__(self, other: Self | int | Fraction) -> Self:
        if isinstance(other, QInt):
            value = self.value // other.value
            return QInt(value, self.precision - other.precision)
        elif isinstance(other, Fraction):
            value = (self.value * other.denominator) // other.numerator
            return QInt(value, self.precision)
        else:
            value = self.value // other
            return QInt(value, self.precision)

    def __mod__(self, other: Self | int) -> Self:
        if isinstance(other, QInt):
            if self.precision != other.precision:
                raise ValueError(
                    "Modulo operation requires same precision for both QInts"
                )

            mod_value = self.value % other.value
            return QInt(mod_value, self.precision)

    def __pow__(self, other: int) -> Self:
        """
        The exponentiation of quantized integers is a known problem in advanced
        mathematics. There are basically two options:
        1. only allow integer exponents so that scaling does not get out of
        control.
        2. allow for any exponent, but then we must rely on floating point math
        and lose true quantization.

        We choose option 1 here.
        """
        if isinstance(other, QInt):
            raise TypeError("Cannot exponentiate QInt with QInt")
        elif isinstance(other, int):
            return QInt(self.value**other, self.precision * other)

    def __iadd__(self, other: Self | int) -> Self:
        return self.__add__(other)

    def __isub__(self, other: Self | int) -> Self:
        return self.__sub__(other)

    def __imul__(self, other: Self | int | Fraction) -> Self:
        return self.__mul__(other)

    def __itruediv__(self, other: Self | int | Fraction) -> Self:
        return self.__truediv__(other)

    def __and__(self, _: Self | Number) -> Self:
        raise TypeError("Bitwise AND is not supported for instances of QInt")

    def __or__(self, _: Self | Number) -> Self:
        raise TypeError("Bitwise OR is not supported for instances of QInt")

    def __xor__(self, _: Self | Number) -> Self:
        raise TypeError("Bitwise XOR is not supported for instances of QInt")

    def __lshift__(self, _: Self | Number) -> Self:
        raise TypeError("Bitwise left shift is not supported for instances of QInt")

    def __rshift__(self, _: Self | Number) -> Self:
        raise TypeError("Bitwise right shift is not supported for instances of QInt")

    def __neg__(self) -> Self:
        return QInt(-self.value, self.precision)

    def __pos__(self) -> Self:
        return QInt(self.value, self.precision)

    def __abs__(self) -> Self:
        return QInt(abs(self.value), self.precision)

    def __eq__(self, __obj: Self) -> bool:
        return self.value == __obj.value

    def __ne__(self, __obj: Self) -> bool:
        return self.value != __obj.value

    def __gt__(self, __obj: Self) -> bool:
        return self.value > __obj.value

    def __ge__(self, __obj: Self) -> bool:
        return self.value >= __obj.value

    def __lt__(self, __obj: Self) -> bool:
        return self.value < __obj.value

    def __le__(self, __obj: Self) -> bool:
        return self.value <= __obj.value
