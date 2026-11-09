"""
Part 1 - Argumentation Engine (Dung-style abstract argumentation frameworks).

An AF is a pair <A, ->> : a finite set of arguments A and an attack relation
(a, b) meaning "a attacks b".  Everything is brute force over subsets / labellings,
which is fine for the small frameworks used in the course (n <= ~15).
"""
from itertools import combinations, product


class ArgumentationFramework:
    """Q1: the framework object <A, attacks>."""

    def __init__(self, arguments, attacks):
        self.arguments = frozenset(arguments)
        self.attacks = frozenset((a, b) for a, b in attacks)
        for a, b in self.attacks:
            if a not in self.arguments or b not in self.arguments:
                raise ValueError(f"Attack ({a},{b}) uses an unknown argument")
        self._attackers = {x: frozenset(a for a, b in self.attacks if b == x)
                           for x in self.arguments}
        self._targets = {x: frozenset(b for a, b in self.attacks if a == x)
                         for x in self.arguments}

    # ---------- helpers ----------
    def attackers_of(self, a):
        return self._attackers[a]

    def targets_of(self, a):
        return self._targets[a]

    def attacked_by(self, S):
        """S+ : every argument attacked by some member of S."""
        out = set()
        for a in S:
            out |= self._targets[a]
        return frozenset(out)

    def all_subsets(self):
        args = sorted(self.arguments, key=str)
        for r in range(len(args) + 1):
            for c in combinations(args, r):
                yield frozenset(c)

    def induced(self, subset):
        """Sub-framework induced by a subset of the arguments."""
        subset = frozenset(subset)
        return ArgumentationFramework(
            subset, {(a, b) for a, b in self.attacks if a in subset and b in subset})

    def __repr__(self):
        return (f"AF(args={sorted(self.arguments, key=str)}, "
                f"attacks={sorted(self.attacks, key=str)})")

    # ---------- Q2 ----------
    def is_conflict_free(self, S):
        S = frozenset(S)
        return not any(a in S and b in S for a, b in self.attacks)

    # ---------- Q3 ----------
    def defends(self, S, a):
        """S defends a  iff every attacker of a is itself attacked by a member of S."""
        S = frozenset(S)
        return all(self._attackers[b] & S for b in self._attackers[a])

    # ---------- Q4 ----------
    def characteristic(self, S):
        """F(S) = { a | S defends a }."""
        S = frozenset(S)
        return frozenset(a for a in self.arguments if self.defends(S, a))

    # ---------- Q5 ----------
    def is_admissible(self, S):
        S = frozenset(S)
        return self.is_conflict_free(S) and S <= self.characteristic(S)

    def is_complete(self, S):
        S = frozenset(S)
        return self.is_conflict_free(S) and S == self.characteristic(S)

    # ---------- Q6 ----------
    def grounded_extension(self):
        """(A) least fixed point of F: iterate F from the empty set."""
        S = frozenset()
        while True:
            T = self.characteristic(S)
            if T == S:
                return S
            S = T

    def complete_extensions(self):
        """(B) all complete extensions."""
        return [S for S in self.all_subsets() if self.is_complete(S)]

    def admissible_sets(self):
        return [S for S in self.all_subsets() if self.is_admissible(S)]

    def preferred_extensions(self):
        """Maximal (w.r.t. set inclusion) admissible sets."""
        adm = self.admissible_sets()
        return [S for S in adm if not any(S < T for T in adm)]

    def stable_extensions(self):
        """Conflict-free sets attacking every argument outside them."""
        return [S for S in self.all_subsets()
                if self.is_conflict_free(S)
                and S | self.attacked_by(S) == self.arguments]

    def semi_stable_extensions(self):
        """Admissible sets whose range S u S+ is maximal w.r.t. inclusion."""
        adm = self.admissible_sets()
        rng = {S: S | self.attacked_by(S) for S in adm}
        return [S for S in adm if not any(rng[S] < rng[T] for T in adm)]

    def all_extensions(self):
        """(C) dict with every semantics."""
        return {
            "grounded": [self.grounded_extension()],
            "complete": self.complete_extensions(),
            "preferred": self.preferred_extensions(),
            "stable": self.stable_extensions(),
            "semi-stable": self.semi_stable_extensions(),
        }

    # ---------- labellings ----------
    def is_legal_labelling(self, lab):
        """lab: dict arg -> 'in' | 'out' | 'undec'.
        in   <=> all attackers are out
        out  <=> some attacker is in
        undec otherwise (not all attackers out, and no attacker in)."""
        for a in self.arguments:
            att = [lab[b] for b in self._attackers[a]]
            if lab[a] == "in":
                ok = all(l == "out" for l in att)
            elif lab[a] == "out":
                ok = any(l == "in" for l in att)
            else:
                ok = (not all(l == "out" for l in att)) and not any(l == "in" for l in att)
            if not ok:
                return False
        return True

    def labellings(self):
        """(D) all legal in/out/undec labellings (3^n brute force)."""
        args = sorted(self.arguments, key=str)
        res = []
        for combo in product(("in", "out", "undec"), repeat=len(args)):
            lab = dict(zip(args, combo))
            if self.is_legal_labelling(lab):
                res.append(lab)
        return res

    @staticmethod
    def labelling_to_extension(lab):
        return frozenset(a for a, l in lab.items() if l == "in")

    # ---------- acceptance ----------
    def acceptance_status(self, a, semantics="preferred"):
        """(E) 'skeptically accepted' (in every extension), 'credulously accepted'
        (in some but not all), or 'rejected' (in none)."""
        exts = self.all_extensions()[semantics]
        if not exts:                      # e.g. no stable extension
            return "rejected"
        n_in = sum(a in E for E in exts)
        if n_in == len(exts):
            return "skeptically accepted"
        return "credulously accepted" if n_in else "rejected"


# Convenience function-style API (the assignment asks for "functions").
def is_conflict_free(af, S): return af.is_conflict_free(S)
def defends(af, S, a): return af.defends(S, a)
def characteristic_function(af, S): return af.characteristic(S)
def is_admissible(af, S): return af.is_admissible(S)
def is_complete(af, S): return af.is_complete(S)
def grounded_extension(af): return af.grounded_extension()
def complete_extensions(af): return af.complete_extensions()
def all_extensions(af): return af.all_extensions()
def legal_labellings(af): return af.labellings()
def acceptance_status(af, a, semantics="preferred"): return af.acceptance_status(a, semantics)
