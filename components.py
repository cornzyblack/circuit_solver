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
    prefix_value = None

    if type(value) is not float:
        try:
            value = re.sub(r"[,\s]+", "", value.strip())
            prefix_match = re.search(r"([pnµkMGTYZEPmhdadcfayz]{1})", value)
            prefix_value = prefix_match.group(1) if prefix_match else 1
            value = float(
                re.search(r"([\d]+\.*\d*)", value).group(1)
            ) * PREFIX_LIST.get(prefix_match, 1)
        except Exception as e:
            print(e)
    return value


class Wire:
    """ A model of a wire that connects two nodes

    Attributes
        value: the value of the wire (which is always 1)
        start_node: the start node the wire is connected to
        end_node: the end node the wire is connected to
    """

    def __init__(self, start_node, end_node):
        self.value = 1
        self.start_node = start_node
        self.end_node = end_node

    def __str__(self):
        print(f"This is a wire that connects node {self.node_a} and {self.node_b}")

    def prettify(self):
        return f"{self.start_node}------{self.end_node}"


class BaseElement:
    """ The Base element class for all elements"""

    pass


class LinearElement(BaseElement):
    """ The Base element for all Linear elements

    Attributes
        value: the value of the element
        start_node: the start node where the element is connected to
        end_node: the end node where the element is connected to
        tag: the name of the element in the circuit
        prefix: the prefix of the value of the element (m -> milli, M -> Mega, ...)
        symbol: the symbol of the element (R -> Resistor, L -> Inductor,...)
    """

    def __init__(
        self, value: Union[str, float], start_node: str, end_node: int, symbol: Optional[str], element_tag: str
    ):
        """ Initializes the Linearelement """
        self.start_node, self.end_node = sorted((start_node, end_node))
        self.tag = element_tag + "_" + str(start_node) + str(end_node)
        self.prefix = None
        self.voltage = None
        self.current = None

        self.value = convert_value(value)
        self.symbol = symbol

    def __str__(self):
        return f"{self.__class__.__name__} has a value of {self.value} {self.symbol} and starts at Node {self.start_node} and Node {self.end_node}"

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
        return f"{self.start_node}----{self.tag} ({self.value})---- {self.end_node}"


class Resistor(LinearElement):
    def __init__(
        self, value: str, start_node: str, end_node: str, symbol="Ω", element_tag="R"
    ):
        super().__init__(
            value=value,
            start_node=start_node,
            end_node=end_node,
            symbol=symbol,
            element_tag=element_tag,
        )

    def get_conductance(self):
        return 1 / self.value

    def __add__(self, series_resistor: Resistor) -> Resistor:
        """
        Args:
            series_resistor (Resistor): The resistor in Series

        Returns:
            Resistor: A resistor with the equivalent Resistance of the combined
            seried resistors
        """
        equivalent_resistance_value = self.value + series_resistor.value
        equivalent_voltage = None
        equivalent_current = self.current if self.voltage else series_resistor.current

        return Resistor(value=equivalent_resistance_value, start_node=, end_node=)

    def __div__(self, parallel_resistor: Resistor) -> Resistor:
        """
        Args:
            parallel_resistor (Resistor): The resistor in Parallel

        Returns:
            Resistor: A resistor with the equivalent Resistance of the combined
            parallel resistors
        """
        equivalent_resistance_value = 1 / (self.value + parallel_resistor.value)
        equivalent_voltage = self.voltage if self.voltage else series_resistor.voltage
        equivalent_current = None
        return Resistor(
            value=equivalent_resistance_value,
            start_node=self.start_node,
            end_node=self.end_node,
        )


class LinearInductor(LinearElement):
    def __init__(
        self, value: str, start_node: str, end_node: str, symbol="H", element_tag="L"
    ):
        super().__init__(
            value=value,
            start_node=start_node,
            end_node=end_node,
            symbol=symbol,
            element_tag=element_tag,
        )


class LinearCapacitor(LinearElement):
    def __init__(
        self, value: str, start_node: str, end_node: str, symbol="F", element_tag="C"
    ):
        super().__init__(
            value=value,
            start_node=start_node,
            end_node=end_node,
            symbol=symbol,
            element_tag=element_tag,
        )


class VoltageSource(LinearElement):
    def __init__(
        self, value: str, start_node: str, end_node: str, symbol="v", element_tag="V"
    ):
        super().__init__(
            value=value,
            start_node=start_node,
            end_node=end_node,
            symbol=symbol,
            element_tag=element_tag,
        )


class CurrentSource(LinearElement):
    def __init__(
        self, value: str, start_node: str, end_node: str, symbol="A", element_tag="v"
    ):
        super().__init__(
            value=value,
            start_node=start_node,
            end_node=end_node,
            symbol=symbol,
            element_tag=element_tag,
        )


class ParallelElements(LinearElement):
    def __init__(self, elements: List[LinearElement]):
        super().__init__(
            value=None, start_node=None, end_node=None, symbol=None, element_tag=None,
        )


class SeriesElements(LinearElement):
    def __init__(self, elements: List[LinearElement]):
        super().__init__(
            value=None, start_node=None, end_node=None, symbol=None, element_tag=None,
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
