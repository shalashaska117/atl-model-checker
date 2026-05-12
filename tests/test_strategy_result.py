import unittest

from logic.parser import parse_formula
from model.json_loader import load_cgs_from_json
from model_checker.atl_checker import ATLModelChecker
from model_checker.strategy_result import StrategyResult


class TestStrategyResult(unittest.TestCase):
    def setUp(self):
        model, _ = load_cgs_from_json("examples/controller_env.json")
        self.checker = ATLModelChecker(model)

    def test_extract_strategy_result_returns_structured_object(self):
        formula = parse_formula("<<Controller>> F goal")

        result = self.checker.extract_strategy_result(formula)

        self.assertIsInstance(result, StrategyResult)
        self.assertEqual(result.coalition, frozenset({"Controller"}))
        self.assertTrue(result.holds_in("start"))
        self.assertTrue(result.holds_in("goal"))
        self.assertFalse(result.holds_in("unstable"))

    def test_strategy_result_contains_winning_action(self):
        formula = parse_formula("<<Controller>> F goal")

        result = self.checker.extract_strategy_result(formula)

        self.assertTrue(result.has_action_for("start"))
        self.assertEqual(result.action_for("start"), {"Controller": "repair"})
        self.assertIsNone(result.action_for("goal"))

    def test_strategy_result_rejects_non_strategic_formula(self):
        formula = parse_formula("goal")

        with self.assertRaises(TypeError):
            self.checker.extract_strategy_result(formula)


if __name__ == "__main__":
    unittest.main()
