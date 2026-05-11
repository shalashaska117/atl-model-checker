import tempfile
import unittest
from pathlib import Path

from model.json_loader import load_cgs_from_json


class TestJsonLoader(unittest.TestCase):
    def test_load_controller_environment_model(self):
        model, initial = load_cgs_from_json("examples/controller_env.json")

        self.assertEqual(initial, "start")
        self.assertEqual(model.states, {"start", "unstable", "goal"})
        self.assertEqual(model.agents, {"Controller", "Environment"})
        self.assertTrue(model.is_total())
        self.assertEqual(model.get_labels("goal"), {"safe", "goal"})

    def test_loader_rejects_non_total_models(self):
        incomplete_model = """
        {
          "agents": ["A"],
          "states": ["s0", "s1"],
          "initial": "s0",
          "actions": {
            "A": ["go"]
          },
          "labels": {
            "s0": [],
            "s1": ["goal"]
          },
          "transitions": [
            {
              "from": "s0",
              "joint_action": {
                "A": "go"
              },
              "to": "s1"
            }
          ]
        }
        """

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "model.json"
            path.write_text(incomplete_model, encoding="utf-8")

            with self.assertRaises(ValueError):
                load_cgs_from_json(path)
