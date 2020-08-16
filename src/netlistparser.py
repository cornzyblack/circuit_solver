from __future__ import annotations
from typing import List, Optional, Union
from src.components import (
    Resistor,
    LinearInductor,
    Loop,
    LinearCapacitor,
    LinearElement,
    VoltageSource,
    CurrentSource,
)
from src.errors import ErrorParsing
import re
from pathlib import Path
from collections import Counter
from itertools import accumulate
from operator import __or__, __add__


class Netlist(object):
    """ This is a netlist object that parses a Netlist file
    Parameters:
        file_path (Path): The path of the file on the system
        components_dict (Dict): The dictionary containing the components

    Attributes:
        elements: the elements/components detected from the Netlist file
        voltage_sources: the voltage sources detected from the Netlist file
        current_sources: the current sources detected from the Netlist file
        resistors: the resistors detected from the Netlist file
        inductors: the inductors detected from the Netlist file
        capacitors: the capacitors detected from the Netlist file
    """

    def __init__(self, file_path: Optional[Path] = None, components_dict : Optional[dict] = None):
        self._is_parsed = True
        try:
            if not (file_path or components_dict):
                raise ErrorParsing()

            if file_path:
                with open(file_path, "r") as f:
                    self._netlist_lines = f.readlines()[1:-1]

                self._elements = {"v": [], "l": [], "r": [], "i": [], "c": []}

                for line in self._netlist_lines:
                    element_symbol = line[0].lower()
                    start_node = int(line.split(" ")[1].strip())
                    end_node = int(line.split(" ")[2].strip())
                    value = line.split(" ")[-1].strip()

                    self._elements.get(element_symbol).append(
                        self.__supported_elements(element_symbol=element_symbol)(
                            start_node=start_node, end_node=end_node, value=value
                        )
                    )

            elif components_dict:
                self._elements = components_dict


            self.branches = self._elements
            self.parallel_nodes = self.get_parallel_nodes()

        except Exception as e:
            self._is_parsed = False
            print(f"Issue parsing Netlist {e}, file could be corrupt")

    @classmethod
    def load(cls, netlist_components: dict) -> Netlist:
        return Netlist(components_dict = netlist_components)

    @classmethod
    def parse(cls, file_path: Path) -> Netlist:
        """Loads and Parses a Netlist object

        Parameters:
          file_path (Path): The path of the file on the system
        Returns:
            Netlist: the object representation of the parsed Netlist file
        """

        netlist_obj = Netlist(file_path=file_path)
        return netlist_obj

    def __supported_elements(self, element_symbol) -> LinearElement:
        """Returns the currently supported elements

        Parameters:
          element_symbol (str): The symbol of the element
          value (str): The value of the element
          start_node (str): The start node of the element
          end_node (str): The end node of the element
          value (str): The voltage through the element
          current (str): The current through the element

        Returns:
            LinearElement: the linear element representation
        """
        elements = {
            "v": VoltageSource,
            "c": LinearCapacitor,
            "i": CurrentSource,
            "r": Resistor,
            "l": LinearInductor,
        }
        return elements.get(element_symbol)

    def __get_loop(self):
        pass

    def __get_branches(self):
        """Get the total elements in the Netlist file

      Returns:
          List[LinearElement]: A list of the linear Elements discovered
      """
        return (
            self._elements.get("i")
            + self._elements.get("v")
            + self._elements.get("r")
            + self._elements.get("c")
            + self._elements.get("l")
        )

    def get_sources(self) -> List:
        """Returns the current sources and voltage sources found in the Netlist

        Returns:
            Optional[List]: A list of current and voltage sources
        """
        if self._netlist_lines:
            return self.get_voltage_sources() + self.get_current_sources()

    def get_voltage_sources(self):
        """Returns a list of voltage sources found in the Netlist

        Returns:
            Optional[List]: A list of voltage sources
        """

        return self._elements.get("v")

    def get_current_sources(self):
        """Returns a list of current sources found in the Netlist

        Returns:
            Optional[List]: A list of current sources
        """
        return self._elements.get("i")

    def get_series_resistors(self):
        self._elements.get("r")

    def get_parallel_resistors(self):
        self._elements.get("r")

    @staticmethod
    def calculate_recursive(resistor_list):
        # if len(resistor_list) != 1:
        pass

    def calculate_effective_resistance(self, explain: bool = False):
        parallel_resistors = self.get_parallel_resistors()
        series_resistors = self.get_series_resistors()

        effective_resistance = []
        eq_series_resistor = None
        eq_parallel_resistor = None
        explanation_text = ""

        if series_resistors:
            eq_series_resistor = accumulate(series_resistors)
            effective_resistance.append(eq_series_resistor[-1])
        if parallel_resistors:
            eq_parallel_resistor = accumulate(parallel_resistors, func=__or__)
            effective_resistance.append(eq_parallel_resistor[-1])

        if explain:
            pass

        return {
            "effective_resistance": sum(effective_resistance),
            "effective_series_resistors": eq_series_resistor,
            "effective_parallel_resistors": eq_parallel_resistor,
            "effective_netlist_obj":
        }

    def get_parallel_nodes(self):
        """Returns a list of nodes in parallel found in the Netlist

        Returns:
            Optional[List]: A list of nodes in parallel
        """
        element_nodes = [
            (element.start_node, element.end_node) for element in self.__get_branches()
        ]
        distinct_element_nodes = Counter(element_nodes)
        self._series_element_nodes = list(distinct_element_nodes.keys())

        counted_connected_nodes = distinct_element_nodes
        self._parallel_element_nodes = [
            node for node, count in counted_connected_nodes.items() if count > 1
        ]

        return self._parallel_element_nodes
