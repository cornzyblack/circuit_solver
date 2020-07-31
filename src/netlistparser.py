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
import re
from pathlib import Path
from collections import Counter


class Netlist(object):
    """ This is a netlist object that parses a Netlist file

    Attributes
        elements: the elements/components detected from the Netlist file
        voltag_sources: the voltage sources detected from the Netlist file
        current_sources: the current sources detected from the Netlist file
        resistors: the resistors detected from the Netlist file
        inductors: the inductors detected from the Netlist file
        capacitors: the capacitors detected from the Netlist file
    """

    def __init__(self, file_path: Path):
        self._is_parsed = True
        try:
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
            self.branches = self._elements

        except Exception as e:
            self._is_parsed = False
            print(f"Issue parsing Netlist {e}")

    @classmethod
    def load(cls, file_path: Path) -> Netlist:
        """Loads and Parses a Netlist object

        Parameters:
          file_path (Path): The path of the file on the system
        Returns:
            Netlist: the object representation of the parsed Netlist file
        """

        netlist_obj = Netlist(file_path)
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

    def get_sources(self):
        if self._netlist_lines:
            return self.get_voltage_source() + self.get_current_source()

    def get_voltage_source(self):
        return self._elements.get("v")

    def get_current_source(self):
        return self._elements.get("i")

    def get_parallel_nodes(self):
        element_nodes = [
            (element.start_node, element.end_node) for element in self.__get_branches()
        ]
        distinct_element_nodes = Counter(element_nodes)
        self._series_element_nodes = list(distinct_element_nodes.keys())

        counted_connected_nodes = distinct_element_nodes
        self._parallel_element_nodes = [
            node for node, count in counted_connected_nodes.items() if count > 1
        ]

        print(f"{distinct_element_nodes=}")
        print(f"{self._series_element_nodes=}")
        print(f"{counted_connected_nodes=}")
        print(f"{self._parallel_element_nodes=}")

        return self._parallel_element_nodes
