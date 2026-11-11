"""The two worked examples from the book (Examples 5.10 and 5.11, Figures 5.4 and 5.5).

Book notation  ->  code names
    alpha_k    ->  "a1" ... "a6"
    A_x, A_y, A_z (agent types)  ->  agents["x"], agents["y"], agents["z"]
    R (defeat relation)          ->  the set of pairs (attacker, target)

Misprints in the book (stated in the assignment) and how this code treats them
  * Example 5.10: the book writes u_y(o,{a3}) = 1 and u_z(o,{a2}) = 0, i.e. it swaps the agents'
    argument sets.  Correct: A_y = {a2} and A_z = {a3}, so u_y = |{a1,a3} n {a2}| = 0 and
    u_z = |{a1,a3} n {a3}| = 1.  The code never takes the sets from the text: utility is always
    computed from each agent's own TRUE set, so it is right automatically.
  * Discussion after Example 5.11: the argument that cancels the indirect self-defeat of agent x
    is a6, NOT a5.  (a1 indirectly defeats a4 and a5 via the odd paths a1->a2->a3->a4 and
    a1->a2->a3->a5; the extra argument a6 defeats a3, which restores a4 and a5.)
"""

# ---------------- Example 5.10 / Figure 5.4(a) ----------------
AGENTS_5_10 = {
    "x": frozenset({"a1", "a4", "a5"}),
    "y": frozenset({"a2"}),
    "z": frozenset({"a3"}),
}
ATTACKS_5_10 = {("a1", "a2"), ("a2", "a3"), ("a3", "a4"), ("a3", "a5")}

# ---------------- Example 5.11 / Figure 5.5 ----------------
# Same as 5.10 plus argument a6 (owned by x) and the defeat (a6, a3).
AGENTS_5_11 = {
    "x": frozenset({"a1", "a4", "a5", "a6"}),
    "y": frozenset({"a2"}),
    "z": frozenset({"a3"}),
}
ATTACKS_5_11 = ATTACKS_5_10 | {("a6", "a3")}

# Values stated in the book (with the misprints corrected) - asserted in tests.py.
EXPECTED = {
    "5.10 truthful outcome": frozenset({"a1", "a3"}),
    "5.10 utilities (x, y, z)": (1, 0, 1),                 # book prints y and z swapped
    "5.10 x hides a1 -> outcome (Fig 5.4b)": frozenset({"a2", "a4", "a5"}),
    "5.10 x hides a1 -> utility of x": 2,
    "5.11 truthful outcome": frozenset({"a1", "a4", "a5", "a6"}),
}
