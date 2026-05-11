# Formal Semantics

This project implements an educational explicit-state model checker for a fragment of Alternating-time Temporal Logic (ATL) over finite Concurrent Game Structures.

## Concurrent Game Structures

A Concurrent Game Structure is represented by:

- a finite set of states;
- a finite set of agents;
- a set of available actions for each agent;
- a transition function depending on joint actions;
- a labeling function assigning atomic propositions to states.

The transition function has the form:

```text
delta(state, joint_action) = next_state
A joint action contains one action choice for each agent.

Satisfaction Sets

The model checker evaluates formulas by computing the set of states in which each formula is satisfied.

For an atomic proposition p:

Sat(p) = { s | p is in L(s) }

Boolean operators are interpreted by set operations.

Strategic Predecessor

The core ATL operator is the controllable predecessor:

Pre_A(X)

A state belongs to Pre_A(X) if coalition A has a joint action such that, for every possible action of the agents outside A, the resulting next state belongs to X.

Formally:

s in Pre_A(X)
iff
exists alpha_A such that for all alpha_not_A:
    delta(s, alpha_A union alpha_not_A) in X
Strategic Operators

The implemented ATL operators are based on fixed-point computations.

Strategic Next
<<A>> X phi

Coalition A can force phi in one step.

Strategic Eventually
<<A>> F phi

Computed as a least fixed point:

lfp Z . Sat(phi) union Pre_A(Z)
Strategic Always
<<A>> G phi

Computed as a greatest fixed point:

gfp Z . Sat(phi) intersection Pre_A(Z)
Strategic Until
<<A>> (phi U psi)

Computed as a least fixed point:

lfp Z . Sat(psi) union (Sat(phi) intersection Pre_A(Z))
Goal

The project is intentionally small and educational. Its purpose is to make the operational meaning of ATL strategic modalities explicit and testable.
