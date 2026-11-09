"""Random experiments: strategyproofness vs. the Theorem 5.4 condition."""
import random, json, sys
from strategic import is_strategyproof, theorem_5_4_condition, check_truthfulness

def random_instance(rng, p, self_attacks=False):
    n = rng.randint(6, 8)
    args = [f"a{k+1}" for k in range(n)]
    attacks = {(a, b) for a in args for b in args
               if (self_attacks or a != b) and rng.random() < p}
    agents = {i: set() for i in range(3)}
    for a in args:
        agents[rng.randrange(3)].add(a)
    return {i: frozenset(s) for i, s in agents.items()}, attacks

def run(N=1000, seed=2024, self_attacks=False, ps=(0.15, 0.25, 0.35)):
    rng = random.Random(seed)
    results = {}
    for p in ps:
        rows = []
        for _ in range(N):
            agents, attacks = random_instance(rng, p, self_attacks)
            sp = is_strategyproof(agents, attacks)
            cw, vw = theorem_5_4_condition(agents, attacks, "walk")
            cs, vs = theorem_5_4_condition(agents, attacks, "simple")
            rows.append(dict(agents=agents, attacks=attacks, sp=sp,
                             cond_walk=cw, cond_simple=cs, viol_walk=vw, viol_simple=vs))
        results[p] = rows
    return results

def summarise(results):
    out = {}
    for p, rows in results.items():
        N = len(rows)
        d = dict(N=N,
                 sp=sum(r["sp"] for r in rows),
                 cond_walk=sum(r["cond_walk"] for r in rows),
                 cond_simple=sum(r["cond_simple"] for r in rows),
                 cond_walk_not_sp=sum(r["cond_walk"] and not r["sp"] for r in rows),
                 cond_simple_not_sp=sum(r["cond_simple"] and not r["sp"] for r in rows),
                 sp_not_cond_walk=sum(r["sp"] and not r["cond_walk"] for r in rows),
                 sp_not_cond_simple=sum(r["sp"] and not r["cond_simple"] for r in rows))
        out[p] = d
    return out

if __name__ == "__main__":
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
    sa = len(sys.argv) > 2 and sys.argv[2] == "self"
    res = run(N, self_attacks=sa)
    s = summarise(res)
    for p, d in s.items():
        print(p, d)
