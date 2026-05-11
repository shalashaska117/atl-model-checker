# ATL Model Checker

**Strategic Verification of Open Systems using Alternating-time Temporal Logic**

This repository contains a small, educational, explicit-state model checker for a finite fragment of **ATL** (Alternating-time Temporal Logic) over **Concurrent Game Structures**.

The goal is not to compete with industrial or research-grade verification tools, but to provide a readable and formally grounded prototype that shows how strategic properties of multi-agent systems can be verified in code.

## Why ATL?

Classical temporal logics such as CTL reason about paths in a transition system. ATL goes one step further: it reasons about what a coalition of agents can force, independently of the choices made by the other agents.

For example, instead of asking:

```text
Is there a path that eventually reaches goal?
```

ATL asks:

```text
Does coalition A have a strategy to force goal, no matter how the other agents behave?
```

This distinction is crucial for open systems, where the system interacts with an external environment that may be nondeterministic or adversarial.

## Core Idea

The project models systems as finite **Concurrent Game Structures**. A transition does not depend on a single choice, but on a **joint action** containing one action for each agent.

```text
delta(state, joint_action) = next_state
```

The theoretical core of the implementation is the controllable predecessor operator:

```text
Pre_A(X)
```

A state belongs to `Pre_A(X)` when coalition `A` has a joint action that guarantees reaching a state in `X`, regardless of the actions chosen by the agents outside the coalition.

## Supported Logic Fragment

The current implementation supports:

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

where `A` is a coalition of agents.

## Implemented ATL Operators

| Operator | Meaning |
|---|---|
| `<<A>> X phi` | Coalition `A` can force `phi` in the next state. |
| `<<A>> F phi` | Coalition `A` can eventually force `phi`. |
| `<<A>> G phi` | Coalition `A` can keep `phi` true forever. |
| `<<A>> (phi U psi)` | Coalition `A` can force `psi` while maintaining `phi` until then. |

The temporal strategic operators are implemented through fixed-point computations.

## Demonstration Model

The main example models a simple interaction between two agents:

```text
Agents = {Controller, Environment}
```

The Controller represents the agent whose strategic ability we want to verify. The Environment represents an external adversarial component.

The model has three states:

| State | Labels | Meaning |
|---|---|---|
| `start` | `{safe}` | The system is safe but has not reached the objective. |
| `unstable` | `{}` | The system is unsafe and problematic. |
| `goal` | `{safe, goal}` | The objective has been reached; this state is absorbing. |

The Controller can choose:

```text
wait
repair
```

The Environment can choose:

```text
calm
disturb
```

From `start`, action `repair` is a winning move for the Controller because it reaches `goal` both when the Environment is calm and when it disturbs.

## Example Properties

### The Controller can force goal in the next step

```text
<<Controller>> X goal
```

Expected result:

```text
true in start
```

The Controller chooses `repair`, and the system reaches `goal` regardless of the Environment's action.

### The Controller can eventually force goal

```text
<<Controller>> F goal
```

Expected result:

```text
true in start
```

Since the Controller can already force `goal` in one step, it can also force it eventually.

### The Environment cannot force an unsafe state from start

```text
<<Environment>> F !safe
```

Expected result:

```text
false in start
```

Even if the Environment chooses `disturb`, the Controller can choose `repair` and force the system to `goal`, which is safe.

### The Environment can keep goal false from unstable

```text
<<Environment>> G !goal
```

Expected result:

```text
false in start
true in unstable
```

From `start`, the Controller can reach `goal`. From `unstable`, the Environment can keep disturbing and prevent recovery.

## Strategy Extraction

For strategic formulas, the model checker can also extract a simple witness strategy.

Example:

```text
<<Controller>> F goal
```

Possible witness strategy:

```text
start -> {Controller: repair}
goal  -> objective already satisfied
```

This highlights the constructive nature of ATL model checking: when a strategic property is true, the checker can show how the coalition can guarantee it.

## Project Structure

```text
atl-model-checker/
├── README.md
├── docs/
│   └── semantics.md
├── examples/
│   ├── __init__.py
│   └── controller_env.py
├── logic/
│   ├── __init__.py
│   ├── ast.py
│   └── parser.py
├── main.py
├── model/
│   ├── __init__.py
│   └── game_structure.py
├── model_checker/
│   ├── __init__.py
│   └── atl_checker.py
├── pyproject.toml
├── requirements-dev.txt
└── tests/
    ├── __init__.py
    └── test_atl_checker.py
```

## Main Components

| File | Role |
|---|---|
| `model/game_structure.py` | Defines the Concurrent Game Structure. |
| `logic/ast.py` | Defines the formula AST classes. |
| `logic/parser.py` | Parses formulas into AST nodes. |
| `model_checker/atl_checker.py` | Implements ATL semantics, strategic predecessor, fixed points, and strategy extraction. |
| `examples/controller_env.py` | Builds the Controller vs Environment demonstration model. |
| `tests/test_atl_checker.py` | Contains tests for parsing, semantics, fixed points, and strategies. |
| `docs/semantics.md` | Contains a compact formal description of the implemented semantics. |

## Installation

Create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the project in editable mode:

```bash
pip install -e .
```

For development tools:

```bash
pip install -r requirements-dev.txt
```

## Usage

Run the demonstration:

```bash
python main.py
```

Run the tests:

```bash
python -m unittest discover -s tests
pytest
```

Run formatting and lint checks:

```bash
black --check .
ruff check .
```

## Expected Output

The demo prints:

- the states of the model;
- the agents;
- the verified formulas;
- the parsed formula;
- the set of satisfying states;
- the result in the initial state;
- a witness strategy, when available.

Example:

```text
Formula: <<Controller>> F goal
Parsed : <<Controller>> F (goal)
States : {'start', 'goal'}
start  : True
Strategy:
- goal: objective already satisfied
- start: choose {'Controller': 'repair'}
```

## Scope and Limitations

This project is intentionally small. It currently focuses on:

- finite Concurrent Game Structures;
- explicit-state model checking;
- a compact ATL fragment;
- memoryless witness strategies for the implemented examples;
- educational clarity over performance.

Future extensions could include:

- JSON input for models;
- a command-line interface for checking formulas over external model files;
- more examples comparing CTL-style reachability with ATL strategic ability;
- richer strategy extraction;
- additional strategic logics or quantitative extensions.

## Motivation

The project is a compact prototype of symbolic AI applied to the formal verification of multi-agent systems. It shows how strategic reasoning can be implemented using a clear semantic core: the controllable predecessor and fixed-point computations.
