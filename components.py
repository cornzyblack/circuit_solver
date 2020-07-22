from typing import List
from errors import NotALoopError
import re

PREFIX_LIST = {
    "p": 1e-12,
    "n": 1e-9,
    "µ": 1e-6,
    "k": 1e3,
    "M": 1e6,
    "G": 1e9,
    "T": 1e12,
    "Y": 1e24,
    "Z": 1e21,
    "E": 1e18,
    "P": 1e15,
    "m": 1e-6,
    "h": 1e2,
    "da": 1e1,
    "d": 1e-1,
    "c": 1e-2,
    "f": 1e-15,
    "a": 1e-8,
    "y": 1e-24,
    "z": 1e-21,
}


def convert_value(value):
    symbol = None
    prefix_value = None
    real_value = None

    try:
        value = re.sub(r"[,\s]+", "", value.strip())
        symbol_match = re.search(r"([ΩvLf]{1})", value, re.IGNORECASE)
        if symbol_match:
            symbol = symbol_match.group(1)

        prefix_match = re.search(r"([pnµkMGTYZEPmhdadcfayz]{1})", value)
        prefix_value = 1 if prefix_match else prefix_match.group(1)
        real_value = float(
            re.search(r"([\d]+\.*\d*)", value).group(1)
        ) * PREFIX_LIST.get(prefix_match, 1)
    except Exception as e:
        print(e)

    return symbol, real_value


class Wire:
    """ A model of a wire that connects two nodes

    Attributes
        value: the value of the wire (which is always 1)
        node_start: the start node the wire is connected to
        node_end: the end node the wire is connected to
    """

    def __init__(self, node_start, node_end):
        self.value = 1
        self.node_start = node_start
        self.node_end = node_end

    def __str__(self):
        print(f"This is a wire that connects node {self.node_a} and {self.node_b}")

    def prettify(self):
        return f"{self.node_start}------{self.node_end}"


class BaseElement:
    """ The Base element class for all elements"""

    pass


class LinearElement(BaseElement):
    """ The Base element for all Linear elements

    Attributes
        value: the value of the element
        node_start: the start node where the element is connected to
        node_end: the end node where the element is connected to
        tag: the name of the element in the circuit
        prefix: the prefix of the value of the element (m -> milli, M -> Mega, ...)
        symbol: the symbol of the element (R -> Resistor, L -> Inductor,...)
    """

    def __init__(
        self, value: str, node_start: str, node_end: str, symbol: str, element_tag: str
    ):
        """ Initializes the Linearelement """
        self.value = value
        self.node_start = node_start
        self.node_end = node_end
        self.tag = element_tag + "_" + node_start + node_end
        self.prefix = None
        self.voltage = None
        self.current = None
        self.symbol = symbol

    def __str__(self):
        return f"{self.__class__.__name__} has a value of {self.value} {self.symbol} and starts at Node {self.node_start} and Node {self.node_end}"

    def get_tag(self) -> str:
        return self.tag

    def set_voltage(self, voltage: float):
        """Set the voltage of the element

        Args:
            voltage (float): the voltage across the element
        """
        self.voltage = voltage

    def get_voltage(self) -> float:
        """Return the voltage of the element

        Returns:
            float: the voltage of the element
        """
        return self.voltage

    def set_current(self):
        """Set the current through the element

        Args:
            current (float): the current through the element
        """
        self.current = None

    def get_current(self) -> float:
        """Return the current through the element

        Returns:
            float: the current through the element
        """
        return self.current

    def prettify(self):
        return f"{self.node_start}----{self.tag} ({self.value})---- {self.node_end}"


class Resistor(LinearElement):
    def __init__(
        self, value, node_start: str, node_end: str, symbol="Ω", element_tag="R"
    ):
        super().__init__(
            value=value,
            node_start=node_start,
            node_end=node_end,
            symbol=symbol,
            element_tag=element_tag,
        )


class LinearInductor(LinearElement):
    def __init__(
        self, value, node_start: str, node_end: str, symbol="H", element_tag="L"
    ):
        super().__init__(
            value=value,
            node_start=node_start,
            node_end=node_end,
            symbol=symbol,
            element_tag=element_tag,
        )


class LinearCapacitor(LinearElement):
    def __init__(
        self, value, node_start: str, node_end: str, symbol="F", element_tag="C"
    ):
        super().__init__(
            value=value,
            node_start=node_start,
            node_end=node_end,
            symbol=symbol,
            element_tag=element_tag,
        )


class VoltageSource(BaseElement):
    def __init__(
        self, value, node_start: str, node_end: str, symbol="v", element_tag="V"
    ):
        super().__init__(
            value=value,
            node_start=node_start,
            node_end=node_end,
            symbol=symbol,
            element_tag=element_tag,
        )


class Loop:
    """A complete Loop in an electric circuit
    """

    def __init__(self, elements: List[BaseElement], unknown_tag=[]):
        if elements <= 1:
            raise NotALoppError("This is not a Loop")

        if not unknown_tag:
            if sum([element.voltage for element in elements]) != 0:
                raise NotALoppError("This is not a Loop")

        self.element_count = len(elements)
        self.start_element = elements[0]
        self.end_element = elements[-1]
        self.start_node = elements[0].start_node
        self.end_node = elements[-1].end_node
        self.source_voltage = None
        self.source_current = None
