# basics
import datetime, os, random
from itertools import chain, combinations, product

# IABC
from types_classes import *
from parameters import set_params
from iterations import run_profiles

## PARAMETERS
num_elections       = 10000

# BALLOT GENERATION
# skip profiles with empty ballots
skip_empty_ballots  = True
# if using ordinal preferences
ordinal             = True
# factor for average ballot size (1: average ballot size==k)
avg_ballot_size     = 1
# define sampling model (resampling, urn, interval, manual, ...)
culture             = "urn"
# dispersion coefficient for urn models
alpha               = 0.3
# resampling probability
phi                 = 0.75
# for ordinal preferences: initial cutoff points random or manual
random_cutoff       = True
# manual settings (preference/ballots: lists of len num_elections)
# list(map(len, []))
cutoff_points       = [1,1,3,4,1] 
manual_preference   = [[[4, 1, 0, 2, 3], [1, 4, 0, 2, 3], [4, 1, 0, 2, 3], [1, 0, 4, 3, 2], [3, 0, 2, 1, 4]]]*num_elections
manual_ballots      = [seqphragmen_ejrplus_vio]*num_elections

# ABC VOTING
abc_rule            = "cc"
n                   = 6
m                   = 6
k                   = 2
# True: use abcvoting resoluteness parameter (not always lexicographically minimal!)
# False: choose lexicographically minimal committee from tied committees
resolute            = False

# ITERATIONS
# maximum number of iterations per profile
max_iterations      = 100
# True: cycle over voters, False: randomly choose voters
cycle_iteration     = True

# DEVIATIONS
# cutoff, subset, swap_j (swap_j used) or brute_force
deviation_type      = "swap_j"
swap_j              = 2
# dichotomous: AV, CCAV, ordinal: K (Kelly), F (Fishburn), PD (Pairwise Dominance)
set_preference      = "K"
# restrict search to profiles with unique winning committee
skip_ties           = False

trace               = False


# run once for fixed (global) parameters
def run_batch():
    # set file output path
    filename = "/Users/Gast/Simulations/results/" + abc_rule.upper() + "/n" + str(n) + " m" + str(m) + " k" + str(k) + " x" + str(num_elections) + " " + str(datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
    os.mkdir(filename)
    # set parameters and run elections
    parameters = set_params(num_elections,skip_empty_ballots,ordinal,culture,avg_ballot_size,alpha,phi,manual_ballots,manual_preference,random_cutoff,cutoff_points,abc_rule,n,m,k,resolute,max_iterations,cycle_iteration,deviation_type,swap_j,set_preference,skip_ties,trace,filename)
    stats = run_profiles(parameters)
    # write parameters and stats to file
    with open(parameters.filename + "/params_stats.txt", "a") as f:
        print("Parameters:",file=f)
        print_dataclass(parameters,file=f)
        print("-------------------------------------------------",file=f)
        print("Stats:",file=f)
        print_dataclass(stats,file=f)
    # print parameters and stats to console
    print("\033[96m-------------------------------------------------")
    print("Parameters:")
    print_dataclass(parameters)
    print("\033[92m-------------------------------------------------")
    print("Stats:")
    print_dataclass(stats)
    print("-------------------------------------------------\033[0m")
    # write log to file
    write_log(stats,parameters)


if __name__ == "__main__":
    run_batch()

