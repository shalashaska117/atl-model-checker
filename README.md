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

Formally:

```text
s in Pre_A(X)
iff
exists alpha_A such that for all alpha_not_A:
    delta(s, alpha_A union alpha_not_A) in X
```

This existential-universal structure is the key difference between simple graph reachability and ATL strategic reasoning.

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

## Adversarial Choice Example

The repository also includes an adversarial example showing the difference between **reachability** and **strategic enforceability**.

In `examples/adversarial_choice.json`, the Controller can choose between a safe action and a risky action:

```text
Controller = safe  -> remain safe
Controller = risky + Environment = allow -> goal
Controller = risky + Environment = block -> trap
```

Therefore, `goal` is reachable along some execution path, but the Controller cannot guarantee reaching it against an adversarial Environment.

For example:

```text
<<Controller>> F goal
```

is false from the initial state, even though a path to `goal` exists.

On the other hand:

```text
<<Controller>> G safe
```

is true from the initial state, because the Controller can avoid risk and keep the system safe.

This example highlights the main purpose of ATL: verifying what coalitions can **guarantee**, not merely what can happen.

## Example Properties

### The Controller can force goal in the next step

```text
<<Controller>> X goal
```

Expected result in the main controller/environment model:

```text
true in start
```

The Controller chooses `repair`, and the system reaches `goal` regardless of the Environment's action.

### The Controller can eventually force goal

```text
<<Controller>> F goal
```

Expected result in the main controller/environment model:

```text
true in start
```

Since the Controller can already force `goal` in one step, it can also force it eventually.

### The Environment cannot force an unsafe state from start

```text
<<Environment>> F !safe
```

Expected result in the main controller/environment model:

```text
false in start
```

Even if the Environment chooses `disturb`, the Controller can choose `repair` and force the system to `goal`, which is safe.

### The Controller cannot force goal in the adversarial choice model

```text
<<Controller>> F goal
```

Expected result in the adversarial choice model:

```text
false in start
```

The Controller can try the risky action, but the Environment can block it and send the system to `trap`.

## Strategy Extraction

For strategic formulas, the model checker can extract a simple witness strategy.

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

The project also supports a structured strategy result object, `StrategyResult`, which stores:

- the original formula;
- the coalition;
- the satisfying states;
- the extracted witness strategy.

This is useful for tests, CLI output, and future API extensions.

## JSON Model Loader

Models can be loaded from external JSON files instead of being hardcoded in Python.

A JSON model contains:

- `agents`;
- `states`;
- `initial`;
- `actions`;
- `labels`;
- `transitions`.

Example structure:

```json
{
  "agents": ["Controller", "Environment"],
  "states": ["start", "goal"],
  "initial": "start",
  "actions": {
    "Controller": ["wait", "repair"],
    "Environment": ["calm", "disturb"]
  },
  "labels": {
    "start": ["safe"],
    "goal": ["safe", "goal"]
  },
  "transitions": [
    {
      "from": "start",
      "joint_action": {
        "Controller": "repair",
        "Environment": "calm"
      },
      "to": "goal"
    }
  ]
}
```

The loader supports both global actions per agent and state-dependent actions.

## Command-Line Interface

After installing the project, the checker can be used from the command line:

```bash
atl-check MODEL FORMULA
```

Example:

```bash
atl-check examples/controller_env.json "<<Controller>> F goal"
```

You can also select a specific state:

```bash
atl-check examples/controller_env.json "<<Controller>> F goal" --state start
```

To print a witness strategy when available:

```bash
atl-check examples/controller_env.json "<<Controller>> F goal" --strategy
```

The CLI prints:

- the original formula;
- the parsed formula;
- the selected state;
- all satisfying states;
- whether the formula holds in the selected state;
- an optional witness strategy.

## Project Structure

```text
atl-model-checker/
├── .github/
│   └── workflows/
│       └── ...
├── README.md
├── docs/
│   ├── semantics.md
│   └── technical-report.md
├── examples/
│   ├── __init__.py
│   ├── adversarial_choice.json
│   ├── controller_env.py
│   └── controller_env.json
├── logic/
│   ├── __init__.py
│   ├── ast.py
│   └── parser.py
├── model/
│   ├── __init__.py
│   ├── game_structure.py
│   └── json_loader.py
├── model_checker/
│   ├── __init__.py
│   ├── atl_checker.py
│   └── strategy_result.py
├── tests/
│   ├── __init__.py
│   ├── test_adversarial_choice.py
│   ├── test_atl_checker.py
│   ├── test_json_loader.py
│   ├── test_predecessor.py
│   └── test_strategy_result.py
├── cli.py
├── main.py
├── pyproject.toml
└── requirements-dev.txt
```

## Main Components

| File | Role |
|---|---|
| `model/game_structure.py` | Defines the Concurrent Game Structure. |
| `model/json_loader.py` | Loads Concurrent Game Structures from JSON files. |
| `logic/ast.py` | Defines the formula AST classes. |
| `logic/parser.py` | Parses formulas into AST nodes. |
| `model_checker/atl_checker.py` | Implements ATL semantics, strategic predecessor, fixed points, and strategy extraction. |
| `model_checker/strategy_result.py` | Defines a structured object for witness strategy results. |
| `examples/controller_env.py` | Builds the Controller vs Environment demonstration model in Python. |
| `examples/controller_env.json` | JSON version of the main demonstration model. |
| `examples/adversarial_choice.json` | Example showing reachability versus strategic enforceability. |
| `tests/test_atl_checker.py` | Tests parsing, semantics, fixed points, and strategies. |
| `tests/test_predecessor.py` | Tests the strategic predecessor operator directly. |
| `tests/test_json_loader.py` | Tests JSON model loading. |
| `tests/test_adversarial_choice.py` | Tests the adversarial example. |
| `tests/test_strategy_result.py` | Tests the structured strategy result object. |
| `docs/semantics.md` | Contains a compact formal description of the implemented semantics. |
| `docs/technical-report.md` | Provides a longer technical overview of the project. |
| `cli.py` | Provides the command-line interface. |

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

Run the checker from the CLI:

```bash
atl-check examples/controller_env.json "<<Controller>> F goal"
```

Run the adversarial example:

```bash
atl-check examples/adversarial_choice.json "<<Controller>> F goal"
atl-check examples/adversarial_choice.json "<<Controller>> G safe"
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

## Expected CLI Output

Example:

```bash
atl-check examples/controller_env.json "<<Controller>> F goal" --strategy
```

Possible output:

```text
Formula: <<Controller>> F goal
Parsed formula: <<Controller>> F (goal)
Selected state: start
Satisfying states: ['goal', 'start']
Holds in selected state: True
Witness strategy:
Coalition: ['Controller']
  goal: objective already satisfied
  start: choose {'Controller': 'repair'}
```

Adversarial example:

```bash
atl-check examples/adversarial_choice.json "<<Controller>> F goal"
```

Expected result:

```text
Holds in selected state: False
```

because the Controller cannot force the goal against a blocking Environment.

## Testing

The project includes automated tests for:

- Boolean formula semantics;
- ATL strategic operators;
- parser integration;
- fixed-point computations;
- the strategic predecessor operator;
- JSON model loading;
- adversarial strategic behavior;
- structured strategy results.

Run:

```bash
python3 -m pytest
```

The repository also includes a GitHub Actions workflow for automated checks.

## Scope and Limitations

This project is intentionally small. It currently focuses on:

- finite Concurrent Game Structures;
- explicit-state model checking;
- a compact ATL fragment;
- memoryless witness strategies for the implemented examples;
- educational clarity over performance.

Current limitations include:

- no symbolic state representation;
- no optimized fixed-point algorithms;
- no counterexample generation;
- no probabilistic or quantitative extensions;
- no graphical visualization of models or strategies.

## Possible Future Extensions

Future extensions could include:

- richer strategy extraction;
- counterexample generation;
- model visualization;
- symbolic state-space representation;
- more examples comparing CTL-style reachability with ATL strategic ability;
- additional strategic logics or quantitative extensions;
- integration with research-oriented verification formats.

## Motivation

The project is a compact prototype of symbolic AI applied to the formal verification of multi-agent systems. It shows how strategic reasoning can be implemented using a clear semantic core: the controllable predecessor and fixed-point computations.

It is designed to be readable, testable, and useful as a small research-oriented portfolio project.
