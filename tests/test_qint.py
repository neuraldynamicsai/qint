from fractions import Fraction

import pytest

from qint.qint import QInt


class TestQIntCreation:
    def test_init(self):
        q = QInt(123, 2)
        assert q.value == 123
        assert q.precision == 2

    def test_create(self):
        q = QInt.create(1.23, 2)
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

        assert q2.value == 45723
        assert q2.precision == 2

    def test_addition_precision_mismatch(self):
        q1 = QInt(123, 2)
        q2 = QInt(456, 3)
        with pytest.raises(ValueError):
            return q1 + q2

    def test_addition_inplace(self):
        q1 = QInt(123, 2)
        q1 += 456

        assert q1.value == 45723
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
        assert q2.value == -11844
        assert q2.precision == 2

    def test_subtraction_inplace(self):
        q1 = QInt(456, 2)
        q1 -= 123
        assert q1.value == -11844
        assert q1.precision == 2


class TestQIntMultiplication:
    def test_multiplication(self):
        q1 = QInt(123, 2)
        q2 = QInt(456, 2)
        q3 = q1 * q2
        assert q3.value == 560
        assert q3.precision == 2

    def test_multiplication_scalar(self):
        q1 = QInt(123, 2)
        q2 = q1 * 456
        assert q2.value == 56088
        assert q2.precision == 2

    def test_multiplication_inplace(self):
        q1 = QInt(123, 2)
        q1 *= 456
        assert q1.value == 56088
        assert q1.precision == 2

    def test_multiplication_fraction(self):
        q1 = QInt(246, 2)
        q2 = q1 * Fraction(1, 2)
        assert q2.value == 123
        assert q2.precision == 2


class TestQIntDivision:
    def test_truedivision(self):
        q1 = QInt(123, 2)
        q2 = QInt(456, 2)
        q3 = q1 / q2
        assert q3.value == 0
        assert q3.precision == 2

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
        q1 = QInt(123, 2)
        q2 = QInt(456, 2)
        q3 = q1 // q2
        assert q3.value == 0
        assert q3.precision == 0

    def test_floordivision_scalar(self):
        q1 = QInt(6300, 2)
        q2 = q1 // 4
        assert q2.value == 15
        assert q2.precision == 0

    def test_floordivision_inplace(self):
        q1 = QInt(456, 2)
        q1 //= 2
        assert q1.value == 2
        assert q1.precision == 0


class TestQIntOtherOperations:
    def test_modulo(self):
        q1 = QInt(456, 2)
        q2 = QInt(123, 2)
        q3 = q1 % q2
        assert q3.value == 87
        assert q3.precision == 2

    def test_modulo_scalar(self):
        q1 = QInt(456, 2)
        q2 = q1 % 1
        assert q2.value == 56
        assert q2.precision == 2

    def test_exponentiation(self):
        q1 = QInt(2, 0)
        q2 = QInt(3, 0)

        q3 = q1**2
        q4 = q2**3

        assert q3 == QInt(4, 0)
        assert q4 == QInt(27, 0)

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
    def test_addition(self):
        q1 = QInt(1230, 3)
        q2 = QInt(456, 2)
        q3 = q1.add(q2)
        assert q3.value == 5790
        assert q3.precision == 3

    def test_subtraction(self):
        q1 = QInt(456, 2)
        q2 = QInt(1230, 3)
        q3 = q1.sub(q2)
        assert q3.value == 3330
        assert q3.precision == 3

    def test_multiplication(self):
        q1 = QInt(200, 2)
        q2 = QInt(4000, 3)
        q3 = q1.mul(q2)
        assert q3.value == 8000
        assert q3.precision == 3

    def test_division(self):
        q1 = QInt(400, 2)
        q2 = QInt(2000, 3)
        q3 = q1.div(q2)
        assert q3.value == 2000
        assert q3.precision == 3
