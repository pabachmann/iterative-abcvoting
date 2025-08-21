from types_classes import *
from set_preferences import U_AV

# CALCULATE STATS
# calculate stats for batch from list of data from single elections

# HELPER FUNCTIONS
# calculate number of elements in list that satisfy predicate P
def count_if(P, l):
    return len(list(filter(P, l)))

# calculate sum of function f over list
def sum_f(f, l):
    if l == []: return 0
    return sum([f(x) for x in l])

# calculate PSC stats from list of data from single elections
def get_psc_stats(psc_data_list: list[PSCData]):
    num_elections = len(psc_data_list)
    num_violations_T = count_if(lambda x: x.coalition_T != set(),psc_data_list)
    num_violations_F = count_if(lambda x: x.coalition_F != set(),psc_data_list)
    
    percent_psc_violations_T = num_violations_T / num_elections * 100
    percent_psc_violations_F = num_violations_F / num_elections * 100
    avg_size_psc_violations_T = sum_f(lambda x: len(x.coalition_T),psc_data_list) / (max(1,num_violations_T))
    avg_size_psc_violations_F = sum_f(lambda x: len(x.coalition_F),psc_data_list) / (max(1,num_violations_F))
    return PSCStats(percent_psc_violations_T,percent_psc_violations_F,avg_size_psc_violations_T,avg_size_psc_violations_F,psc_data_list)

# calculate EJR+ stats from list of data from single elections
def get_ejrplus_stats(ejrplus_data_list: list[EJRPlusData]):
    num_elections = len(ejrplus_data_list)
    num_violations_T = count_if(lambda x: x.candidate_T != None,ejrplus_data_list)
    num_violations_F = count_if(lambda x: x.candidate_F != None,ejrplus_data_list)

    percent_ejrplus_violations_T = num_violations_T / num_elections * 100
    percent_ejrplus_violations_F = num_violations_F / num_elections * 100
    avg_size_ejrplus_violations_T = sum_f(lambda x: len(x.unrep_set_T),ejrplus_data_list) / (max(1,num_violations_T))
    avg_size_ejrplus_violations_F = sum_f(lambda x: len(x.unrep_set_F),ejrplus_data_list) / (max(1,num_violations_F))
    return EJRPlusStats(percent_ejrplus_violations_T,percent_ejrplus_violations_F,avg_size_ejrplus_violations_T,avg_size_ejrplus_violations_F,ejrplus_data_list)

# calculate JR stats from list of data from single elections
def get_jr_stats(jr_data_list: list[JRData]):
    num_elections = len(jr_data_list)
    num_violations_T = count_if(lambda x: x.candidate_T != None,jr_data_list)
    num_violations_F = count_if(lambda x: x.candidate_F != None,jr_data_list)

    percent_jr_violations_T = num_violations_T / num_elections * 100
    percent_jr_violations_F = num_violations_F / num_elections * 100
    avg_size_jr_violations_T = sum_f(lambda x: len(x.unrep_set_T),jr_data_list) / (max(1,num_violations_T))
    avg_size_jr_violations_F = sum_f(lambda x: len(x.unrep_set_F),jr_data_list) / (max(1,num_violations_F))
    return JRStats(percent_jr_violations_T,percent_jr_violations_F,avg_size_jr_violations_T,avg_size_jr_violations_F,jr_data_list)

# calculate iteration stats from list of data from single elections
def get_iteration_stats(iteration_data_list: list[IterationData]):
    # helper calculations
    ordinal = iteration_data_list[0].preferences_truthful != None
    num_elections = len(iteration_data_list)
    num_converging = count_if(lambda x: x.converged,iteration_data_list)
    num_cycling = count_if(lambda x: x.cycled,iteration_data_list)
    num_deviating = count_if(lambda x: len(x.all_deviations) > 0,iteration_data_list)

    # calculate stats for output
    percent_converging = num_converging / num_elections * 100
    percent_cycling = num_cycling / num_elections * 100
    percent_deviating = num_deviating / num_elections * 100
    avg_num_deviations = sum_f(lambda x: len(x.all_deviations),iteration_data_list) / num_elections
    avg_num_manipulators = sum_f(lambda x: len(x.manipulators),iteration_data_list) / num_elections
    return IterationStats(percent_converging,percent_cycling,percent_deviating,avg_num_deviations,avg_num_manipulators,iteration_data_list)


# calculate average welfare per voter for given committee using AV utility
def avg_voter_welfare_AV(approval_sets,committee):
    return sum_f(lambda A_i:U_AV(A_i,committee),approval_sets)/len(approval_sets)

# calculate welfare stats from list of data from single elections using AV utility, only for dichotomous setting
def get_welfare_stats(n,iteration_data_list: list[IterationData]):
    # helper calculations
    all_voters = set(range(n))
    num_elections = len(iteration_data_list)
    iteration_data_list_deviations = [x for x in iteration_data_list if x.manipulators != set()]
    num_elections_deviations = max(1,len(iteration_data_list_deviations))

    # calculate average overall welfare
    avg_welfare_T = sum_f(lambda x: avg_voter_welfare_AV(x.ballots_truthful,x.committee_truthful),iteration_data_list) / num_elections
    avg_welfare_F = sum_f(lambda x: avg_voter_welfare_AV(x.ballots_truthful,x.committee_final),iteration_data_list) / num_elections

    # calculate average welfare in elections with deviations
    avg_welfare_T_if_deviations = sum_f(lambda x: avg_voter_welfare_AV(x.ballots_truthful,x.committee_truthful),iteration_data_list_deviations) / num_elections_deviations
    avg_welfare_F_if_deviations = sum_f(lambda x: avg_voter_welfare_AV(x.ballots_truthful,x.committee_final),iteration_data_list_deviations) / num_elections_deviations
    
    # calculate average welfare of manipulators in elections with deviations
    avg_welfare_manipulators_T = sum_f(lambda x: avg_voter_welfare_AV([x.ballots_truthful[i] for i in x.manipulators],x.committee_truthful),iteration_data_list_deviations) / num_elections_deviations
    avg_welfare_manipulators_F = sum_f(lambda x: avg_voter_welfare_AV([x.ballots_truthful[i] for i in x.manipulators],x.committee_final),iteration_data_list_deviations) / num_elections_deviations

    # calculate average welfare of non-manipulators in elections with deviations
    # cannot handle non-manipulators of size 0 (cases where all voters are manipulators)
    # avg_welfare_non_manipulators_T = sum_f(lambda x: avg_voter_welfare_AV([x.ballots_truthful[i] for i in all_voters - x.manipulators],x.committee_truthful),iteration_data_list_deviations) / num_elections_deviations
    #avg_welfare_non_manipulators_F = sum_f(lambda x: avg_voter_welfare_AV([x.ballots_truthful[i] for i in all_voters - x.manipulators],x.committee_final),iteration_data_list_deviations) / num_elections_deviations

    return WelfareStats(avg_welfare_T,avg_welfare_F,avg_welfare_T_if_deviations,avg_welfare_F_if_deviations,avg_welfare_manipulators_T,avg_welfare_manipulators_F)

# calculate all availablestats from list of data from single elections, depending on domain
def get_stats(n,ordinal,election_data_list: list[ElectionData]):
    iteration_stats = get_iteration_stats([x.iteration_data for x in election_data_list])
    if ordinal:
        psc_stats = get_psc_stats([x.psc_data for x in election_data_list])
        return Stats(iteration_stats,psc_stats,None,None,None)
    else: 
        welfare_stats = get_welfare_stats(n,[x.iteration_data for x in election_data_list])
        jr_stats = get_jr_stats([x.jr_data for x in election_data_list])
        ejrplus_stats = get_ejrplus_stats([x.ejrplus_data for x in election_data_list])
        return Stats(iteration_stats,None,welfare_stats,jr_stats,ejrplus_stats)
