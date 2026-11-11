"""Runs the full experiment (3 values of p, N instances each) and writes results/."""
import json, os, sys
from collections import Counter
from experiments import run, summarise
from analyse import classify_instance, find_swap_example

N = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
os.makedirs("results", exist_ok=True)
lines = []


def ser(r):
    return dict(agents={str(k): sorted(v) for k, v in r["agents"].items()},
                attacks=sorted(r["attacks"]), sp=r["sp"],
                cond_walk=r["cond_walk"], cond_simple=r["cond_simple"])


def size(r):
    return (len(frozenset().union(*r["agents"].values())), len(r["attacks"]))


for tag, sa in (("main (no self-attacks)", False), ("variant (self-attacks allowed)", True)):
    res = run(N, seed=2024, self_attacks=sa)
    s = summarise(res)
    lines.append(f"\n### {tag}, N={N} per p\n")
    lines.append("| p | strategyproof | cond. holds (walk) | cond. holds (simple path) | cond holds & NOT SP | SP & cond fails (walk) | SP & cond fails (simple) |")
    lines.append("|---|---|---|---|---|---|---|")
    for p, d in s.items():
        lines.append(f"| {p} | {d['sp']}/{d['N']} = {d['sp']/d['N']:.3f} | {d['cond_walk']} | {d['cond_simple']} | "
                     f"{d['cond_walk_not_sp']} (walk) / {d['cond_simple_not_sp']} (simple) | {d['sp_not_cond_walk']} | {d['sp_not_cond_simple']} |")
    # Why are SP instances with a failing condition still strategyproof?  (computed, see analyse.py)
    lines.append("\nStrategyproof instances whose condition FAILS (walk reading), classified by the kind of "
                 "deviation they contain (swap / loss-only / inert, defined in analyse.py):\n")
    lines.append("| p | #SP & cond fails | swap | loss-only | inert |")
    lines.append("|---|---|---|---|---|")
    classes = {}
    for p, rows in res.items():
        tgt = [r for r in rows if r["sp"] and not r["cond_walk"]]
        labelled = [(classify_instance(r["agents"], r["attacks"]), r) for r in tgt]
        c = Counter(l for l, _ in labelled)
        classes[p] = labelled
        lines.append(f"| {p} | {len(tgt)} | {c['swap']} | {c['loss-only']} | {c['inert']} |")
    if not sa:
        json.dump({str(p): [ser(r) for r in rows] for p, rows in res.items()},
                  open("results/instances.json", "w"))
        notable = {"cond_fails_not_sp": [], "sp_cond_fails_by_class": {}, "cond_holds_not_sp": []}
        for p, rows in res.items():
            for r in rows:
                if not r["sp"] and not r["cond_walk"] and len(notable["cond_fails_not_sp"]) < 3:
                    notable["cond_fails_not_sp"].append((p, ser(r)))
                if not r["sp"] and r["cond_walk"]:
                    notable["cond_holds_not_sp"].append((p, ser(r)))
        # smallest (fewest arguments, then attacks) example of each class, over all p
        for cls in ("swap", "loss-only", "inert"):
            cands = [(size(r), p, r) for p, lab in classes.items() for l, r in lab if l == cls]
            if cands:
                _, p, r = min(cands, key=lambda t: t[0])
                ex = dict(p=p, **ser(r))
                if cls == "swap":
                    ex["swap_deviation"] = find_swap_example(r["agents"], r["attacks"])
                notable["sp_cond_fails_by_class"][cls] = ex
        json.dump(notable, open("results/notable_instances.json", "w"), indent=1)
open("results/results.md", "w").write("\n".join(lines))
print("\n".join(lines))
