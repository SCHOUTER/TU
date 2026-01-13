#!/usr/bin/env python
# coding: utf-8

# # Bonus Exercise 1
# In the following you will implement search algorithms and tests heuristics. <br>
# First enter your name and matrikelnummer. Without those we can't give you points.
# 

# In[21]:


#TODO: Enter your matriculation number and name
matrikelnummer = 3602227
name = "Niclas Kusenbach"


# # Romania & Germany Search (DFS, A*)
# Below you will find the Russell & Norvig Romania road map, additional Germany subset map, and a toy map to practice DFS and A*. Complete the code cells so the algorithms find routes and verify heuristics.
# 
# - Work with provided adjacency lists and multiple heuristics (admissible and non-admissible).
# - Keep implementations deterministic: expand neighbors in listed order.
# - Return complete paths; A* returns `(path, cost)`.
# - Add helpers if you like, but keep the signatures of the given functions.
# 

# ## Map data: Romania
# Straight-line heuristic to Bucharest.
# 

# In[22]:


# Romania road map (bidirectional graph)
romania_map = {
    "Arad": [("Zerind", 75), ("Sibiu", 140), ("Timisoara", 118)],
    "Zerind": [("Arad", 75), ("Oradea", 71)],
    "Oradea": [("Zerind", 71), ("Sibiu", 151)],
    "Sibiu": [("Arad", 140), ("Oradea", 151), ("Fagaras", 99), ("Rimnicu Vilcea", 80)],
    "Timisoara": [("Arad", 118), ("Lugoj", 111)],
    "Lugoj": [("Timisoara", 111), ("Mehadia", 70)],
    "Mehadia": [("Lugoj", 70), ("Drobeta", 75)],
    "Drobeta": [("Mehadia", 75), ("Craiova", 120)],
    "Craiova": [("Drobeta", 120), ("Rimnicu Vilcea", 146), ("Pitesti", 138)],
    "Rimnicu Vilcea": [("Sibiu", 80), ("Craiova", 146), ("Pitesti", 97)],
    "Fagaras": [("Sibiu", 99), ("Bucharest", 211)],
    "Pitesti": [("Rimnicu Vilcea", 97), ("Craiova", 138), ("Bucharest", 101)],
    "Bucharest": [("Fagaras", 211), ("Pitesti", 101), ("Giurgiu", 90), ("Urziceni", 85)],
    "Giurgiu": [("Bucharest", 90)],
    "Urziceni": [("Bucharest", 85), ("Hirsova", 98), ("Vaslui", 142)],
    "Hirsova": [("Urziceni", 98), ("Eforie", 86)],
    "Eforie": [("Hirsova", 86)],
    "Vaslui": [("Urziceni", 142), ("Iasi", 92)],
    "Iasi": [("Vaslui", 92), ("Neamt", 87)],
    "Neamt": [("Iasi", 87)],
}

straight_line_heuristic = {
    "Arad": 366,
    "Bucharest": 0,
    "Craiova": 160,
    "Drobeta": 242,
    "Eforie": 161,
    "Fagaras": 176,
    "Giurgiu": 77,
    "Hirsova": 151,
    "Iasi": 226,
    "Lugoj": 244,
    "Mehadia": 241,
    "Neamt": 234,
    "Oradea": 380,
    "Pitesti": 100,
    "Rimnicu Vilcea": 193,
    "Sibiu": 253,
    "Timisoara": 329,
    "Urziceni": 80,
    "Vaslui": 199,
    "Zerind": 374,
}


# ## Map data: Germany subset
# Straight-line heuristic to Berlin (admissible) and a deliberately non-admissible variant.
# 

# In[23]:


# Germany road map (subset, bidirectional graph)
germany_map = {
    "Berlin": [("Hamburg", 289), ("Leipzig", 190), ("Frankfurt", 546)],
    "Hamburg": [("Berlin", 289), ("Cologne", 360)],
    "Leipzig": [("Berlin", 190), ("Munich", 430)],
    "Frankfurt": [("Berlin", 546), ("Cologne", 190), ("Stuttgart", 204), ("Munich", 394)],
    "Cologne": [("Hamburg", 360), ("Frankfurt", 190)],
    "Stuttgart": [("Frankfurt", 204), ("Munich", 220)],
    "Munich": [("Leipzig", 430), ("Frankfurt", 394), ("Stuttgart", 220)],
}

straight_line_heuristic_berlin = {
    "Berlin": 0,
    "Hamburg": 255,
    "Leipzig": 150,
    "Frankfurt": 424,
    "Cologne": 480,
    "Stuttgart": 510,
    "Munich": 504,
}

# Non-admissible on purpose (overestimates several nodes)
straight_line_heuristic_berlin_bad = {
    "Berlin": 5,
    "Hamburg": 400,
    "Leipzig": 300,
    "Frankfurt": 424,
    "Cologne": 600,
    "Stuttgart": 520,
    "Munich": 700,
}


# ## Map data: Toy graph
# Tiny graph for quick checks with admissible and non-admissible heuristics.
# 

# In[24]:


toy_map = {
    "Start": [("Mid", 2)],
    "Mid": [("Start", 2), ("Goal", 2)],
    "Goal": [("Mid", 2)],
}

toy_heuristic_good = {
    "Start": 3,
    "Mid": 2,
    "Goal": 0,
}

toy_heuristic_bad = {
    "Start": 10,
    "Mid": 5,
    "Goal": 1,
}


# ## Map data: Islands graph
# A third dataset for private checks with good and bad heuristics.
# 

# In[25]:


islands_map = {
    "Start": [("A", 2), ("B", 5)],
    "A": [("Start", 2), ("C", 2)],
    "B": [("Start", 5), ("C", 2)],
    "C": [("A", 2), ("B", 2), ("Goal", 3)],
    "Goal": [("C", 3)],
}

islands_heuristic_good = {
    "Start": 6,
    "A": 4,
    "B": 4,
    "C": 3,
    "Goal": 0,
}

islands_heuristic_bad = {
    "Start": 12,
    "A": 7,
    "B": 8,
    "C": 5,
    "Goal": 1,
}


# ## Task 1: Depth-first search
# Implement a stack-based DFS that returns a path from a start city to a goal city.
# Tipp: elements of the stack can have the form (city, path to city)

# In[26]:


def depth_first_search(graph, start, goal):
    '''
    Iterative depth-first search on a weighted graph.
    graph: dict[str, list[tuple[str, int]]]
    Returns a path as a list of city names from start to goal (inclusive).
    '''
    visited = set()
    stack = []
    # TODO: seed the stack with the start node and its path
    # Format: (current_node, path_so_far)
    stack.append((start, [start]))

    while stack:
        # TODO: pop the next node to explore (LIFO)
        current_city, path = stack.pop()

        # TODO: check if we've reached the goal
        if current_city == goal:
            return path

        # TODO: skip if visited, otherwise mark visited
        if current_city in visited:
            continue
        else:
            visited.add(current_city)

        # TODO: iterate over neighbors in order and push unseen ones with their new paths
        for neighbor, distance in reversed(graph[current_city]):
            if neighbor not in visited:
                new_path = path + [neighbor]
                stack.append((neighbor, new_path))

    raise ValueError("No path found from {start} to {goal}")


# ## Task 2: A* search
# Use the straight-line distance as an admissible heuristic to guide the search.
# 

# In[27]:


import heapq

def reconstruct_path(came_from, current):
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    return list(reversed(path))


def a_star_search(graph, start, goal, heuristic):
    '''
    A* search on a weighted graph.
    Returns (path, total_cost) where path includes start and goal.
    '''
    g_score = {start: 0}
    f_score = {start: heuristic[start]}
    open_set = []  # store nodes to explore
    # TODO: add the start node to open_set
    heapq.heappush(open_set, (f_score[start], start))
    came_from = {}  # child -> parent

    while open_set:
        # TODO: select the node in open_set with the smallest f-score
        current_f_score, current = heapq.heappop(open_set)

        if current_f_score > f_score.get(current, float('inf')):
            continue

        # TODO: if current is goal, reconstruct path and return (path, g_score[current])
        if current == goal:
            final_path = reconstruct_path(came_from, current)
            return final_path, g_score[current]

        for neighbor, edge_cost in graph.get(current, []):
            tentative_g = g_score[current] + edge_cost
            # TODO: if this path to neighbor is better, record it and ensure neighbor is in open_set
            if tentative_g < g_score.get(neighbor, float('inf')):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                total_f = tentative_g + heuristic[neighbor]
                f_score[neighbor] = total_f
                heapq.heappush(open_set, (total_f, neighbor))

    raise ValueError("No path found from {start} to {goal}")


# ## Task 3: Check heuristic admissibility/consistency
# Compute true costs (e.g., Dijkstra from the goal) and report if a heuristic is admissible and consistent.
# 

# In[28]:


def compute_true_costs(graph, goal):
    '''Compute shortest-path cost from every node to goal (e.g., Dijkstra).'''
    # TODO: implement Dijkstra (or another shortest-path algorithm) from goal
    queue = []
    queue.append(goal)

    visited = set()
    costs = {}

    for node in graph:
        costs[node] = float('inf')

    costs[goal] = 0

    while queue:
        node = min(queue, key=lambda x: costs[x])
        queue.remove(node)
        visited.add(node)
        # TODO berechne neue Kosten für alle Nachfolger j von k die nicht Element von E sind
        for j, dist in graph[node]:
            if j not in visited:
                new_cost = costs[node] + dist

                if new_cost < costs[j]:
                    costs[j] = new_cost

                    if j not in queue:
                        queue.append(j)

    return costs
    # Return a dict {node: cost_to_goal}
    raise NotImplementedError("Compute true costs to the goal")


def check_heuristic(graph, heuristic, goal):
    '''
    Returns (admissible, consistent) for the given heuristic.
    Automatically uses computed true costs; no external input needed.
    '''
    true_costs = compute_true_costs(graph, goal)
    admissible = True 
    consistent = True 

    if heuristic.get(goal, None) != 0:
        consistent = False

    for node, neighbors in graph.items():
        h_node = heuristic[node]

        if h_node > true_costs.get(node, float('inf')):
            admissible = False

        for neighbor, cost in neighbors:
            if h_node > cost + heuristic[neighbor]:
               consistent = False

    return admissible, consistent


# ## Quick checks
# Uncomment to sanity-check your solution on multiple datasets and heuristics.
# 

# In[29]:


dfs_path_ro = depth_first_search(romania_map, "Arad", "Bucharest")
astar_path_ro, astar_cost_ro = a_star_search(romania_map, "Arad", "Bucharest", straight_line_heuristic)
print("Romania A*:", astar_path_ro, astar_cost_ro)

dfs_path_de = depth_first_search(germany_map, "Hamburg", "Berlin")
astar_path_de, astar_cost_de = a_star_search(germany_map, "Hamburg", "Berlin", straight_line_heuristic_berlin)
print("Germany A*:", astar_path_de, astar_cost_de)

astar_path_toy, astar_cost_toy = a_star_search(toy_map, "Start", "Goal", toy_heuristic_good)
print("Toy A*:", astar_path_toy, astar_cost_toy)

astar_path_islands, astar_cost_islands = a_star_search(islands_map, "Start", "Goal", islands_heuristic_good)
print("Islands A*:", astar_path_islands, astar_cost_islands)

print(check_heuristic(romania_map, straight_line_heuristic, "Bucharest"))
print(check_heuristic(germany_map, straight_line_heuristic_berlin, "Berlin"))
print(check_heuristic(germany_map, straight_line_heuristic_berlin_bad, "Berlin"))
print(check_heuristic(toy_map, toy_heuristic_good, "Goal"))
print(check_heuristic(toy_map, toy_heuristic_bad, "Goal"))
print(check_heuristic(islands_map, islands_heuristic_good, "Goal"))
print(check_heuristic(islands_map, islands_heuristic_bad, "Goal"))

