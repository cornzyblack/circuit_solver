class BaseError(Exception):
    pass


class ErrorParsing(BaseError):
    def __init__(self):
        self.message = "Could not parse, please supply a path or a Dictionary containing components"

    def __str__(self):
        return self.message


class NotALoopError(BaseError):
    """Exception raised when the connected components do not constitute a valid loop.
    A valid Loop is one starts from a source and ends back at that source. In general,
    the first component is a

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f"This is not a Loop"


class NotInSeries(BaseError):
    """Exception raised when the connected components are not in Series.
    """

    def __init__(self, resistor_a, resistor_b):
        self.resistor_a = resistor_a
        self.resistor_b = resistor_

    def __str__(self):
        return f"The Resistors {self.resistor_a}, {self.resistor_b} are not in Series"


class NotInParallel(BaseError):
    """Exception raised when the connected components are not in Parallel.
    """

    def __init__(self, resistor_a, resistor_b):
        self.resistor_a = resistor_a
        self.resistor_b = resistor_b

    def __str__(self):
        return f"The Resistors {self.resistor_a}, {self.resistor_b} are not in Parallel"


class SameNodeError(BaseError):
    """Exception raised when the .
    """

    def __str__(self):
        return f"The Nodes cannot be the same (start_node != end_node)"
