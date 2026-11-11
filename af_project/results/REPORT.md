# Argumentation Engine and Strategic Argumentation
## Autonomous Systems Assignment Report

Authors: 
- Sarah Fatima (B23EE1093)
- Sahil Narkhede (B23CS1060)
- Namya Dhingra (B23CS1040)
- Anshit Agarwal (B23CS1087)

Date: 11 November 2026

**Summary.** We implemented (i) an engine for Dung-style abstract argumentation frameworks (conflict-freeness, defence, the characteristic function,
admissible / complete / grounded / preferred / stable / semi-stable extensions, in/out/undec labellings, acceptance status) and (ii) the grounded direct
argumentation mechanism together with checks for Theorems 5.3 and 5.4 of the book. Both parts are validated on the book's Examples 5.10 and 5.11 and by
cross-checks between independent implementations. In 3000 random 3-agent instances (6–8 arguments, p = 0.15 / 0.25 / 0.35) the fraction of strategyproof
instances fell from 63.2 % to 12.6 % as p increased; the Theorem 5.4 condition never held for a non-strategyproof instance (0 cases), and 514 / 286 / 122
instances were strategyproof although the condition fails, mostly because hiding an argument only swaps one accepted argument for another.

Code, tests, demo and raw results are in the `af_project/` folder; see `README.md` for how to run them. All numbers below are produced by that code
(fixed seed 2024) and can be regenerated.

**Contents:** 0 Notation · 1 Background · 2 Implementation · 3 Verification on the book's examples · 4 Experiments · 5 Limitations · 6 Reproducing

---------------------------------------------------------------------------------------------------

## 0. Notation used in this report (plain-text legend)

| Symbol | Meaning |
|---|---|
| A | set of arguments of a framework |
| `a -> b` | "a attacks (defeats) b"; the attack relation is a set of such pairs (the book's R) |
| S⁺ | all arguments attacked by some member of S |
| F(S) | characteristic function: the set of arguments that S defends |
| E_GR(AF) | grounded extension of AF |
| A_i | agent i's **true type**: the arguments agent i owns (disjoint between agents) |
| report / A°_i | the subset of A_i that agent i actually reveals |
| A_-i | the union of what all the *other* agents reveal |
| o | outcome of the mechanism = grounded extension of the revealed arguments |
| u_i(o) = \|A_i ∩ o\| | utility of agent i = how many of its **own true** arguments are accepted |
| α ⇝ β | "α indirectly defeats β": an **odd-length** directed path from α to β exists |

---------------------------------------------------------------------------------------------------

## 1. Background: what is being computed

### 1.1 Part 1 – Dung argumentation frameworks (AF = ⟨A, →⟩)

* **Conflict-free** S: no member of S attacks another member (or itself).
* **S defends a**: every attacker of a is itself attacked by some member of S. (An unattacked argument is defended by every set, including ∅.)
* **Characteristic function** F(S) = { a | S defends a }. F is monotone (bigger S defends more).
* **Admissible**: conflict-free and S ⊆ F(S) (S defends all of its own members).
* **Complete extension**: conflict-free and S = F(S) (S contains exactly what it defends).
* **Grounded extension**: the *least* fixed point of F, found by iterating ∅, F(∅), F(F(∅)), … until nothing changes. It is unique, and it is the smallest complete extension.
* **Preferred**: ⊆-maximal admissible sets. **Stable**: conflict-free S that attacks every argument outside it (S ∪ S⁺ = A).
  **Semi-stable**: admissible S whose range S ∪ S⁺ is ⊆-maximal.
* **Labellings** (in / out / undec): *in* ⇔ all attackers are *out*; *out* ⇔ at least one attacker is *in*; *undec* otherwise.
  Legal labellings correspond one-to-one to complete extensions (the set of *in* arguments); labellings with no *undec* correspond to stable extensions.
* **Acceptance status** of an argument under a chosen semantics: *skeptically accepted* (in every extension), *credulously accepted* (in some, not all), *rejected* (in none).

### 1.2 Part 2 – grounded direct argumentation mechanism

Every agent i owns a set A_i of arguments (its type). A global attack relation R is public. Each agent reports a subset of A_i (it may **hide**
arguments but may not invent any). The mechanism builds the graph induced by the union of the reports and outputs its **grounded extension** o.
An agent with *acceptability-maximising preferences* (book, Def. 5.22) values an outcome by the number of its own true arguments in o: u_i(o) = |A_i ∩ o|.

* **Strategyproof** here means: for every agent and every combination of what the others reveal, revealing all of A_i is a best response (no other report gives strictly higher utility).
* **Theorem 5.3** (exact characterisation): the mechanism is strategyproof iff for all agents i, all S ⊆ A_i and all A_-i:
  |A_i ∩ E_GR(⟨A_i ∪ A_-i, R⟩)| ≥ |A_i ∩ E_GR(⟨(A_i \ S) ∪ A_-i, R⟩)|. In words: hiding any part S of your own arguments never increases the number of accepted own arguments.
* **Theorem 5.4** (sufficient condition): if no agent owns two arguments α₁, α₂ with α₁ ⇝ α₂ (an odd-length path in the **full** graph, i.e. the agent's own
  arguments are neither directly nor indirectly in conflict), the mechanism is strategyproof. *Sufficient, not necessary* (Example 5.11).

---------------------------------------------------------------------------------------------------

## 2. Implementation – where each assignment item lives

### Part 1 (`af_project/argumentation.py`)
| Assignment item | Code |
|---|---|
| 1. framework class | `ArgumentationFramework(arguments, attacks)` (validates that attacks use known arguments) |
| 2. conflict-free | `is_conflict_free(S)` |
| 3. S defends a | `defends(S, a)` |
| 4. characteristic function | `characteristic(S)` |
| 5. admissible / complete | `is_admissible(S)`, `is_complete(S)` |
| 6A. grounded | `grounded_extension()` |
| 6B. all complete | `complete_extensions()` |
| 6C. preferred, stable, semi-stable | `preferred_extensions()`, `stable_extensions()`, `semi_stable_extensions()`; `all_extensions()` returns all five; `extensions(name)` returns one |
| 6D. labellings | `labellings()` (all 3ⁿ assignments are tested against the in/out/undec rules) |
| 6E. acceptance status | `acceptance_status(a, semantics)`, `acceptance_by_semantics(a)` |

Design points that are easy to get wrong (and what we did):
* `acceptance_status` computes only the semantics asked for (earlier it recomputed all five on every call).
* **No-extension case.** Only stable semantics can have *no* extension. Skeptical acceptance over an empty family is vacuously true and credulous acceptance is
  false, so the three standard labels would be misleading. The function returns the explicit label `NO_EXTENSIONS` ("undefined (no extension under this semantics)"). Example: the 3-cycle a→b→c→a has no stable extension (shown in `af_project/demo_output.txt`, A3).
* "Rejected" means *in no extension of the chosen semantics*. Under preferred semantics an argument can be "rejected" although it is *undecided* in the grounded labelling (odd cycle: all three are rejected).

### Part 2 (`af_project/strategic.py`)
| Assignment item | Code |
|---|---|
| 1. the mechanism | `mechanism(attacks, reports)` – grounded extension of the subgraph induced by the union of the reports |
| 2. best responses | `best_responses(agent, agents, attacks, others_reports)` – enumerates all 2^\|A_i\| reports, returns (best utility, all maximising reports) |
| 3. Theorem 5.3 check | `check_truthfulness` (revealing everything is a best response against every combination of the others' subsets) and, independently, `check_theorem_5_3` (the book's inequality verbatim) |
| 4. Theorem 5.4 check | `theorem_5_4_condition(agents, attacks, mode)`; `find_odd_path` returns a *witness* path; `explain_violations` lists violations with witnesses |

* `check_truthfulness` uses a bitmask grounded-extension routine for speed; `af_project/tests.py` verifies it equals the class-based version on 200 random cases.
* `check_theorem_5_3` is deliberately slow and uses only the class-based code, so it is an independent implementation. Theorem 5.3 says the two must agree; `af_project/tests.py` confirms they agree on 150 random instances (61 strategyproof, 89 not – both outcomes were exercised).
* **Input validation**: the agents' true sets must be disjoint and attacks must only mention owned arguments, otherwise `ValueError`. (The exhaustive check enumerates the others' reports through the *union* of their arguments, which only identifies reports uniquely if the sets are disjoint.)
* **Cycles in the odd-path test.** In a cyclic graph "a path" can mean a *walk* (nodes may repeat) or a *simple path* (no repeated node). We implement both.
  The walk search is a breadth-first search over states (node, parity of length so far); there are only 2·n states, so it terminates even though cycles give infinitely many walks.
  Example from `af_project/demo_output.txt` (3-cycle x→y→z→x plus x→b): there is an odd walk y ⇝ x (y,z,x,y,z,x, length 5) but no odd simple path.
  The walk reading flags *more* violations, so the condition holds in slightly fewer instances than under the simple-path reading.
  "Two arguments" is read as α ≠ β.

---------------------------------------------------------------------------------------------------

## 3. Verification on the book's examples

Arguments α₁…α₆ are written a1…a6 in the code. Defeat relation of Example 5.10: R = {(a1,a2), (a2,a3), (a3,a4), (a3,a5)}. Types: A_x = {a1,a4,a5}, A_y = {a2}, A_z = {a3}.
Everything below is asserted in `af_project/tests.py` (`test_book_example_5_10`, `test_book_example_5_11`) and printed in `af_project/demo_output.txt`, section B/C.

**Example 5.10 / Figure 5.4(a)** (all truthful): grounded extension a1 in; a2 out (attacked by in a1); a3 in (its only attacker a2 is out); a4, a5 out (attacked by in a3).
Outcome o = {a1, a3}, matching the book. Every semantics (complete, preferred, stable, semi-stable) gives that same single extension. Utilities: u_x = 1, u_y = 0, u_z = 1.

**Misprint 1 (assignment).** The book prints "u_y(o,{a3}) = 1; u_z(o,{a2}) = 0", attaching each agent to the *other's* argument set. With the right sets u_y = |{a1,a3} ∩ {a2}| = 0 and u_z = |{a1,a3} ∩ {a3}| = 1.
The code computes utility from each agent's own true set, so it reproduces the corrected values without special treatment.

**Figure 5.4(b), x hides a1.** Revealed arguments {a2,a3,a4,a5}: a2 unattacked → in; a3 out; a4, a5 in. Outcome {a2,a4,a5}, u_x = 2 > 1. `best_responses` for x (others truthful) returns utility 2 with the single best report {a4,a5} – exactly the book's claim.
For y and z, revealing the truth is among the best responses (book: "weakly dominates revealing nothing"). Hence the mechanism is **not strategyproof** – both `check_truthfulness` and `check_theorem_5_3` return the counterexample (agent x, others y and z truthful).
Theorem 5.4's condition fails too, with witnesses a1→a2→a3→a4 and a1→a2→a3→a5 (odd length 3, both endpoints owned by x). This is the "implicit conflict" the book describes: y and z's arguments reveal that x's own a1 indirectly defeats a4 and a5.

**Example 5.11 / Figure 5.5.** Add a6 (owned by x) and the defeat (a6,a3). Truthful outcome: a1 in, a2 out, a6 in, a3 out (attacked by a6), a4, a5 in → o = {a1,a4,a5,a6}; u_x = 4 of 4 (matches the book).
Both strategyproofness checks return **True**, yet Theorem 5.4's condition **fails** (same odd paths a1⇝a4, a1⇝a5). This is the book's point that 5.4 is sufficient but not necessary.

**Misprint 2 (assignment).** After Example 5.11 the book says the argument that cancels the indirect self-defeat is α₅; it is **α₆**. The reason: a6 is unattacked, so while x reveals it a6 is *in* and forces a3 *out*;
then the chain a1→a2→a3 can never knock out a4 or a5, so hiding a1 would only cost x an argument. (a5 is one of the arguments being *protected*, not the protector.) The code takes arguments from the input and is unaffected.

### Other tests (`python tests.py`, all pass)
* Hand-checked classic frameworks (chain, even cycle, odd cycle, self-attacker, stable-vs-semi-stable cases, semi-stable-but-not-stable, preferred-but-not-semi-stable).
* 300 random frameworks: grounded is the least complete extension; complete ⊆ admissible; preferred exist and are complete; stable ⊆ preferred; semi-stable ⊆ preferred; if a stable extension exists then semi-stable = stable; labellings are in bijection with complete extensions; labellings without *undec* are exactly the stable extensions.
* `acceptance_status` incl. the no-stable-extension label and error handling; `defends`, `characteristic`, `is_admissible`, `is_complete` unit tests.
* Odd-path search: BFS result compared with a brute-force walk enumeration on 100 random graphs; returned witnesses are checked to be genuine odd walks.
* Theorem 5.3 literal vs. best-response check agree (150 instances); Theorem 5.4: on 232 random condition-satisfying checks (both path readings) the instance was always strategyproof.

---------------------------------------------------------------------------------------------------

## 4. Experiments

### 4.1 Setup
3 agents; per instance n ∈ {6,7,8} arguments (uniform); every ordered pair (a,b), a ≠ b, is an attack with probability p; each argument is assigned to one of the 3 agents uniformly at random
(an agent may get none). p ∈ {0.15, 0.25, 0.35}; **1000 instances per p** (3000 in total; seed 2024). Strategyproofness is decided **exhaustively**
(every agent × every combination of the others' subsets × every own subset; no sampling). A second run allows self-attacks (a,a) as well (the assignment's "each possible attack" is ambiguous on this).
Raw data: `af_project/results/instances.json`; tables: `af_project/results/results.md`.

### 4.2 Result 1 – fraction of strategyproof instances

| p | strategyproof (main) | with self-attacks allowed |
|---|---|---|
| 0.15 | **0.632** (632/1000) | 0.535 |
| 0.25 | **0.317** (317/1000) | 0.254 |
| 0.35 | **0.126** (126/1000) | 0.101 |

Strategyproofness falls steeply as the graph gets denser: more attacks create more odd paths between an agent's own arguments, so there are more arguments whose acceptance can be influenced by hiding something.
Note also that with only 6–8 arguments over 3 agents many agents hold very few arguments, which makes strategyproofness easy at small p.

### 4.3 Result 2 – condition holds but not strategyproof: **0 instances**

| p | condition holds (walk) | … and not strategyproof | condition holds (simple) | … and not strategyproof |
|---|---|---|---|---|
| 0.15 | 118 | **0** | 120 | **0** |
| 0.25 | 31 | **0** | 33 | **0** |
| 0.35 | 4 | **0** | 5 | **0** |

(Also 0 with self-attacks allowed: 84/12/1 walk-satisfying and 99/16/1 simple-satisfying instances, none non-strategyproof.)
There is nothing to explain away: Theorem 5.4 says the condition is *sufficient* for strategyproofness, so a counterexample would mean a bug or a different reading of "path". The experiment is an independent empirical confirmation,
including for cyclic graphs and for both readings (the simple-path reading is the easier-to-satisfy condition, and it also yields no counterexample). Note that the check is only as strong as the number of condition-satisfying instances (only 4–5 at p = 0.35).
`af_project/results/notable_instances.json` has an empty slot `cond_holds_not_sp` that would hold any counterexample.

### 4.4 Result 3 – strategyproof although the condition fails: many

| p | strategyproof & condition fails (walk) | (simple) | share of all strategyproof instances |
|---|---|---|---|
| 0.15 | **514** | 512 | 514/632 = 81% |
| 0.25 | **286** | 284 | 286/317 = 90% |
| 0.35 | **122** | 121 | 122/126 = 97% |

So the condition is very far from necessary; at high density it is almost never satisfied, yet one instance in eight is still strategyproof.

**Why are they strategyproof?** An odd path α ⇝ β between two of an agent's own arguments only creates the *possibility* of manipulation. Hiding (something on the path)
can flip β from out to in – but it must also be profitable: what the agent gains must exceed what it loses by hiding. In grounded semantics the gain and the loss are tied together, so very often they cancel.
Every deviation (agent hides a strictly smaller part of its arguments, against a combination of the others' reports) was classified by comparing the agent's accepted own arguments, truthful versus after hiding (`af_project/analyse.py`):

* **same** – the accepted own arguments are identical;
* **swap** – the *set* of accepted own arguments changes but its *size* (utility) is equal: the agent loses one argument and releases another;
* **loss** – utility is strictly lower.

(No deviation can have strictly higher utility in a strategyproof instance.) Each strategyproof instance with a failing condition is labelled by the most interesting deviation it contains: **swap** > **loss-only** > **inert**:

| p | #SP & cond fails | swap | loss-only | inert |
|---|---|---|---|---|
| 0.15 | 514 | 445 (87%) | 69 | 0 |
| 0.25 | 286 | 243 (85%) | 43 | 0 |
| 0.35 | 122 | 103 (84%) | 19 | 0 |

(With self-attacks allowed: swap/loss-only/inert = 330/121/0, 155/87/0, 47/53/0 for p = 0.15/0.25/0.35.)

* **Swap (zero-sum), ≈ 85 %.** Smallest example (from the data, p = 0.15): agent 1 owns {a1,a2,a4,a5}, the only attack is a5→a4, agent 0 owns {a3,a6}, agent 2 owns nothing. The condition fails because a5 ⇝ a4 (length 1) are both agent 1's.
  Truthfully a1, a2, a5 are accepted (a4 is out) → utility 3. If agent 1 hides a5, then a4 is freed: accepted {a1,a2,a4} → utility 3 again. It *can* change which arguments are accepted, but never gains: truthful is still a (non-unique) best response, which is all strategyproofness (weak, as in the book) requires.
  In general: α attacks β, α accepted, β out; hiding α releases β but loses α, −1 + 1 = 0.
* **Loss-only, ≈ 15 %.** Smallest example (p = 0.15): agent 1 owns {a3,a4,a5}, attacks a3→a4 and a5→a4 (agent 0 owns {a1,a2,a6}). The condition fails (a3 ⇝ a4, a5 ⇝ a4), but a4 has *two* attackers: hiding a3 leaves a5 attacking a4 and costs a3 (utility 2 → 1). Only hiding both would free a4 (utility 1). The redundant attacker blocks every attempt to gain.
* **Inert: 0** in this data – in every strategyproof instance whose condition fails, at least one deviation does change which of the agent's arguments are accepted (either as a swap or as a loss).

In short: a manipulation needs (i) something cheap to hide whose absence (ii) releases an own argument that is otherwise blocked, with net gain > 0. The Theorem 5.4 condition only detects that a structure for (i)+(ii) *could* exist; it ignores whether the net value is positive and ignores which reports the other agents will make.
The book's Example 5.11 is the hand-made version of the same phenomenon: the extra argument a6 forces the blocking argument a3 to be out, so the indirect self-defeat never materialises.

### 4.5 Example: condition fails *and* the mechanism is not strategyproof
Example 5.10 itself (above), and a smaller hand-made one in `af_project/demo.py` (section D): agent 1 owns {α,β}, agent 2 owns {d,e}, attacks α→β, α→d, d→e, e→α.
α, d, e form an odd cycle, so all of them are undecided under grounded semantics and so is β: utility 0. If agent 1 hides α, then d→e leaves d in, e out, and β becomes accepted: utility 1. The violating odd path is α→β.
Splitting all arguments over four different agents makes the condition hold vacuously (nobody owns two arguments), and the mechanism is strategyproof (also in `af_project/demo.py`).
A non-vacuous satisfying example: agent 1 owns {a,b}, agent 2 owns {c}, attacks a→c→b – the only path a ⇝ b has even length 2, the condition holds, and the mechanism is strategyproof.

---------------------------------------------------------------------------------------------------

## 5. Limitations and remarks
* Semantics are brute force (2ⁿ subsets, 3ⁿ labellings); fine for the n ≤ 8 required (and up to roughly n = 12–14) but not scalable. The strategyproofness check is exponential too: for each agent it enumerates every combination of the others' subsets and its own subsets.
* The parameters 0.15 / 0.25 / 0.35 are the three values of p used; the results should be read as a function of p and of the "random split" model (an agent can have 0 or 1 arguments, and such an agent can never gain by hiding), not as a property of argumentation in general.
* Two readings of "odd path" on cyclic graphs are reported side by side; they differ in only 2/2/1 instances (p = 0.15/0.25/0.35), so no conclusion depends on the choice.
* Strategyproofness is the *weak* notion used in the book: truthful reporting is *a* best response, not necessarily the only one (this is exactly why swap deviations do not break it).
* The assignment’s condition concerns pairs α ≠ β, which is what we check. With self-attacks allowed (a possible reading of ‘each possible attack’), a self-attacking argument additionally makes its owner’s type non-conflict-free in the book’s formulation; we report that setting alongside the main one and find the same pattern (0 violations of the theorem).
* Theorem 5.4 is taken from the book; our experiment can confirm it empirically but does not prove it.

## 6. Reproducing
From the `af_project/` folder: `python tests.py`, `python demo.py`, `python run_experiments.py` (see `README.md`). Instances are generated with `random.Random(2024)`, so every number above is reproducible.
