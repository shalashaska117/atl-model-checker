"""
This file defines a small but meaningful ATL example: Controller vs Environment.

There are two agents:

- Controller:
  tries to reach the goal and keep the system safe.

- Environment:
  may disturb the system.

The example is designed to highlight the difference between possibility and strategy.

From state "start", reaching "goal" is not merely possible: Controller can force it
by choosing action "repair", regardless of whether Environment chooses "calm" or
"disturb".

This makes the formula:

    <<Controller>> F goal

true at "start".
"""

from model.game_structure import ConcurrentGameStructure


# Builds the controller-vs-environment concurrent game structure.
#
# Input parameters:
# - none.
#
# Return:
# - ConcurrentGameStructure instance.
def build_controller_environment_model():
    model = ConcurrentGameStructure()

    model.add_agent("Controller")
    model.add_agent("Environment")

    model.add_state("start", labels={"safe"})
    model.add_state("unstable", labels=set())
    model.add_state("goal", labels={"safe", "goal"})

    for state in model.states:
        model.set_actions(state, "Controller", {"wait", "repair"})
        model.set_actions(state, "Environment", {"calm", "disturb"})

    # From start:
    # Controller can force goal by choosing repair.
    model.add_transition(
        "start",
        {"Controller": "repair", "Environment": "calm"},
        "goal"
    )
    model.add_transition(
        "start",
        {"Controller": "repair", "Environment": "disturb"},
        "goal"
    )
    model.add_transition(
        "start",
        {"Controller": "wait", "Environment": "calm"},
        "start"
    )
    model.add_transition(
        "start",
        {"Controller": "wait", "Environment": "disturb"},
        "unstable"
    )

    # From unstable:
    # Controller cannot force immediate recovery if Environment keeps disturbing.
    model.add_transition(
        "unstable",
        {"Controller": "repair", "Environment": "calm"},
        "start"
    )
    model.add_transition(
        "unstable",
        {"Controller": "repair", "Environment": "disturb"},
        "unstable"
    )
    model.add_transition(
        "unstable",
        {"Controller": "wait", "Environment": "calm"},
        "unstable"
    )
    model.add_transition(
        "unstable",
        {"Controller": "wait", "Environment": "disturb"},
        "unstable"
    )

    # From goal:
    # The goal state is absorbing.
    model.add_transition(
        "goal",
        {"Controller": "repair", "Environment": "calm"},
        "goal"
    )
    model.add_transition(
        "goal",
        {"Controller": "repair", "Environment": "disturb"},
        "goal"
    )
    model.add_transition(
        "goal",
        {"Controller": "wait", "Environment": "calm"},
        "goal"
    )
    model.add_transition(
        "goal",
        {"Controller": "wait", "Environment": "disturb"},
        "goal"
    )

    model.validate_totality()
    return model