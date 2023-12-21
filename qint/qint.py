from __future__ import annotations
from typing import NamedTuple, Self
from fractions import Fraction
from functools import total_ordering, wraps

import qint.utils as ut
from .utils import Number
from .exceptions import QIntPrecisionError, QIntTypeError


def check_operand(valid_types: tuple[type, ...], operation: str):
    """
    Decorator for checking the type of the operand in QInt operations. The
    operand must be of one of the types in `valid_types`.
    """

    def decorator(method):
        @wraps(method)
        def wrapper(self: "QInt", other):
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
        def wrapper(self: "QInt", other):
            if not isinstance(other, QInt):
                raise QIntTypeError(other, operation)

            max_precision = max(self.precision, other.precision)

            def scale(q: QInt) -> QInt:
                precision_difference = max_precision - q.precision

                if precision_difference == 0:
                    return q  # Precision stays the same

                scaled_value = int(round(q.value * (10**precision_difference)))
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

    Examples:
    >>> QInt(123, 2)
    QInt(value=123, precision=2)
    >>> QInt.from_float(1.23, 2) # create from float
    QInt(value=123, precision=2)
    >>> QInt(123, 2) + QInt(456, 2) # add two QInts
    QInt(value=579, preision=2)
    >>> QInt(123, 2) + 456 # add QInt with scalar
    QInt(value=579, precision=2)
    >>> QInt(123, 2) + QInt(456, 3) # cannot add QInts with different precision
    ValueError: Cannot add QInt with precision 2 with QInt with precision 3

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

    def __quantize(self, other: Self | Number) -> int:
        return (
            other.value
            if isinstance(other, QInt)
            else ut.quantize(other, self.precision)
        )

    def __float__(self) -> float:
        return ut.unquantize(self.value, self.precision)

    def __int__(self) -> int:
        return int(round(self.__float__()))

    @check_operand((int,), "addition")
    def __add__(self, other: Self | int) -> Self:
        return QInt(self.value + self.__quantize(other), self.precision)

    @scale_safe("addition")
    def add(self, other: Self) -> Self:
        return self.__add__(other)

    @check_operand((int,), "subtraction")
    def __sub__(self, other: Self | int) -> Self:
        return QInt(self.value - self.__quantize(other), self.precision)

    @scale_safe("subtraction")
    def sub(self, other: Self) -> Self:
        return self.__sub__(other)

    @check_operand((int, Fraction), "multiplication")
    def __mul__(self, other: Self | int | Fraction) -> Self:
        if isinstance(other, Fraction):
            return self.__truediv__(Fraction(other.denominator, other.numerator))

        value = self.value * self.__quantize(other) // (10**self.precision)
        return QInt(value, self.precision)

    @scale_safe("multiplication")
    def mul(self, other: Self) -> Self:
        return self.__mul__(other)

    @check_operand((int, Fraction), "division")
    def __truediv__(self, other: Self | int | Fraction) -> Self:
        if isinstance(other, Fraction):
            value = ut.banker_division(self.value * other.denominator, other.numerator)
        elif isinstance(other, QInt):
            value = ut.banker_division(self.value, other.value) * (
                10**other.precision
            )
        else:
            value = ut.banker_division(self.value, other)
        return QInt(value, self.precision)

    @scale_safe("division")
    def div(self, other: Self) -> Self:
        return self.__truediv__(other)

    @check_operand((int, Fraction), "floor division")
    def __floordiv__(self, other: Self | int | Fraction) -> Self:
        q = self.__truediv__(other)
        value = q.value // (10**self.precision)
        return QInt(value, 0)

    @check_operand((int,), "modulo")
    def __mod__(self, other: Self | int) -> Self:
        return QInt(self.value % self.__quantize(other), self.precision)

    @check_operand((int,), "exponentiation")
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

        value = self.value**other // (10**self.precision)
        return QInt(value, self.precision)

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

    @check_operand((), "comparison")
    def __eq__(self, __obj: Self) -> bool:
        return self.value == __obj.value

    @check_operand((), "comparison")
    def __ne__(self, __obj: Self) -> bool:
        return self.value != __obj.value

    @check_operand((), "comparison")
    def __gt__(self, __obj: Self) -> bool:
        return self.value > __obj.value

    @check_operand((), "comparison")
    def __ge__(self, __obj: Self) -> bool:
        return self.value >= __obj.value

    @check_operand((), "comparison")
    def __lt__(self, __obj: Self) -> bool:
        return self.value < __obj.value

    @check_operand((), "comparison")
    def __le__(self, __obj: Self) -> bool:
        return self.value <= __obj.value
