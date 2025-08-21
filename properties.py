import math

from types_classes import EJRPlusData, JRData, PSCData
from set_preferences import U_AV
from basics_and_helpers import support_set

def jr_violation_max(n, m, k, approval_sets, W):
    n_div_k = math.ceil(n/k)
    # initialise maximum violation
    max_candidate, max_set = None, set()
    for c in range(m):
        if not c in W:
            # add all voters that support c and that are not represented in W
            unrepresented_voters_c = {i for i in support_set(approval_sets,c) if approval_sets[i].isdisjoint(W)}
            # if the set is larger than the largest so far and at least n/k, update
            if len(unrepresented_voters_c) >= max(len(max_set)+1,n_div_k):
                max_candidate = c
                max_set = unrepresented_voters_c
    # return candidate, voter set with with largest JR violation
    return max_candidate, max_set

# EJR+: find largest EJR+ violation
# returns candidate, l-deprived set and l-value of largest EJR+ violation
# returns (None, set(), None) if no EJR+ violation is found
def ejr_plus_violation_max(n, m, k, approval_sets, W):
    max_candidate, max_set, max_l = None, set(), None
    for c in range(m):
        if not c in W:
            voters_c = support_set(approval_sets,c)
            # iterate values for l, backwards in order to return violation with largest l
            l_range = range(min(k,math.ceil(len(voters_c)/(n/k))),0,-1)
            for l in l_range:
                deprived_set_c = set()
                l_n_div_k = int(math.ceil(l*(n/k)))
                # add all voters of c that are represented by <l candidates in W
                deprived_set_c = {v for v in voters_c if U_AV(approval_sets[v],W) < l}
                # if the set is larger than the largest so far and at least l*n/k, update
                if len(deprived_set_c) >= max(len(max_set)+1,l_n_div_k):
                    max_candidate,max_set,max_l = c, deprived_set_c.copy(), l
                    break
                # optimisation: in the next iteration, only check voters that were in the set for the previous l
                voters_c = deprived_set_c.copy()
    return max_candidate, max_set, max_l

# Proportionality for Solid Coalitions
# find PSC violation using Hare quota (n/k)
def psc_violation(n, m, k, preferences_truthful, W):
    quota = n/k
    checked_cutoffs = set()
    max_coalition, max_cutoff, max_l = set(), None, None
    for v in range(n):
        cutoff_sets = map(lambda i: set(preferences_truthful[v][:i]),range(m-1,0,-1))
        for current_cutoff in cutoff_sets:
            # avoid checking previous cutoff sets and subsets of W
            if frozenset(current_cutoff) in checked_cutoffs or current_cutoff.issubset(W):
                continue
            checked_cutoffs.add(frozenset(current_cutoff))
            # collect voter preferences coinciding up to cutoff
            coalition = {i for i in range(n) if set(preferences_truthful[i][:len(current_cutoff)]) == current_cutoff}
            # ignore coalitions smaller than quota
            if len(coalition) < quota:
                continue
            # check for violation of PSC criterion
            l = len(coalition)//quota
            if len(current_cutoff.intersection(W)) < min(l,len(current_cutoff)) and len(coalition) > len(max_coalition):
                max_coalition = coalition
                max_cutoff = current_cutoff
                max_l = l
    # return coalition, cutoff and l-value of largest PSC violation
    return max_coalition, max_cutoff, max_l

# check truthful and final committee for EJR+ violations
def check_ejr_plus(n, m, k, ballots_truthful, W_truthful, W_final):
    candidate_t,unrep_set_t,l_t   = ejr_plus_violation_max(n,m,k,ballots_truthful,W_truthful)
    candidate_f,unrep_set_f,l_f   = ejr_plus_violation_max(n,m,k,ballots_truthful,W_final)
    return EJRPlusData(candidate_t,unrep_set_t,l_t,candidate_f,unrep_set_f,l_f)

# check truthful and final committee for JR violations
def check_jr(n, m, k, ballots_truthful, W_truthful, W_final):
    candidate_t,unrep_set_t   = jr_violation_max(n,m,k,ballots_truthful,W_truthful)
    candidate_f,unrep_set_f   = jr_violation_max(n,m,k,ballots_truthful,W_final)
    return JRData(candidate_t,unrep_set_t,candidate_f,unrep_set_f)

def check_psc(n, m, k, preferences_truthful, W_truthful, W_final):
    coalition_t, cutoff_t, l_t = psc_violation(n,m,k,preferences_truthful,W_truthful)
    coalition_f, cutoff_f, l_f = psc_violation(n,m,k,preferences_truthful,W_final)
    return PSCData(coalition_t,cutoff_t,l_t,coalition_f,cutoff_f,l_f)