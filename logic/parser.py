"""
This file implements a small parser for the ATL fragment used by the project.

Supported syntax examples:

    safe
    !safe
    safe & ready
    safe | goal
    safe -> goal

    <<Controller>> X safe
    <<Controller>> F goal
    <<Controller>> G safe
    <<Controller>> (safe U goal)

    <<Controller,Environment>> F goal

The parser is intentionally small and explicit. It is not meant to support the whole ATL
language, but it is enough to write readable formulas in the demo and in tests.
"""

import re

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


class Token:
    """
    Represents a lexical token.
    """

    # Creates a token.
    #
    # Input parameters:
    # - kind: token type.
    # - value: token text.
    #
    # Return:
    # - nothing.
    def __init__(self, kind, value):
        self.kind = kind
        self.value = value

    # Returns a readable representation of the token.
    #
    # Input parameters:
    # - none.
    #
    # Return:
    # - string representation.
    def __repr__(self):
        return f"Token({self.kind}, {self.value})"


class ATLParser:
    """
    Recursive descent parser for a small ATL fragment.
    """

    # Initializes the parser with a formula string.
    #
    # Input parameters:
    # - text: formula string.
    #
    # Return:
    # - nothing.
    def __init__(self, text):
        self.tokens = self._tokenize(text)
        self.position = 0

    # Parses the whole input string.
    #
    # Input parameters:
    # - none.
    #
    # Return:
    # - parsed Formula object.
    def parse(self):
        formula = self._parse_implication()

        if self._current().kind != "EOF":
            raise ValueError(f"Unexpected token at end: {self._current()}")

        return formula

    # Tokenizes the input string.
    #
    # Input parameters:
    # - text: formula string.
    #
    # Return:
    # - list of Token objects.
    def _tokenize(self, text):
        token_specification = [
            ("SPACE", r"[ \t\n]+"),
            ("COALITION", r"<<[^>]+>>"),
            ("ARROW", r"->"),
            ("AND", r"&|AND\b"),
            ("OR", r"\||OR\b"),
            ("NOT", r"!|NOT\b"),
            ("LPAREN", r"\("),
            ("RPAREN", r"\)"),
            ("U", r"U\b"),
            ("X", r"X\b"),
            ("F", r"F\b"),
            ("G", r"G\b"),
            ("TRUE", r"TRUE\b|true\b"),
            ("FALSE", r"FALSE\b|false\b"),
            ("ID", r"[A-Za-z_][A-Za-z0-9_]*"),
        ]

        combined_regex = "|".join(
            f"(?P<{name}>{pattern})"
            for name, pattern in token_specification
        )

        tokens = []

        for match in re.finditer(combined_regex, text):
            kind = match.lastgroup
            value = match.group()

            if kind != "SPACE":
                tokens.append(Token(kind, value))

        tokens.append(Token("EOF", ""))
        return tokens

    # Parses implication with right associativity.
    #
    # Input parameters:
    # - none.
    #
    # Return:
    # - parsed Formula object.
    def _parse_implication(self):
        left = self._parse_or()

        if self._accept("ARROW"):
            right = self._parse_implication()
            return Implies(left, right)

        return left

    # Parses disjunction.
    #
    # Input parameters:
    # - none.
    #
    # Return:
    # - parsed Formula object.
    def _parse_or(self):
        formula = self._parse_and()

        while self._accept("OR"):
            right = self._parse_and()
            formula = Or(formula, right)

        return formula

    # Parses conjunction.
    #
    # Input parameters:
    # - none.
    #
    # Return:
    # - parsed Formula object.
    def _parse_and(self):
        formula = self._parse_unary()

        while self._accept("AND"):
            right = self._parse_unary()
            formula = And(formula, right)

        return formula

    # Parses unary formulas, atoms, parentheses, and strategic ATL operators.
    #
    # Input parameters:
    # - none.
    #
    # Return:
    # - parsed Formula object.
    def _parse_unary(self):
        if self._accept("NOT"):
            return Not(self._parse_unary())

        if self._accept("TRUE"):
            return BoolConstant(True)

        if self._accept("FALSE"):
            return BoolConstant(False)

        if self._current().kind == "COALITION":
            return self._parse_strategic_formula()

        if self._accept("LPAREN"):
            formula = self._parse_implication()
            self._expect("RPAREN")
            return formula

        if self._current().kind == "ID":
            token = self._expect("ID")
            return Atom(token.value)

        raise ValueError(f"Unexpected token: {self._current()}")

    # Parses ATL strategic operators after a coalition token.
    #
    # Input parameters:
    # - none.
    #
    # Return:
    # - parsed strategic Formula object.
    def _parse_strategic_formula(self):
        coalition_token = self._expect("COALITION")
        coalition = self._parse_coalition(coalition_token.value)

        if self._accept("X"):
            return StrategicNext(coalition, self._parse_unary())

        if self._accept("F"):
            return StrategicEventually(coalition, self._parse_unary())

        if self._accept("G"):
            return StrategicAlways(coalition, self._parse_unary())

        if self._accept("LPAREN"):
            left = self._parse_implication()
            self._expect("U")
            right = self._parse_implication()
            self._expect("RPAREN")
            return StrategicUntil(coalition, left, right)

        raise ValueError("Expected one of X, F, G, or an until formula after coalition")

    # Parses a coalition token like <<A,B>> into a set of agent names.
    #
    # Input parameters:
    # - text: coalition token text.
    #
    # Return:
    # - set of agent names.
    def _parse_coalition(self, text):
        inner = text[2:-2].strip()

        if not inner:
            return set()

        return {agent.strip() for agent in inner.split(",") if agent.strip()}

    # Returns the current token without consuming it.
    #
    # Input parameters:
    # - none.
    #
    # Return:
    # - current Token.
    def _current(self):
        return self.tokens[self.position]

    # Consumes a token if it has the expected kind.
    #
    # Input parameters:
    # - kind: expected token type.
    #
    # Return:
    # - True if a token was consumed, False otherwise.
    def _accept(self, kind):
        if self._current().kind == kind:
            self.position += 1
            return True

        return False

    # Consumes and returns a token of the expected kind.
    #
    # Input parameters:
    # - kind: expected token type.
    #
    # Return:
    # - consumed Token.
    def _expect(self, kind):
        token = self._current()

        if token.kind != kind:
            raise ValueError(f"Expected token {kind}, found {token}")

        self.position += 1
        return token


# Parses a formula string into an AST.
#
# Input parameters:
# - text: formula string.
#
# Return:
# - parsed Formula object.
def parse_formula(text):
    return ATLParser(text).parse()