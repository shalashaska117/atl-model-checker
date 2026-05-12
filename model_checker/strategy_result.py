"""
Structured result object for extracted ATL witness strategies.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class StrategyResult:
    """
    Result of strategy extraction for a strategic ATL formula.
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
        """
        return self.strategy[state]
