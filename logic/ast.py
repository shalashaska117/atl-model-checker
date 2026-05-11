"""
This file defines the Abstract Syntax Tree for a small but formal ATL fragment.

The implemented fragment contains:

- Boolean constants: TRUE and FALSE;
- atomic propositions;
- Boolean connectives: NOT, AND, OR, IMPLIES;
- strategic temporal operators:
    <<A>> X phi
    <<A>> F phi
    <<A>> G phi
    <<A>> (phi U psi)

The purpose of this file is only to represent formulas structurally.
The semantics is implemented in model_checker/atl_checker.py.
"""


class Formula:
    """
    Base class for all formulas.
    """

    pass


class BoolConstant(Formula):
    """
    Boolean constant.

    TRUE is satisfied in every state.
    FALSE is satisfied in no state.
    """

    # Creates a Boolean constant.
    #
    # Input parameters:
    # - value: True or False.
    #
    # Return:
    # - nothing.
    def __init__(self, value):
        self.value = bool(value)

    # Returns a readable representation of the formula.
    #
    # Input parameters:
    # - none.
    #
    # Return:
    # - string representation.
    def __repr__(self):
        return "TRUE" if self.value else "FALSE"


class Atom(Formula):
    """
    Atomic proposition.

    Example:
    Atom("safe") represents the proposition safe.
    """

    # Creates an atomic proposition.
    #
    # Input parameters:
    # - name: proposition name.
    #
    # Return:
    # - nothing.
    def __init__(self, name):
        self.name = name

    # Returns a readable representation of the formula.
    #
    # Input parameters:
    # - none.
    #
    # Return:
    # - string representation.
    def __repr__(self):
        return self.name


class Not(Formula):
    """
    Logical negation.
    """

    # Creates a negated formula.
    #
    # Input parameters:
    # - formula: formula to negate.
    #
    # Return:
    # - nothing.
    def __init__(self, formula):
        self.formula = formula

    # Returns a readable representation of the formula.
    #
    # Input parameters:
    # - none.
    #
    # Return:
    # - string representation.
    def __repr__(self):
        return f"!({self.formula})"


class And(Formula):
    """
    Logical conjunction.
    """

    # Creates a conjunction.
    #
    # Input parameters:
    # - left: left subformula.
    # - right: right subformula.
    #
    # Return:
    # - nothing.
    def __init__(self, left, right):
        self.left = left
        self.right = right

    # Returns a readable representation of the formula.
    #
    # Input parameters:
    # - none.
    #
    # Return:
    # - string representation.
    def __repr__(self):
        return f"({self.left} AND {self.right})"


class Or(Formula):
    """
    Logical disjunction.
    """

    # Creates a disjunction.
    #
    # Input parameters:
    # - left: left subformula.
    # - right: right subformula.
    #
    # Return:
    # - nothing.
    def __init__(self, left, right):
        self.left = left
        self.right = right

    # Returns a readable representation of the formula.
    #
    # Input parameters:
    # - none.
    #
    # Return:
    # - string representation.
    def __repr__(self):
        return f"({self.left} OR {self.right})"


class Implies(Formula):
    """
    Logical implication.
    """

    # Creates an implication.
    #
    # Input parameters:
    # - left: antecedent.
    # - right: consequent.
    #
    # Return:
    # - nothing.
    def __init__(self, left, right):
        self.left = left
        self.right = right

    # Returns a readable representation of the formula.
    #
    # Input parameters:
    # - none.
    #
    # Return:
    # - string representation.
    def __repr__(self):
        return f"({self.left} -> {self.right})"


class StrategicNext(Formula):
    """
    ATL strategic next formula.

    <<A>> X phi means:
    coalition A has a joint action such that, whatever the other agents do,
    the next state satisfies phi.
    """

    # Creates a strategic next formula.
    #
    # Input parameters:
    # - coalition: set of agents.
    # - formula: formula to be forced in the next state.
    #
    # Return:
    # - nothing.
    def __init__(self, coalition, formula):
        self.coalition = set(coalition)
        self.formula = formula

    # Returns a readable representation of the formula.
    #
    # Input parameters:
    # - none.
    #
    # Return:
    # - string representation.
    def __repr__(self):
        coalition_text = ",".join(sorted(self.coalition))
        return f"<<{coalition_text}>> X ({self.formula})"


class StrategicEventually(Formula):
    """
    ATL strategic eventually formula.

    <<A>> F phi means:
    coalition A has a strategy to eventually force phi.
    """

    # Creates a strategic eventually formula.
    #
    # Input parameters:
    # - coalition: set of agents.
    # - formula: target formula.
    #
    # Return:
    # - nothing.
    def __init__(self, coalition, formula):
        self.coalition = set(coalition)
        self.formula = formula

    # Returns a readable representation of the formula.
    #
    # Input parameters:
    # - none.
    #
    # Return:
    # - string representation.
    def __repr__(self):
        coalition_text = ",".join(sorted(self.coalition))
        return f"<<{coalition_text}>> F ({self.formula})"


class StrategicAlways(Formula):
    """
    ATL strategic always formula.

    <<A>> G phi means:
    coalition A has a strategy to keep phi true forever.
    """

    # Creates a strategic always formula.
    #
    # Input parameters:
    # - coalition: set of agents.
    # - formula: invariant formula.
    #
    # Return:
    # - nothing.
    def __init__(self, coalition, formula):
        self.coalition = set(coalition)
        self.formula = formula

    # Returns a readable representation of the formula.
    #
    # Input parameters:
    # - none.
    #
    # Return:
    # - string representation.
    def __repr__(self):
        coalition_text = ",".join(sorted(self.coalition))
        return f"<<{coalition_text}>> G ({self.formula})"


class StrategicUntil(Formula):
    """
    ATL strategic until formula.

    <<A>> (phi U psi) means:
    coalition A has a strategy to force psi eventually,
    while maintaining phi until psi becomes true.
    """

    # Creates a strategic until formula.
    #
    # Input parameters:
    # - coalition: set of agents.
    # - left: formula that must remain true until the target is reached.
    # - right: target formula that must eventually become true.
    #
    # Return:
    # - nothing.
    def __init__(self, coalition, left, right):
        self.coalition = set(coalition)
        self.left = left
        self.right = right

    # Returns a readable representation of the formula.
    #
    # Input parameters:
    # - none.
    #
    # Return:
    # - string representation.
    def __repr__(self):
        coalition_text = ",".join(sorted(self.coalition))
        return f"<<{coalition_text}>> ({self.left} U {self.right})"
