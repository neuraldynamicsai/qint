class QIntPrecisionError(ValueError):
    """Exception raised for errors in the precision matching of QInt objects."""

    def __init__(self, precision1, precision2):
        self.precision1 = precision1
        self.precision2 = precision2

        message = (
            "Cannot operate on QInt objects with differing precisions: "
            f"{precision1} and {precision2}."
        )

        super().__init__(message)
