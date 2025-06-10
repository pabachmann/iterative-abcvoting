import os, random
from iterations import run_profiles
from parameters import set_params
from types_classes import *

# data storage
import pandas as pd

# manual approval preferences for ejr+ violations in seqphragmen and seqpav
seqphragmen_ejrplus_vio = [{0,1,2}]*2 + [{0,1,3}]*2 + [{2,3,4,5,6,7,8,9,10,11,12,13}]*6 + [{3,4,5,6,7,8,9,10,11,12,13}]*5 + [{4,5,6,7,8,9,10,11,12,13}]*9
random.shuffle(seqphragmen_ejrplus_vio)

seqpav_ejrplus_vio = [{0,1,2,3,4},{0,1,2,3,5}] + [{0,1,3,4}]*9 + [{0,1,3,5}]*8 + [{0,2,4}]*8 + [{0,2,5}]*10 + [{0,3,5}] + [{1,2,3}]*4 + [{1,2,5}]*5 + [{1,4}]*7 + [{1,5}]*2 + [{2,3}]*4 + [{2,4}]*3 + [{2,5}] + [{3}]*9 + [{4}]*8 + [{5}]*9 + [{6}]*18
random.shuffle(seqpav_ejrplus_vio)

## SET FIXED PARAMETERS
# variable parameters will overwrite fixed ones
num_elections       = 1000

# BALLOT GENERATION
skip_empty_ballots  = True
ordinal             = False
avg_ballot_size     = 1
culture             = "resampling"
alpha               = 0.3
phi                 = 0.75
random_cutoff       = True
# manual settings
cutoff_points       = list(map(len, []))
manual_preference   = []
manual_ballots      = [seqpav_ejrplus_vio]*num_elections

# ABC VOTING
abc_rule            = "sav"
n                   = 4
m                   = 10
k                   = 2
resolute            = False

# ITERATIONS
max_iterations      = 100
cycle_iteration     = True

# DEVIATIONS
deviation_type      = "swap_j"
swap_j              = 1
set_preference      = "AV"
skip_ties           = False
trace               = False

krange = [2,4,6,8]
mrange = [6,8,10,12,14]
nrange = [2,4,8,12,16,20]

## RUN BATCHES FOR SIMULATIONS
def plot_elections_rules(data_filename):
    # initialise lists for dataframe
    parameters_list, stats_list = [], []
    # set file output path
    os.mkdir(data_filename)
    #["av","cc", "seqcc", "pav", "seqpav", "sav", "equal-shares", "equal-shares-with-av-completion", "seqphragmen"]
    for abc_rule in ["seqcc", "seqpav", "sav", "equal-shares", "seqphragmen"]:
        for max_iterations in [20,40,60,80,100]:
            for cycle_iteration in [True, False]:
                filename = data_filename + "/" + str(abc_rule) + "_" + str(max_iterations) + "_" + str(cycle_iteration)
                os.mkdir(filename)
                parameters = set_params(num_elections,skip_empty_ballots,ordinal,culture,avg_ballot_size,alpha,phi,manual_ballots,manual_preference,random_cutoff,cutoff_points,abc_rule,n,m,k,resolute,max_iterations,cycle_iteration,deviation_type,swap_j,set_preference,skip_ties,trace,filename)
                stats = run_profiles(parameters)
                with open(parameters.filename + "/params_stats.txt", "a") as f:
                    print("Parameters:",file=f)
                    print_dataclass(parameters,file=f)
                    print("-------------------------------------------------",file=f)
                    print("Stats:",file=f)
                    print_dataclass(stats,file=f)
                write_log(stats,parameters)
                # save parameters and stats for dataframe
                parameters_list.append(parameters)
                stats_list.append(stats)
    # store to dataframe
    df = pd.DataFrame({
        "parameters": parameters_list,
        "stats": stats_list
    })
    # store dataframe to file
    df.to_pickle(data_filename+"/params_stats.pkl")
    return

def plot_elections_two_params(data_filename):
    # initialise lists for dataframe
    parameters_list, stats_list = [], []
    # set file output path
    os.mkdir(data_filename)
    for n in [2,4,8,12,16]:
        for m in [10,20,30,40,50]:
            filename = data_filename + "/" + str(n) + "_" + str(m)
            os.mkdir(filename)
            parameters = set_params(num_elections,skip_empty_ballots,ordinal,culture,avg_ballot_size,alpha,phi,manual_ballots,manual_preference,random_cutoff,cutoff_points,abc_rule,n,m,k,resolute,max_iterations,cycle_iteration,deviation_type,swap_j,set_preference,skip_ties,trace,filename)
            stats = run_profiles(parameters)
            with open(parameters.filename + "/params_stats.txt", "a") as f:
                print("Parameters:",file=f)
                print_dataclass(parameters,file=f)
                print("-------------------------------------------------",file=f)
                print("Stats:",file=f)
                print_dataclass(stats,file=f)
            write_log(stats,parameters)
            # save parameters and stats for dataframe
            parameters_list.append(parameters)
            stats_list.append(stats)
    # store to dataframe
    df = pd.DataFrame({
        "parameters": parameters_list,
        "stats": stats_list
    })
    # store dataframe to file
    df.to_pickle(data_filename+"/params_stats.pkl")
    return

data_filename = ""

if __name__ == "__main__":
    plot_elections_two_params(data_filename)