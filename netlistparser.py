from typing import List, Optional, Union
from .components import Resistor, LinearInductor, Loop, LinearCapacitor

class Netlist:
# Multiple dc sources
#  v1 1 0 dc 24
#  v2 3 0 dc 15
#  r1 1 2 10k
#  r2 2 3 8.1k
#  r3 2 0 4.7k .end

    def load_file(self, file_path: str):
        self.is_parsed = True
        try:
            with open(file_path, "r") as f:
                self.netlist = f.read()
        except:
            self.is_parsed = False
            print("Issue parsing Netlist")

        self.netlist_lines = self.netlist.split("\n")
        self.voltage_sources = [line.split(" ")[0] for line in self.net_list_lines if line[0].lower() == "v"]
        self.current_sources = [line.split(" ")[0] for line in self.net_list_lines if line[0].lower() == "i"]
        self.resistors = [components.reline.split(" ")[0]  for line in self.net_list_lines if line[0].lower() == "r"]
        self.capacitors = [line.split(" ")[0]  for line in self.net_list_lines if line[0].lower() == "c"]
        self.inductors = [line.split(" ")[0]  for line in self.net_list_lines if line[0].lower() == "l"]
        self.capacitors = [line.split(" ")[0]  for line in self.net_list_lines if line[0].lower() == "c"]


    def get_sources(self):
        if self.netlist_lines:
            return self.voltage_sources + self.current_sources

    def get_voltage_source(self):
        return self.voltage_sources

    def get_current_source(self):
        return self.current_sources
