# Assignment 3 – Argumentation Engine & Strategic Argumentation

Pure Python 3 (standard library only, no installs needed).

## Files
| File | Content |
|---|---|
| `argumentation.py` | **Part 1.** `ArgumentationFramework` class + conflict-free, defends, characteristic function, admissible / complete, grounded, complete / preferred / stable / semi-stable extensions, legal labellings, acceptance status. Function-style wrappers at the bottom. |
| `strategic.py` | **Part 2.** `mechanism` (grounded direct mechanism), `best_responses`, `check_truthfulness` (Thm 5.3 check), `is_strategyproof`, `theorem_5_4_condition` / `odd_path_exists` (Thm 5.4 condition, cycle-safe). |
| `experiments.py` | Random instance generator + per-instance records. |
| `analyse.py` | Helpers used to explain "strategyproof although the condition fails". |
| `run_experiments.py` | Runs the whole experiment, writes `results/`. |
| `tests.py` | Sanity tests and cross-checks (e.g. labellings <-> complete extensions, fast bitmask grounded == class-based grounded). |
| `demo.py`, `demo_output.txt` | Demonstration script and its captured output. |
| `REPORT.md` | Report with results and explanations. |
| `results/` | `results.md` (tables), `instances.json` (all 3000 instances), `notable_instances.json`. |

## Run
```
python3 tests.py              # all tests
python3 demo.py               # demonstration (Part 1 examples + Part 2 examples)
python3 run_experiments.py    # 1000 instances per p (about 1 min); optional arg = N
```

## Usage
```python
from argumentation import ArgumentationFramework as AF
af = AF("abc", {("a","b"), ("b","c")})        # a attacks b, b attacks c
af.grounded_extension(); af.complete_extensions(); af.all_extensions()
af.labellings(); af.acceptance_status("a")     # 'skeptically accepted'

from strategic import *
agents  = {1: frozenset({"x","y"}), 2: frozenset({"z"})}   # TRUE argument sets
attacks = {("x","z"), ("z","y")}
mechanism(attacks, {1: {"x"}, 2: {"z"}})                    # grounded ext. of revealed graph
best_responses(1, agents, attacks, {2: agents[2]})          # (best utility, [best reports])
check_truthfulness(agents, attacks)                         # (True, None) or (False, counterexample)
theorem_5_4_condition(agents, attacks, mode="walk")         # (holds, violating (agent, a, b) triples)
```

## Design decisions
* Semantics are computed by brute force (subsets / 3^n labellings): clear and fine for n <= ~12.
* Semi-stable = admissible set with maximal range S u S+ (w.r.t. inclusion). Acceptance status is w.r.t. preferred
  semantics by default (`semantics=` argument changes it).
* Utility of agent i = |grounded extension ∩ A_i| where A_i is its **true** set (this also avoids the Example 5.10 misprint issue).
* Truthfulness check: for every agent and every combination of subsets of the others' sets, revealing A_i must give
  utility >= every other subset of A_i. Exhaustive: 2^n grounded computations per agent.
* Theorem 5.4 condition, odd-length path on graphs with cycles: default `mode="walk"` allows repeated nodes
  (BFS over (node, parity) states, so cycles terminate); `mode="simple"` uses simple paths only. Both are reported.
  "Two arguments" is read as alpha != beta.
* Random instances: n uniform in {6,7,8}; each ordered pair (a,b), a != b, is an attack with probability p; every argument is
  assigned to one of 3 agents uniformly at random (an agent can end up with no argument). A variant with self-attacks allowed is also run.
* Seeds are fixed (2024), so results are reproducible.

## Note on the book examples
The assignment PDF does not contain the book's examples, so `demo.py` uses standard Dung examples (chain, even cycle, odd cycle,
stable vs semi-stable, self-attacker) and a hand-built strategic example. To test on the book's frameworks, just pass them to
`ArgumentationFramework(args, attacks)` / `mechanism(...)`.
