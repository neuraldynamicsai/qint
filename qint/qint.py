from typing import NamedTuple, Self
from functools import total_ordering

import qint.utils as ut
from .utils import Number


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

    def __add__(self, other: Self | int) -> Self:
        if isinstance(other, QInt):
            if self.precision != other.precision:
                raise ValueError(
                    f"Cannot add QInt(precision={self.precision}) with "
                    f"QInt(precision={other.precision})"
                )
            return QInt(self.value + other.value, self.precision)
        elif isinstance(other, int):
            # simple scalar addition
            return QInt(self.value + other, self.precision)
        else:
            raise ValueError(f"Cannot add QInt with {type(other)}")

    def __sub__(self, other: Self | int) -> Self:
        if isinstance(other, QInt):
            if self.precision != other.precision:
                raise ValueError(
                    f"Cannot subtract QInt(precision={self.precision}) with"
                    f"QInt(precision={other.precision})"
                )
            return QInt(self.value - other.value, self.precision)
        elif isinstance(other, int):
            # simple scalar subtraction
            return QInt(self.value - other, self.precision)
        else:
            raise ValueError(f"Cannot subtract QInt with {type(other)}")

    def __mul__(self, other: Self | Number) -> Self:
        if isinstance(other, QInt):
            if self.precision != other.precision:
                raise ValueError(
                    f"Cannot multiply QInt(precision={self.precision}) with "
                    f"QInt(precision={other.precision})"
                )
            return QInt(self.value * other.value, self.precision)
        elif isinstance(other, Number):
            # simple scalar multiplication
            return QInt(ut.int_mul(self.value, other), self.precision)
        else:
            raise ValueError(f"Cannot multiply QInt with {type(other)}")

    def __truediv__(self, other: Self | Number) -> Self:
        if isinstance(other, QInt):
            if self.precision != other.precision:
                raise ValueError(
                    f"Cannot divide QInt(precision={self.precision}) with "
                    f"QInt(precision={other.precision})"
                )
            return QInt(ut.int_div(self.value, other.value), self.precision)
        elif isinstance(other, Number):
            # simple scalar division
            return QInt(ut.int_div(self.value, other), self.precision)
        else:
            raise ValueError(f"Cannot divide QInt with {type(other)}")

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, QInt):
            if self.precision != __value.precision:
                raise ValueError(
                    f"Cannot compare QInt(precision={self.precision}) "
                    f"with QInt(precision={__value.precision})"
                )
            return self.value == __value.value
        else:
            raise TypeError(f"Cannot compare QInt with {type(__value)}")

    def __gt__(self, __value: object) -> bool:
        if isinstance(__value, QInt):
            if self.precision != __value.precision:
                raise ValueError(
                    f"Cannot compare QInt(precision={self.precision}) "
                    f"with QInt(precision={__value.precision})"
                )
            return self.value > __value.value
        else:
            raise TypeError(f"Cannot compare QInt with {type(__value)}")
