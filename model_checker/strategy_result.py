"""
Structured result object for extracted ATL witness strategies.

A StrategyResult makes strategy extraction easier to inspect, test, and expose
through the command-line interface.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class StrategyResult:
    """
    Result of strategy extraction for a strategic ATL formula.

    Attributes:
        formula: The ATL formula for which the strategy was extracted.
        coalition: The coalition responsible for enforcing the formula.
        satisfying_states: States satisfying the formula.
        strategy: Mapping from states to coalition actions.
                  A value of None means that the objective is already satisfied
                  in that state and no action is required.
    """

    formula: object
    coalition: frozenset
    satisfying_states: frozenset
    strategy: dict

    def holds_in(self, state):
        """
        Return True if the formula holds in the given state.
        """
        return state in self.satisfying_states

    def has_action_for(self, state):
        """
        Return True if the strategy provides an actual action for the state.
        """
        return state in self.strategy and self.strategy[state] is not None

    def action_for(self, state):
        """
        Return the coalition action associated with a state.

        Returns None when the objective is already satisfied in that state.
        Raises KeyError if the state is not part of the extracted strategy.
        """
        return self.strategy[state]
