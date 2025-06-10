# parameter class datatypes
from types_classes import Parameters


"""
Functions for set comparisons using different set preferences
cmp-functions return True if A is preferred to B
"""

# DICHOTOMOUS
# AV-Utility comparison
# use intersection size as utility measure
def U_AV(ballot:set, W:set) -> int:
    return len(ballot.intersection(W))

def cmp_AV(ballot:set, A:set, B:set) -> bool:
    return U_AV(ballot,A) > U_AV(ballot,B)

# CCAV-Utility comparison
# idea: indicator function whether voter is represented
def U_CCAV(ballot:set, W:set) -> int:
    return 0 if len(ballot.intersection(W)) == 0 else 1

def cmp_CCAV(ballot:set, A:set, B:set) -> bool:
    return U_CCAV(ballot,A) > U_CCAV(ballot,B)

# ORDINAL
# compare committees according to Kelly's set extension
def cmp_kelly_strict(preference:list[int], A:set, B:set) -> bool:
    strict = False
    for a in A:
        for b in B:
            comp = preference.index(b) - preference.index(a)
            if comp < 0:
                return False
            if comp > 0:
                strict = True
    return strict

# Fishburn comparison
def cmp_fishburn(preference:list[int], A:set, B:set) -> bool:
    A_minus_B = A-B
    B_minus_A = B-A
    for a in A_minus_B:
        for b in B:
            comp = preference.index(b) - preference.index(a)
            if comp < 0:
                return False
    for a in A:
        for b in B_minus_A:
            comp = preference.index(b) - preference.index(a)
            if comp < 0:
                return False
    return True

# Fishburn comparison - strict
def cmp_fishburn_strict(preference:list[int], A:set, B:set) -> bool:
    return cmp_fishburn(preference, A, B) and not cmp_fishburn(preference, B, A)

# Pairwise dominance comparison
"""
    equivalent to
        - Stochastic Dominance (used for calculation here)
        - Responsive Set
        - Additive Utility
"""
def cmp_PD(preference:list[int], A:set, B:set) -> bool:
    for c in preference:
        # number of elements in A and B that are strictly preferred to c
        cA = len({a for a in A if preference.index(c) >= preference.index(a)})
        cB = len({b for b in B if preference.index(c) >= preference.index(b)})
        if cA < cB:
            return False
    return True

# Stochastic dominance comparison - strict
def cmp_PD_strict(preference:list[int], A:set, B:set) -> bool:
    return cmp_PD(preference, A, B) and not cmp_PD(preference, B, A)

# compare committees using specified comparison function
def cmp_committees(params:Parameters, preferences_t, ballots_t, i, A, B):
    if params.ballot_generation.ordinal:
        match params.deviation.set_preference:
            case "K":
                is_better = cmp_kelly_strict(preferences_t[i], A, B)
            case "F":
                is_better = cmp_fishburn_strict(preferences_t[i], A, B)
            case "PD":
                is_better = cmp_PD_strict(preferences_t[i], A, B)
            case _:
                print("\033[91mUnknown or incompatible set preference: " + str(params.deviation.set_preference) + "\033[0m")
    else:
        match params.deviation.set_preference:
            case "AV":
                is_better = cmp_AV(ballots_t[i],A,B)
            case "CCAV":
                is_better = cmp_CCAV(ballots_t[i],A,B)
            case _:
                print("\033[91mUnknown or incompatible set preference: " + str(params.deviation.set_preference) + "\033[0m")
                return
    return is_better