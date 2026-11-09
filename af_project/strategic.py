"""
Part 2 - Strategic argumentation: the grounded direct argumentation mechanism.

Notation
  attacks : global attack relation, set of (a, b) pairs
  agents  : dict agent_id -> frozenset of the agent's TRUE argument set A_i
  reports : dict agent_id -> frozenset revealed by that agent (subset of A_i)
Utility of agent i = number of its OWN true arguments in the grounded extension.
"""
from itertools import combinations
from argumentation import ArgumentationFramework


def powerset(S):
    S = sorted(S, key=str)
    for r in range(len(S) + 1):
        for c in combinations(S, r):
            yield frozenset(c)


# ---------------------------------------------------------------- Q1
def mechanism(attacks, reports):
    """Grounded extension of the framework induced by the union of the reports."""
    revealed = frozenset().union(*reports.values()) if reports else frozenset()
    af = ArgumentationFramework(
        revealed, {(a, b) for a, b in attacks if a in revealed and b in revealed})
    return af.grounded_extension()


def utility(agent_args, grounded):
    return len(frozenset(agent_args) & grounded)


# ---------------------------------------------------------------- Q2
def best_responses(agent, agents, attacks, others_reports):
    """Enumerate all 2^|A_i| subsets agent i could reveal, given fixed reports of the
    others.  Returns (best_utility, [all utility-maximising reports])."""
    best, arg = -1, []
    for R in powerset(agents[agent]):
        reports = dict(others_reports)
        reports[agent] = R
        u = utility(agents[agent], mechanism(attacks, reports))
        if u > best:
            best, arg = u, [R]
        elif u == best:
            arg.append(R)
    return best, arg


# ---- fast bitmask grounded extension (used for the exhaustive checks) ----
class _Fast:
    def __init__(self, agents, attacks):
        self.args = sorted(frozenset().union(*agents.values()), key=str)
        self.idx = {a: i for i, a in enumerate(self.args)}
        self.att = [0] * len(self.args)          # att[x] = bitmask of attackers of x
        for a, b in attacks:
            self.att[self.idx[b]] |= 1 << self.idx[a]
        self.targ = [0] * len(self.args)         # targ[x] = bitmask of targets of x
        for a, b in attacks:
            self.targ[self.idx[a]] |= 1 << self.idx[b]

    def mask(self, S):
        m = 0
        for a in S:
            m |= 1 << self.idx[a]
        return m

    def grounded(self, present):
        """grounded extension (as bitmask) of the subgraph induced by `present`."""
        IN = OUT = 0
        n = len(self.args)
        changed = True
        while changed:
            changed = False
            for x in range(n):
                bit = 1 << x
                if not present & bit or IN & bit:
                    continue
                if (self.att[x] & present) & ~OUT == 0:      # all present attackers are out
                    IN |= bit
                    changed = True
            for x in range(n):
                bit = 1 << x
                if present & bit and not OUT & bit and self.att[x] & IN:
                    OUT |= bit
                    changed = True
        return IN


# ---------------------------------------------------------------- Q3
def check_truthfulness(agents, attacks, return_all=False):
    """Check the dominant-strategy property behind Theorem 5.3: for EVERY agent and
    EVERY combination of subsets the others might reveal, revealing all of A_i
    gives utility >= any other report.
    Returns (True, None) or (False, counterexample dict)."""
    F = _Fast(agents, attacks)
    ids = list(agents)
    A = {i: F.mask(agents[i]) for i in ids}
    subs = {i: [m for m in _submasks(A[i])] for i in ids}
    bad = []
    for i in ids:
        others = [j for j in ids if j != i]
        # all combinations of the others' subsets
        combos = [0]
        for j in others:
            combos = [c | s for c in combos for s in subs[j]]
        # (union is enough: the grounded ext. only depends on the union; arguments
        #  are partitioned so the union determines each report uniquely)
        for oth in combos:
            u_truth = bin(F.grounded(oth | A[i]) & A[i]).count("1")
            for R in subs[i]:
                u = bin(F.grounded(oth | R) & A[i]).count("1")
                if u > u_truth:
                    ce = dict(agent=i, others_reports=_decode(F, others, agents, oth),
                              truthful_utility=u_truth, deviation=_set(F, R),
                              deviation_utility=u)
                    if not return_all:
                        return False, ce
                    bad.append(ce)
    return (not bad), (bad or None)


def _submasks(m):
    s = m
    while True:
        yield s
        if s == 0:
            break
        s = (s - 1) & m


def _set(F, m):
    return frozenset(F.args[i] for i in range(len(F.args)) if m >> i & 1)


def _decode(F, others, agents, m):
    return {j: _set(F, m) & agents[j] for j in others}


def is_strategyproof(agents, attacks):
    return check_truthfulness(agents, attacks)[0]


# ---------------------------------------------------------------- Q4  (Theorem 5.4)
def odd_path_exists(attacks, src, dst, mode="walk"):
    """Is there a directed path of ODD length from src to dst?
    mode='walk'  : any directed walk (cycles allowed) -> BFS on (node, parity) states.
    mode='simple': only simple paths (no repeated node) -> DFS."""
    succ = {}
    for a, b in attacks:
        succ.setdefault(a, set()).add(b)
    if mode == "walk":
        seen = {(src, 0)}
        stack = [(src, 0)]
        while stack:
            v, p = stack.pop()
            for w in succ.get(v, ()):
                st = (w, 1 - p)
                if st == (dst, 1):
                    return True
                if st not in seen:
                    seen.add(st)
                    stack.append(st)
        return False
    # simple paths
    def dfs(v, length, visited):
        for w in succ.get(v, ()):
            if w == dst and (length + 1) % 2 == 1:
                return True
            if w not in visited and dfs(w, length + 1, visited | {w}):
                return True
        return False
    return dfs(src, 0, frozenset({src}))


def theorem_5_4_condition(agents, attacks, mode="walk"):
    """True iff NO agent holds two (distinct) arguments alpha, beta with an odd-length
    directed path alpha -> ... -> beta in the full graph.  Returns (holds, violations)."""
    viol = []
    for i, Ai in agents.items():
        for a in Ai:
            for b in Ai:
                if a != b and odd_path_exists(attacks, a, b, mode):
                    viol.append((i, a, b))
    return (not viol), viol
