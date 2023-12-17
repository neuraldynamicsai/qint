from typing import NamedTuple, Self
from functools import total_ordering

import qint.utils as ut
from .utils import Number
from .exceptions import QIntPrecisionError, QIntTypeError, QIntMutationError


def check_qint(method):
    def wrapper(self, other):
        if not isinstance(other, QInt):
            raise QIntTypeError(other)

        if self.precision != other.precision:
            raise QIntPrecisionError(self.precision, other.precision)

        return method(self, other)

    return wrapper


def check_qint_or_number(method):
    def wrapper(self, other):
        if not isinstance(other, QInt) and not isinstance(other, Number):
            raise QIntTypeError(other)

        if isinstance(other, QInt) and self.precision != other.precision:
            raise QIntPrecisionError(self.precision, other.precision)

        return method(self, other)

    return wrapper


def check_qint_or_int(method):
    def wrapper(self, other):
        if not isinstance(other, QInt) and not isinstance(other, int):
            raise QIntTypeError(other)

        if isinstance(other, QInt) and self.precision != other.precision:
            raise QIntPrecisionError(self.precision, other.precision)

        return method(self, other)

    return wrapper


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

    @property
    def true_value(self) -> float:
        """True unquantized value"""
        return ut.unquantize(self.value, self.precision)

    @classmethod
    def from_float(cls, value: Number, precision: int) -> Self:
        """Create a QInt from a float with a given precision"""
        if not isinstance(value, Number):
            raise ValueError(f"Value must be a number, not {type(value)}")

        return cls(ut.quantize(value, precision), precision)

    @check_qint_or_int
    def __add__(self, other: Self | int) -> Self:
        if isinstance(other, QInt):
            value = self.value + other.value
        else:
            value = self.value + other

        return QInt(value, self.precision)

    @check_qint_or_int
    def __sub__(self, other: Self | int) -> Self:
        if isinstance(other, QInt):
            value = self.value - other.value
        else:
            value = self.value - other

        return QInt(value, self.precision)

    @check_qint_or_number
    def __mul__(self, other: Self | Number) -> Self:
        if isinstance(other, QInt):
            value = self.value * other.value
        else:
            value = ut.int_mul(self.value, other)

        return QInt(value, self.precision)

    @check_qint_or_number
    def __truediv__(self, other: Self | Number) -> Self:
        if isinstance(other, QInt):
            value = ut.int_div(self.value, other.value)
        else:
            value = ut.int_div(self.value, other)

        return QInt(value, self.precision)

    @check_qint_or_number
    def __floordiv__(self, other: Self | Number) -> Self:
        if isinstance(other, QInt):
            value = ut.int_floordiv(self.value, other.value, self.precision)
        else:
            value = ut.int_floordiv(self.value, other, self.precision)

        return QInt(value, 0)

    @check_qint_or_number
    def __mod__(self, other: Self | Number) -> Self:
        if isinstance(other, QInt):
            value = ut.int_mod(self.value, other.value, self.precision)
        else:
            value = ut.int_mod(self.value, other, self.precision)

        return QInt(value, self.precision)

    @check_qint_or_number
    def __pow__(self, _: Self | Number) -> Self:
        raise TypeError("Exponentiation is not supported for instances of QInt")

    def __iadd__(self, _: Self | int) -> Self:
        raise QIntMutationError()

    def __isub__(self, _: Self | int) -> Self:
        raise QIntMutationError()

    def __imul__(self, _: Self | Number) -> Self:
        raise QIntMutationError()

    def __itruediv__(self, _: Self | Number) -> Self:
        raise QIntMutationError()

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

    @check_qint
    def __eq__(self, __obj: Self) -> bool:
        return self.value == __obj.value

    @check_qint
    def __ne__(self, __obj: Self) -> bool:
        return self.value != __obj.value

    @check_qint
    def __gt__(self, __obj: Self) -> bool:
        return self.value > __obj.value

    @check_qint
    def __ge__(self, __obj: Self) -> bool:
        return self.value >= __obj.value

    @check_qint
    def __lt__(self, __obj: Self) -> bool:
        return self.value < __obj.value

    @check_qint
    def __le__(self, __obj: Self) -> bool:
        return self.value <= __obj.value
