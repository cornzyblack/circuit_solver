from __future__ import annotations
from __future__ import division
from numbers import Number
from typing import List, Union
from src import errors
import re
import numpy as np
from itertools import accumulate

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


def convert_value(value: Union[str, float]) -> Union[float, int]:
    """This converts a string value into a float equivalent

    Args:
        value Union[str, float]: The value of the equivalent element together with its prefix

    Returns:
        Union[float, int]: The converted value of the object
    """
    prefix_value = None
    if not isinstance(value, Number):
        try:
            value = re.sub(r"[,\s]+", "", value.strip())
            prefix_match = re.search(r"([pnµkMGTYZEPmhdadcfayz]{1})", value)
            prefix_value = prefix_match.group(1) if prefix_match else 1
            value = float(
                re.search(r"([\d]+\.*\d*)", value).group(1)
            ) * PREFIX_LIST.get(prefix_value, 1)
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
        print(
            f"This is a wire that connects node {self.start_node} and {self.end_node}"
        )

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
        voltage: the voltage across the element
        current: the current through the element
    """

    def __init__(
        self,
        value: Union[str, float],
        start_node: int,
        end_node: int,
        symbol: str,
        element_tag: str,
        voltage: Optional[float] = None,
        current: Optional[float] = None,
    ):
        """ Initializes the Linearelement """
        if start_node == end_node:
            raise errors.SameNodeError()

        self.start_node, self.end_node = sorted((int(start_node), int(end_node)))
        self.tag = element_tag + "_" + str(self.start_node) + str(self.end_node)
        self.prefix = None
        self.voltage = voltage
        self.current = current
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
        self,
        value: str,
        start_node: int,
        end_node: int,
        symbol="Ω",
        element_tag="R",
        voltage=None,
        current=None,
    ):
        super().__init__(
            value=value,
            start_node=start_node,
            end_node=end_node,
            symbol=symbol,
            element_tag=element_tag,
            voltage=voltage,
            current=current,
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
        if not (
            abs(self.end_node - self.start_node)
            == abs(series_resistor.end_node - series_resistor.start_node)
        ):
            raise errors.NotInSeries(self.tag, series_resistor.tag)

        equivalent_resistance_value = self.value + series_resistor.value
        equivalent_voltage = None
        equivalent_current = self.current if self.voltage else series_resistor.current
        return Resistor(
            value=equivalent_resistance_value,
            start_node=self.start_node,
            end_node=series_resistor.start_node,
            voltage=equivalent_voltage,
            current=equivalent_current,
        )

    def __truediv__(self, parallel_resistor: Resistor) -> Resistor:
        """
        Args:
            parallel_resistor (Resistor): The resistor in Parallel

        Returns:
            Resistor: A resistor with the equivalent Resistance of the combined
            parallel resistors
        """

        if (self.start_node != parallel_resistor.start_node) or (
            self.end_node != parallel_resistor.end_node
        ):
            raise errors.NotInParallel(self.tag, parallel_resistor.tag)

        equivalent_resistance_value = 1 / (
            (1 / self.value) + (1 / parallel_resistor.value)
        )
        equivalent_voltage = self.voltage if self.voltage else parallel_resistor.voltage
        equivalent_current = None
        return Resistor(
            value=equivalent_resistance_value,
            start_node=self.start_node,
            end_node=self.end_node,
            voltage=equivalent_voltage,
            current=equivalent_current,
        )

    def __floordiv__(self, parallel_resistor: Resistor) -> Resistor:
        return self.__truediv__(parallel_resistor)

    def __radd__(self, other_resistor):
        if other_resistor == 0:
            return self
        else:
            return self.__add__(other_resistor)


class LinearInductor(LinearElement):
    def __init__(
        self,
        value: str,
        start_node: int,
        end_node: int,
        symbol="H",
        element_tag="L",
        voltage=None,
        current=None,
    ):
        super().__init__(
            value=value,
            start_node=start_node,
            end_node=end_node,
            symbol=symbol,
            element_tag=element_tag,
            voltage=voltage,
            current=current,
        )


class LinearCapacitor(LinearElement):
    def __init__(
        self,
        value: str,
        start_node: int,
        end_node: int,
        symbol="F",
        element_tag="C",
        voltage=None,
        current=None,
    ):
        super().__init__(
            value=value,
            start_node=start_node,
            end_node=end_node,
            symbol=symbol,
            element_tag=element_tag,
            voltage=voltage,
            current=current,
        )


class VoltageSource(LinearElement):
    def __init__(
        self,
        value: str,
        start_node: int,
        end_node: int,
        symbol="v",
        element_tag="V",
        voltage=None,
        current=None,
    ):
        super().__init__(
            value=value,
            start_node=start_node,
            end_node=end_node,
            symbol=symbol,
            element_tag=element_tag,
            voltage=None,
            current=None,
        )


class CurrentSource(LinearElement):
    def __init__(
        self,
        value: str,
        start_node: int,
        end_node: int,
        symbol="A",
        element_tag="v",
        voltage=None,
        current=None,
    ):
        super().__init__(
            value=value,
            start_node=start_node,
            end_node=end_node,
            symbol=symbol,
            element_tag=element_tag,
            voltage=None,
            current=None,
        )


class SeriesResistors(Resistor):
    def __init__(self, elements: List[LinearElement]):
        self.elements = elements
        self.voltage = None
        self.current = None
        self.value = list(self.solve_series(elements))

    @classmethod
    def solve_series(cls, resistors: List[Resistor]) -> Resistor:
        """
        This calculates the equivalent resistance step by step of a List of Resistors in Series
        Args:
            resistors (List[Resistor]): A list of resistors

        Returns:
            Resistor: Returns a resistor with the equivalent combined resistance
        """
        equivalent_resistance = accumulate(
            resistors, lambda resistor_0, resistor_1: resistor_0 + resistor_1
        )
        return equivalent_resistance


class ParallelResistors(Resistor):
    def __init__(self, elements: List[LinearElement]):
        self.elements = elements
        self.voltage = None
        self.current = None
        self.value = list(self.solve_parallel(elements))

    @classmethod
    def solve_parallel(cls, resistors: List[Resistor]) -> Resistor:
        """
        This calculates the equivalent resistance step by step of a List of Resistors in Parallel
        Args:
            resistors (List[Resistor]): A list of resistors

        Returns:
            Resistor: Returns a resistor with the equivalent combined resistance
        """
        equivalent_resistance = accumulate(
            resistors, lambda resistor_0, resistor_1: resistor_0 / resistor_1
        )

        return equivalent_resistance


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
