# basics
import random

# IABC
from types_classes import *
from basics_and_helpers import hashable_set_list, compute_committee, random_list, cycle_list
from ballot_generation import generate_ballots
from deviations import get_deviation
from properties import check_ejr_plus, check_jr, check_psc
from stats import get_stats

# parallelisation
from multiprocessing import Pool

# plotting
import pandas as pd



# ITERATIONS
# find and apply improving deviations for all voters in the indices list
def iterate_deviations(params:Parameters, preferences_t, ballots_t, W_t):
    # initialise current ballots and committee
    ballots_current = ballots_t[:]
    W_current       = W_t

    # initialise iteration list (random or cycling)
    index_list      = cycle_list(params.iteration.max_iterations,params.abcvoting.n) if params.iteration.cycle_iteration else random_list(params.iteration.max_iterations,params.abcvoting.n)

    # initialise iteration stats
    converged       = True
    cycle           = False
    all_deviations  = []
    manipulators    = set()

    # store all profiles seen to detect cycles 
    profiles_seen   = set()

    # convergence detection: track last change (cyclic) / track set of non-manipulating voters (random)
    if params.iteration.cycle_iteration:
        last_change = 0
    else:
        non_manipulators = set()
    for j in range(len(index_list)):
        # convergence detection
        if params.iteration.cycle_iteration:
            if j-last_change >= params.abcvoting.n:
                converged = True
                break
        elif non_manipulators == set(range(params.abcvoting.n)):
            converged = True
            break
        # get next voter i
        i = index_list[j]
        # store current profile for cycle detection
        profiles_seen.add(hashable_set_list(ballots_current))

        # obtain a best deviation for voter i
        deviation = get_deviation(params, preferences_t, ballots_t, i, ballots_current[:], W_current)
        # apply deviating ballot if one is found
        if deviation != None:
            # update current ballots
            ballot_i_new, W_new = deviation
            ballots_current[i] = ballot_i_new
            W_current = W_new

            # track iteration statistics
            converged = False
            all_deviations.append((i,ballots_current[:],W_current))
            manipulators.add(i)
            
            # reset convergence detection
            if params.iteration.cycle_iteration:
                last_change = j
            else:
                non_manipulators = {i}

            # cycle detection
            if hashable_set_list(ballots_current) in profiles_seen:
                cycle = True
                break
        elif not params.iteration.cycle_iteration: 
            # optimisation: add to set of non-manipulating voters
            non_manipulators.add(i)
    # compute total manipulators and store iteration stats
    iteration_data = IterationData(converged,cycle,preferences_t,ballots_t,W_t,W_current,manipulators,all_deviations)
    return iteration_data

# run a single preference profile through iterations, collect and return stats
def run_profile(index, params:Parameters):
    print("Profile " + str(index))

    # generate preferences and ballots, compute truthful committee
    preferences_truthful,ballots_truthful = generate_ballots(params,index)
    committee_truthful,tied  = compute_committee(params,ballots_truthful)

    while params.deviation.skip_ties and tied:
        if params.trace: print("\033[91mProfile " + str(index) + " has a tied committee, regenerating preferences ...\033[0m")
        preferences_truthful,ballots_truthful = generate_ballots(params,index)
        committee_truthful,tied  = compute_committee(params,ballots_truthful)

    # iterate over the given voters and find improving deviations, collect data
    iteration_data = iterate_deviations(params,preferences_truthful,ballots_truthful,committee_truthful)
    # output cycles if found
    if iteration_data.cycled:
        with open(params.filename + "/cycles.txt", "a") as f:
            print("Profile " + str(index),file=f)
            print_dataclass(iteration_data,file=f)
            print("-------------------------------------------------",file=f)
    # print iteration data for each election if trace enabled
    if params.trace:
        print_dataclass(iteration_data)
    
    # check proportionality violations and return collected data
    if params.ballot_generation.ordinal:
        psc_data = check_psc(params.abcvoting.n,params.abcvoting.m,params.abcvoting.k,preferences_truthful,iteration_data.committee_truthful,iteration_data.committee_final)
        return ElectionData(index,iteration_data,psc_data,None,None)
    else:
        ejrplus_data = check_ejr_plus(params.abcvoting.n,params.abcvoting.m,params.abcvoting.k,ballots_truthful,committee_truthful,iteration_data.committee_final)
        jr_data = check_jr(params.abcvoting.n,params.abcvoting.m,params.abcvoting.k,ballots_truthful,committee_truthful,iteration_data.committee_final)
        return ElectionData(index,iteration_data,None,jr_data,ejrplus_data)

# run num_elections profiles for the given parameters, collect and return stats
def run_profiles(params:Parameters):
    with Pool() as pool:
        data_total = list(pool.starmap(run_profile,[(i, params) for i in range(params.num_elections)]))

    # filter out None and check for empty result
    iteration_data_total = list(filter(lambda x: x != None, data_total))
    if iteration_data_total == []:
        print("\033[91mNo data collected, probably only tied committees.\033[0m")
        raise ValueError

    return get_stats(params.abcvoting.n,params.ballot_generation.ordinal,iteration_data_total)
