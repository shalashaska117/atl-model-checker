"""
This file runs a complete demonstration of the ATL model checker.

The demo verifies several strategic properties over a small open system.

The important formulas are:

    <<Controller>> X goal
    <<Controller>> F goal
    <<Controller>> G safe
    <<Controller>> (safe U goal)
    <<Environment>> F !safe
    <<Environment>> G !goal

These formulas demonstrate that ATL is not just CTL with different notation.
ATL asks whether a coalition has a strategy against all possible choices of the
remaining agents.

The demo also prints witness strategies for strategic formulas. This is important
because it shows the constructive side of ATL model checking: when a coalition can
force a property, the tool can show one possible symbolic strategy.
"""

from examples.controller_env import build_controller_environment_model
from logic.parser import parse_formula
from model_checker.atl_checker import ATLModelChecker


# Prints a strategy returned by the ATL model checker.
#
# Input parameters:
# - strategy: dictionary state -> coalition action.
#
# Return:
# - nothing.
def print_strategy(strategy):
    if not strategy:
        print("Strategy: no winning strategy found")
        return

    print("Strategy:")

    for state in sorted(strategy.keys()):
        action = strategy[state]

        if action is None:
            print(f"- {state}: objective already satisfied")
        else:
            print(f"- {state}: choose {action}")


# Prints the result of checking a formula over all states.
#
# Input parameters:
# - checker: ATLModelChecker instance.
# - formula_text: formula written as a string.
# - show_strategy: whether to print a witness strategy.
#
# Return:
# - nothing.
def print_check_result(checker, formula_text, show_strategy=True):
    formula = parse_formula(formula_text)
    satisfying_states = checker.sat(formula)

    print(f"Formula: {formula_text}")
    print(f"Parsed : {formula}")
    print(f"States : {satisfying_states}")
    print(f"start  : {checker.check('start', formula)}")

    if show_strategy:
        try:
            strategy = checker.extract_strategy(formula)
            print_strategy(strategy)
        except TypeError:
            print("Strategy: not applicable to non-strategic formula")

    print()


# Prints a non-strategic Boolean query with a small explanatory title.
#
# Input parameters:
# - checker: ATLModelChecker instance.
# - title: title shown before the formula.
# - formula_text: formula written as a string.
#
# Return:
# - nothing.
def print_boolean_result(checker, title, formula_text):
    print(title)
    print("-" * len(title))

    formula = parse_formula(formula_text)
    satisfying_states = checker.sat(formula)

    print(f"Formula: {formula_text}")
    print(f"Parsed : {formula}")
    print(f"States : {satisfying_states}")
    print(f"start  : {checker.check('start', formula)}")
    print()


# Runs the project demo.
#
# Input parameters:
# - none.
#
# Return:
# - nothing.
def main():
    model = build_controller_environment_model()
    checker = ATLModelChecker(model)

    print("ATL Model Checker Demo")
    print("======================")
    print()

    print("States:")
    for state in sorted(model.states):
        print(f"- {state}: labels = {model.get_labels(state)}")

    print()

    print("Agents:")
    for agent in sorted(model.agents):
        print(f"- {agent}")

    print()

    print("Strategic verification results")
    print("------------------------------")
    print()

    print_check_result(checker, "<<Controller>> X goal")
    print_check_result(checker, "<<Controller>> F goal")
    print_check_result(checker, "<<Controller>> G safe")
    print_check_result(checker, "<<Controller>> (safe U goal)")
    print_check_result(checker, "<<Environment>> F !safe")
    print_check_result(checker, "<<Environment>> G !goal")

    print_boolean_result(
        checker,
        "Safe states from which Controller can force goal",
        "safe & <<Controller>> F goal"
    )


if __name__ == "__main__":
    main()