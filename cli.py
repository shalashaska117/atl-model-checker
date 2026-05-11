"""
Command-line interface for the ATL model checker.
"""

import argparse

from logic.parser import parse_formula
from model.json_loader import load_cgs_from_json
from model_checker.atl_checker import ATLModelChecker


def main():
    parser = argparse.ArgumentParser(
        description="Check ATL formulas over finite Concurrent Game Structures."
    )
    parser.add_argument("model", help="Path to a JSON Concurrent Game Structure.")
    parser.add_argument("formula", help="ATL formula to check.")
    parser.add_argument(
        "--state",
        help="State where the formula should be evaluated. Defaults to the JSON initial state.",
    )
    parser.add_argument(
        "--strategy",
        action="store_true",
        help="Print a witness strategy when the formula is strategic and satisfied.",
    )

    args = parser.parse_args()

    model, initial_state = load_cgs_from_json(args.model)
    selected_state = args.state or initial_state

    if selected_state is None:
        raise SystemExit(
            "No state selected. Provide --state or define 'initial' in the JSON model."
        )

    formula = parse_formula(args.formula)
    checker = ATLModelChecker(model)

    satisfying_states = checker.sat(formula)
    holds = selected_state in satisfying_states

    print(f"Formula: {args.formula}")
    print(f"Parsed formula: {formula}")
    print(f"Selected state: {selected_state}")
    print(f"Satisfying states: {sorted(satisfying_states)}")
    print(f"Holds in selected state: {holds}")

    if args.strategy:
        try:
            strategy = checker.extract_strategy(formula)
        except TypeError as error:
            print(f"Witness strategy: unavailable ({error})")
            return

        print("Witness strategy:")
        for state in sorted(strategy):
            action = strategy[state]
            if action is None:
                print(f"  {state}: objective already satisfied")
            else:
                print(f"  {state}: choose {action}")


if __name__ == "__main__":
    main()
