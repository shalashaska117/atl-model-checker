# ATL Model Checker — Technical Report

## 1. Overview

This project implements a compact explicit-state model checker for a finite
fragment of Alternating-time Temporal Logic (ATL).

The goal of the project is educational and experimental: it shows how strategic
properties of multi-agent systems can be verified over Concurrent Game
Structures using the semantic core of ATL.

Unlike classical temporal logics such as CTL, ATL does not only ask whether a
path exists. It asks whether a coalition of agents has a strategy to enforce a
property independently of the choices made by the remaining agents.

## 2. Concurrent Game Structures

The system is represented as a finite Concurrent Game Structure.

A model contains:

- a finite set of states;
- a finite set of agents;
- available actions for each agent;
- a transition function defined over joint actions;
- a labeling function assigning atomic propositions to states.

The transition function has the form:

```text
delta(state, joint_action) = next_state
```

A joint action contains exactly one action for each agent.

## 3. Strategic Predecessor

The central semantic operator is the strategic predecessor:

```text
Pre_A(X)
```

A state belongs to `Pre_A(X)` when coalition `A` has a joint action that
guarantees reaching a state in `X`, regardless of the actions chosen by agents
outside the coalition.

Formally:

```text
s in Pre_A(X)
iff
exists alpha_A such that for all alpha_not_A:
    delta(s, alpha_A union alpha_not_A) in X
```

This existential-universal structure is the key difference between simple graph
reachability and ATL strategic reasoning.

## 4. Supported ATL Fragment

The model checker supports Boolean formulas:

```text
TRUE
FALSE
p
!phi
phi & psi
phi | psi
phi -> psi
```

and the following ATL strategic operators:

```text
<<A>> X phi
<<A>> F phi
<<A>> G phi
<<A>> (phi U psi)
```

## 5. Fixed-Point Semantics

The temporal strategic operators are implemented through fixed-point
computations.

### Strategic Next

```text
<<A>> X phi
```

This is implemented directly through the strategic predecessor of the states
satisfying `phi`.

### Strategic Eventually

```text
<<A>> F phi
```

This is implemented as a least fixed point. The computation starts from states
already satisfying `phi` and repeatedly adds states from which the coalition can
force a transition into the current winning region.

### Strategic Always

```text
<<A>> G phi
```

This is implemented as a greatest fixed point. The computation starts from all
states satisfying `phi` and removes states from which the coalition cannot keep
the game inside the current candidate winning region.

### Strategic Until

```text
<<A>> (phi U psi)
```

This is implemented as a least fixed point. States satisfying `psi` are winning
immediately. Other states are added only if they satisfy `phi` and the coalition
can force the game into the current winning region.

## 6. Strategy Extraction

For strategic formulas, the checker can extract witness strategies.

A witness strategy maps states to coalition actions. This makes the result
constructive: when a formula is true, the checker can show how the coalition can
enforce it.

The project can expose this information through a structured strategy result
object containing:

- the original formula;
- the responsible coalition;
- the satisfying states;
- the extracted witness strategy.

This keeps the public API cleaner than returning only a raw dictionary.

## 7. JSON Model Loader

Models can be loaded from external JSON files.

This makes the checker usable from the command line without hardcoding models in
Python. The loader supports both global actions per agent and state-dependent
actions.

A JSON model describes:

- agents;
- states;
- initial state;
- available actions;
- labels;
- transitions.

## 8. Command-Line Interface

The project exposes a command-line interface through:

```bash
atl-check MODEL FORMULA
```

Example:

```bash
atl-check examples/controller_env.json "<<Controller>> F goal"
```

The CLI prints:

- the original formula;
- the parsed formula;
- the selected state;
- all satisfying states;
- whether the formula holds in the selected state;
- an optional witness strategy.

## 9. Adversarial Choice Example

The `adversarial_choice` example demonstrates the difference between
reachability and strategic enforceability.

In that model, the Controller can choose a risky action that reaches the goal
only if the Environment allows it. If the Environment blocks it, the system goes
to a trap state.

Therefore, the goal is reachable along some path, but the Controller cannot
force it against an adversarial Environment.

This shows why ATL is useful: it reasons about guaranteed strategic ability, not
only possible execution paths.

## 10. Testing

The project includes tests for:

- formula parsing;
- Boolean semantics;
- ATL strategic operators;
- fixed-point computations;
- the strategic predecessor operator;
- JSON model loading through examples;
- adversarial strategic behavior.

The predecessor tests are especially important because `Pre_A(X)` is the core
semantic operator behind the ATL fragment implemented in the checker.

## 11. Limitations

The project intentionally focuses on clarity rather than performance.

Current limitations include:

- finite explicit-state models only;
- no symbolic representation of state sets;
- no optimized fixed-point algorithms;
- basic witness strategies;
- no quantitative or probabilistic extensions;
- no graphical model visualization.

## 12. Possible Extensions

Future work could include:

- richer strategy result objects;
- counterexample generation;
- symbolic state-space representation;
- support for additional strategic logics;
- model visualization;
- integration with research-oriented verification formats;
- benchmark examples for larger game structures.

## 13. Conclusion

This project provides a small but formally grounded implementation of ATL model
checking.

Its core value is showing how strategic reasoning can be implemented in code
through the controllable predecessor operator and fixed-point computations.

The checker is intentionally compact, but it already captures the central idea
of ATL: verifying what coalitions can guarantee in the presence of other agents.
