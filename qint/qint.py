from decimal import Decimal
from fractions import Fraction
from functools import wraps
from typing import Callable, NamedTuple, Optional, Self, Tuple, TypeVar
from warnings import warn

import qint.utils as ut

from .exceptions import QIntPrecisionError, QIntTypeError
from .utils import Number, Rational_Number, Scalar

T = TypeVar("T", bound="QInt")
Method = Callable[[T, T | Scalar], T]


def check_operand(
    valid_types: Optional[Tuple[type, ...]] = None, include_self: bool = True
) -> Method:
    """
    Decorator for checking the type of the operand in QInt operations. The
    operand must be of one of the types in `valid_types`. If `valid_types` is
    not provided, only QInt is considered valid.

    :param valid_types: A tuple of types that are valid for the operation, or None to
        default to QInt only.
    :param include_self: Whether to include the type of the QInt instance itself in
        the valid types.
    :return: A callable that takes a QInt instance and an operand.
    """

    if valid_types is None:
        valid_types = tuple()

    def decorator(method: Method) -> Method:
        @wraps(method)
        def wrapper(self: T, other: T | Scalar, *args, **kwargs) -> T:
            _types = (type(self), *valid_types) if include_self else valid_types
            if not isinstance(other, _types):
                operation = method.__name__
                raise QIntTypeError(other, operation)
            return method(self, other, *args, **kwargs)

        return wrapper

    return decorator


def require_same_precision(method: Method) -> Method:
    """
    Decorator for arithmetic methods of QInt to ensure that the precision of
    both operands match when the other operand is a QInt. Scalars like ints or
    Fractions are treated as such and do not require a precision check.

    :param method: The arithmetic method to be wrapped.
    :return: Wrapped method that checks precision compatibility.
    """

    @wraps(method)
    def wrapper(self: T, other: T | Scalar) -> T:
        if isinstance(other, QInt) and self.precision != other.precision:
            raise QIntPrecisionError(self.precision, other.precision)
        return method(self, other)

    return wrapper


class QInt(NamedTuple):
    """
    Class for representing quantized integers. The value is stored as an
    integer, but the true value is calculated by dividing the integer by
    10^precision. This allows for exact arithmetic on the quantized integers.

    QInts are comparable to other QInts with the same precision.

    QInts are immutable.

    Unless otherwise specified, Operations that result in fractional values
    will be rounded to the nearest integer using banker's rounding (round half even).

    :param value: quantized value
    :param precision: precision of the quantized value
    """

    value: int
    precision: int

    @classmethod
    def create(cls, value: Rational_Number | str, precision: int) -> Self:
        """
        Create a QInt from a rational number with a given precision. Use this when the
        value we are passing in is NOT already quantized.

        NOTE: Creating QInts from floats may result in inexact quantization at extreme
        precision levels.

        :param value: The value to quantize. Can be a float, int, Fraction, or Decimal.
        :param precision: The precision to quantize to.
        """
        if isinstance(value, int):
            return cls._from_int(value, precision)
        elif isinstance(value, float):
            return cls._from_float(value, precision)
        elif isinstance(value, Decimal):
            return cls._from_decimal(value, precision)
        elif isinstance(value, Fraction):
            return cls._from_fraction(value, precision)
        elif isinstance(value, str):
            return cls._from_str(value, precision)
        else:
            raise TypeError(f"Cannot create QInt from {type(value)}")

    def scale(self, targ: int) -> Self:
        """
        Scale the precision of the QInt to the given target.

        :param targ: The target precision.
        """
        if not isinstance(targ, int):
            raise TypeError(f"Target precision must be an integer, got {type(targ)}")

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

    @check_operand((int,))
    @require_same_precision
    def __add__(self, other: Self | int) -> Self:
        if isinstance(other, QInt):
            return QInt(self.value + other.value, self.precision)
        else:
            return QInt(self.value + other, self.precision)

    @check_operand()
    def add(self, other: Self, targ: Optional[int] = None) -> Self:
        """
        Add two QInts together and scale the result to the given target precision.

        :param other: The other QInt to add.
        :param targ: The target precision. If None, the precision of the result will
            be the maximum of the precisions of the two operands.
        """
        if targ is None:
            targ = max(self.precision, other.precision)

        if other.precision == self.precision:
            return self.__add__(other).scale(targ)
        else:
            return self.scale(targ).__add__(other.scale(targ))

    @check_operand((int,))
    @require_same_precision
    def __sub__(self, other: Self | int) -> Self:
        if isinstance(other, QInt):
            return QInt(self.value - other.value, self.precision)
        else:
            return QInt(self.value - other, self.precision)

    @check_operand()
    def sub(self, other: Self, targ: Optional[int] = None) -> Self:
        """
        Subtract `other` QInt from this QInt and scale the result to the given target

        :param other: The other QInt to subtract.
        :param targ: The target precision. If None, the precision of the result will
            be the maximum of the precisions of the two operands.
        """
        if targ is None:
            targ = max(self.precision, other.precision)

        if other.precision == self.precision:
            return self.__sub__(other).scale(targ)
        else:
            return self.scale(targ).__sub__(other.scale(targ))

    @check_operand((Scalar,))
    def __mul__(self, other: Self | Scalar) -> Self:
        if isinstance(other, QInt):
            return QInt(self.value * other.value, self.precision + other.precision)
        elif isinstance(other, Fraction):
            value = ut.banker_division(self.value * other.numerator, other.denominator)
            return QInt(value, self.precision)
        else:
            return QInt(self.value * other, self.precision)

    @check_operand()
    def mul(self, other: Self, targ: Optional[int] = None) -> Self:
        """
        Multiply two QInts together and scale the result to the given target precision.

        :param other: The other QInt to multiply.
        :param targ: The target precision. If None, the precision of the result will
            be the sum of the precisions of the two operands.
        """
        if targ is None:
            targ = self.precision + other.precision

        return self.__mul__(other).scale(targ)

    @check_operand((Scalar,))
    def __truediv__(self, other: Self | Scalar) -> Self:
        if isinstance(other, QInt):
            value = ut.banker_division(self.value, other.value)
            return QInt(value, self.precision - other.precision)
        elif isinstance(other, Fraction):
            value = ut.banker_division(self.value * other.denominator, other.numerator)
            return QInt(value, self.precision)
        else:
            value = ut.banker_division(self.value, other)
            return QInt(value, self.precision)

    @check_operand()
    def div(self, other: Self, targ: Optional[int] = None) -> Self:
        """
        Divide two QInts together and scale the result to the given target precision.

        :param other: The other QInt to divide.
        :param targ: The target precision. If None, the precision of the result will
            be the difference of the precisions of the two operands.
        """
        # for div we scale upfront to avoid precision loss
        div_prec = other.precision + targ if targ is not None else None
        return self.scale(div_prec).__truediv__(other)

    @check_operand((Scalar,))
    def __floordiv__(self, other: Self | Scalar) -> Self:
        if isinstance(other, QInt):
            value = self.value // other.value
            return QInt(value, self.precision - other.precision)
        elif isinstance(other, Fraction):
            value = (self.value * other.denominator) // other.numerator
            return QInt(value, self.precision)
        else:
            value = self.value // other
            return QInt(value, self.precision)

    @check_operand()
    @require_same_precision
    def __mod__(self, other: Self | int) -> Self:
        mod_value = self.value % other.value
        return QInt(mod_value, self.precision)

    @check_operand((int,), include_self=False)
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

    @check_operand()
    @require_same_precision
    def __eq__(self, __obj: Self) -> bool:
        return self.value == __obj.value

    @check_operand()
    @require_same_precision
    def __ne__(self, __obj: Self) -> bool:
        return self.value != __obj.value

    @check_operand()
    @require_same_precision
    def __gt__(self, __obj: Self) -> bool:
        return self.value > __obj.value

    @check_operand()
    @require_same_precision
    def __ge__(self, __obj: Self) -> bool:
        return self.value >= __obj.value

    @check_operand()
    @require_same_precision
    def __lt__(self, __obj: Self) -> bool:
        return self.value < __obj.value

    @check_operand()
    @require_same_precision
    def __le__(self, __obj: Self) -> bool:
        return self.value <= __obj.value

    @classmethod
    def _from_int(cls, value: int, precision: int) -> Self:
        return cls(ut.quantize(value, precision), precision)

    @classmethod
    def _from_float(cls, value: float, precision: int) -> Self:
        warn("Creating QInt from float may result in inexact quantization.")
        return cls(ut.quantize(value, precision), precision)

    @classmethod
    def _from_decimal(cls, value: Decimal, precision: int) -> Self:
        num, denom = value.as_integer_ratio()
        return cls._from_fraction(Fraction(num, denom), precision)

    @classmethod
    def _from_fraction(cls, value: Fraction, precision: int) -> Self:
        scaled_numerator = ut.scale(value.numerator, precision)
        value = ut.banker_division(scaled_numerator, value.denominator)
        return cls(value, precision)

    @classmethod
    def _from_str(cls, value: str, precision: int) -> Self:
        return cls._from_decimal(Decimal(value), precision)
