import math

import pytest

from qint.utils import quantize, unquantize, banker_division, scale


class TestQuantize:
    def test_positive_float_values(self):
        assert quantize(1.23, 2) == 123
        assert quantize(3.456, 3) == 3456
        assert quantize(0.12345, 4) == 1234

    def test_negative_float_values(self):
        assert quantize(-1.23, 2) == -123
        assert quantize(-3.456, 3) == -3456
        assert quantize(-0.12345, 4) == -1234

    def test_zero(self):
        assert quantize(0, 2) == 0

    def test_precision_zero(self):
        assert quantize(123.45, 0) == 123


class TestUnquantize:
    def test_positive_integer_values(self):
        assert math.isclose(unquantize(123, 2), 1.23, abs_tol=1e-6)
        assert math.isclose(unquantize(3456, 3), 3.456, abs_tol=1e-6)
        assert math.isclose(unquantize(1234, 4), 0.1234, abs_tol=1e-6)

    def test_negative_integer_values(self):
        assert math.isclose(unquantize(-123, 2), -1.23, abs_tol=1e-6)
        assert math.isclose(unquantize(-3456, 3), -3.456, abs_tol=1e-6)
        assert math.isclose(unquantize(-1234, 4), -0.1234, abs_tol=1e-6)

    def test_zero(self):
        assert unquantize(0, 2) == 0.0

    def test_precision_zero(self):
        assert unquantize(123, 0) == 123.0


class TestBankerDivision:
    def test_positive_values_even_denominator(self):
        assert banker_division(7, 2) == 4
        assert banker_division(10, 2) == 5
        assert banker_division(8, 2) == 4

    def test_positive_values_odd_denominator(self):
        assert banker_division(7, 3) == 2
        assert banker_division(10, 3) == 3
        assert banker_division(8, 3) == 3

    def test_negative_values_even_denominator(self):
        assert banker_division(-7, 2) == -4
        assert banker_division(-10, 2) == -5
        assert banker_division(-8, 2) == -4

    def test_negative_values_odd_denominator(self):
        assert banker_division(-7, 3) == -2
        assert banker_division(-10, 3) == -3
        assert banker_division(-8, 3) == -3

    def test_division_by_zero(self):
        with pytest.raises(ZeroDivisionError):
            banker_division(5, 0)


class TestScale:
    def test_positive_values(self):
        assert scale(123, 2) == 12300
        assert scale(3456, 3) == 3456000
        assert scale(1234, 4) == 12340000

    def test_negative_values(self):
        assert scale(-123, 2) == -12300
        assert scale(-3456, 3) == -3456000
        assert scale(-1234, 4) == -12340000

    def test_zero(self):
        assert scale(0, 2) == 0

    def test_positive_delta(self):
        assert scale(123, 2) == 12300
        assert scale(3456, 3) == 3456000
        assert scale(1234, 4) == 12340000

    def test_negative_delta(self):
        assert scale(12300, -2) == 123
        assert scale(3456000, -3) == 3456
        assert scale(12340000, -4) == 1234

    def test_zero_delta(self):
        assert scale(123, 0) == 123
        assert scale(3456, 0) == 3456
        assert scale(1234, 0) == 1234
