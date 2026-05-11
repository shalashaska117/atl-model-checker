"""
JSON loader for Concurrent Game Structures.

The loader makes the project usable as a small command-line tool: models can be
written as external JSON files instead of being hardcoded in Python examples.
"""

import json
from pathlib import Path

from model.game_structure import ConcurrentGameStructure


def load_cgs_from_json(path):
    """
    Load a Concurrent Game Structure from a JSON file.

    The "actions" field may either define global actions per agent:

        "actions": {
          "Controller": ["wait", "repair"],
          "Environment": ["calm", "disturb"]
        }

    or state-dependent actions:

        "actions": {
          "start": {
            "Controller": ["wait", "repair"],
            "Environment": ["calm", "disturb"]
          }
        }
    """
    data = json.loads(Path(path).read_text(encoding="utf-8"))

    model = ConcurrentGameStructure()

    for state in data["states"]:
        model.add_state(state, data.get("labels", {}).get(state, []))

    for agent in data["agents"]:
        model.add_agent(agent)

    _load_actions(model, data)
    _load_transitions(model, data)

    model.validate_totality()

    return model, data.get("initial")


def _load_actions(model, data):
    actions = data["actions"]

    if _uses_state_dependent_actions(actions):
        for state, per_agent_actions in actions.items():
            for agent, available_actions in per_agent_actions.items():
                model.set_actions(state, agent, available_actions)
        return

    for state in model.states:
        for agent, available_actions in actions.items():
            model.set_actions(state, agent, available_actions)


def _uses_state_dependent_actions(actions):
    if not actions:
        return False

    first_value = next(iter(actions.values()))
    return isinstance(first_value, dict)


def _load_transitions(model, data):
    for transition in data["transitions"]:
        model.add_transition(
            transition["from"],
            transition["joint_action"],
            transition["to"],
        )
