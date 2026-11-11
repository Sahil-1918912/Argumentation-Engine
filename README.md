# Argumentation Engine & Strategic Argumentation

Pure Python 3 (standard library only, nothing to install). Developed and tested on Python 3.11.

## Layout
`README.md` and `REPORT.md` are in the repository root; **all code, tests, demo files and results are in `af_project/`**.

## Files (inside `af_project/`)
| File | Content |
|---|---|
| `argumentation.py` | **Part 1.** `ArgumentationFramework` class: conflict-free, `defends`, characteristic function, admissible / complete, grounded, complete / preferred / stable / semi-stable extensions, legal labellings, acceptance status. Function-style wrappers at the bottom. |
| `strategic.py` | **Part 2.** `mechanism`, `best_responses`, `check_truthfulness` (Theorem 5.3, best-response form), `check_theorem_5_3` (Theorem 5.3, literal inequality form), `is_strategyproof`, `theorem_5_4_condition`, `find_odd_path` / `odd_path_exists`, `explain_violations`, `validate_instance`. |
| `book_examples.py` | The book's Examples 5.10 and 5.11 (Figures 5.4, 5.5) as data, with the misprints documented. |
| `experiments.py` | Random instance generator + per-instance records. |
| `analyse.py` | Classifies *why* an instance is strategyproof although the Theorem 5.4 condition fails (swap / loss-only / inert). |
| `run_experiments.py` | Runs the whole experiment and writes `results/`. |
| `tests.py` | 14 test groups: known results, book examples, cross-checks between independent implementations. |
| `demo.py`, `demo_output.txt` | Demonstration script and its captured output. `DEMO.md` is a talk-through guide for the demonstration. |
| `results/` | `results.md` (tables), `instances.json` (all 3000 main-setting instances), `notable_instances.json` (concrete examples). |

## Run
Open a terminal in the repository root, then:
```
cd af_project
python tests.py              # all tests (a few seconds)
python demo.py               # demonstration (prints only; to save: python demo.py > demo_output.txt)
python run_experiments.py    # 1000 instances per p, main + self-attack variant (about 1-2 minutes); optional arg = N
```

## Usage
```python
from argumentation import ArgumentationFramework as AF
af = AF("abc", {("a","b"), ("b","c")})        # a attacks b, b attacks c
af.grounded_extension(); af.complete_extensions(); af.all_extensions()
af.extensions("stable")                        # one semantics only
af.labellings()
af.acceptance_status("a")                      # 'skeptically accepted' (preferred semantics by default)
af.acceptance_status("a", "stable")            # any of: grounded complete preferred stable semi-stable
af.acceptance_by_semantics("a")                # the status under all five

from strategic import *
agents  = {1: frozenset({"x","y"}), 2: frozenset({"z"})}   # TRUE argument sets (must be disjoint)
attacks = {("x","z"), ("z","y")}
mechanism(attacks, {1: {"x"}, 2: {"z"}})                    # grounded ext. of the revealed graph
best_responses(1, agents, attacks, {2: agents[2]})          # (best utility, [best reports])
check_truthfulness(agents, attacks)                         # (True, None) or (False, counterexample)
check_theorem_5_3(agents, attacks)                          # same question, literal formulation
theorem_5_4_condition(agents, attacks, mode="walk")         # (holds, violating (agent, a, b) triples)
explain_violations(agents, attacks)                         # ... with a witness odd path for each
```

## Design decisions
* **Brute force** for semantics (subsets / 3^n labellings): clear and fine for n <= ~12.
* **Semi-stable** = admissible set whose range S u S+ is maximal w.r.t. inclusion.
* **Acceptance status** is computed under ONE semantics at a time (default preferred). "Rejected" means *in no extension of that semantics*.
  If the semantics has **no extension at all** (only possible for stable) the result is the explicit label
  `NO_EXTENSIONS` = "undefined (no extension under this semantics)": skeptical acceptance would be vacuously true and credulous acceptance false, so none of the
  three requested labels would be honest.
* **Utility** of agent i = |grounded extension n A_i| with A_i the agent's **true** set (this also makes the Example 5.10 misprint irrelevant).
* **Truthfulness / Theorem 5.3.** Two independent implementations: `check_truthfulness` (bitmask grounded, best-response formulation, used in the
  experiments) and `check_theorem_5_3` (class-based grounded, the book's inequality verbatim). `tests.py` checks that they agree on 150 random instances.
* **Input validation.** The agents' true sets must be pairwise **disjoint** and every attack must be between owned arguments; otherwise `ValueError`
  (the exhaustive search relies on disjointness: the union of the reports determines who revealed what).
* **Theorem 5.4 on graphs with cycles.** "Odd-length path" is ambiguous when cycles exist, so both readings are implemented:
  `mode="walk"` (nodes may repeat; BFS over (node, parity) states, so it terminates; this is the default) and `mode="simple"` (no repeated node).
  "Two arguments" is read as alpha != beta. Both readings are reported in the experiments.
* **Random instances.** n uniform in {6,7,8}; each ordered pair (a,b), a != b, is an attack with probability p in {0.15, 0.25, 0.35}; every argument goes to one
  of 3 agents uniformly at random (an agent can end up with none). A variant that also allows self-attacks is run. Fixed seed (2024) -> reproducible.

## Report
`REPORT.md` (repository root): definitions, design, verification on the book's examples, experimental results and explanations.
