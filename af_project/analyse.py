"""Explain WHY an instance can be strategyproof although the Theorem 5.4 condition fails.

For a strategyproof instance we look at every 'deviation' (agent i, a combination of the
others' reports, a strictly smaller report R of i) and compare it with truthful reporting.
Strategyproofness means no deviation is strictly better, so every deviation is either

  * 'same'  : own accepted set  A_i n E  is unchanged                 (deviation is irrelevant)
  * 'swap'  : own accepted set changes but its SIZE (= utility) is equal   (zero-sum trade-off)
  * 'loss'  : utility is strictly lower                                  (deviation hurts)

Each strategyproof instance is labelled by the 'most interesting' kind of deviation it contains:
    swap  >  loss-only  >  inert
  swap       : at least one deviation is a swap (hiding really changes what is accepted, but
               the agent gains exactly as much as it loses).
  loss-only  : no swap, at least one deviation strictly hurts the agent.
  inert      : every deviation leaves the agent's accepted set unchanged.
(The three labels are exhaustive and mutually exclusive.)
"""
from strategic import _Fast, _submasks


def _popcount(m):
    return bin(m).count("1")


def _deviations(agents, attacks):
    """Yield (agent, others_mask, R_mask, truthful_set_mask, dev_set_mask) for every strictly
    smaller report R of every agent against every combination of the others' reports."""
    F = _Fast(agents, attacks)
    ids = list(agents)
    A = {i: F.mask(agents[i]) for i in ids}
    for i in ids:
        combos = [0]
        for j in ids:
            if j != i:
                combos = [c | s for c in combos for s in _submasks(A[j])]
        for oth in combos:
            g_truth = F.grounded(oth | A[i]) & A[i]
            for R in _submasks(A[i]):
                if R != A[i]:
                    yield F, i, oth, R, g_truth, F.grounded(oth | R) & A[i]


def classify_instance(agents, attacks):
    """Label a strategyproof instance 'swap', 'loss-only' or 'inert' (see module doc).
    Raises AssertionError if a deviation is strictly profitable (instance not strategyproof)."""
    has_swap = has_loss = False
    for _F, _i, _oth, _R, gt, gd in _deviations(agents, attacks):
        ut, ud = _popcount(gt), _popcount(gd)
        assert ud <= ut, "instance is not strategyproof"
        if ud < ut:
            has_loss = True
        elif gd != gt:
            has_swap = True
    return "swap" if has_swap else ("loss-only" if has_loss else "inert")


def has_tie_deviation(agents, attacks):
    """True iff the instance contains a 'swap' deviation (equal utility, different accepted set)."""
    for _F, _i, _oth, _R, gt, gd in _deviations(agents, attacks):
        if gd != gt and _popcount(gd) == _popcount(gt):
            return True
    return False


def find_swap_example(agents, attacks):
    """A concrete swap deviation, decoded for printing, or None."""
    for F, i, oth, R, gt, gd in _deviations(agents, attacks):
        if gd != gt and _popcount(gd) == _popcount(gt):
            dec = lambda m: sorted(F.args[k] for k in range(len(F.args)) if m >> k & 1)
            return dict(agent=i, others_reveal=dec(oth), agent_hides=dec(F.mask(agents[i]) & ~R),
                        accepted_truthful=dec(gt), accepted_after_hiding=dec(gd))
    return None
