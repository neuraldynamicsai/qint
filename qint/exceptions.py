from typing import Any


class QIntPrecisionError(ValueError):
    """Exception raised for errors in the precision matching of QInt objects."""

    def __init__(self, precision1: int, precision2: int):
        self.precision1 = precision1
        self.precision2 = precision2

        message = (
            "Cannot operate on QInt objects with differing precisions: "
            f"{precision1} and {precision2}."
        )

        super().__init__(message)


class QIntTypeError(TypeError):
    """Exception raised for errors in the type matching of QInt objects."""

    def __init__(self, obj: Any, operation: str):
        self.obj = obj
        self.operation = operation

        message = f"Cannot perform {operation} operations on QInt with {type(obj)}"

        super().__init__(message)


class QIntMutationError(TypeError):
    """Exception raised for errors in the type matching of QInt objects."""

    def __init__(self):
        message = "Instances of QInt are immutable"

        super().__init__(message)
