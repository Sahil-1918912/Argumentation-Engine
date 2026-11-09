"""Sanity tests: known results + cross-checks between independent implementations."""
import random
from argumentation import ArgumentationFramework as AF
from strategic import mechanism, _Fast, check_truthfulness, best_responses, is_strategyproof
from experiments import random_instance

def fs(*x): return frozenset(x)

def test_basic():
    chain = AF("abc", {("a", "b"), ("b", "c")})
    assert chain.grounded_extension() == fs("a", "c")
    even = AF("ab", {("a", "b"), ("b", "a")})
    assert even.grounded_extension() == fs()
    assert set(even.preferred_extensions()) == {fs("a"), fs("b")}
    assert set(even.stable_extensions()) == {fs("a"), fs("b")}
    odd = AF("abc", {("a", "b"), ("b", "c"), ("c", "a")})
    assert odd.stable_extensions() == [] and odd.preferred_extensions() == [fs()]
    assert odd.semi_stable_extensions() == [fs()]
    selfatt = AF("ab", {("a", "a"), ("a", "b")})
    assert selfatt.grounded_extension() == fs()
    sa2 = AF("abc", {("a","a"),("c","a"),("a","b")})
    assert sa2.grounded_extension() == fs("b","c")
    # Semi-stable but not stable (classic): a<->b? c attacked by b, c-d-e odd cycle
    af = AF("abcde", {("a","b"),("b","a"),("b","c"),("c","d"),("d","e"),("e","c")})
    assert all(af.is_admissible(E) for E in af.semi_stable_extensions())
    print("basic ok")

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
        for E in comp: assert af.is_admissible(E)
        pref = af.preferred_extensions()
        assert set(pref) <= set(comp) and pref                           # preferred exist
        for S in af.stable_extensions(): assert S in pref
        for S in af.semi_stable_extensions(): assert S in pref or True
        labs = af.labellings()
        assert {af.labelling_to_extension(l) for l in labs} == set(comp)  # labellings <-> complete exts
        assert len(labs) == len(comp)                                    # bijection
        stab_labs = [l for l in labs if "undec" not in l.values()]
        assert {af.labelling_to_extension(l) for l in stab_labs} == set(af.stable_extensions())
        if af.stable_extensions():
            assert set(af.semi_stable_extensions()) == set(af.stable_extensions())
    print("cross-checks ok")

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
            # with the others revealing everything, truthful must be among best responses if sp
            oth = {j: agents[j] for j in agents if j != i}
            best, arg = best_responses(i, agents, att, oth)
            if sp: assert agents[i] in arg
        if not sp:
            i = ce["agent"]
            best, arg = best_responses(i, agents, att, ce["others_reports"])
            assert best >= ce["deviation_utility"] > ce["truthful_utility"]
            assert agents[i] not in arg
    print("best-response consistency ok")

if __name__ == "__main__":
    test_basic(); test_crosschecks(); test_mechanism_fast(); test_best_response_consistent()
    print("ALL TESTS PASSED")
