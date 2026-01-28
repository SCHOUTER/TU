#!/usr/bin/env python
# coding: utf-8

# # Bonus Exercise 3
# In this bonus exercise you will work with Bayesian networks and rejection sampling. <br>
# First enter your name and matrikelnummer. Without those we can't give you points.
# 

# In[30]:


#TODO: Enter your matriculation number and name
matrikelnummer = 3602227
name = "Niclas Kusenbach"


# # Bayesian Networks & Rejection Sampling
# Below you will find two Bayesian networks (Burglary-Alarm and Sprinkler). Complete the code cells to compute joint probabilities and approximate inference by rejection sampling.
# 
# ### General notes
# - All variables are **Boolean** (take values `True` or `False`).
# - For every variable `X`, the CPT stores **P(X=True | parents(X))**.
# - If `X` is `False`, then **P(X=False | parents) = 1 - P(X=True | parents)**.
# - `variable_order` is a **topological order**; iterate in this order when sampling.
# - For posterior queries you must return a **normalized** distribution of the form `dict {True: p, False: p}`.
# - Keep the function signatures unchanged.
# 

# ## Bayesian Network: Burglary Alarm
# Classic network with Burglary (B), Earthquake (E), Alarm (A), JohnCalls (J), MaryCalls (M).
# 

# In[31]:


# Burglary-Alarm network
burglary_bn = {
    "B": {"parents": [], "cpt": {(): 0.001}},
    "E": {"parents": [], "cpt": {(): 0.002}},
    "A": {
        "parents": ["B", "E"],
        "cpt": {
            (True, True): 0.95,
            (True, False): 0.94,
            (False, True): 0.29,
            (False, False): 0.001,
        },
    },
    "J": {"parents": ["A"], "cpt": {(True,): 0.90, (False,): 0.05}},
    "M": {"parents": ["A"], "cpt": {(True,): 0.70, (False,): 0.01}},
}

burglary_order = ["B", "E", "A", "J", "M"]


# ## Bayesian Network: Sprinkler
# Cloudy (C) influences Sprinkler (S) and Rain (R), which together influence WetGrass (W).
# 

# In[32]:


# Sprinkler network
sprinkler_bn = {
    "C": {"parents": [], "cpt": {(): 0.5}},
    "S": {"parents": ["C"], "cpt": {(True,): 0.1, (False,): 0.5}},
    "R": {"parents": ["C"], "cpt": {(True,): 0.8, (False,): 0.2}},
    "W": {
        "parents": ["S", "R"],
        "cpt": {
            (True, True): 0.99,
            (True, False): 0.90,
            (False, True): 0.90,
            (False, False): 0.0,
        },
    },
}

sprinkler_order = ["C", "S", "R", "W"]


# ## Helper functions (provided)
# These helpers are available for the tasks. Feel free to use or ignore them.
# 

# In[33]:


import itertools

def normalize(dist):
    total = sum(dist.values())
    if total == 0:
        return {k: 0 for k in dist}
    return {k: v / total for k, v in dist.items()}


def all_assignments(variables):
    return [
        dict(zip(variables, values))
        for values in itertools.product([False, True], repeat=len(variables))
    ]


# ## Task 1: Joint probability
# Compute the joint probability of a **full assignment** using the network CPTs.
# 
# **Details:**
# - `assignment` contains a value for **every** variable in `variable_order`.
# - For each variable `X`, read its parents via `bayes_net[X]["parents"]`.
# - Build `parent_values` as a tuple in the **same order** as the parents list.
# - Let `p_true = P(X=True | parents)` from the CPT.
#   - If `assignment[X]` is `True`, multiply by `p_true`.
#   - If `assignment[X]` is `False`, multiply by `1 - p_true`.
# 

# In[34]:


def joint_probability(bayes_net, assignment, variable_order):
    '''
    Compute P(assignment) using product of CPTs.
    assignment: dict[str, bool] containing all variables in variable_order.
    '''
    prob = 1.0
    # TODO: multiply probabilities for each variable in variable_order
    for var in variable_order:
        parents = bayes_net[var]["parents"]
        parent_values = tuple(assignment[p] for p in parents)
        p_true = bayes_net[var]["cpt"][parent_values]

        if assignment[var]:
            prob *= p_true
        else:
            prob *= (1.0 - p_true)
    # Hint: use bayes_net[var]["parents"] to read parents and bayes_net[var]["cpt"] for P(var=True | parents)
    return prob


# ## Task 2: Markov blanket (Russell & Norvig)
# Implement a function that returns the Markov blanket of a variable in a Bayesian network.
# 
# The Markov blanket of `X` is:
# `Parents(X) ∪ Children(X) ∪ Parents(Children(X))` **excluding `X` itself**.
# 
# **Requirements:**
# - Return a **Python `set`** of variable names.
# - Make sure `X` is **not** included in the returned set.
# 

# In[35]:


def markov_blanket(bayes_net, var):
    '''
    Returns the Markov blanket of var as a set of variable names.
    bayes_net: dict[var] = {"parents": [...], "cpt": {...}}
    '''
    # TODO: compute parents(var), children(var), and parents of children(var)
    parents = set(bayes_net[var]["parents"])
    children = set()
    for node, data in bayes_net.items():
        if var in data["parents"]:
            children.add(node)

    parents_of_children = set()
    for child in children:
        parents_of_children.update(bayes_net[child]["parents"])

    # TODO: return a set excluding var itself
    blanket = parents | children | parents_of_children
    blanket.discard(var)
    return blanket


# ## Task 3: Rejection sampling
# Approximate the posterior distribution using rejection sampling.
# 
# **Goal:** Approximate `P(query_var | evidence)` and return a distribution `{True: p, False: p}`.
# 
# **Algorithm:**
# 1. Use `rng = random.Random(seed)` for reproducibility.
# 2. For each of `n` iterations, generate a full sample using `sample_from_bn(...)`.
# 3. **Reject** the sample if it does not match the evidence (i.e., any evidence variable has the wrong value).
# 4. For accepted samples, increment the count for `sample[query_var]`.
# 5. Normalize the counts by the number of accepted samples.
# 
# **Edge case:** If no samples are accepted (`accepted == 0`), return `{True: 0.0, False: 0.0}`.
# 

# In[36]:


import random

def sample_from_bn(bayes_net, variable_order, rng):
    '''Generate a full assignment by sampling each variable in topological order.'''
    assignment = {}
    for var in variable_order:
        parents = bayes_net[var]["parents"]
        parent_values = tuple(assignment[p] for p in parents)
        p_true = bayes_net[var]["cpt"][parent_values]
        # TODO: sample True/False based on p_true and store in assignment
        assignment[var] = rng.random() < p_true
    return assignment


def rejection_sampling(query_var, evidence, bayes_net, variable_order, n, seed=0):
    '''
    Returns a dict {True: p, False: p} approximating P(query_var | evidence).
    '''
    rng = random.Random(seed)
    counts = {True: 0, False: 0}
    accepted = 0

    for _ in range(n):
        sample = sample_from_bn(bayes_net, variable_order, rng)
        # TODO: reject samples that do not match evidence
        matches_evidence = True
        for ev_var, ev_val in evidence.items():
            if sample[ev_var] != ev_val:
                matches_evidence = False
                break
        if matches_evidence:
            accepted += 1
            counts[sample[query_var]] += 1

    if accepted == 0:
        return {True: 0.0, False: 0.0}
        # TODO: update counts for query_var and accepted count
        pass

    # TODO: normalize counts (only over accepted samples) and return
    return {True: counts[True] / accepted, False: counts[False] / accepted}


# ## Quick checks
# Uncomment to sanity-check your solution on the provided networks.
# 

# In[37]:


print(joint_probability(burglary_bn, {"B": True, "E": False, "A": True, "J": True, "M": False}, burglary_order))
print(markov_blanket(burglary_bn, "A"))
print(rejection_sampling("R", {"W": True}, sprinkler_bn, sprinkler_order, n=5000, seed=0))


# 
# 

# In[ ]:




