import random

# culture generation
from prefsampling.approval import impartial, urn, resampling
from prefsampling.ordinal import impartial as impartial_ordinal, urn as urn_ordinal

# IABC
from basics_and_helpers import random_number_between
from types_classes import Parameters

# CUTOFF BALLOTS
# cannot use truncated_ordinal as we need the original ordinal profile for comparisons

# int64 to int conversion for a ballot
def to_int_ballot(ballot):
    return [int(c) for c in ballot]

# int64 to int conversion for a list of ballots (profile)
def to_int_profile(ballots):
    return [to_int_ballot(b) for b in ballots]

# cut off ballots from ordinal preference profile according to provided cutoff points
def cutoff_from_ordinal(ballots, cutoffs):
    return [set(to_int_ballot(ballots[i][:cutoffs[i]])) for i in range(0,len(ballots))]

# randomly cut-off ballots from ordinal preference profile according to average size 
def cutoff_from_ordinal_r(ballots, avg_size, skip_empty_ballots):
    return [set(to_int_ballot(p[:random_number_between(skip_empty_ballots,len(p),avg_size,len(p)/8)])) for p in ballots]

# generate all possible cutoffs from ordinal preference
def all_cutoffs_from_ordinal(ballot):
    return [set(to_int_ballot(ballot[:cutoff])) for cutoff in range(1,len(ballot)+1)]


# CANDIDATE INTERVAL
# generate a candidate interval ballot of average size avg_size
def generate_candidate_interval_ballot(num_candidates,avg_size,skip_empty_ballots):
    size = random_number_between(skip_empty_ballots,num_candidates,avg_size,num_candidates/8)
    startpoint = random.randint(0,num_candidates-size)
    return set(list(range(0,num_candidates))[startpoint:startpoint+size])

# generate a profile of candidate interval ballots
def candidate_interval(num_voters,num_candidates,avg_size,skip_empty_ballots):
    return [generate_candidate_interval_ballot(num_candidates,avg_size,skip_empty_ballots) for _ in range(0,num_voters)]


# VOTER INTERVAL
# generate a voter interval support set for a candidate 
def generate_voter_interval_support_set(num_voters,avg_size_support_set):
    size = random_number_between(0,num_voters,avg_size_support_set,num_voters/8)
    startpoint = random.randint(0,num_voters-size)
    return set(list(range(0,num_voters))[startpoint:startpoint+size])

# obtain ballot for voter i from list of support sets
# picks random singleton ballot if empty and skip_empty_ballots
def ballot_from_support_sets(i,support_sets,skip_empty_ballots):
    ballot = {c for c in range(len(support_sets)) if i in support_sets[c]}
    if skip_empty_ballots and ballot == set():
        ballot = {random.randint(0,len(support_sets)-1)}
    return ballot

# generate a profile of voter interval ballots
def voter_interval(num_voters,num_candidates,avg_size,skip_empty_ballots):
    avg_size_support_set = (avg_size * num_voters)/num_candidates
    support_sets = [generate_voter_interval_support_set(num_voters,avg_size_support_set) for _ in range(num_candidates)]
    return [ballot_from_support_sets(i,support_sets,skip_empty_ballots) for i in range(num_voters)]


# GENERAL BALLOT GENERATION
# generate ballots from given parameters
def generate_ballots(params:Parameters,index:int):
    # set candidate approval probability p to k/m * avg_ballot_size
    if not params.ballot_generation.ordinal and not params.ballot_generation.culture == "manual":
        p = params.abcvoting.k/params.abcvoting.m * params.ballot_generation.avg_ballot_size
    # generate preferences and ballots according to parameters
    if params.ballot_generation.ordinal:
        match params.ballot_generation.culture:
            case "impartial":
                preferences_truthful = impartial_ordinal(num_voters=params.abcvoting.n, num_candidates=params.abcvoting.m)
            case "mallows":
                preferences_truthful = mallows(num_voters=params.abcvoting.n, num_candidates=params.abcvoting.m, phi=params.ballot_generation.phi)
            case "urn":
                preferences_truthful = urn_ordinal(num_voters=params.abcvoting.n,num_candidates=params.abcvoting.m,alpha=params.ballot_generation.alpha)
            case "manual":
                preferences_truthful = params.ballot_generation.manual_preference[index]
        if params.ballot_generation.random_cutoff:
            ballots_truthful = cutoff_from_ordinal_r(preferences_truthful,params.abcvoting.k*params.ballot_generation.avg_ballot_size,params.ballot_generation.skip_empty_ballots)
        else:
            ballots_truthful = cutoff_from_ordinal(preferences_truthful,params.ballot_generation.cutoff_points)
        preferences_truthful = to_int_profile(preferences_truthful)
    else:
        preferences_truthful = None
        match params.ballot_generation.culture:
            case "impartial":
                ballots_truthful = impartial(num_voters=params.abcvoting.n, num_candidates=params.abcvoting.m, p=p)
            case "resampling":
                ballots_truthful = resampling(num_voters=params.abcvoting.n, num_candidates=params.abcvoting.m, phi=params.ballot_generation.phi, rel_size_central_vote=p)
            case "urn":
                ballots_truthful = urn(num_voters=params.abcvoting.n, num_candidates=params.abcvoting.m, p=p, alpha=params.ballot_generation.alpha)
            case "candidate_interval":
                ballots_truthful = candidate_interval(num_voters=params.abcvoting.n, num_candidates=params.abcvoting.m,avg_size=params.abcvoting.k*params.ballot_generation.avg_ballot_size,skip_empty_ballots=params.ballot_generation.skip_empty_ballots)
            case "voter_interval":
                ballots_truthful = voter_interval(num_voters=params.abcvoting.n, num_candidates=params.abcvoting.m,avg_size=params.abcvoting.k*params.ballot_generation.avg_ballot_size,skip_empty_ballots=params.ballot_generation.skip_empty_ballots)
            case "manual":
                ballots_truthful = params.ballot_generation.manual_ballots[index]
    # regenerate ballots and preferences if empty set contained
    if params.ballot_generation.skip_empty_ballots and set() in ballots_truthful:
        return generate_ballots(params,index)
    return (preferences_truthful, ballots_truthful)