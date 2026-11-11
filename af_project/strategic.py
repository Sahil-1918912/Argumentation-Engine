"""
Part 2 - Strategic argumentation: the grounded direct argumentation mechanism.

Notation
  attacks : global attack relation, set of (a, b) pairs
  agents  : dict agent_id -> frozenset of the agent's TRUE argument set A_i
  reports : dict agent_id -> frozenset revealed by that agent (subset of A_i)
Utility of agent i = number of its OWN true arguments in the grounded extension.
"""
from collections import deque
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
    Returns (True, None) or (False, counterexample dict).
    The input is validated first (see validate_instance): the agents' true argument sets
    must be pairwise disjoint, because the search enumerates each agent's report
    separately and relies on the union of the reports identifying who revealed what."""
    validate_instance(agents, attacks)
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


def validate_instance(agents, attacks):
    """Raise ValueError unless: agents' type sets are pairwise disjoint and every attack
    is between arguments that belong to some agent."""
    seen = {}
    for i, Ai in agents.items():
        for a in Ai:
            if a in seen:
                raise ValueError(f"argument {a!r} belongs to both agent {seen[a]!r} and "
                                 f"agent {i!r}; types must be disjoint")
            seen[a] = i
    for a, b in attacks:
        if a not in seen or b not in seen:
            raise ValueError(f"attack ({a!r},{b!r}) mentions an argument no agent owns")


def check_theorem_5_3(agents, attacks):
    """Theorem 5.3, implemented LITERALLY as stated in the book, independently of
    check_truthfulness (slow class-based grounded computation, no bitmasks):

        for all i, all S subset of A_i, all A_-i (subset of the others' arguments):
            |A_i  n  E_GR(<A_i u A_-i, R>)|  >=  |A_i  n  E_GR(<(A_i \\ S) u A_-i, R>)|

    Returns (holds, counterexample or None).  By the theorem 'holds' <=> the mechanism is
    strategyproof, so this must always agree with is_strategyproof (tests.py checks it)."""
    validate_instance(agents, attacks)
    for i, Ai in agents.items():
        others = frozenset().union(*(Aj for j, Aj in agents.items() if j != i)) \
            if len(agents) > 1 else frozenset()
        for A_minus_i in powerset(others):
            full = utility(Ai, mechanism(attacks, {"me": Ai, "others": A_minus_i}))
            for S in powerset(Ai):
                dev = utility(Ai, mechanism(attacks, {"me": Ai - S, "others": A_minus_i}))
                if dev > full:
                    return False, dict(agent=i, hidden=S, others=A_minus_i,
                                       with_all=full, with_S_hidden=dev)
    return True, None


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
def find_odd_path(attacks, src, dst, mode="walk"):
    """Return a directed path src -> ... -> dst of ODD length as a list of nodes
    (e.g. ['a','b','c','d'] has length 3), or None if there is none.
    mode='walk'  : any directed walk (nodes may repeat, so cycles are allowed).  BFS over
                   (node, parity) states, so it terminates on cyclic graphs and returns a
                   shortest odd walk.
    mode='simple': only simple paths (no node repeated) -> DFS.  Callers pass src != dst
                   (theorem_5_4_condition does), so no closed paths are considered."""
    succ = {}
    for a, b in attacks:
        succ.setdefault(a, []).append(b)
    for k in succ:
        succ[k].sort(key=str)                       # deterministic witnesses
    if mode == "walk":
        parent = {(src, 0): None}
        queue = deque([(src, 0)])
        while queue:
            st = queue.popleft()
            v, p = st
            for w in succ.get(v, ()):
                nxt = (w, 1 - p)
                if nxt not in parent:
                    parent[nxt] = st
                    if nxt == (dst, 1):
                        path, cur = [], nxt
                        while cur is not None:
                            path.append(cur[0])
                            cur = parent[cur]
                        return path[::-1]
                    queue.append(nxt)
        return None
    if mode != "simple":
        raise ValueError("mode must be 'walk' or 'simple'")

    def dfs(v, path):
        for w in succ.get(v, ()):
            if w == dst and len(path) % 2 == 1:     # path has len(path)-1 edges; +1 edge
                return path + [w]
            if w not in path:
                r = dfs(w, path + [w])
                if r:
                    return r
        return None
    return dfs(src, [src])


def odd_path_exists(attacks, src, dst, mode="walk"):
    """Is there a directed path of ODD length from src to dst?  (see find_odd_path)"""
    return find_odd_path(attacks, src, dst, mode) is not None


def theorem_5_4_condition(agents, attacks, mode="walk"):
    """True iff NO agent holds two (distinct) arguments alpha, beta with an odd-length
    directed path alpha -> ... -> beta in the full graph.  Returns (holds, violations)."""
    viol = []
    for i, Ai in agents.items():
        for a in sorted(Ai, key=str):
            for b in sorted(Ai, key=str):
                if a != b and odd_path_exists(attacks, a, b, mode):
                    viol.append((i, a, b))
    return (not viol), viol


def explain_violations(agents, attacks, mode="walk"):
    """Like theorem_5_4_condition but each violation carries a witness path:
    [(agent, alpha, beta, [alpha, ..., beta]), ...]."""
    out = []
    for i, a, b in theorem_5_4_condition(agents, attacks, mode)[1]:
        out.append((i, a, b, find_odd_path(attacks, a, b, mode)))
    return out
