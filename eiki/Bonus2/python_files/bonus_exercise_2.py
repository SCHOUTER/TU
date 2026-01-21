#!/usr/bin/env python
# coding: utf-8

# # Bonus Exercise 2
# In the following you will implement a sudoku solver, which uses Backtracking with CSPs. <br>
# First enter your name and matrikelnummer. Without those we can't give you points.

# In[1]:


#TODO: Enter your matriculation number and name
matrikelnummer = 3602227
name = "Niclas Kusenbach"


# ## Sudoku Data
# Below is the Sudoku and two further examples we want to solve in this exercise, stored as a 2D array. Run the code below to visualize the Sudoku.

# In[2]:


import copy
import matplotlib.pyplot as plt
import numpy as np
import os
import time

assignment_ctr = 0  # for backtracking task

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def clear_console():
    print("\033[H\033[J", end="")

def print_sudoku(sudoku):
    for i in range(9):
        if i % 3 == 0 and i != 0:
            print("-" * 21)
        for j in range(9):
            if j % 3 == 0 and j != 0:
                print("|", end=" ")
            print(sudoku[i][j] if sudoku[i][j] != 0 else ".", end=" ")
        print()


sudoku1 = [
    [2, 0, 5, 3, 0, 8, 4, 0, 9],
    [0, 7, 0, 0, 0, 0, 0, 5, 0],
    [9, 0, 4, 0, 0, 0, 6, 0, 7],
    [5, 0, 0, 0, 4, 0, 0, 0, 2],
    [0, 0, 0, 5, 0, 7, 0, 0, 0],
    [6, 0, 0, 0, 3, 0, 0, 0, 8],
    [4, 0, 6, 0, 0, 0, 8, 0, 1],
    [0, 2, 0, 0, 0, 0, 0, 6, 0],
    [8, 0, 1, 2, 0, 9, 7, 0, 4]
]

sudoku2 = [
    [0, 2, 0, 0, 3, 0, 0, 4, 0],
    [6, 0, 0, 0, 0, 0, 0, 0, 3],
    [0, 0, 4, 0, 0, 0, 5, 0, 0],
    [0, 0, 0, 8, 0, 6, 0, 0, 0],
    [8, 0, 0, 0, 1, 0, 0, 0, 6],
    [0, 0, 0, 7, 0, 5, 0, 0, 0],
    [0, 0, 7, 0, 0, 0, 6, 0, 0],
    [4, 0, 0, 0, 0, 0, 0, 0, 8],
    [0, 3, 0, 0, 4, 0, 0, 2, 0]
]

sudoku3 = [
    [0, 7, 0, 5, 8, 3, 0, 2, 0],
    [0, 5, 9, 2, 0, 0, 3, 0, 0],
    [3, 4, 0, 0, 0, 6, 5, 0, 7],
    [7, 9, 5, 0, 0, 0, 6, 3, 2],
    [0, 0, 3, 6, 9, 7, 1, 0, 0],
    [6, 8, 0, 0, 0, 2, 7, 0, 0],
    [9, 1, 4, 8, 3, 5, 0, 7, 6],
    [0, 3, 0, 7, 0, 1, 4, 9, 5],
    [5, 6, 7, 4, 2, 9, 0, 1, 3]
]

print_sudoku(sudoku1)


# ## Constraints
# The first step is to implement the constraints that apply to each entry in the Sudoku grid.

# In[3]:


def constraints(sudoku, row, col, value):
    """
    The function enforces the standard Sudoku constraints:
    - the value must not already appear in the same row
    - the value must not already appear in the same column
    - the value must not already appear in the corresponding 3x3 subgrid

    Parameters:
        sudoku (list[list[int]]): 9x9 Sudoku grid, where 0 represents an empty cell
        row (int): row index (0–8)
        col (int): column index (0–8)
        value (int): value to test (1–9)

    Returns:
        bool: True if the value can be legally placed at (row, col), False otherwise
    """
    # TODO: check that `value` does not already appear in the given row
    for i in range(9):
        if sudoku[row][i] == value:
            return False

    # TODO: check that `value` does not already appear in the given column
    for i in range(9):
        if sudoku[i][col] == value:
            return False

    # TODO: compute the top-left coordinates of the corresponding 3x3 subgrid
    start_row = (row // 3) * 3
    start_col = (col // 3) * 3

    # TODO: check that `value` does not already appear in the 3x3 subgrid
    for i in range(3):
        for j in range(3):
            if sudoku[start_row + i][start_col + j] == value:
                return False

    # TODO: return True if all checks pass, otherwise False
    return True


# ## Backtracking algorithm
# We can now implement the backtracking algorithm using the previously defined constraints. The function print_sudoku() can be used to visualize the backtracking process.
# For comparability between different constraints-inputs you'll also need to implement a counter for keeping track how often the algorithm assigns a value to a sudoku field.

# In[ ]:


def backtracking(sudoku, constraints, row=0, col=0):
    """
    Depth-first backtracking Sudoku solver.

    - Mutates `sudoku` in-place.
    - Uses `constraints(sudoku, row, col, value)` only for *empty* cells.
    - Returns True if solved, otherwise False.

    Required by tests:
    - global variable `assignment_ctr` exists and is incremented on each assignment.
    """
    global assignment_ctr

    # TODO: check termination condition (all rows processed -> solved)
    if row == 9:
        return True

    # TODO: compute coordinates of the next cell (row, col order)
    next_row, next_col = (row + 1, 0) if col == 8 else (row, col + 1)

    # TODO: if current cell is already filled
    #       - skip constraint checking
    #       - recursively continue with the next cell
    if sudoku[row][col] != 0:
        return backtracking(sudoku, constraints, next_row, next_col)

    for num in range(1,10):
    # TODO: check constraints for the current empty cell
        if constraints(sudoku, row, col, num):
        #       - assign the value to the cell
                sudoku[row][col] = num

    #       - increment assignment_ctr
                assignment_ctr += 1

    #       - recursively continue with the next cell
                if backtracking(sudoku, constraints, next_row, next_col):
    #       - if recursion succeeds, return True
                        return True

                sudoku[row][col] = 0 # undo

    # TODO: if no value fits, return False (dead end)
    return False


# ## Forward-Checking
# To improve performance, we extend our backtracking approach by implementing Forward-checking and a Minimum Remaining Values Heuristic.

# In[6]:


def init_domains(sudoku):
    """
    Initializes the domain for each Sudoku cell.

    - Returns a 9x9 array `domains`, where each entry is a list of possible values.
    - For empty cells (value 0), the domain contains all values 1–9 that satisfy
      `constraints(sudoku, row, col, value)` in the current state.
    - For filled cells, the domain is a singleton list containing the fixed value.
    - Does NOT mutate `sudoku`.
    """
    domains = np.empty((9, 9), dtype=object)
    for r in range(9):
        for c in range(9):
            if sudoku[r][c] == 0:
                domains[r][c] = [
                    n for n in range(1, 10)
                    if constraints(sudoku, r, c, n)
                ]
            else:
                domains[r][c] = [sudoku[r][c]]
    return domains


# First we implement the Minimum Remaining Values Heuristic.

# In[7]:


def select_unassigned_variable(sudoku, domains):
    """
    Selects the next unassigned cell using the MRV heuristic
    (Minimum Remaining Values).

    - Scans all empty cells (sudoku[r][c] == 0).
    - Chooses the cell with the smallest domain size.
    - Returns a tuple (row, col).
    - Returns None if all cells are assigned (Sudoku solved).
    """
    # TODO: initialize variables to track the best cell and smallest domain
    best_cell = None
    min_size = 10
    # TODO: iterate over all cells
    for row in range(9):
        for col in range(9):
    # TODO: consider only unassigned cells (value 0 in sudoku)
            if sudoku[row][col] == 0 and len(domains[row][col]) < min_size:
    # TODO: update the best cell if a smaller domain is found
                best_cell = (row, col)
                min_size = len(domains[row][col])

    # TODO: return the selected cell (row, col) or None
    return best_cell


# Now we want to implement the forward checking.

# In[ ]:


def forward_checking(sudoku, domains, row, col, value):
    """
    Forward Checking propagation step.

    - Works on a deep copy of `domains` (no global side effects).
    - Assumes that `value` is assigned to cell (row, col).
    - Removes `value` from the domains of all neighboring cells
      (same row, same column, same 3x3 block).
    - If any neighbor domain becomes empty, returns None (dead end).
    - Otherwise returns the reduced domains.
    """
    # TODO: create a deep copy of the domains
    domain = copy.deepcopy(domains)

    # TODO: fix the domain of (row, col) to [value]
    domain[row][col] = [value]

    # TODO: remove value from domains of all cells in the same row
    for c in range(9):
        if value in domain[row][c] and c != col:
            domain[row][c].remove(value)

    # TODO: remove value from domains of all cells in the same column
    for r in range(9):
        if value in domain[r][col] and r != row:
            domain[r][col].remove(value)

    # TODO: remove value from domains of all cells in the same 3x3 block
    start_row = (row // 3) * 3
    start_col = (col // 3) * 3

    for i in range(3):
        for j in range(3):
            if value in domain[start_row + i][start_col + j] and (row != start_row + i or col != start_col + j):
                domain[start_row + i][start_col + j].remove(value)

    # TODO: if any domain becomes empty, return None
    for r in range(9):
        for c in range(9):
            if not domain[r][c]:
                return None

    # TODO: otherwise return the updated domains
    return domain


# This cells you can run to solve the sudoku using forward checking.

# In[1]:


def solve_sudoku_fc(sudoku, domains):
    """
    Depth-first backtracking Sudoku solver with Forward Checking.

    - Mutates `sudoku` in-place.
    - Uses MRV to select the next unassigned variable.
    - Uses `constraints(sudoku, row, col, value)` for local consistency checks.
    - Applies Forward Checking after each assignment to detect dead ends early.
    - Returns True if the Sudoku is solved, otherwise False.
    """

    global assignment_ctr

    pos = select_unassigned_variable(sudoku, domains)
    if pos is None:
        print_sudoku(sudoku)
        return True  # done

    row, col = pos

    for value in domains[row][col]:
        if constraints(sudoku, row, col, value):
            sudoku[row][col] = value
            assignment_ctr += 1
            new_domains = forward_checking(
                sudoku, domains, row, col, value
            )

            if new_domains is not None:
                if solve_sudoku_fc(sudoku, new_domains):
                    return True
            sudoku[row][col] = 0  # Backtracking

    return False

