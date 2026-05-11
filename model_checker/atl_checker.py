"""
This file implements a finite ATL model checker.

The checker evaluates ATL formulas over a Concurrent Game Structure.

The most important semantic operator is the strategic predecessor:

    Pre_A(X)

A state s belongs to Pre_A(X) iff coalition A has a joint action such that,
for every possible joint action of the other agents, the resulting successor state
belongs to X.

Formally:

    s in Pre_A(X)
    iff
    exists alpha_A such that for all alpha_not_A:
        delta(s, alpha_A union alpha_not_A) in X

This is the central distinction between CTL and ATL:

- CTL: path quantification.
- ATL: strategic quantification over coalitions.

The temporal operators are implemented through fixed points:

    <<A>> X phi       one-step strategic predecessor
    <<A>> F phi       least fixed point
    <<A>> G phi       greatest fixed point
    <<A>> (phi U psi) least fixed point

This file also implements a minimal form of strategy extraction.

When a strategic formula is true, the checker can return a witness strategy:
a mapping from states to coalition actions. This is useful because it shows not only
that a property is true, but also how the coalition can enforce it.
"""

from logic.ast import (
    And,
    Atom,
    BoolConstant,
    Implies,
    Not,
    Or,
    StrategicAlways,
    StrategicEventually,
    StrategicNext,
    StrategicUntil,
)


class ATLModelChecker:
    """
    Model checker for a finite fragment of ATL.
    """

    # Initializes the model checker.
    #
    # Input parameters:
    # - model: ConcurrentGameStructure instance.
    #
    # Return:
    # - nothing.
    def __init__(self, model):
        self.model = model
        self.model.validate_totality()

    # Evaluates a formula and returns all states satisfying it.
    #
    # Input parameters:
    # - formula: AST formula.
    #
    # Return:
    # - set of states satisfying the formula.
    def sat(self, formula):
        if isinstance(formula, BoolConstant):
            return self._sat_bool_constant(formula)

        if isinstance(formula, Atom):
            return self._sat_atom(formula)

        if isinstance(formula, Not):
            return self._sat_not(formula)

        if isinstance(formula, And):
            return self._sat_and(formula)

        if isinstance(formula, Or):
            return self._sat_or(formula)

        if isinstance(formula, Implies):
            return self._sat_implies(formula)

        if isinstance(formula, StrategicNext):
            return self._sat_strategic_next(formula)

        if isinstance(formula, StrategicEventually):
            return self._sat_strategic_eventually(formula)

        if isinstance(formula, StrategicAlways):
            return self._sat_strategic_always(formula)

        if isinstance(formula, StrategicUntil):
            return self._sat_strategic_until(formula)

        raise TypeError(f"Unsupported formula type: {type(formula)}")

    # Checks whether a specific state satisfies a formula.
    #
    # Input parameters:
    # - state: state to check.
    # - formula: formula to evaluate.
    #
    # Return:
    # - True if state satisfies formula, False otherwise.
    def check(self, state, formula):
        if state not in self.model.states:
            raise ValueError(f"Unknown state: {state}")

        return state in self.sat(formula)

    # Extracts a witness strategy for a strategic ATL formula.
    #
    # Input parameters:
    # - formula: StrategicNext, StrategicEventually, StrategicAlways, or StrategicUntil.
    #
    # Return:
    # - dictionary state -> coalition action, restricted to states satisfying the formula.
    #
    # Notes:
    # - For target states in eventually/until formulas, the value is None because no action
    #   is required: the objective is already satisfied.
    # - For non-strategic formulas, strategy extraction is not meaningful.
    def extract_strategy(self, formula):
        if isinstance(formula, StrategicNext):
            return self._extract_strategy_next(formula)

        if isinstance(formula, StrategicEventually):
            return self._extract_strategy_eventually(formula)

        if isinstance(formula, StrategicAlways):
            return self._extract_strategy_always(formula)

        if isinstance(formula, StrategicUntil):
            return self._extract_strategy_until(formula)

        raise TypeError(
            "Strategy extraction is only defined for strategic ATL formulas"
        )

    # Computes satisfaction set for TRUE or FALSE.
    #
    # Input parameters:
    # - formula: BoolConstant.
    #
    # Return:
    # - all states if TRUE, empty set if FALSE.
    def _sat_bool_constant(self, formula):
        if formula.value:
            return set(self.model.states)

        return set()

    # Computes satisfaction set for an atomic proposition.
    #
    # Input parameters:
    # - formula: Atom.
    #
    # Return:
    # - states where the atom is present in the labeling function.
    def _sat_atom(self, formula):
        result = set()

        for state in self.model.states:
            if formula.name in self.model.get_labels(state):
                result.add(state)

        return result

    # Computes satisfaction set for negation.
    #
    # Input parameters:
    # - formula: Not.
    #
    # Return:
    # - complement of the inner satisfaction set.
    def _sat_not(self, formula):
        inner_states = self.sat(formula.formula)

        # Since the model is finite, logical negation is implemented as set complement.
        return set(self.model.states) - inner_states

    # Computes satisfaction set for conjunction.
    #
    # Input parameters:
    # - formula: And.
    #
    # Return:
    # - intersection of the two satisfaction sets.
    def _sat_and(self, formula):
        left_states = self.sat(formula.left)
        right_states = self.sat(formula.right)

        return left_states & right_states

    # Computes satisfaction set for disjunction.
    #
    # Input parameters:
    # - formula: Or.
    #
    # Return:
    # - union of the two satisfaction sets.
    def _sat_or(self, formula):
        left_states = self.sat(formula.left)
        right_states = self.sat(formula.right)

        return left_states | right_states

    # Computes satisfaction set for implication.
    #
    # Input parameters:
    # - formula: Implies.
    #
    # Return:
    # - states satisfying not left or right.
    def _sat_implies(self, formula):
        left_states = self.sat(formula.left)
        right_states = self.sat(formula.right)

        # Classical implication phi -> psi is equivalent to not(phi) or psi.
        return (set(self.model.states) - left_states) | right_states

    # Computes satisfaction set for <<A>> X phi.
    #
    # Input parameters:
    # - formula: StrategicNext.
    #
    # Return:
    # - states from which coalition A can force phi in one step.
    def _sat_strategic_next(self, formula):
        target_states = self.sat(formula.formula)

        return self._strategic_predecessor(formula.coalition, target_states)

    # Computes satisfaction set for <<A>> F phi.
    #
    # Input parameters:
    # - formula: StrategicEventually.
    #
    # Return:
    # - states from which coalition A can force phi eventually.
    def _sat_strategic_eventually(self, formula):
        target_states = self.sat(formula.formula)

        # Least fixed point:
        # Initially, every state satisfying phi is already winning.
        winning_states = set(target_states)

        changed = True

        while changed:
            changed = False

            # Add states from which coalition A can force a transition
            # into the current winning region.
            predecessors = self._strategic_predecessor(
                formula.coalition, winning_states
            )

            new_winning_states = winning_states | predecessors

            if new_winning_states != winning_states:
                winning_states = new_winning_states
                changed = True

        return winning_states

    # Computes satisfaction set for <<A>> G phi.
    #
    # Input parameters:
    # - formula: StrategicAlways.
    #
    # Return:
    # - states from which coalition A can keep phi true forever.
    def _sat_strategic_always(self, formula):
        invariant_states = self.sat(formula.formula)

        # Greatest fixed point:
        # Start from all states where phi holds.
        # Remove states from which coalition A cannot force the next state
        # to remain in the current candidate winning region.
        winning_states = set(invariant_states)

        changed = True

        while changed:
            changed = False

            predecessors = self._strategic_predecessor(
                formula.coalition, winning_states
            )

            new_winning_states = invariant_states & predecessors

            if new_winning_states != winning_states:
                winning_states = new_winning_states
                changed = True

        return winning_states

    # Computes satisfaction set for <<A>> (phi U psi).
    #
    # Input parameters:
    # - formula: StrategicUntil.
    #
    # Return:
    # - states from which coalition A can force psi eventually while maintaining phi.
    def _sat_strategic_until(self, formula):
        left_states = self.sat(formula.left)
        right_states = self.sat(formula.right)

        # Least fixed point:
        # psi states are immediately winning.
        # Other states are winning only if phi holds and coalition A can force
        # the game into the current winning region.
        winning_states = set(right_states)

        changed = True

        while changed:
            changed = False

            predecessors = self._strategic_predecessor(
                formula.coalition, winning_states
            )

            new_winning_states = winning_states | (left_states & predecessors)

            if new_winning_states != winning_states:
                winning_states = new_winning_states
                changed = True

        return winning_states

    # Extracts a witness strategy for <<A>> X phi.
    #
    # Input parameters:
    # - formula: StrategicNext.
    #
    # Return:
    # - dictionary state -> coalition action.
    def _extract_strategy_next(self, formula):
        target_states = self.sat(formula.formula)
        satisfying_states = self._sat_strategic_next(formula)

        strategy = {}

        for state in satisfying_states:
            action = self.get_winning_action(state, formula.coalition, target_states)
            strategy[state] = action

        return strategy

    # Extracts a witness strategy for <<A>> F phi.
    #
    # Input parameters:
    # - formula: StrategicEventually.
    #
    # Return:
    # - dictionary state -> coalition action or None for target states.
    def _extract_strategy_eventually(self, formula):
        target_states = self.sat(formula.formula)

        # Target states need no action: the eventual objective is already satisfied.
        winning_states = set(target_states)
        strategy = {state: None for state in target_states}

        changed = True

        while changed:
            changed = False

            for state in sorted(self.model.states):
                if state in winning_states:
                    continue

                action = self.get_winning_action(
                    state, formula.coalition, winning_states
                )

                if action is not None:
                    winning_states.add(state)
                    strategy[state] = action
                    changed = True

        return strategy

    # Extracts a witness strategy for <<A>> G phi.
    #
    # Input parameters:
    # - formula: StrategicAlways.
    #
    # Return:
    # - dictionary state -> coalition action.
    def _extract_strategy_always(self, formula):
        winning_states = self._sat_strategic_always(formula)
        strategy = {}

        # Once the greatest fixed point is computed, every winning state must have
        # a coalition action that keeps the game inside the winning region.
        for state in sorted(winning_states):
            action = self.get_winning_action(state, formula.coalition, winning_states)
            strategy[state] = action

        return strategy

    # Extracts a witness strategy for <<A>> (phi U psi).
    #
    # Input parameters:
    # - formula: StrategicUntil.
    #
    # Return:
    # - dictionary state -> coalition action or None for target states.
    def _extract_strategy_until(self, formula):
        left_states = self.sat(formula.left)
        right_states = self.sat(formula.right)

        # States satisfying psi already satisfy the until objective.
        winning_states = set(right_states)
        strategy = {state: None for state in right_states}

        changed = True

        while changed:
            changed = False

            for state in sorted(self.model.states):
                if state in winning_states:
                    continue

                # For an until formula, the state can be added only if phi holds now.
                if state not in left_states:
                    continue

                action = self.get_winning_action(
                    state, formula.coalition, winning_states
                )

                if action is not None:
                    winning_states.add(state)
                    strategy[state] = action
                    changed = True

        return strategy

    # Computes the ATL strategic predecessor Pre_A(X).
    #
    # Input parameters:
    # - coalition: set of agents.
    # - target_states: set X of desired successor states.
    #
    # Return:
    # - states from which coalition can force the next state into X.
    def _strategic_predecessor(self, coalition, target_states):
        self._validate_coalition(coalition)

        result = set()

        for state in self.model.states:
            if self._coalition_can_force(state, coalition, target_states):
                result.add(state)

        return result

    # Checks whether coalition A can force the next state into a target set.
    #
    # Input parameters:
    # - state: current state.
    # - coalition: set of agents acting as the strategic coalition.
    # - target_states: set of desired successor states.
    #
    # Return:
    # - True if the coalition has a one-step forcing action, False otherwise.
    def _coalition_can_force(self, state, coalition, target_states):
        action = self.get_winning_action(state, coalition, target_states)

        return action is not None

    # Returns one winning one-step action for a coalition, if it exists.
    #
    # Input parameters:
    # - state: current state.
    # - coalition: selected coalition.
    # - target_states: set of desired successor states.
    #
    # Return:
    # - a dictionary agent -> action if a forcing action exists, otherwise None.
    def get_winning_action(self, state, coalition, target_states):
        self._validate_coalition(coalition)

        if state not in self.model.states:
            raise ValueError(f"Unknown state: {state}")

        coalition = set(coalition)
        opponents = self.model.agents - coalition

        coalition_joint_actions = self.model.get_joint_actions(state, coalition)
        opponent_joint_actions = self.model.get_joint_actions(state, opponents)

        # ATL has an existential-universal structure:
        #
        # exists action of the coalition
        # such that
        # for all actions of the opponents
        # the successor is in the target set.
        for coalition_action in coalition_joint_actions:
            action_is_winning = True

            for opponent_action in opponent_joint_actions:
                complete_joint_action = self.model.merge_joint_actions(
                    coalition_action, opponent_action
                )

                next_state = self.model.get_next_state(state, complete_joint_action)

                if next_state not in target_states:
                    action_is_winning = False
                    break

            if action_is_winning:
                return coalition_action

        return None

    # Validates that a coalition contains only known agents.
    #
    # Input parameters:
    # - coalition: set of agent names.
    #
    # Return:
    # - nothing.
    def _validate_coalition(self, coalition):
        unknown_agents = set(coalition) - self.model.agents

        if unknown_agents:
            raise ValueError(f"Unknown agents in coalition: {unknown_agents}")
