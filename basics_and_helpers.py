# basic
import sys
import numpy.random as random
from itertools import chain, combinations

# caching (memoisation)
from functools import lru_cache

# IABC
from abcvoting.preferences import Profile
from abcvoting import abcrules
from types_classes import *

# HELPER FUNCTIONS
# powerset
def powerset(iterable):
    s = list(iterable)
    return list(map(set, chain.from_iterable(combinations(s,r) for r in range(1,len(s)+1))))

# returns all subsets of length k
def get_subsets_len_k(input_set:set,k:int):
    return list(map(set,combinations(input_set,k)))

# convert ballot profile to tuple of frozensets to make it hashable
def hashable_set_list(set_list:list[set]):
    return tuple(map(frozenset,set_list))

# convert ballot profile to sorted tuple of frozensets to make it hashable
def hashable_sorted_set_list(set_list:list[set]):
    return hashable_set_list(sorted(map(sorted,set_list),key=lambda x: tuple(iter(x))))

# count non-zero elements in list, returns 1 if empty to avoid division by zero
def len_nonzero(l):
    l = len([1 for x in l if x != 0])
    if l == 0: return 1
    return l

# generate a random number between a and b, mean m and standard deviation s
def random_number_between(a,b,m,s):
    num = round(random.normal(m,s))
    return max(a,min(b,num))

# print election ballots and winning committee
# optional: custom string, file specifier and color
def print_election(ballots, W, add_str = "", io = sys.stdout, color = "\033[0m"):
    print(color + add_str + "ballots:   \t" + str(ballots) + "\n" + add_str + "committee: \t" + str(W) + "\033[0m", file=io)

def support_set(ballots_truthful, c):
    return {v for v in range(len(ballots_truthful)) if c in ballots_truthful[v]}

# ITERATION LIST GENERATION
# list of l random numbers between 0 and n-1
def random_list(l, n):
    return [random.randint(0,n) for _ in range(l)]

# list of l numbers cycling through 0 to n-1
def cycle_list(l, n):
    return [i % n for i in range(l)]

# COMMITTEE COMPUTATION
# generalised Thiele rule (experimental for finding cycles, not fully implemented for simulations)
def score_thiele(score_vector,ballots,W):
    return sum([sum(score_vector[:len(A.intersection(W))]) for A in ballots])

w_small = [1,0.1,0.01,0.001,0.0001,0.00001,0.000001,0.0000001,0.00000001]
w_large = [1,0.99999999,0.9999999,0.999999,0.99999,0.9999,0.999,0.99,0.9]
w_pav = [1,1/2,1/3,1/4,1/5,1/6,1/7,1/8,1/9]

@lru_cache(maxsize=100000)
def compute_thiele(m,k,ballots):
    committees = sorted(get_subsets_len_k(range(m),k),key=lambda x: tuple(iter(x)))
    W_small = max(committees,key=lambda W:score_thiele(w_small,ballots,W))
    W_large = max(committees,key=lambda W:score_thiele(w_large,ballots,W))
    if W_small == W_large:
        return frozenset(W_small), (len([W for W in committees if score_thiele(w_small,ballots,W) == score_thiele(w_small,ballots,W_small)]) != 1)
    else:
        return None, True

# computes winning committees
# optimisation: memoized
# can only be used with hashable ballots (frozensets)
# returns (hashable) sorted tuple of frozensets
@lru_cache(maxsize=100000)
def compute_committees_memoized(abc_rule,m,k,resolute,ballots):
    profile = Profile(num_cand=m)
    profile.add_voters(ballots)
    return hashable_sorted_set_list(abcrules.compute(abc_rule,profile,k,resolute=resolute))

# computes winning committee and checks if tied
# makes parameters hashable for and unpacks tuples from memoized function
# returns lexicographically first committee and bool whether committee is tied
def compute_committee(params:Parameters, ballots):
    ballots_hashable = hashable_sorted_set_list(ballots)
    if params.abcvoting.abc_rule == "thiele_manual":
        W, tied = compute_thiele(params.abcvoting.m,params.abcvoting.k,ballots_hashable)
        if W is None:
            return None, True
        return set(W),tied
    else:
        committees = compute_committees_memoized(params.abcvoting.abc_rule,params.abcvoting.m,params.abcvoting.k,resolute,ballots_hashable)
        committee = set(committees[0])
        tied = len(committees) > 1
        return committee,tied

