import json
import pytest
import errors
from components import Resistor


class TestResistorComponent:
    def create_resistor_1(self):
        resistor = Resistor("1.50", 1, 0)
        assert (
            resistor.start_node == 0
        ), "The credit flag for this transaction should be 0"
        assert (
            resistor.start_node == 1
        ), "The credit flag for this transaction should be 0"
