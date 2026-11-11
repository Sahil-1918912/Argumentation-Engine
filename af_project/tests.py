"""Tests: known results, the book's examples, and cross-checks between independent implementations.
Run with:  python tests.py     (plain asserts, no pytest needed; pytest also works)"""
import random
from argumentation import ArgumentationFramework as AF, NO_EXTENSIONS
from strategic import (mechanism, utility, _Fast, check_truthfulness, check_theorem_5_3,
                       best_responses, is_strategyproof, odd_path_exists, find_odd_path,
                       theorem_5_4_condition, explain_violations, validate_instance)
from experiments import random_instance
from analyse import classify_instance
import book_examples as B


def fs(*x): return frozenset(x)


def raises(exc, fn, *a):
    try:
        fn(*a)
    except exc:
        return True
    return False


# ------------------------------------------------------------------ Part 1
def test_basic_notions():
    af = AF("abcd", {("a", "b"), ("b", "c"), ("c", "d")})
    assert af.is_conflict_free({"a", "c"}) and not af.is_conflict_free({"a", "b"})
    assert af.is_conflict_free(set())
    assert af.defends({"a"}, "c") and not af.defends(set(), "c")
    assert af.defends(set(), "a")                          # unattacked: defended by anything
    assert af.characteristic(set()) == fs("a")
    assert af.characteristic({"a"}) == fs("a", "c")
    assert af.is_admissible({"a", "c"}) and not af.is_admissible({"c"})
    assert af.is_complete({"a", "c"}) and not af.is_complete({"a"})
    assert raises(ValueError, AF, "ab", {("a", "z")})
    print("basic notions ok")


def test_semantics_known():
    chain = AF("abc", {("a", "b"), ("b", "c")})
    assert chain.grounded_extension() == fs("a", "c")
    even = AF("ab", {("a", "b"), ("b", "a")})
    assert even.grounded_extension() == fs()
    assert set(even.preferred_extensions()) == {fs("a"), fs("b")}
    assert set(even.stable_extensions()) == {fs("a"), fs("b")}
    odd = AF("abc", {("a", "b"), ("b", "c"), ("c", "a")})
    assert odd.stable_extensions() == [] and odd.preferred_extensions() == [fs()]
    assert odd.semi_stable_extensions() == [fs()]
    sa = AF("abc", {("a", "a"), ("c", "a"), ("a", "b")})
    assert sa.grounded_extension() == fs("b", "c")
    # semi-stable & stable exist and differ from preferred: b kills c but c-d-e is an odd cycle
    af = AF("abcde", {("a", "b"), ("b", "a"), ("b", "c"), ("c", "d"), ("d", "e"), ("e", "c")})
    assert set(af.preferred_extensions()) == {fs("a"), fs("b", "d")}
    assert af.stable_extensions() == [fs("b", "d")]
    assert af.semi_stable_extensions() == [fs("b", "d")]
    # semi-stable but NOT stable: an unattacked argument a plus an independent odd cycle c-d-e
    af2 = AF("acde", {("c", "d"), ("d", "e"), ("e", "c")})
    assert af2.stable_extensions() == []
    assert af2.semi_stable_extensions() == [fs("a")]
    # preferred but not semi-stable: a<->b, b->c, and c attacks itself.  Range of {a} is {a,b},
    # range of {b} is {a,b,c}, so only {b} is semi-stable.
    af3 = AF("abc", {("a", "b"), ("b", "a"), ("b", "c"), ("c", "c")})
    assert set(af3.preferred_extensions()) == {fs("a"), fs("b")}
    assert af3.semi_stable_extensions() == [fs("b")]                 # range {b,a,c} beats {a,b}
    print("known semantics ok")


def test_acceptance_status():
    even = AF("ab", {("a", "b"), ("b", "a")})
    assert even.acceptance_status("a") == "credulously accepted"
    assert even.acceptance_status("a", "grounded") == "rejected"
    chain = AF("abc", {("a", "b"), ("b", "c")})
    assert chain.acceptance_status("a") == "skeptically accepted"
    assert chain.acceptance_status("b") == "rejected"
    odd = AF("abc", {("a", "b"), ("b", "c"), ("c", "a")})
    assert odd.acceptance_status("a", "stable") == NO_EXTENSIONS      # no stable extension
    assert odd.acceptance_status("a", "preferred") == "rejected"
    assert odd.acceptance_by_semantics("a")["stable"] == NO_EXTENSIONS
    assert raises(ValueError, odd.acceptance_status, "zz")
    assert raises(ValueError, odd.acceptance_status, "a", "bogus")
    print("acceptance status ok")


def test_crosschecks():
    rng = random.Random(1)
    for _ in range(300):
        n = rng.randint(1, 6)
        args = list(range(n))
        att = {(a, b) for a in args for b in args if rng.random() < 0.3}
        af = AF(args, att)
        G = af.grounded_extension()
        comp = af.complete_extensions()
        assert G in comp and all(G <= E for E in comp)                  # grounded = least complete
        for E in comp:
            assert af.is_admissible(E)
        pref = af.preferred_extensions()
        assert set(pref) <= set(comp) and pref                           # preferred exist, complete
        stab, semi = af.stable_extensions(), af.semi_stable_extensions()
        for S in stab:
            assert S in pref
        for S in semi:
            assert S in comp and S in pref                               # semi-stable are preferred
        if stab:
            assert set(semi) == set(stab)
        labs = af.labellings()
        assert {af.labelling_to_extension(l) for l in labs} == set(comp)  # labellings <-> complete
        assert len(labs) == len(comp)                                    # bijection
        no_undec = [l for l in labs if "undec" not in l.values()]
        assert {af.labelling_to_extension(l) for l in no_undec} == set(stab)
        assert af.extensions("grounded") == [G]
        assert af.all_extensions()["stable"] == stab
    print("cross-checks ok")


# ------------------------------------------------------------------ book examples
def test_book_example_5_10():
    ag, at = B.AGENTS_5_10, B.ATTACKS_5_10
    af = AF(set().union(*ag.values()), at)
    assert af.grounded_extension() == B.EXPECTED["5.10 truthful outcome"] == fs("a1", "a3")
    assert all(len(v) == 1 for v in af.all_extensions().values())       # single extension everywhere
    o = mechanism(at, ag)
    assert o == fs("a1", "a3")
    assert (utility(ag["x"], o), utility(ag["y"], o), utility(ag["z"], o)) == (1, 0, 1)
    # Figure 5.4(b): x hides a1
    rep = {"x": fs("a4", "a5"), "y": ag["y"], "z": ag["z"]}
    o2 = mechanism(at, rep)
    assert o2 == fs("a2", "a4", "a5") and utility(ag["x"], o2) == 2
    best, arg = best_responses("x", ag, at, {"y": ag["y"], "z": ag["z"]})
    assert best == 2 and arg == [fs("a4", "a5")]
    # y and z: revealing the truth weakly dominates (book text)
    for ag_id in ("y", "z"):
        oth = {j: ag[j] for j in ag if j != ag_id}
        b, a_ = best_responses(ag_id, ag, at, oth)
        assert ag[ag_id] in a_
    # not strategyproof; Theorem 5.3 (literal) and the best-response check agree
    assert not is_strategyproof(ag, at) and not check_theorem_5_3(ag, at)[0]
    # Thm 5.4 condition fails because of the odd paths a1->a2->a3->a4 / a5
    holds, viol = theorem_5_4_condition(ag, at)
    assert not holds and {(i, a, b) for i, a, b in viol} == {("x", "a1", "a4"), ("x", "a1", "a5")}
    assert find_odd_path(at, "a1", "a4") == ["a1", "a2", "a3", "a4"]
    print("book example 5.10 ok")


def test_book_example_5_11():
    ag, at = B.AGENTS_5_11, B.ATTACKS_5_11
    o = mechanism(at, ag)
    assert o == B.EXPECTED["5.11 truthful outcome"] == fs("a1", "a4", "a5", "a6")
    assert utility(ag["x"], o) == 4                                      # all of x's arguments accepted
    assert is_strategyproof(ag, at) and check_theorem_5_3(ag, at)[0]    # truth is dominant
    holds, viol = theorem_5_4_condition(ag, at)
    assert not holds                                                    # ... although the condition fails
    assert {(i, a, b) for i, a, b in viol} == {("x", "a1", "a4"), ("x", "a1", "a5")}
    # a6 is what repairs it: a6 -> a3 puts a3 out, so a4, a5 can no longer be killed via a3
    assert ("a6", "a3") in at
    print("book example 5.11 ok")


# ------------------------------------------------------------------ Part 2
def test_odd_paths():
    atk = {("x", "y"), ("y", "z"), ("z", "x"), ("x", "b")}
    assert odd_path_exists(atk, "x", "y", "walk") and odd_path_exists(atk, "x", "y", "simple")
    assert odd_path_exists(atk, "y", "x", "walk") and not odd_path_exists(atk, "y", "x", "simple")
    assert odd_path_exists(atk, "z", "b", "walk") and not odd_path_exists(atk, "z", "b", "simple")
    assert not odd_path_exists({("a", "b"), ("b", "c")}, "a", "c")      # length 2 only
    assert find_odd_path({("a", "b"), ("b", "c")}, "a", "b") == ["a", "b"]
    assert find_odd_path(atk, "y", "x", "walk") is not None
    # a returned witness is a real walk of odd length
    for src in "xyzb":
        for dst in "xyzb":
            for mode in ("walk", "simple"):
                p = find_odd_path(atk, src, dst, mode)
                if p:
                    assert p[0] == src and p[-1] == dst and (len(p) - 1) % 2 == 1
                    assert all((u, v) in atk for u, v in zip(p, p[1:]))
    # walk BFS and simple DFS agree with a brute-force walk enumeration (bounded length)
    rng = random.Random(3)
    for _ in range(100):
        n = rng.randint(2, 6)
        att = {(a, b) for a in range(n) for b in range(n) if rng.random() < 0.3}
        for s in range(n):
            for t in range(n):
                brute = False
                frontier = {s}
                for step in range(1, 2 * n + 2):
                    frontier = {w for v in frontier for (u, w) in att if u == v}
                    if step % 2 == 1 and t in frontier:
                        brute = True
                assert odd_path_exists(att, s, t, "walk") == brute
    print("odd paths ok")


def test_theorem_5_4_condition():
    ag = {1: fs("a", "b"), 2: fs("c")}
    even_path = {("a", "c"), ("c", "b")}                 # a->c->b has length 2 (even): allowed
    assert theorem_5_4_condition(ag, even_path)[0] and is_strategyproof(ag, even_path)
    odd_edge = {("a", "b")}                              # direct defeat inside one agent's type
    assert theorem_5_4_condition(ag, odd_edge) == (False, [(1, "a", "b")])
    assert explain_violations(ag, odd_edge) == [(1, "a", "b", ["a", "b"])]
    print("theorem 5.4 condition ok")


def test_validation():
    assert raises(ValueError, validate_instance, {1: fs("a"), 2: fs("a")}, set())   # overlap
    assert raises(ValueError, check_truthfulness, {1: fs("a"), 2: fs("a")}, set())
    assert raises(ValueError, validate_instance, {1: fs("a")}, {("a", "zzz")})        # unknown arg
    print("validation ok")


def test_mechanism_fast():
    rng = random.Random(5)
    for _ in range(200):
        agents, att = random_instance(rng, 0.25)
        F = _Fast(agents, att)
        reports = {i: frozenset(a for a in agents[i] if rng.random() < .6) for i in agents}
        slow = mechanism(att, reports)
        union = frozenset().union(*reports.values())
        fast = frozenset(F.args[k] for k in range(len(F.args)) if F.grounded(F.mask(union)) >> k & 1)
        assert slow == fast
    print("mechanism fast==slow ok")


def test_best_response_consistent():
    rng = random.Random(9)
    for _ in range(100):
        agents, att = random_instance(rng, 0.2)
        sp, ce = check_truthfulness(agents, att)
        for i in agents:
            oth = {j: agents[j] for j in agents if j != i}
            best, arg = best_responses(i, agents, att, oth)
            if sp:
                assert agents[i] in arg
        if not sp:
            i = ce["agent"]
            best, arg = best_responses(i, agents, att, ce["others_reports"])
            assert best >= ce["deviation_utility"] > ce["truthful_utility"]
            assert agents[i] not in arg
    print("best-response consistency ok")


def test_theorem_5_3_literal_matches_best_response_check():
    """Two independent implementations of 'strategyproof' must agree on every instance."""
    rng = random.Random(11)
    n_sp = 0
    for _ in range(150):
        agents, att = random_instance(rng, rng.choice([0.1, 0.2, 0.3]))
        fast = is_strategyproof(agents, att)
        slow, _ = check_theorem_5_3(agents, att)
        assert fast == slow
        n_sp += fast
    assert 0 < n_sp < 150                      # both outcomes were actually exercised
    print(f"theorem 5.3 literal == best-response check ok ({n_sp}/150 strategyproof)")


def test_theorem_5_4_is_sufficient():
    """Theorem 5.4: condition => strategyproof (both path readings)."""
    rng = random.Random(13)
    seen_cond = 0
    for _ in range(400):
        agents, att = random_instance(rng, rng.choice([0.05, 0.1, 0.15]))
        for mode in ("walk", "simple"):
            if theorem_5_4_condition(agents, att, mode)[0]:
                seen_cond += 1
                assert is_strategyproof(agents, att)
    assert seen_cond > 50
    print(f"theorem 5.4 sufficient ok ({seen_cond} condition-satisfying instances)")


def test_classifier():
    assert classify_instance(B.AGENTS_5_11, B.ATTACKS_5_11) in ("swap", "loss-only", "inert")
    # chain a->b, agent owns both, nobody else: hiding a frees b (swap: lose a, gain b)
    ag = {1: fs("a", "b")}
    assert classify_instance(ag, {("a", "b")}) == "swap"
    assert classify_instance({1: fs("a")}, set()) == "loss-only"       # hiding a only loses it
    assert classify_instance({1: fs("a", "b")}, set()) == "loss-only"
    assert classify_instance({1: fs()}, set()) == "inert"
    print("classifier ok")


if __name__ == "__main__":
    test_basic_notions(); test_semantics_known(); test_acceptance_status(); test_crosschecks()
    test_book_example_5_10(); test_book_example_5_11()
    test_odd_paths(); test_theorem_5_4_condition(); test_validation()
    test_mechanism_fast(); test_best_response_consistent()
    test_theorem_5_3_literal_matches_best_response_check(); test_theorem_5_4_is_sufficient()
    test_classifier()
    print("ALL TESTS PASSED")
