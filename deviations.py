# basics
from types_classes import *
from itertools import combinations
import random

# IABC
from ballot_generation import all_cutoffs_from_ordinal
from basics_and_helpers import compute_committee, powerset
from set_preferences import cmp_committees, U_AV, U_CCAV


# DEVIATIONS
# all ballots obtained by swap-j heuristic (iterative up to j, adapted from Martinez)
def get_ballots_swap_j(ballot, j, m):
    ballots_result = []
    for i in range(1,j+1):
        flip_tuples = combinations(range(m), i)
        for flip_candidates in flip_tuples:
            new_ballot = ballot.copy()
            for c in flip_candidates:
                if c in new_ballot:
                    new_ballot.remove(c)
                else:
                    new_ballot.add(c)
            ballots_result.append(new_ballot)
    return ballots_result

# generate all possible deviating ballots
# takes parameters, a voter's truthful preference/ballot and the current ballot
def get_deviation_ballots(params:Parameters,preferences_t,ballots_t,ballots,i):
    match params.deviation.deviation_type:
        case "cutoff":
            deviation_ballots = all_cutoffs_from_ordinal(preferences_t[i])
        case "subset":
            deviation_ballots = powerset(ballots_t[i])
        case "brute_force":
            deviation_ballots = powerset(range(params.abcvoting.m))
        case "swap_j":
            deviation_ballots = get_ballots_swap_j(ballots[i],params.deviation.swap_j,params.abcvoting.m)
        case _:
            print("\033[91mUnknown deviation type: " + str(params.deviation.deviation_type) + "\033[0m")
            raise ValueError
    # shuffle deviation ballots to avoid bias
    random.shuffle(deviation_ballots)
    return deviation_ballots
            
# find a best deviation for voter i according to deviation type and comparison function
def get_deviation(params:Parameters, preferences_t, ballots_t, i, ballots, W_current):
    ballot_old = ballots[i]
    # generate all possible deviating ballots in random order according to deviation type
    deviation_ballots = get_deviation_ballots(params,preferences_t,ballots_t,ballots,i)
    # initialise: current best ballot and committee W
    ballot_best,W_best = ballot_old, W_current
    for ballot_test in deviation_ballots:
        # optimisation: if utility is already maximal, no need to continue
        if (params.deviation.set_preference == "AV" and U_AV(W_best,ballots_t[i]) == min(params.abcvoting.k,len(ballots_t[i]))) or (params.deviation.set_preference == "CCAV" and U_CCAV(W_best,ballots_t[i]) == 1) or (params.ballot_generation.ordinal and W_best == set(preferences_t[i][:params.abcvoting.k])):
            break
        # copy ballots and insert current swap ballot to check new W
        ballots[i] = ballot_test
        # compute committee with test ballot, check if tied
        W_test,tied = compute_committee(params,ballots)
        if params.deviation.skip_ties and tied:
            continue
        # update current best deviation if W_test is better than W_best
        if cmp_committees(params,preferences_t,ballots_t,i,W_test,W_best):
            ballot_best,W_best = ballot_test,W_test
    if ballot_best == ballot_old:
        return None
    return ballot_best,W_best


