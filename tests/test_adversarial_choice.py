import unittest

from logic.parser import parse_formula
from model.json_loader import load_cgs_from_json
from model_checker.atl_checker import ATLModelChecker


class TestAdversarialChoiceExample(unittest.TestCase):
    def setUp(self):
        model, _ = load_cgs_from_json("examples/adversarial_choice.json")
        self.checker = ATLModelChecker(model)

    def test_controller_cannot_force_goal(self):
        formula = parse_formula("<<Controller>> F goal")

        self.assertFalse(self.checker.check("start", formula))

    def test_controller_can_keep_safe_by_avoiding_risk(self):
        formula = parse_formula("<<Controller>> G safe")

        self.assertTrue(self.checker.check("start", formula))

    def test_goal_is_reachable_but_not_forceable_in_one_step(self):
        formula = parse_formula("<<Controller>> X goal")

        self.assertFalse(self.checker.check("start", formula))

    def test_environment_cannot_force_bad_from_start(self):
        formula = parse_formula("<<Environment>> F bad")

        self.assertFalse(self.checker.check("start", formula))


if __name__ == "__main__":
    unittest.main()
