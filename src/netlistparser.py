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
import networkx as nx
import re
from pathlib import Path
from collections import Counter
from itertools import groupby
from functools import reduce
from operator import __or__, __add__


class Netlist(object):
    """ This is a netlist object that parses a Netlist file
    Parameters:
        components_dict (Dict): The dictionary containing the components
        explanatory_parts (Optional[Dict[str, List[str]]]): A dict of texts explaining the necessary steps of the current state

    Attributes:
        elements: the elements/components detected from the Netlist file
        voltage_sources: the voltage sources detected from the Netlist file
        current_sources: the current sources detected from the Netlist file
        resistors: the resistors detected from the Netlist file
        inductors: the inductors detected from the Netlist file
        capacitors: the capacitors detected from the Netlist file
    """

    def __init__(
        self,
        components_dict: Optional[dict],
        explanatory_parts: Optional[Dict[str, List[str]]] = [],
    ):
        self._is_parsed = True
        try:
            self._elements = components_dict
            self.branches = self._elements
            (
                self._floating_element_nodes,
                self._parallel_element_nodes,
            ) = self.get_element_connection_nodes()
            self.explanatory_parts = explanatory_parts
            self.is_reduced = False
        except Exception as e:
            self._is_parsed = False
            print(f"Issue parsing Netlist file")

    @classmethod
    def read_netlist_file(cls, file_path: Path):
        """ This is a netlist reader method that parses a Netlist file
        Parameters:
            file_path (Dict): The dictionary containing the components
        """
        if not (file_path):
            raise ErrorParsing()
        _elements = None
        try:
            _elements = {"v": [], "l": [], "r": [], "i": [], "c": []}

            with open(file_path, "r") as f:
                _netlist_lines = f.readlines()[1:-1]

            for line in _netlist_lines:
                element_symbol = line[0].lower()
                start_node = int(line.split(" ")[1].strip())
                end_node = int(line.split(" ")[2].strip())
                value = line.split(" ")[-1].strip()

                _elements.get(element_symbol).append(
                    Netlist.get_supported_elements(element_symbol=element_symbol)(
                        start_node=start_node, end_node=end_node, value=value
                    )
                )

        except Exception as e:
            print(f"Issue parsing Netlist {e}, file could be corrupt")

        return _elements

    @classmethod
    def load(cls, netlist_components: dict) -> Netlist:
        return Netlist(components_dict=netlist_components)

    @classmethod
    def parse(cls, file_path: Path) -> Netlist:
        """Loads and Parses a Netlist object

        Parameters:
          file_path (Path): The path of the file on the system
        Returns:
            Netlist: the object representation of the parsed Netlist file
        """
        _elements = cls.read_netlist_file(file_path)
        netlist_obj = None
        if _elements:
            netlist_obj = Netlist(_elements)
        return netlist_obj

    @classmethod
    def get_supported_elements(cls, element_symbol) -> LinearElement:
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
        if self._is_parsed:
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

    def get_combination_resistors(self):
        series_nodes, parallel_nodes = self.get_element_connection_nodes()

        parallel_resistors = {}
        series_resistors = []
        temp_floating_resistors = []

        floating_resistors = []

        for resistor in self._elements.get("r"):
            node = (resistor.start_node, resistor.end_node)
            if node in series_nodes:
                temp_floating_resistors.append(resistor)

            if node in parallel_nodes:
                if node in parallel_resistors:
                    parallel_resistors[node].append(resistor)
                else:
                    parallel_resistors[node] = [resistor]
        floating_resistors_edges = [
            (resistor.start_node, resistor.end_node)
            for resistor in temp_floating_resistors
        ]

        G = nx.from_edgelist(floating_resistors_edges)
        l = list(nx.connected_components(G))
        # print(l)

        series_nodes = set.union(*[set(), *filter(lambda x: len(x) > 2, l)])
        floating_nodes = set.union(*[set(), *filter(lambda x: len(x) <= 2, l)])

        for resistor in temp_floating_resistors:
            if resistor.start_node in series_nodes or resistor.end_node in series_nodes:
                series_resistors.append(resistor)
            if (
                resistor.start_node in floating_nodes
                or resistor.end_node in floating_nodes
            ):
                floating_resistors.append(resistor)

        series_resistors = sorted(
            series_resistors,
            key=lambda resistor: (
                resistor.start_node * abs(resistor.end_node - resistor.start_node)
            ),
            reverse=True,
        )
        return series_resistors, parallel_resistors, floating_resistors

    @classmethod
    def calculate_effective_resistance(cls, netlist_obj: Netlist):
        result = None

        if len(netlist_obj._elements.get("r")) == 1:
            result = netlist_obj

        else:
            (
                series_resistors,
                parallel_resistors,
                floating_resistors,
            ) = netlist_obj.get_combination_resistors()

            effective_resistance = []
            eq_series_resistor = None
            eq_parallel_resistor = None
            explanatory_parts = netlist_obj.explanatory_parts
            voltage_sources = netlist_obj.get_voltage_sources()
            current_sources = netlist_obj.get_current_sources()

            if parallel_resistors:
                for node in parallel_resistors:
                    eq_parallel_resistor = reduce(
                        lambda x, y: x | y, parallel_resistors[node]
                    )
                    effective_resistance.append(eq_parallel_resistor)

            if series_resistors:
                eq_series_resistor = reduce(lambda x, y: x + y, series_resistors)
                effective_resistance.append(eq_series_resistor)
            explanatory_parts.append(
                {
                    "series_resistors": series_resistors,
                    "parallel_resistors": parallel_resistors,
                    "series_accumulation": eq_series_resistor,
                    "parallel_accumulation": eq_parallel_resistor,
                }
            )
            effective_resistance.extend(floating_resistors)
            components = {
                "v": voltage_sources,
                "l": [],
                "r": effective_resistance,
                "i": current_sources,
                "c": [],
            }

            simplified_netlist = Netlist(
                components_dict=components, explanatory_parts=explanatory_parts
            )
            return Netlist.calculate_effective_resistance(simplified_netlist)
        return result

    def get_explanation(self):
        explanatory_text = ""
        series_explanation = ""
        parallel_explanation = ""
        reversed_explanation_part = self.explanatory_parts[::-1]

        for explanation_part in reversed_explanation_part:
            if explanation_part["series_resistors"]:
                series_explanation = " ".join(
                    map(
                        lambda resistor: f"{resistor.tag} ({resistor.value}{resistor.symbol})",
                        explanation_part["series_resistors"][::-1],
                    )
                )
                series_explanation_1 = " + ".join(
                    map(
                        lambda resistor: f" ({resistor.value}{resistor.symbol}) ",
                        explanation_part["series_resistors"][::-1],
                    )
                )
                series_accumulation = explanation_part["series_accumulation"]
                series_explanation = (
                    "\nThe following resistors are in Series: "
                    + series_explanation
                    + "\n( "
                    + series_explanation_1
                    + " ) "
                    + f" = {series_accumulation.value}{series_accumulation.symbol}"
                    + "\n"
                )

            if len(explanation_part["parallel_resistors"]) > 0:
                print(explanation_part["parallel_resistors"])
                par_r = reduce(
                    lambda x, y: x + y, explanation_part["parallel_resistors"].values(),
                )[::-1]

                parallel_explanation = " ".join(
                    map(
                        lambda resistor: f"{resistor.tag} ({resistor.value}{resistor.symbol})",
                        par_r,
                    )
                )
                parallel_explanation_1 = " + ".join(
                    map(
                        lambda resistor: f" 1/({resistor.value}{resistor.symbol}) ",
                        par_r,
                    )
                )
                parallel_accumulation = explanation_part["parallel_accumulation"]

                parallel_explanation = (
                    "\nThe following resistors are in Parallel: "
                    + parallel_explanation
                    + "\n1 /"
                    + "("
                    + parallel_explanation_1
                    + ")"
                    + f" = {parallel_accumulation.value}{parallel_accumulation.symbol}"
                    + "\n"
                )

        explanatory_text = series_explanation + parallel_explanation
        return explanatory_text

    def get_element_connection_nodes(self):
        """Returns a list of nodes in parallel, series found in the Netlist

        Returns:
            Optional[List]: A list of nodes in parallel
        """
        parallel_element_nodes = []
        floating_element_nodes = []

        try:
            element_nodes = [
                (element.start_node, element.end_node)
                for element in self.__get_branches()
            ]
            distinct_element_nodes = Counter(element_nodes)
            counted_connected_nodes = distinct_element_nodes

            for node, count in counted_connected_nodes.items():
                if count > 1:
                    parallel_element_nodes.append(node)
                else:
                    floating_element_nodes.append(node)

            self._floating_element_nodes = floating_element_nodes
            self._parallel_element_nodes = parallel_element_nodes

        except Exception as e:
            print(e)

        return (
            self._floating_element_nodes,
            self._parallel_element_nodes,
        )
