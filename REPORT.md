# Report – Argumentation Engine and Strategic Argumentation

## 1. Implementation summary
**Part 1** (`argumentation.py`). `ArgumentationFramework(A, attacks)` offers: `is_conflict_free`, `defends(S,a)` (every attacker of a is attacked by S),
`characteristic(S)` = F(S), `is_admissible` (cf and S ⊆ F(S)), `is_complete` (cf and S = F(S)), `grounded_extension` (least fixed point, iterating F from ∅),
`complete_extensions`, `preferred_extensions` (⊆-maximal admissible), `stable_extensions` (cf and S ∪ S⁺ = A), `semi_stable_extensions`
(admissible with ⊆-maximal range S ∪ S⁺), `labellings` (all legal in/out/undec labellings: in ⇔ all attackers out; out ⇔ some attacker in; undec otherwise),
and `acceptance_status` (skeptically / credulously accepted / rejected). Correctness is tested (`tests.py`) on 300 random frameworks:
grounded is the least complete extension; every complete extension is admissible; preferred extensions exist and are complete; stable ⊆ preferred;
if a stable extension exists then semi-stable = stable; labellings are in bijection with complete extensions; labellings without `undec` ↔ stable extensions.
Demonstrated on Dung's chain, even cycle, odd cycle, a stable/semi-stable example and a self-attacker (`demo_output.txt`).

**Part 2** (`strategic.py`).
1. `mechanism(attacks, reports)`: grounded extension of the subgraph induced by the union of the revealed sets.
2. `best_responses(i, agents, attacks, others_reports)`: enumerates all 2^|A_i| reports, returns the maximal utility and all maximising reports.
3. `check_truthfulness(agents, attacks)`: for every agent and every combination of subsets of the others' sets, compares the utility of revealing all of A_i
   with every sub-report; returns a counterexample (agent, others' reports, deviation, utilities) on failure. This is the "revealing everything is a (dominant) best response" test, i.e. strategyproofness.
   For speed it uses a bitmask grounded computation, cross-checked against the class-based version in `tests.py`.
4. `theorem_5_4_condition(agents, attacks)`: true iff no agent holds α ≠ β joined by an odd-length directed path in the full graph.
   **Cycles:** a path in a cyclic graph can be read as a walk or as a simple path. Walks are handled by BFS over (node, parity) states (terminates on cycles);
   simple paths by DFS. Both readings were run in the experiments.

## 2. Experimental setup
For each p ∈ {0.15, 0.25, 0.35}: 1000 random instances; n uniform in {6,7,8}; each ordered pair of distinct arguments is an attack with probability p;
each argument is assigned uniformly at random to one of 3 agents. Strategyproofness is decided exhaustively (no sampling). Seed 2024.
A variant that also allows self-attacks was run for robustness. Raw data: `results/`.

## 3. Results

**(1) Fraction of strategyproof instances** (main setting):

| p | strategyproof | Thm 5.4 condition holds (walk) | (simple path) |
|---|---|---|---|
| 0.15 | **0.632** (632/1000) | 118 | 120 |
| 0.25 | **0.317** (317/1000) | 31 | 33 |
| 0.35 | **0.126** (126/1000) | 4 | 5 |

With self-attacks allowed: 0.535, 0.254, 0.101. Strategyproofness drops sharply as the graph gets denser, since more odd paths between an agent's arguments appear and more arguments become vulnerable.
Note that with 6–8 arguments split over 3 agents, a fair share of instances are small or have agents with few arguments, which makes strategyproofness easy at low p.

**(2) Condition holds but not strategyproof: 0 instances** in all three p values, for both the walk and the simple-path reading, with and without self-attacks
(0 of 3000 and 0 of 3000). This agrees with Theorem 5.4, which states that the condition is *sufficient* for strategyproofness. There is therefore nothing to explain
here, and the code gives an independent empirical validation of the theorem (including its cycle handling: the simple-path reading, which makes the condition *easier* to satisfy, also produced no counterexample).
If a counterexample ever appeared it would indicate a bug or a different reading of "path"; `results/notable_instances.json` has a slot `cond_holds_not_sp` for it (empty).

**(3) Strategyproof although the condition fails: many** (walk reading): 514 / 286 / 122 instances for p = 0.15 / 0.25 / 0.35
(512 / 284 / 121 with the simple-path reading). So the condition is sufficient but far from necessary: among instances where it fails,
the large majority are still strategyproof (e.g. 514 of 632 strategyproof instances at p=0.15 do not satisfy it).

*Why are they strategyproof?* An odd path α ⇝ β only gives a **possibility** of manipulation: hiding α (or something on the path) can flip β.
It becomes a **profitable** manipulation only if the agent loses less than it gains, and in all cases of the data it does not. Classification
(`analyse.py`, `run_experiments.py`):

* **Swap / zero-sum (≈ 85%: 445/514, 243/286, 103/122).** A deviation exists that changes which of the agent's arguments are accepted, but the utility is unchanged.
  Typical case α→β, α ∈ grounded, β out: hiding α releases β but loses α: −1 +1 = 0. Truthful is still a (non-unique) best response, so the mechanism is strategyproof in the weak sense used here.
* **Redundancy.** Example (from the random data): agent 1 holds {a3,a4,a5} with a3→a4 and a5→a4. The condition fails (odd paths a3⇝a4, a5⇝a4). Truthful: a3,a5 in, a4 out → utility 2. Hiding a3 does not free a4 (a5 still attacks it) and costs a3 → 1.
* **Chain cost.** Agent 0 holds {a2,a3,a4,a5} with a5→a4→a2 (odd paths a5⇝a4, a4⇝a2). Truthful: a5, a2, a3 in → 3. Hiding a5 flips the chain: a4 in, a2 out → {a3,a4} = 2. The hidden argument and the knock-on effects cost more than what is released.
* **Endpoints already settled.** In the full graph α and β are in/out/undec in a way hiding cannot improve (e.g. β is already in, or β stays out because of another attacker). The instances without any swap deviation (69/43/19) are of this type or of the redundancy / chain-cost type.

A gain needs: (i) hiding something that is cheap (an argument that is out or undecided anyway), and (ii) which releases an own argument that is otherwise blocked. The condition only checks that the structure for (i)+(ii) *could* exist, not that it does with positive net value, and it ignores the other agents' possible reports, so it is conservative.

**Example of failing condition and not strategyproof** (the converse direction is the "interesting" one for the theorem). Hand-built (`demo.py`): agent 1 = {α, β}, agent 2 = {d, e}, attacks α→β, α→d, d→e, e→α.
α, d, e form an odd cycle, so all arguments are undecided; utility of agent 1 is 0. If agent 1 hides α, then d→e leaves d in, e out, and β becomes accepted: utility 1. The odd path α→β (length 1) is exactly what Theorem 5.4 forbids.
Moving each argument to a separate agent makes the condition hold vacuously and the mechanism strategyproof (also in `demo.py`).

## 4. Remarks
* Book examples: the assignment PDF does not include them, so the demonstration uses standard examples; the book's frameworks can be plugged in directly.
* The misprints mentioned in the assignment do not affect the code: utilities are computed from each agent's own true set, and the argument that cancels the indirect self-defeat is just another argument of the input.
* Limits: brute-force enumeration (2^n subsets, 3^n labellings) is fine for the n ≤ 8 required but not scalable.
