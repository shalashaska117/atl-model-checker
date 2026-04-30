"""
This file contains unit tests for the ATL model checker.

The tests verify that the semantic components are coherent:

- atomic propositions;
- Boolean operators;
- strategic next;
- strategic eventually;
- strategic always;
- strategic until;
- parser integration.

The goal is not only to test code correctness, but also to show that the theoretical
ATL semantics is implemented consistently.
"""

import unittest

from examples.controller_env import build_controller_environment_model
from logic.ast import (
    Atom,
    Not,
    StrategicAlways,
    StrategicEventually,
    StrategicNext,
    StrategicUntil,
)
from logic.parser import parse_formula
from model_checker.atl_checker import ATLModelChecker


class TestATLModelChecker(unittest.TestCase):
    """
    Unit tests for the ATL model checker.
    """

    # Initializes the model and checker before each test.
    #
    # Input parameters:
    # - none.
    #
    # Return:
    # - nothing.
    def setUp(self):
        self.model = build_controller_environment_model()
        self.checker = ATLModelChecker(self.model)

    # Tests atomic proposition evaluation.
    #
    # Input parameters:
    # - none.
    #
    # Return:
    # - nothing.
    def test_atom_goal(self):
        formula = Atom("goal")

        self.assertEqual(self.checker.sat(formula), {"goal"})
        self.assertTrue(self.checker.check("goal", formula))
        self.assertFalse(self.checker.check("start", formula))

    # Tests negation evaluation.
    #
    # Input parameters:
    # - none.
    #
    # Return:
    # - nothing.
    def test_not_safe(self):
        formula = Not(Atom("safe"))

        self.assertEqual(self.checker.sat(formula), {"unstable"})

    # Tests strategic next.
    #
    # Input parameters:
    # - none.
    #
    # Return:
    # - nothing.
    def test_controller_can_force_goal_next_from_start(self):
        formula = StrategicNext({"Controller"}, Atom("goal"))

        self.assertTrue(self.checker.check("start", formula))
        self.assertFalse(self.checker.check("unstable", formula))

    # Tests strategic eventually.
    #
    # Input parameters:
    # - none.
    #
    # Return:
    # - nothing.
    def test_controller_can_eventually_force_goal(self):
        formula = StrategicEventually({"Controller"}, Atom("goal"))

        self.assertTrue(self.checker.check("start", formula))
        self.assertTrue(self.checker.check("goal", formula))
        self.assertFalse(self.checker.check("unstable", formula))

    # Tests that Environment cannot force unsafe from start.
    #
    # Input parameters:
    # - none.
    #
    # Return:
    # - nothing.
    def test_environment_cannot_force_unsafe_from_start(self):
        formula = StrategicEventually({"Environment"}, Not(Atom("safe")))

        self.assertFalse(self.checker.check("start", formula))
        self.assertTrue(self.checker.check("unstable", formula))

    # Tests strategic always.
    #
    # Input parameters:
    # - none.
    #
    # Return:
    # - nothing.
    def test_controller_can_keep_safe_from_start(self):
        formula = StrategicAlways({"Controller"}, Atom("safe"))

        self.assertTrue(self.checker.check("start", formula))
        self.assertTrue(self.checker.check("goal", formula))
        self.assertFalse(self.checker.check("unstable", formula))

    # Tests strategic until.
    #
    # Input parameters:
    # - none.
    #
    # Return:
    # - nothing.
    def test_controller_can_maintain_safe_until_goal(self):
        formula = StrategicUntil({"Controller"}, Atom("safe"), Atom("goal"))

        self.assertTrue(self.checker.check("start", formula))
        self.assertTrue(self.checker.check("goal", formula))
        self.assertFalse(self.checker.check("unstable", formula))

    # Tests parser integration with strategic eventually.
    #
    # Input parameters:
    # - none.
    #
    # Return:
    # - nothing.
    def test_parser_strategic_eventually(self):
        formula = parse_formula("<<Controller>> F goal")

        self.assertTrue(self.checker.check("start", formula))

    # Tests parser integration with strategic always.
    #
    # Input parameters:
    # - none.
    #
    # Return:
    # - nothing.
    def test_parser_strategic_always(self):
        formula = parse_formula("<<Controller>> G safe")

        self.assertTrue(self.checker.check("start", formula))

    # Tests parser integration with strategic until.
    #
    # Input parameters:
    # - none.
    #
    # Return:
    # - nothing.
    def test_parser_strategic_until(self):
        formula = parse_formula("<<Controller>> (safe U goal)")

        self.assertTrue(self.checker.check("start", formula))


if __name__ == "__main__":
    unittest.main()