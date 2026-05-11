# Formal Semantics

This document summarizes the formal semantics implemented by the ATL Model Checker.

The project implements a finite explicit-state model checker for a fragment of **Alternating-time Temporal Logic** (ATL) over **Concurrent Game Structures**.

## Concurrent Game Structures

A finite Concurrent Game Structure can be described as a tuple:

```text
M = (Ag, S, Act, d, delta, L)
```

where:

- `Ag` is a finite set of agents;
- `S` is a finite set of states;
- `Act` is a finite set of actions;
- `d(a, s)` gives the actions available to agent `a` in state `s`;
- `delta` is the transition function;
- `L` is a labeling function assigning atomic propositions to states.

A transition depends on a joint action, that is, one action choice for each agent:

```text
delta(s, alpha) = s'
```

where `alpha` is a complete joint action profile.

## Labeling Function

The labeling function maps each state to the set of atomic propositions true in that state:

```text
L : S -> 2^AP
```

For an atomic proposition `p`, the satisfaction condition is:

```text
M, s |= p iff p in L(s)
```

## Satisfaction Sets

The implementation evaluates formulas by computing satisfaction sets.

For a formula `phi`, `Sat(phi)` is the set of states where `phi` is true:

```text
Sat(phi) = { s in S | M, s |= phi }
```

This makes model checking a bottom-up computation over formula syntax trees.

## Boolean Operators

Boolean formulas are interpreted as set operations.

```text
Sat(TRUE)  = S
Sat(FALSE) = empty set
Sat(!phi)  = S \ Sat(phi)
Sat(phi & psi) = Sat(phi) intersection Sat(psi)
Sat(phi | psi) = Sat(phi) union Sat(psi)
Sat(phi -> psi) = Sat(!phi | psi)
```

## Coalitions

A coalition is a subset of agents:

```text
A subset Ag
```

ATL formulas quantify over the strategic ability of coalitions. A coalition controls only the actions of its own agents. The remaining agents are treated adversarially or nondeterministically.

## Strategic Predecessor

The central operation is the controllable predecessor:

```text
Pre_A(X)
```

A state `s` belongs to `Pre_A(X)` if coalition `A` has a joint action such that every compatible choice of the agents outside `A` leads to a state in `X`.

Formally:

```text
s in Pre_A(X)
iff
exists alpha_A such that for all alpha_not_A:
    delta(s, alpha_A union alpha_not_A) in X
```

This is the key distinction between ATL and path-based temporal logics.

In CTL, one quantifies over paths. In ATL, one quantifies over strategic choices of coalitions.

## Strategic Next

The ATL next operator is:

```text
<<A>> X phi
```

Its satisfaction set is:

```text
Sat(<<A>> X phi) = Pre_A(Sat(phi))
```

Meaning: coalition `A` can force the next state to satisfy `phi`.

## Strategic Eventually

The ATL eventually operator is:

```text
<<A>> F phi
```

It is computed as a least fixed point:

```text
Sat(<<A>> F phi) = lfp Z . Sat(phi) union Pre_A(Z)
```

Operationally:

1. start with the states where `phi` already holds;
2. repeatedly add states from which coalition `A` can force entry into the current set;
3. stop when no new states are added.

## Strategic Always

The ATL always operator is:

```text
<<A>> G phi
```

It is computed as a greatest fixed point:

```text
Sat(<<A>> G phi) = gfp Z . Sat(phi) intersection Pre_A(Z)
```

Operationally:

1. start with all states satisfying `phi`;
2. remove states from which coalition `A` cannot force the computation to remain inside the candidate set;
3. stop when the set stabilizes.

## Strategic Until

The ATL until operator is:

```text
<<A>> (phi U psi)
```

It is computed as a least fixed point:

```text
Sat(<<A>> (phi U psi)) =
    lfp Z . Sat(psi) union (Sat(phi) intersection Pre_A(Z))
```

Meaning: coalition `A` can force `psi` to become true while maintaining `phi` until then.

## Strategy Witnesses

When a strategic formula is true, the checker may extract a witness strategy.

A witness strategy maps states to coalition actions:

```text
state -> coalition joint action
```

For example:

```text
start -> {Controller: repair}
```

The extracted strategy is intended as an explanatory witness for the implemented finite examples.

## Example: Controller vs Environment

The demo model has two agents:

```text
Ag = {Controller, Environment}
```

The Controller can choose:

```text
wait, repair
```

The Environment can choose:

```text
calm, disturb
```

From `start`, the action `repair` forces the system to `goal` regardless of the Environment's action. Therefore:

```text
M, start |= <<Controller>> X goal
M, start |= <<Controller>> F goal
```

However, the Environment cannot force an unsafe state from `start`, because the Controller can always choose `repair`:

```text
M, start not|= <<Environment>> F !safe
```

This demonstrates the difference between possible behavior and strategically enforceable behavior.

## Scope of the Semantics

The implementation focuses on:

- finite models;
- explicit-state model checking;
- deterministic transition functions over complete joint actions;
- a compact ATL fragment;
- fixed-point characterizations of temporal strategic modalities.

It does not aim to provide a complete implementation of all ATL variants or optimized symbolic algorithms.
