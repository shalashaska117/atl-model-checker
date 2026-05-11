# ATL Model Checker

## Project Title

Strategic Verification of Open Systems using Alternating-time Temporal Logic

## Objective

This project implements a small model checker for a finite fragment of ATL, Alternating-time Temporal Logic. The goal is not to build a complete industrial tool, but to create a readable and formally grounded prototype that shows how strategic properties of multi-agent systems can be verified.

The central point is to distinguish between:

- path verification, typical of CTL;
- strategy verification, typical of ATL.

In CTL, one may ask, for example, whether there exists a path that reaches a target state. In ATL, instead, one asks whether a coalition of agents has a strategy to force the achievement of that target, independently of the choices made by the other agents.

## Theoretical Motivation

The project is based on the idea that many systems of interest in symbolic artificial intelligence, formal verification and multi-agent systems are not closed systems, but open systems. An open system interacts with an external environment, and its behavior does not depend only on internal decisions, but also on the decisions of the environment.

For this reason, a simple Kripke structure is not sufficient to explicitly represent who controls which transition. The project therefore uses a Concurrent Game Structure, where each transition depends on a joint action, namely the combination of actions chosen simultaneously by all agents.

## Formal Model

The implemented model is a finite Concurrent Game Structure.

A Concurrent Game Structure can be seen as a tuple composed of:

- a finite set of states S;
- a finite set of agents Ag;
- for each state and agent, a set of available actions;
- a transition function delta;
- a labeling function L that assigns to each state the atomic propositions that are true in that state.

In the project, the transition function has the form:

    delta(state, joint_action) = next_state

Where a joint_action contains one choice for each agent.

In the demonstration model:

    Agents = {Controller, Environment}

The Controller represents the agent we want to verify. The Environment represents the external environment, which may be adversarial.

## States of the Demonstration Model

The main model contains three states:

### start

Labels:

    {safe}

Meaning:

The system is safe, but it has not yet reached the objective.

### unstable

Labels:

    {}

Meaning:

The system is not safe and has not reached the objective. It is a problematic state.

### goal

Labels:

    {safe, goal}

Meaning:

The system has reached the objective and is safe. In the demo model, goal is absorbing: once reached, the system remains in goal.

## Agents' Actions

The Controller can choose:

    wait
    repair

The Environment can choose:

    calm
    disturb

Interpretation:

- wait: the Controller does not intervene;
- repair: the Controller applies a countermeasure;
- calm: the environment does not disturb;
- disturb: the environment tries to disturb the system.

## Model Transitions

From start:

    delta(start, repair, calm)    = goal
    delta(start, repair, disturb) = goal
    delta(start, wait, calm)      = start
    delta(start, wait, disturb)   = unstable

Interpretation:

From start, repair is a strong winning move for the Controller, because it leads to goal both when the environment is calm and when the environment disturbs. wait, instead, is risky: if the environment disturbs, the system becomes unstable.

From unstable:

    delta(unstable, repair, calm)    = start
    delta(unstable, repair, disturb) = unstable
    delta(unstable, wait, calm)      = unstable
    delta(unstable, wait, disturb)   = unstable

Interpretation:

From unstable, the Controller can recover only if the environment is calm. If the Environment keeps disturbing, the system remains unstable. Therefore, from unstable the Controller cannot force the achievement of goal.

From goal:

    delta(goal, repair, calm)    = goal
    delta(goal, repair, disturb) = goal
    delta(goal, wait, calm)      = goal
    delta(goal, wait, disturb)   = goal

Interpretation:

Goal is absorbing. Once it is reached, no action can make the system leave goal.

## Supported Logical Language

The project supports a fragment of ATL sufficient to express the main strategic properties.

The following are supported:

    TRUE
    FALSE
    p
    !phi
    phi & psi
    phi | psi
    phi -> psi

ATL strategic operators:

    <<A>> X phi
    <<A>> F phi
    <<A>> G phi
    <<A>> (phi U psi)

Where A is a coalition of agents.

## Meaning of the ATL Operators

### Strategic Next

    <<A>> X phi

Meaning:

Coalition A has a choice of actions such that, whatever action is chosen by the agents outside A, the next state satisfies phi.

### Strategic Eventually

    <<A>> F phi

Meaning:

Coalition A has a strategy to eventually force a state satisfying phi, whatever the agents outside the coalition do.

### Strategic Always

    <<A>> G phi

Meaning:

Coalition A has a strategy to keep phi true forever.

### Strategic Until

    <<A>> (phi U psi)

Meaning:

Coalition A has a strategy to eventually force psi while keeping phi true until psi is reached.

## Core Operator: Strategic Predecessor

The theoretical core of the project is the strategic predecessor operator:

    Pre_A(X)

A state s belongs to Pre_A(X) if and only if coalition A has a joint action such that, for every possible joint action of the agents outside A, the next state belongs to X.

Formally:

    s in Pre_A(X)
    iff
    exists alpha_A such that for all alpha_not_A:
        delta(s, alpha_A union alpha_not_A) in X

This formula expresses the fundamental difference between CTL and ATL.

In CTL, there is quantification over paths. In ATL, there is strategic quantification over the choices of agents.

## Fixed Points Used

The strategic temporal operators are implemented through fixed points.

### <<A>> F phi

Strategic eventually is computed as a least fixed point.

The computation starts from the states where phi is already true. Then, the algorithm iteratively adds the states from which coalition A can force entry into the current set.

### <<A>> G phi

Strategic always is computed as a greatest fixed point.

The computation starts from the states where phi is true. Then, the algorithm iteratively removes the states from which coalition A cannot remain inside the candidate set.

### <<A>> (phi U psi)

Strategic until is computed as a least fixed point.

The computation starts from the states where psi is already true. Then, the algorithm adds the states where phi is true and from which coalition A can force entry into the already winning set.

## Properties Verified in the Demo

### 1. The Controller can force goal in the next step

Formula:

    <<Controller>> X goal

Expected result:

    true in start

Reason:

From start, the Controller can choose repair. If Environment chooses calm, the system goes to goal. If Environment chooses disturb, the system still goes to goal.

Therefore, repair is a winning move in one step.

### 2. The Controller can eventually force goal

Formula:

    <<Controller>> F goal

Expected result:

    true in start

Reason:

Since the Controller can already force goal in one step from start, it can certainly force it eventually.

The witness strategy is:

    start -> repair

### 3. The Controller can keep safe forever

Formula:

    <<Controller>> G safe

Expected result:

    true in start

Reason:

From start, by choosing repair, the Controller forces the transition to goal. goal is safe and absorbing. Therefore, safe can be maintained forever.

### 4. The Controller can keep safe until goal

Formula:

    <<Controller>> (safe U goal)

Expected result:

    true in start

Reason:

From start, safe is true. The Controller chooses repair and reaches goal immediately. Therefore, safe remains true until goal is reached.

### 5. Can the Environment force a non-safe state?

Formula:

    <<Environment>> F !safe

Expected result:

    false in start

Reason:

Environment would like to bring the system to unstable. However, from start, if the Controller chooses repair, the system goes to goal regardless of the disturbance. Therefore, Environment cannot force !safe against all possible actions of the Controller.

### 6. Can the Environment keep goal false forever?

Formula:

    <<Environment>> G !goal

Expected result:

    false in start
    true in unstable

Reason:

From start, the Controller can choose repair and reach goal. Therefore, Environment cannot prevent goal forever.

From unstable, instead, Environment can always choose disturb and keep the system in unstable, where goal is false.

### 7. Safe states from which the Controller can force goal

Formula:

    safe & <<Controller>> F goal

Expected result:

    {start, goal}

Reason:

start is safe and the Controller can force goal. goal is already safe and is already goal. unstable is not safe.

## Strategy Extraction

The project does not only state whether a formula is true or false. For strategic formulas, it can also extract a witness strategy.

Example:

    <<Controller>> F goal

Strategy:

    start -> {Controller: repair}
    goal  -> objective already satisfied

This shows the constructive side of ATL model checking: when a strategic property is true, the program can show how the coalition can guarantee it.

## Project Structure

    atl-model-checker/
    |
    |-- model/
    |   |-- game_structure.py
    |
    |-- logic/
    |   |-- ast.py
    |   |-- parser.py
    |
    |-- model_checker/
    |   |-- atl_checker.py
    |
    |-- examples/
    |   |-- controller_env.py
    |
    |-- tests/
    |   |-- test_atl_checker.py
    |
    |-- main.py
    |-- README.md
    |-- requirements.txt

## File Description

### model/game_structure.py

Defines the Concurrent Game Structure. It manages states, agents, actions, transitions, labeling and totality of the transition relation.

### logic/ast.py

Defines the classes that represent logical formulas as abstract syntax trees.

### logic/parser.py

Transforms formulas written as strings into AST objects.

Example:

    <<Controller>> F goal

is transformed into a StrategicEventually formula with coalition Controller and objective Atom(goal).

### model_checker/atl_checker.py

Contains the semantics of the language. It computes the states that satisfy a formula and implements the ATL operators through strategic predecessor and fixed points.

### examples/controller_env.py

Builds the demonstration model Controller vs Environment.

### tests/test_atl_checker.py

Contains automatic tests to verify consistency between the model, parser, AST, checker and strategy extraction.

### main.py

Runs the demo, prints the states, the agents, the results of the formulas and the witness strategies.

## How to Run

From the main project folder:

    python main.py

To run the tests:

    python -m unittest discover -s tests

## Expected Output

The output shows:

- the states of the model;
- the agents;
- the verified formulas;
- the parsed formula;
- the set of satisfying states;
- the result in the initial state start;
- a witness strategy, when available.

Example:

    Formula: <<Controller>> F goal
    Parsed : <<Controller>> F (goal)
    States : {'start', 'goal'}
    start  : True
    Strategy:
    - goal: objective already satisfied
    - start: choose {'Controller': 'repair'}

## Conclusion

The project shows an essential but formally meaningful fragment of ATL model checking. The demo highlights the difference between possibility and strategic guarantee.

The main result is that the Controller can force the achievement of goal and maintain safety from start, while the Environment cannot force an unsafe state from start. This demonstrates that the system is not analyzed only as a transition graph, but as a game between agents with strategies.

The project is therefore a compact prototype of symbolic AI applied to the formal verification of multi-agent systems.
