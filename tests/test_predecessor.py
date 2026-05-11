import unittest

from model.json_loader import load_cgs_from_json
from model_checker.atl_checker import ATLModelChecker


class TestStrategicPredecessor(unittest.TestCase):
    def setUp(self):
        model, _ = load_cgs_from_json("examples/controller_env.json")
        self.checker = ATLModelChecker(model)

    def test_controller_can_force_goal_from_start(self):
        result = self.checker._strategic_predecessor({"Controller"}, {"goal"})

        self.assertIn("start", result)
        self.assertIn("goal", result)
        self.assertNotIn("unstable", result)

    def test_environment_cannot_force_unsafe_from_start(self):
        unsafe_states = {"unstable"}
        result = self.checker._strategic_predecessor({"Environment"}, unsafe_states)

        self.assertNotIn("start", result)

    def test_environment_can_keep_goal_false_from_unstable(self):
        non_goal_states = {"start", "unstable"}
        result = self.checker._strategic_predecessor({"Environment"}, non_goal_states)

        self.assertIn("unstable", result)

    def test_grand_coalition_can_force_goal_from_start(self):
        result = self.checker._strategic_predecessor(
            {"Controller", "Environment"},
            {"goal"},
        )

        self.assertIn("start", result)

    def test_empty_coalition_requires_all_joint_actions_to_reach_target(self):
        result = self.checker._strategic_predecessor(set(), {"goal"})

        self.assertIn("goal", result)
        self.assertNotIn("start", result)
        self.assertNotIn("unstable", result)
