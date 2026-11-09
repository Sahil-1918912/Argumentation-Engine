"""Classify WHY an instance is strategyproof although the Thm 5.4 condition fails."""
from collections import Counter
from argumentation import ArgumentationFramework
from strategic import odd_path_exists

def status(af, G, x):
    if x in G: return "in"
    if af.attackers_of(x) & G or any(y in G for y in af.attackers_of(x)): return "out"
    return "undec"

def odd_paths_simple(attacks, s, t, maxlen=9):
    succ = {}
    for a, b in attacks: succ.setdefault(a, []).append(b)
    res = []
    def dfs(v, path):
        for w in succ.get(v, []):
            if w == t and len(path) % 2 == 1: res.append(path + [w])
            if w not in path: dfs(w, path + [w])
    dfs(s, [s]); return res

def classify(agents, attacks, viol):
    """Return a reason label for the (first) violating pair of the instance."""
    args = frozenset().union(*agents.values())
    af = ArgumentationFramework(args, attacks)
    G = af.grounded_extension()
    reasons = set()
    for (i, a, b) in viol:
        sa, sb = status(af, G, a), status(af, G, b)
        # an odd path exists but alpha is already decided/never helps hiding:
        reasons.add(f"alpha={sa},beta={sb}")
    return reasons

def explain_stats(rows, key="viol_walk", cond="cond_walk"):
    c = Counter()
    for r in rows:
        if r["sp"] and not r[cond]:
            labs = classify(r["agents"], r["attacks"], r[key])
            # label the instance by the "best" reason: prefer a pair with undec/undec
            c[tuple(sorted(labs))] += 1
    return c


def has_tie_deviation(agents, attacks):
    """Is there an agent / combination of others' reports / strictly smaller own report
    that gives the SAME utility as truthful reporting but a different grounded extension
    restricted to A_i (i.e. a real trade-off, 'swap', rather than irrelevance)?"""
    from strategic import _Fast, _submasks
    F = _Fast(agents, attacks); ids = list(agents)
    A = {i: F.mask(agents[i]) for i in ids}
    for i in ids:
        others = [j for j in ids if j != i]
        combos = [0]
        for j in others:
            combos = [c | s for c in combos for s in _submasks(A[j])]
        for oth in combos:
            g_truth = F.grounded(oth | A[i]) & A[i]
            for R in _submasks(A[i]):
                if R == A[i]: continue
                g = F.grounded(oth | R) & A[i]
                if g != g_truth and bin(g).count("1") == bin(g_truth).count("1"):
                    return True
    return False
