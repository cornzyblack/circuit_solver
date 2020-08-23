import json
import pytest

from src.components import Resistor
from src import errors


class TestResistorComponent:
    def test_create_resistor_1(self):
        resistor = Resistor("1.50", 1, 0)
        assert resistor.start_node == 1, "The start node for this resistor should be 0"
        assert resistor.end_node == 0, "The end node for this resistor should be 0"

    def test_create_resistor_2(self):
        resistor = Resistor("1.50", 0, 1)
        assert resistor.start_node == 0, "The start node for this resistor should be 1"
        assert resistor.end_node == 1, "The end node for this resistor should be 0"

    def test_get_resistor_value_1(self):
        resistor = Resistor("1.50k", 1, 0)
        assert resistor.value == 1500, "The resistance value should be 1,500"

    def test_get_resistor_value_2(self):
        resistor = Resistor("10.5µ", 2, 0)
        assert resistor.value == 0.0000105, "The resistance value should be 0.0000105"

    def test_get_resistor_value_3(self):
        resistor = Resistor("10.5exit", 5, 4)
        assert resistor.value == 10.5, "The resistance value should be 10.5"

    def test_get_resistor_value_4(self):
        resistor = Resistor("10.5Ω", 5, 4)
        assert resistor.tag == "R_45", "The tag for this resistor should be R_045"

    def test_conductance(self):
        resistor = Resistor("2Ω", 5, 4)
        assert resistor.get_conductance() == 0.5, "The conductance value should be 0.5"

    def test_resistors_in_parallel(self):
        pass

    def test_resistors_in_series(self):
        pass
