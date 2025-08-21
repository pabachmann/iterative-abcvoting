# IABC
from types_classes import *

# check parameters for validity
def check_params(params:Parameters):
    valid = True
    valid = valid and params.abcvoting.m >= params.abcvoting.k and params.abcvoting.n > 0 and params.abcvoting.m > 0 and params.abcvoting.k > 0
    if not valid:
        print("\033[91mABC Parameters invalid\033[0m")
        return valid

    valid = valid and params.ballot_generation.culture in ["impartial","urn","resampling","manual","noise","candidate_interval","voter_interval"]
    if not valid:
        print("\033[91mBallot Generation Parameters invalid\033[0m")
        return valid

    valid = valid and params.deviation.deviation_type in ["cutoff","subset","swap_j","brute_force"]
    if not valid:
        print("\033[91mDeviation Parameters invalid\033[0m")
        return valid

    valid = valid and params.deviation.set_preference in ["PD","K","F","AV","CCAV"]
    if not valid:
        print("\033[91mSet Preference Parameters invalid\033[0m")
        return valid
    
    if params.ballot_generation.culture == "manual":
        if params.ballot_generation.ordinal:
            valid = valid and params.ballot_generation.avg_ballot_size > 0
            valid = valid and len(params.ballot_generation.manual_preference) == params.num_elections
            valid = valid and all(len(profile) == params.abcvoting.n for profile in params.ballot_generation.manual_preference)
            valid = valid and all(all(max(preference) < params.abcvoting.m and 0<=min(preference) for preference in profile) for profile in params.ballot_generation.manual_preference)
            valid = valid and all(all(len(set(preference)) == params.abcvoting.m for preference in profile) for profile in params.ballot_generation.manual_preference)
        else:
            valid = valid and len(params.ballot_generation.manual_ballots) == params.num_elections
            valid = valid and all(len(profile) == params.abcvoting.n for profile in params.ballot_generation.manual_ballots)
            valid = valid and all(all(max(ballot) < params.abcvoting.m and 0<=min(ballot) for ballot in profile) for profile in params.ballot_generation.manual_ballots)
    else:
        valid = valid and params.ballot_generation.avg_ballot_size > 0

    if not valid:
        print("\033[91mManual Parameters invalid\033[0m")
        return valid

    if params.deviation.deviation_type == "swap_j":
        valid = valid and params.deviation.swap_j <= params.abcvoting.m and params.deviation.swap_j > 0
    if not valid:
        print("\033[91mSwap-j parameter invalid\033[0m")
        return valid

    if params.deviation.deviation_type == "cutoff":
        valid = valid and params.ballot_generation.ordinal
        if not params.ballot_generation.random_cutoff:
            valid = valid and len(params.ballot_generation.cutoff_points) == params.abcvoting.n
    if not valid:
        print("\033[91mCutoff Parameters invalid\033[0m")
        return valid

    if params.ballot_generation.ordinal:
        valid = valid and params.deviation.set_preference in ["PD","K","F"] and params.ballot_generation.culture in ["impartial","urn","manual"]
    else:
        valid = valid and params.deviation.set_preference in ["AV","CCAV"] and params.ballot_generation.culture in ["impartial","resampling","urn","manual","candidate_interval","voter_interval"]
    if not valid:
        print("\033[91mParameters incompatible with ordinal/dichotomous setting\033[0m")
        return valid
    
    return valid

# convert parameters to dataclass format, set unused parameters to None, check for validity
def set_params(num_elections,skip_empty_ballots,ordinal,culture,avg_ballot_size,alpha,phi,manual_ballots,manual_preference,random_cutoff,cutoff_points,abc_rule,n,m,k,resolute,max_iterations,cycle_iteration,deviation_type,swap_j,set_preference,skip_ties,trace,filename):
    # set unused parameters to None
    if random_cutoff:
        cutoff_points = None
    if not culture == "manual":
        manual_ballots = None
        manual_preference = None
    elif not ordinal:
        avg_ballot_size = None
    if not ordinal:
        manual_preference = None
        cutoff_points = None
        random_cutoff = None
    else:
        manual_ballots = None
    if not deviation_type == "swap_j":
        swap_j = None
    if not (culture == "resampling" or culture == "noise"):
        phi = None
    if not culture == "urn":
        alpha = None

    # set sequential rules to resolute for simulations since their tie-breaking is lexicographic
    #if abc_rule.startswith("seq") or abc_rule.startswith("equal-shares"):
    #    resolute = True

    # set resolute to false in order to detect unique winning committees when skipping ties
    if skip_ties:
        resolute = False

    # create dataclass instances for parameters
    ballot_generation_params = BallotGenerationParams(skip_empty_ballots, ordinal, culture, avg_ballot_size, alpha, phi, manual_ballots, manual_preference, random_cutoff, cutoff_points)
    abc_voting_params = ABCVotingParams(abc_rule, n, m, k, resolute)
    iteration_params = IterationParams(max_iterations, cycle_iteration)
    deviation_params = DeviationParams(deviation_type, swap_j, set_preference, skip_ties)

    parameters = Parameters(num_elections, ballot_generation_params, abc_voting_params, iteration_params, deviation_params, trace, filename)

    # check if parameters are valid
    if not check_params(parameters):
        print("\033[91mParameters not valid!\033[0m")
        raise ValueError

    return parameters

