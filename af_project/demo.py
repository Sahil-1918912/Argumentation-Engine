"""Demonstration: Part 1 on classic Dung examples, Part 2 on hand-made strategic examples."""
from argumentation import ArgumentationFramework as AF
from strategic import (mechanism, best_responses, check_truthfulness, is_strategyproof,
                       theorem_5_4_condition, odd_path_exists)

def show(S): return "{" + ",".join(sorted(map(str, S))) + "}"

def part1(name, args, attacks):
    af = AF(args, attacks)
    print(f"\n=== {name}\n{af}")
    print("grounded      :", show(af.grounded_extension()))
    for sem, exts in af.all_extensions().items():
        if sem != "grounded":
            print(f"{sem:14}:", [show(E) for E in exts])
    print("labellings    :")
    for lab in af.labellings():
        print("   ", dict(sorted(lab.items())))
    print("acceptance (preferred):",
          {a: af.acceptance_status(a) for a in sorted(af.arguments, key=str)})
    return af

print("##### PART 1: ARGUMENTATION ENGINE #####")
part1("Ex1: chain a->b->c", "abc", {("a","b"),("b","c")})
af = part1("Ex2: even cycle a<->b", "ab", {("a","b"),("b","a")})
part1("Ex3: odd cycle a->b->c->a", "abc", {("a","b"),("b","c"),("c","a")})
part1("Ex4: stable vs semi-stable (b kills c, but c-d-e is an odd cycle)", "abcde",
      {("a","b"),("b","a"),("b","c"),("c","d"),("d","e"),("e","c")})
part1("Ex5: self-attacker", "abc", {("a","a"),("c","a"),("a","b")})
af = AF("abcd", {("a","b"),("b","c"),("c","d")})
print("\nQ2-Q5 spot checks on chain a->b->c->d:")
print(" {a,c} conflict-free:", af.is_conflict_free({"a","c"}), "| {a,b}:", af.is_conflict_free({"a","b"}))
print(" {a} defends c:", af.defends({"a"}, "c"), "| F({a}) =", show(af.characteristic({"a"})))
print(" {a,c} admissible:", af.is_admissible({"a","c"}), "complete:", af.is_complete({"a","c"}))
print(" {a,c} complete:", af.is_complete({"a","c"}), "| {a} complete:", af.is_complete({"a"}))

print("\n\n##### PART 2: STRATEGIC ARGUMENTATION #####")
# Hand-made example: agent 1 owns alpha, beta; alpha -> beta; alpha sits on an odd cycle
# alpha -> d -> e -> alpha owned by agent 2 (all three undecided), so beta is undecided too.
agents = {1: frozenset({"alpha", "beta"}), 2: frozenset({"d", "e"})}
attacks = {("alpha","d"),("d","e"),("e","alpha"),("alpha","beta")}
print("agents:", {i: show(s) for i, s in agents.items()}, "\nattacks:", sorted(attacks))
G = mechanism(attacks, agents)
print("truthful grounded extension:", show(G), "-> utility agent1 =", len(G & agents[1]))
best, arg = best_responses(1, agents, attacks, {2: agents[2]})
print("best responses of agent 1 vs. agent 2 truthful: utility", best, [show(a) for a in arg])
ok, ce = check_truthfulness(agents, attacks)
print("truthfulness (Thm 5.3 check) holds?", ok, "| counterexample:", ce)
print("Thm 5.4 condition holds?", theorem_5_4_condition(agents, attacks))
print("strategyproof?", is_strategyproof(agents, attacks))

# Same attacks, but every argument now belongs to a different agent: no agent holds two
# arguments, so the Theorem 5.4 condition holds vacuously and the mechanism is strategyproof.
agents2 = {1: frozenset({"alpha"}), 2: frozenset({"beta"}), 3: frozenset({"d"}), 4: frozenset({"e"})}
print("\nSame attacks, one argument per agent:")
print(" Thm 5.4 condition:", theorem_5_4_condition(agents2, attacks)[0],
      "| strategyproof:", is_strategyproof(agents2, attacks))

# Cycles: odd walk but no odd simple path
atk = {("x","y"),("y","z"),("z","x"),("x","b")}
print("\nCycle handling: odd path x->..->y?  walk:", odd_path_exists(atk,"x","y","walk"),
      " simple:", odd_path_exists(atk,"x","y","simple"))
print("odd path y->..->x?  walk:", odd_path_exists(atk,"y","x","walk"),
      " simple:", odd_path_exists(atk,"y","x","simple"))
print("odd path z->..->b?  walk:", odd_path_exists(atk,"z","b","walk"),
      " simple:", odd_path_exists(atk,"z","b","simple"))
