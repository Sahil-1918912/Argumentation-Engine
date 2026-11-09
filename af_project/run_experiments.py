"""Runs the full experiment (3 values of p, N instances each) and writes results/."""
import json, os, sys
from experiments import run, summarise
from analyse import has_tie_deviation
from strategic import check_truthfulness

N = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
os.makedirs("results", exist_ok=True)
lines = []
for tag, sa in (("main (no self-attacks)", False), ("variant (self-attacks allowed)", True)):
    res = run(N, seed=2024, self_attacks=sa)
    s = summarise(res)
    lines.append(f"\n### {tag}, N={N} per p\n")
    lines.append("| p | strategyproof | cond. holds (walk) | cond. holds (simple path) | cond holds & NOT SP | SP & cond fails (walk) | SP & cond fails (simple) |")
    lines.append("|---|---|---|---|---|---|---|")
    for p, d in s.items():
        lines.append(f"| {p} | {d['sp']}/{d['N']} = {d['sp']/d['N']:.3f} | {d['cond_walk']} | {d['cond_simple']} | "
                     f"{d['cond_walk_not_sp']} (walk) / {d['cond_simple_not_sp']} (simple) | {d['sp_not_cond_walk']} | {d['sp_not_cond_simple']} |")
    if not sa:
        lines.append("\nSP instances with failing condition: how many contain a real *swap* deviation "
                     "(hiding changes which own arguments are accepted, utility equal)?\n")
        for p, rows in res.items():
            tgt = [r for r in rows if r["sp"] and not r["cond_walk"]]
            tie = sum(has_tie_deviation(r["agents"], r["attacks"]) for r in tgt)
            lines.append(f"- p={p}: {tie}/{len(tgt)} have a swap deviation; {len(tgt)-tie} have none")
        ser = lambda r: dict(agents={str(k): sorted(v) for k, v in r["agents"].items()},
                             attacks=sorted(r["attacks"]), sp=r["sp"],
                             cond_walk=r["cond_walk"], cond_simple=r["cond_simple"])
        json.dump({str(p): [ser(r) for r in rows] for p, rows in res.items()},
                  open("results/instances.json", "w"))
        # notable instances
        notable = {"cond_fails_not_sp": [], "sp_cond_fails": [], "cond_holds_not_sp": []}
        for p, rows in res.items():
            for r in rows:
                if not r["sp"] and not r["cond_walk"] and len(notable["cond_fails_not_sp"]) < 3: notable["cond_fails_not_sp"].append((p, ser(r)))
                if r["sp"] and not r["cond_walk"] and len(notable["sp_cond_fails"]) < 6: notable["sp_cond_fails"].append((p, ser(r)))
                if not r["sp"] and r["cond_walk"]: notable["cond_holds_not_sp"].append((p, ser(r)))
        json.dump(notable, open("results/notable_instances.json", "w"), indent=1)
open("results/results.md", "w").write("\n".join(lines))
print("\n".join(lines))
