"""Demonstration script.  Run:  python demo.py      (output saved in demo_output.txt)

  Section A  Part 1 on small classic frameworks (+ the Q2-Q5 building blocks)
  Section B  Part 1 on the book's Example 5.10 graph
  Section C  Part 2 on the book's Examples 5.10 and 5.11 (Figures 5.4 and 5.5)
  Section D  Theorem 5.4: a case where the condition HOLDS (non-vacuously) and a case where it FAILS
  Section E  Cycle handling for the odd-path test
"""
from argumentation import ArgumentationFramework as AF
from strategic import (mechanism, utility, best_responses, check_truthfulness, check_theorem_5_3,
                       is_strategyproof, theorem_5_4_condition, explain_violations,
                       find_odd_path, odd_path_exists)
import book_examples as B


def show(S): return "{" + ",".join(sorted(map(str, S))) + "}"
def title(t): print("\n" + "=" * 78 + f"\n{t}\n" + "=" * 78)


def part1(name, args, attacks):
    af = AF(args, attacks)
    print(f"\n--- {name}\n{af}")
    print("grounded      :", show(af.grounded_extension()))
    for sem, exts in af.all_extensions().items():
        if sem != "grounded":
            print(f"{sem:14}:", [show(E) for E in exts])
    print("labellings    :")
    for lab in af.labellings():
        print("   ", dict(sorted(lab.items())))
    print("acceptance    :")
    for a in sorted(af.arguments, key=str):
        print(f"   {a}: {af.acceptance_by_semantics(a)}")
    return af


# ---------------------------------------------------------------------------------- A
title("A. PART 1 - ARGUMENTATION ENGINE (classic frameworks)")
part1("A1: chain a->b->c", "abc", {("a", "b"), ("b", "c")})
part1("A2: even cycle a<->b", "ab", {("a", "b"), ("b", "a")})
part1("A3: odd cycle a->b->c->a   (no stable extension -> acceptance is 'undefined' under stable)",
      "abc", {("a", "b"), ("b", "c"), ("c", "a")})
part1("A4: b kills c, but c-d-e is an odd cycle", "abcde",
      {("a", "b"), ("b", "a"), ("b", "c"), ("c", "d"), ("d", "e"), ("e", "c")})
part1("A5: self-attacker a", "abc", {("a", "a"), ("c", "a"), ("a", "b")})
af = AF("abcd", {("a", "b"), ("b", "c"), ("c", "d")})
print("\n--- Q2-Q5 building blocks on the chain a->b->c->d")
print(" {a,c} conflict-free:", af.is_conflict_free({"a", "c"}), "| {a,b} conflict-free:", af.is_conflict_free({"a", "b"}))
print(" {a} defends c:", af.defends({"a"}, "c"), "| {} defends c:", af.defends(set(), "c"))
print(" F({}) =", show(af.characteristic(set())), "| F({a}) =", show(af.characteristic({"a"})),
      "| F({a,c}) =", show(af.characteristic({"a", "c"})))
print(" {a,c} admissible:", af.is_admissible({"a", "c"}), "| complete:", af.is_complete({"a", "c"}))
print(" {a}   admissible:", af.is_admissible({"a"}), "| complete:", af.is_complete({"a"}), "(F({a}) = {a,c} is bigger)")

# ---------------------------------------------------------------------------------- B
title("B. PART 1 on the book's Example 5.10 graph  (a1->a2->a3->a4, a3->a5)")
part1("Example 5.10, all five arguments", sorted(set().union(*B.AGENTS_5_10.values())), B.ATTACKS_5_10)

# ---------------------------------------------------------------------------------- C
title("C. PART 2 - GROUNDED DIRECT ARGUMENTATION MECHANISM (book examples)")
ag, at = B.AGENTS_5_10, B.ATTACKS_5_10
print("Example 5.10 / Figure 5.4(a): agents", {i: show(s) for i, s in ag.items()})
print("  attacks:", sorted(at))
o = mechanism(at, ag)
print("  everybody truthful -> outcome", show(o), "(book: {a1,a3})")
print("  utilities  x:", utility(ag["x"], o), " y:", utility(ag["y"], o), " z:", utility(ag["z"], o),
      "  (book prints y and z swapped - misprint; code uses each agent's own set)")
rep = {"x": {"a4", "a5"}, "y": ag["y"], "z": ag["z"]}
o2 = mechanism(at, rep)
print("  x hides a1 (Figure 5.4(b)) -> outcome", show(o2), "-> utility of x =", utility(ag["x"], o2), "(book: 2)")
for who in ("x", "y", "z"):
    oth = {j: ag[j] for j in ag if j != who}
    best, arg = best_responses(who, ag, at, oth)
    print(f"  best responses of {who} when the others are truthful: utility {best}, reports {[show(a) for a in arg]}")
ok, ce = check_truthfulness(ag, at)
print("  Theorem 5.3 check (best-response form) holds?", ok)
print("     counterexample:", {k: (show(v) if isinstance(v, frozenset) else v) for k, v in ce.items() if k != 'others_reports'},
      "others:", {j: show(s) for j, s in ce["others_reports"].items()})
print("  Theorem 5.3 check (literal inequality form) agrees?", check_theorem_5_3(ag, at)[0] == ok)
print("  Theorem 5.4 condition holds?", theorem_5_4_condition(ag, at)[0])
for i, a, b, path in explain_violations(ag, at):
    print(f"     agent {i}: odd path {a} ~> {b}:", " -> ".join(path), f"(length {len(path) - 1})")
print("  => not strategyproof, and the condition correctly fails.")

ag, at = B.AGENTS_5_11, B.ATTACKS_5_11
print("\nExample 5.11 / Figure 5.5: x also owns a6, extra attack (a6,a3)")
o = mechanism(at, ag)
print("  everybody truthful -> outcome", show(o), "(book: {a1,a4,a5,a6});  utility of x =", utility(ag["x"], o), "of", len(ag["x"]))
print("  strategyproof?", is_strategyproof(ag, at), "| Theorem 5.3 literal check:", check_theorem_5_3(ag, at)[0])
print("  Theorem 5.4 condition holds?", theorem_5_4_condition(ag, at)[0])
for i, a, b, path in explain_violations(ag, at):
    print(f"     agent {i}: odd path {a} ~> {b}:", " -> ".join(path))
print("  => strategyproof although the condition FAILS: the condition is sufficient, not necessary.")
print("     Reason: a6 is unattacked, so as long as x reveals it a6 is in and a3 is out; then a1 -> a2 -> a3")
print("     can no longer kill a4/a5, and hiding a1 would only cost x an argument.")
print("     (The book's text names a5 as the cancelling argument - misprint, it is a6.)")

# ---------------------------------------------------------------------------------- D
title("D. THEOREM 5.4 - condition holds / condition fails")
agents = {1: frozenset({"a", "b"}), 2: frozenset({"c"})}
attacks = {("a", "c"), ("c", "b")}
print("Condition HOLDS (non-vacuous): agent 1 = {a,b}, agent 2 = {c}, attacks a->c, c->b.")
print("  The only path from a to b is a->c->b, of EVEN length 2.")
print("  condition:", theorem_5_4_condition(agents, attacks)[0], "| strategyproof:", is_strategyproof(agents, attacks))

agents = {1: frozenset({"alpha", "beta"}), 2: frozenset({"d", "e"})}
attacks = {("alpha", "d"), ("d", "e"), ("e", "alpha"), ("alpha", "beta")}
print("\nCondition FAILS and mechanism NOT strategyproof: agent 1 = {alpha,beta}, agent 2 = {d,e},")
print("  attacks alpha->beta, alpha->d, d->e, e->alpha  (alpha,d,e form an odd cycle)")
G = mechanism(attacks, agents)
print("  truthful outcome:", show(G), "-> utility of agent 1 =", utility(agents[1], G))
best, arg = best_responses(1, agents, attacks, {2: agents[2]})
print("  best response of agent 1:", [show(a) for a in arg], "-> utility", best, "(hiding alpha frees beta)")
print("  condition:", theorem_5_4_condition(agents, attacks)[0],
      "| strategyproof:", is_strategyproof(agents, attacks))
for i, a, b, path in explain_violations(agents, attacks):
    print(f"     agent {i}: odd path {a} ~> {b}:", " -> ".join(path))

agents2 = {1: frozenset({"alpha"}), 2: frozenset({"beta"}), 3: frozenset({"d"}), 4: frozenset({"e"})}
print("\nSame attacks, one argument per agent (no agent holds two arguments, condition vacuous):")
print("  condition:", theorem_5_4_condition(agents2, attacks)[0], "| strategyproof:", is_strategyproof(agents2, attacks))

# ---------------------------------------------------------------------------------- E
title("E. CYCLES in the odd-path test")
atk = {("x", "y"), ("y", "z"), ("z", "x"), ("x", "b")}
print("attacks:", sorted(atk), "  (x->y->z->x is a 3-cycle)")
for s, t in (("x", "y"), ("y", "x"), ("z", "b")):
    print(f" odd path {s} ~> {t}?  walk: {odd_path_exists(atk, s, t, 'walk')!s:5}"
          f" {find_odd_path(atk, s, t, 'walk')}   simple path: {odd_path_exists(atk, s, t, 'simple')}")
print("A 'walk' may go around a cycle (repeat nodes); a 'simple path' may not. Both readings are")
print("implemented; the experiments report both. Walk search = BFS over (node, parity) states, so it")
print("always terminates even though cycles make the number of walks infinite.")
