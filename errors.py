class BaseError(Exception):
    pass

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
