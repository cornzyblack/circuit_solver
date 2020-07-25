from typing import List, Optional, Union
from components import Resistor, LinearInductor, Loop, LinearCapacitor
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

    def __init__(self, file_path):
        self._is_parsed = True

        try:
            with open(file_path, "r") as f:
                self._netlist_lines = f.readlines()[1:-1]

            self.voltage_sources = [
                VoltageSource(
                    line.split(" ")[-1].strip(),
                    int(line.split(" ")[1].strip()),
                    int(line.split(" ")[2].strip()),
                )
                for line in self._netlist_lines
                if line[0].lower() == "v"
            ]
            self.current_sources = [
                CurrentSource(
                    line.split(" ")[-1].strip(),
                    int(line.split(" ")[1].strip()),
                    int(line.split(" ")[2].strip()),
                )
                for line in self._netlist_lines
                if line[0].lower() == "i"
            ]
            self.resistors = [
                Resistor(
                    line.split(" ")[-1].strip(),
                    int(line.split(" ")[1].strip()),
                    int(line.split(" ")[2].strip()),
                )
                for line in self._netlist_lines
                if line[0].lower() == "r"
            ]
            self.capacitors = [
                Capacitor(
                    line.split(" ")[-1].strip(),
                    int(line.split(" ")[1].strip()),
                    int(line.split(" ")[2].strip()),
                )
                for line in self._netlist_lines
                if line[0].lower() == "c"
            ]
            self.inductors = [
                Capacitor(
                    line.split(" ")[-1].strip(),
                    int(line.split(" ")[1].strip()),
                    int(line.split(" ")[2].strip()),
                )
                for line in self._netlist_lines
                if line[0].lower() == "l"
            ]

            self.elements = self.__get_branches()
            self.branches = self.elements

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

    def __get_loop(self):
        pass

    def __get_branches(self):
        """Get the total elements in the Netlist file

      Returns:
          List[LinearElement]: A list of the linear Elements discovered
      """
        return (
            self.current_sources
            + self.voltage_sources
            + self.inductors
            + self.capacitors
            + self.resistors
        )

    def get_sources(self):
        if self._netlist_lines:
            return self.voltage_sources + self.current_sources

    def get_voltage_source(self):
        return self.voltage_sources

    def get_current_source(self):
        return self.current_sources

    def get_parallel_nodes(self):
        nodes_count = len(self.__get_branches())
        element_nodes = [
            (element.start_node, element.end_node) for element in self.elements
        ]
        distinct_element_nodes = set(element_nodes)
        series_element_nodes = distinct_element_nodes

        counted_connected_nodes = Counter(element_nodes)
        parallel_element_nodes = [
            node for node, count in counted_connected_nodes.items() if count > 1
        ]
        print(f"{distinct_element_nodes=}")
        print(f"{series_element_nodes=}")
        print(f"{counted_connected_nodes=}")
        print(f"{parallel_element_nodes=}")

        return parallel_element_nodes
