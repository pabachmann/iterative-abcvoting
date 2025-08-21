from dataclasses import dataclass, is_dataclass
from typing import Literal
import sys,math

# INPUT PARAMETERS
@dataclass
class BallotGenerationParams:
    skip_empty_ballots: bool
    ordinal: bool
    culture: Literal["impartial","mallows","urn","resampling","manual","noise"]
    # avg_ballot_size determines average ballot size (=k if avg_ballot_size=1)
    avg_ballot_size: float
    alpha: float
    phi: float
    manual_ballots: list[list[set[int]]]
    manual_preference: list[list[list[int]]]
    random_cutoff: bool
    cutoff_points: list[int]

@dataclass
class ABCVotingParams:
    abc_rule: Literal["av","cc", "seqcc" "pav", "seqpav", "sav", "equal-shares", "equal-shares-with-av-completion", "seqphragmen"]
    n: int
    m: int
    k: int
    resolute: bool

@dataclass
class IterationParams:
    max_iterations: int
    cycle_iteration: bool
    
@dataclass
class DeviationParams:
    deviation_type: Literal["brute_force","subset","swap_j","cutoff"]
    swap_j: int
    set_preference: Literal["AV","CCAV","kelly","fishburn","PD"]
    skip_ties: bool

@dataclass
class Parameters:
    num_elections: int
    ballot_generation: BallotGenerationParams
    abcvoting: ABCVotingParams
    iteration: IterationParams
    deviation: DeviationParams
    trace: bool
    filename: str

# OUTPUT DATA (for a single instance)
# use list of _Data, calculate necessary stats after all elections
@dataclass
class IterationData:
    # did the deviations converge or cycle?
    converged: bool
    cycled: bool
    # truthful profile and committee
    preferences_truthful: list[list[int]]
    ballots_truthful: list[set[int]]
    committee_truthful: set[int]
    committee_final: set[int]
    manipulators: set[int]
    # all deviations and committees
    # format: (voter,new ballots,new committee)
    all_deviations: list[(int,list[set[int]],set[int])]

@dataclass
class PSCData:
    coalition_T: int
    cutoff_T: set[int]
    l_T: int
    coalition_F: int
    cutoff_F: set[int]
    l_F: int

@dataclass
class JRData:
    candidate_T: int
    unrep_set_T: set[int]
    candidate_F: int
    unrep_set_F: set[int]

@dataclass
class EJRPlusData:
    candidate_T: int
    unrep_set_T: set[int]
    l_T: int
    candidate_F: int
    unrep_set_F: set[int]
    l_F: int

# contains all data for a single election (wrapper for different data types)
@dataclass
class ElectionData:
    election_index: int
    iteration_data: IterationData
    psc_data: PSCData
    jr_data: JRData
    ejrplus_data: EJRPlusData

# STATS (for a batch of elections with the same parameters)
@dataclass
class IterationStats:
    percent_converging: float
    percent_cycling: float
    percent_deviating: float
    avg_num_deviations: float
    avg_num_manipulators: float    
    all_iteration_data: list[IterationData]

# Welfare: only dichotomous
@dataclass
class WelfareStats:
    avg_welfare_T: float
    avg_welfare_F: float
    avg_welfare_dev_T: float
    avg_welfare_dev_F: float
    avg_welfare_manip_dev_T: float
    avg_welfare_manip_dev_F: float
    #avg_welfare_non_manip_dev_T: float
    #avg_welfare_non_manip_dev_F: float

# JR: only dichotomous
@dataclass
class JRStats:
    percent_jr_violations_T: float
    percent_jr_violations_F: float
    avg_size_jr_violation_T: float
    avg_size_jr_violation_F: float
    all_jr_data: list[JRData]

# EJR+: only dichotomous
@dataclass
class EJRPlusStats:
    percent_ejrplus_violations_T: float
    percent_ejrplus_violations_F: float
    avg_size_ejrplus_violation_T: float
    avg_size_ejrplus_violation_F: float
    all_ejrplus_data: list[EJRPlusData]

# PSC: only ordinal
@dataclass
class PSCStats:
    percent_psc_violations_T: float
    percent_psc_violations_F: float
    avg_size_psc_violation_T: float
    avg_size_psc_violation_F: float
    all_psc_data: list[PSCData]

# contains all stats for a batch of elections (wrapper for different stat types)
@dataclass
class Stats:
    iteration_stats: IterationStats
    psc_stats: PSCStats
    welfare_stats: WelfareStats
    jr_stats: JRStats
    ejrplus_stats: EJRPlusStats

# PRINTING
def print_deviations(deviations, add_str="", file=sys.stdout):
    print(add_str + "Deviations:",file=file)
    add_str += "\t"
    for i in range(len(deviations)):
        voter, ballots, comittee = deviations[i]
        ballot_old = "" if i==0 else str(deviations[i-1][1][voter])
        print(add_str + f"Voter {voter}:        \t{ballot_old} -> {ballots[voter]}\n{add_str}  New Ballots:  \t{ballots}\n{add_str}  New Committee:\t{comittee}",file=file)

def print_dataclass(d,noprint={"all_iteration_data","all_ejrplus_data","all_jr_data","all_psc_data"},print_None=False,add_str="",file=sys.stdout):
    for key, value in d.__dict__.items():
        if key in noprint:
            continue
        if is_dataclass(type(value)):
            print(add_str + key,file=file)
            print_dataclass(value,add_str=add_str + "  ",file=file)
        else:
            l = len(key)
            tabs = "\t"*math.ceil(((31-l-len(add_str))/8))
            if value != None or print_None:
                if key == "all_deviations":
                    print_deviations(value,add_str=add_str,file=file)
                else:
                    print(add_str + key + " " + tabs + str(value),file=file)

# write full log from all elections to file
def write_log(stats,parameters):
    with open(parameters.filename + "/full_log.txt", "a") as f:
        for i in range(len(stats.iteration_stats.all_iteration_data)):
            print("PROFILE " + str(i) + ":",file=f)
            print_dataclass(stats.iteration_stats.all_iteration_data[i],add_str="  ",noprint=set(),file=f)
            if parameters.ballot_generation.ordinal:
                if stats.psc_stats.all_psc_data[i].coalition_T != set() or stats.psc_stats.all_psc_data[i].coalition_F != set():
                    print("PSC violated",file=f)
                    print_dataclass(stats.psc_stats.all_psc_data[i],add_str="  ",noprint=set(),print_None=True,file=f)
            else:
                if stats.ejrplus_stats.all_ejrplus_data[i].candidate_T != None or stats.ejrplus_stats.all_ejrplus_data[i].candidate_F != None:
                    print("EJR+ violated",file=f)
                    print_dataclass(stats.ejrplus_stats.all_ejrplus_data[i],add_str="  ",noprint=set(),print_None=True,file=f)
                if stats.jr_stats.all_jr_data[i].candidate_T != None or stats.jr_stats.all_jr_data[i].candidate_F != None:
                    print("JR violated",file=f)
                    print_dataclass(stats.jr_stats.all_jr_data[i],add_str="  ",noprint=set(),print_None=True,file=f)
            print("-------------------------------------------------",file=f)