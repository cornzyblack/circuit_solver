from typing import List, Optional, Union
from components import Resistor, LinearInductor, Loop, LinearCapacitor
import re


class Netlist(object):
    # Multiple dc sources
    #  v1 1 0 dc 24
    #  v2 3 0 dc 15
    #  r1 1 2 10k
    #  r2 2 3 8.1k
    #  r3 2 0 4.7k .end
    def __init__(self, file_path):
        self.is_parsed = True

        try:
          with open(file_path, "r") as f:
              self.netlist_lines = f.readlines()

          self.elements = [line.strip().split(" ") for line in self.netlist_lines]

          self.voltage_sources = [
            line.strip().split(" ")[0] for line in self.netlist_lines if line[0].lower() == "v"
          ]
          self.current_sources = [
            line.strip().split(" ")[0] for line in self.netlist_lines if line[0].lower() == "i"
          ]
          self.resistors = [
            line.split(" ")[0]
            for line in self.netlist_lines
            if line[0].lower() == "r"
          ]
          self.capacitors = [
            line.split(" ")[0] for line in self.netlist_lines if line[0].lower() == "c"
          ]
          self.inductors = [
            line.split(" ")[0] for line in self.netlist_lines if line[0].lower() == "l"
          ]

        except Exception as e:
            self.is_parsed = False
            print(f"Issue parsing Netlist {e}")
    
    @classmethod
    def load(cls, file_path: str):
        obj = Netlist(file_path)
        return obj

    def __get_loop(self):
        pass

    def __get_branch(self):
        return self.inductors + self.capacitors + self.resistors

    def get_sources(self):
        if self.netlist_lines:
            return self.voltage_sources + self.current_sources

    def get_voltage_source(self):
        return self.voltage_sources

    def get_current_source(self):
        return self.current_sources
