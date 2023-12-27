from fractions import Fraction
from decimal import Decimal

import pytest

from qint.qint import QInt


class TestQIntCreation:
    def test_init(self):
        q = QInt(123, 2)
        assert q.value == 123
        assert q.precision == 2

    def test_create_from_int(self):
        q = QInt.create(123, 2)
        assert q.value == 12300
        assert q.precision == 2

    def test_create_from_float(self):
        q = QInt.create(1.23, 2)
        assert q.value == 123
        assert q.precision == 2

    def test_create_from_fraction(self):
        q = QInt.create(Fraction(123, 100), 2)
        assert q.value == 123
        assert q.precision == 2

    def test_create_from_decimal(self):
        q = QInt.create(Decimal("1.23"), 2)
        assert q.value == 123
        assert q.precision == 2

    def test_create_from_string(self):
        q = QInt.create("1.23", 2)
        assert q.value == 123
        assert q.precision == 2

    def test_float_conversion(self):
        q = QInt(123, 2)
        assert float(q) == 1.23

    def test_int_conversion(self):
        q1 = QInt(123, 2)
        q2 = QInt(456, 2)

        assert int(q1) == 1
        assert int(q2) == 5

    def test_fraction_conversion(self):
        q = QInt(123, 2)
        assert q.to_fraction() == Fraction(123, 100)

    def test_decimal_conversion(self):
        q = QInt(123, 2)
        assert q.to_decimal() == Decimal("1.23")

    def test_scale_up(self):
        q = QInt(123, 2)
        q = q.scale(3)
        assert q.value == 1230
        assert q.precision == 3

    def test_scale_down(self):
        q = QInt(1230, 3)
        q = q.scale(2)
        assert q.value == 123
        assert q.precision == 2

    def test_scale_down_rounding(self):
        q = QInt(1235, 3)
        q = q.scale(2)
        assert q.value == 124
        assert q.precision == 2


class TestQIntAddition:
    def test_addition(self):
        q1 = QInt(123, 2)
        q2 = QInt(456, 2)
        q3 = q1 + q2
        assert q3.value == 579
        assert q3.precision == 2

    def test_addition_scalar(self):
        q1 = QInt(123, 2)
        q2 = q1 + 456

        assert q2.value == 123 + 456
        assert q2.precision == 2

    def test_addition_precision_mismatch(self):
        q1 = QInt(123, 2)
        q2 = QInt(456, 3)
        with pytest.raises(ValueError):
            return q1 + q2

    def test_addition_inplace(self):
        q1 = QInt(123, 2)
        q1 += 456

        assert q1.value == 123 + 456
        assert q1.precision == 2


class TestQIntSubtraction:
    def test_subtraction(self):
        q1 = QInt(456, 2)
        q2 = QInt(123, 2)
        q3 = q1 - q2
        assert q3.value == 333
        assert q3.precision == 2

    def test_subtraction_scalar(self):
        q1 = QInt(456, 2)
        q2 = q1 - 123
        assert q2.value == 456 - 123
        assert q2.precision == 2

    def test_subtraction_inplace(self):
        q1 = QInt(456, 2)
        q1 -= 123
        assert q1.value == 456 - 123
        assert q1.precision == 2


class TestQIntMultiplication:
    def test_multiplication(self):
        q1 = QInt(123, 2)
        q2 = QInt(456, 2)
        q3 = q1 * q2
        assert q3.value == 123 * 456
        assert q3.precision == 4

    def test_multiplication_scalar(self):
        q1 = QInt(123, 2)
        q2 = q1 * 456
        assert q2.value == 123 * 456
        assert q2.precision == 2

    def test_multiplication_inplace(self):
        q1 = QInt(123, 2)
        q1 *= 456
        assert q1.value == 123 * 456
        assert q1.precision == 2

    def test_multiplication_fraction(self):
        q1 = QInt(246, 2)
        q2 = q1 * Fraction(1, 2)
        assert q2.value == 123
        assert q2.precision == 2

    def test_multiplication_fraction_round_up(self):
        q1 = QInt(243, 2)
        q2 = q1 * Fraction(1, 2)
        assert q2.value == 122
        assert q2.precision == 2

    def test_multiplication_fraction_round_down(self):
        q1 = QInt(247, 2)
        q2 = q1 * Fraction(1, 2)
        assert q2.value == 124
        assert q2.precision == 2


class TestQIntDivision:
    def test_truedivision(self):
        q1 = QInt(456, 2)
        q2 = QInt(228, 2)
        q3 = q1 / q2
        assert q3.value == 2
        assert q3.precision == 0

    def test_truedivision_scalar(self):
        q1 = QInt(6400, 2)
        q2 = q1 / 2
        assert q2.value == 3200
        assert q2.precision == 2

    def test_truedivision_inplace(self):
        q1 = QInt.create(64, 2)
        q1 /= 4
        assert q1.value == 1600
        assert q1.precision == 2

    def test_truedivision_fraction(self):
        q1 = QInt(123, 2)
        q2 = q1 / Fraction(1, 2)
        assert q2.value == 246
        assert q2.precision == 2

    def test_floordivision(self):
        q1 = QInt(456, 2)
        q2 = QInt(123, 2)
        q3 = q1 // q2
        assert q3.value == 3
        assert q3.precision == 0

    def test_floordivision_scalar(self):
        q1 = QInt(6300, 2)
        q2 = q1 // 8
        assert q2.value == 787
        assert q2.precision == 2

    def test_floordivision_inplace(self):
        q1 = QInt(456, 2)
        q1 //= 2
        assert q1.value == 228
        assert q1.precision == 2


class TestQIntOtherOperations:
    def test_modulo(self):
        q1 = QInt(456, 2)
        q2 = QInt(123, 2)
        q3 = q1 % q2
        assert q3.value == 87
        assert q3.precision == 2

    def test_exponentiation(self):
        q1 = QInt(2, 2)
        q2 = QInt(3, 3)

        q3 = q1**2
        q4 = q2**3

        assert q3 == QInt(4, 4)
        assert q4 == QInt(27, 9)

    def test_comparison(self):
        q1 = QInt(123, 2)
        q2 = QInt(456, 2)
        q3 = QInt(123, 2)

        assert q1 == q3
        assert q1 != q2
        assert q1 < q2
        assert q2 > q1
        assert q1 <= q3
        assert q1 >= q3


class TestQIntScaledOperations:
    def test_addition_default(self):
        q1 = QInt(1230, 3)
        q2 = QInt(456, 2)
        q3 = q1.add(q2)
        assert q3.value == 5790
        assert q3.precision == 3

    def test_addition_targ(self):
        q1 = QInt(1230, 3)
        q2 = QInt(456, 2)
        q3 = q1.add(q2, 5)
        assert q3.value == 579000
        assert q3.precision == 5

    def test_subtraction_default(self):
        q1 = QInt(456, 2)
        q2 = QInt(1230, 3)
        q3 = q1.sub(q2)
        assert q3.value == 3330
        assert q3.precision == 3

    def test_subtraction_targ(self):
        q1 = QInt(456, 2)
        q2 = QInt(1230, 3)
        q3 = q1.sub(q2, 5)
        assert q3.value == 333000
        assert q3.precision == 5

    def test_multiplication_default(self):
        q1 = QInt(200, 2)
        q2 = QInt(4000, 3)
        q3 = q1.mul(q2)
        assert q3.value == 800_000
        assert q3.precision == 5

    def test_multiplication_targ(self):
        q1 = QInt(123, 2)
        q2 = QInt(456, 3)
        q3 = q1.mul(q2, 2)
        assert q3.value == 56
        assert q3.precision == 2

    def test_division_default(self):
        q1 = QInt(500, 3)
        q2 = QInt(3, 1)
        q3 = q1.div(q2)
        assert q3.value == 167
        assert q3.precision == 2

    def test_division_targ(self):
        q1 = QInt(500, 3)
        q2 = QInt(3, 1)
        q3 = q1.div(q2, 5)
        assert q3.value == 166667
        assert q3.precision == 5
