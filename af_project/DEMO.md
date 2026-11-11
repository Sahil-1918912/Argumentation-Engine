# Demonstration guide (for the recording)

Everything on screen comes from `python demo.py` (saved copy: `demo_output.txt`), plus `python tests.py` and `results/results.md`.
Suggested order (about 8–10 minutes). "Say" = key point to make; "Show" = what is on screen.

0. **Setup (30 s).** Show the folder, say it is pure Python, no installs. Run `python tests.py` → ends with `ALL TESTS PASSED`.
   Say: tests include the book's two examples and cross-check independent implementations.

1. **Section A – Part 1 on small frameworks (2 min).**
   * A1 chain a→b→c: grounded {a,c}; one labelling.  *Say:* the grounded extension is built by iterating F from ∅.
   * A2 even cycle a↔b: grounded ∅, complete {∅,{a},{b}}, preferred/stable {a},{b}; three labellings (in/out, out/in, undec/undec); acceptance "credulously accepted" under preferred, "rejected" under grounded.
   * A3 odd cycle: **no stable extension**, so acceptance under stable is printed as `undefined (no extension under this semantics)` – *say why* (skeptical would be vacuously true, credulous false).
   * Q2–Q5 block on the chain a→b→c→d: conflict-free, defends, F(∅)={a}, F({a})={a,c}, {a,c} admissible and complete, {a} admissible but not complete.

2. **Section B/C – the book's Example 5.10 (3 min).**
   * Outcome {a1,a3}; utilities x=1, y=0, z=1. *Mention misprint 1* (book swaps y and z's sets).
   * x hides a1 → outcome {a2,a4,a5}, utility 2 (Figure 5.4(b)). `best_responses` for x: utility 2 with report {a4,a5}.
   * Theorem 5.3 check says **False**, with the counterexample; the literal-inequality version agrees. Theorem 5.4 condition fails; show the printed witness paths a1→a2→a3→a4 and a1→a2→a3→a5.

3. **Example 5.11 (1.5 min).** Strategyproof = True although the condition fails: sufficient, not necessary.
   *Mention misprint 2*: the protecting argument is **a6** (it kills a3), not a5.

4. **Section D – Theorem 5.4 cases (1 min).** (i) condition holds, non-vacuous: a→c→b, even path → strategyproof. (ii) alpha/beta/d/e example: condition fails and not strategyproof; hiding alpha frees beta.
   (iii) same graph, one argument per agent → vacuously true and strategyproof.

5. **Section E – cycles (45 s).** Walk vs simple path; the BFS over (node, parity) terminates on cycles.

6. **Experiments (1.5 min).** Open `results/results.md` (do not rerun live unless asked; it takes 1–2 minutes with `python run_experiments.py`).
   * Fractions strategyproof: 0.632 / 0.317 / 0.126 for p = 0.15 / 0.25 / 0.35.
   * Condition holds but not SP: 0 in every column – consistent with Theorem 5.4.
   * SP but condition fails: 514 / 286 / 122; classified by `analyse.py` into swap (≈85 %) and loss-only (≈15 %); show one example of each from `results/notable_instances.json` (`sp_cond_fails_by_class`).

Close with limitations (brute force, small n) and where each assignment item lives (table in README/REPORT).
