import pathlib
import importlib
import nbformat
from nbconvert import PythonExporter
import sys
import traceback
import warnings
import copy

"""

Public tests for bonus exercise 2.

Usage: Put this file in the same directory as your exercise notebook.

You can run the tests by running this file. Don't use pytest from the command line.

This script will create a new folder called 'python_files' in which a python version of the exercise notebook will be generated into.

Normally running the file regenerates the python files, but if you feel like changes in your python notebook are not tested, delete that folder and run this file again.

Each failed test will cause points to be deducted from the 10 point total.

The public tests are 5 points, and the private test will also be worth 5 points.

Submit you python file with your name and matrikelnummer

  

If you have any troubles with the tests, please post them to moodle.
"""

# ---- Sudoku helper checks (public-test side) ----

def _no_zeros(grid):
    return all(all(v != 0 for v in row) for row in grid)

def _is_valid_solution(grid):
    """
    Valid solution = each row/col/box is exactly {1..9}.
    """
    target = set(range(1, 10))

    # rows
    for r in range(9):
        if set(grid[r]) != target:
            return False

    # cols
    for c in range(9):
        col = [grid[r][c] for r in range(9)]
        if set(col) != target:
            return False

    # boxes
    for br in range(0, 9, 3):
        for bc in range(0, 9, 3):
            box = []
            for r in range(br, br + 3):
                for c in range(bc, bc + 3):
                    box.append(grid[r][c])
            if set(box) != target:
                return False

    return True


# ---- Public test data ----

def _get_public_sudoku_solvable():
    # A standard solvable Sudoku (0 = empty)
    return [
        [0, 5, 0, 0, 0, 9, 8, 1, 3],
        [9, 8, 0, 3, 5, 0, 6, 0, 7],
        [6, 0, 0, 0, 8, 0, 5, 9, 4],
        [8, 3, 2, 0, 0, 6, 0, 0, 0],
        [7, 0, 0, 1, 2, 8, 0, 0, 9],
        [1, 9, 0, 0, 7, 3, 2, 0, 0],
        [3, 7, 0, 6, 9, 0, 0, 5, 0],
        [0, 2, 0, 0, 0, 0, 7, 0, 0],
        [0, 0, 0, 0, 0, 4, 0, 0, 0],
    ]

def _get_public_sudoku_unsolvable():
    # Start from solvable, then force a contradiction: duplicate '5' in row 0
    g = _get_public_sudoku_solvable()
    g[0][2] = 6  # subgrid in top left already has a 6 -> contradiction
    return g


# =========================
# ==== Required public tests
# =========================

def test_backtracking(module_name):
    """
    Public tests (2P total):
    - solves a newly given sudoku puzzle (1P)
    - detects unsolvable puzzle (1P)
    """
    print("\n--- Testing backtracking ---")
    mod = _test_function_exists(module_name, "backtracking")
    if mod is None:
        fail_section("backtracking() missing; Points: -2", deduction=2)
        return

    # constraints is required as parameter
    if not hasattr(mod, "constraints"):
        fail_section("constraints() missing (required by backtracking); Points: -2", deduction=2)
        return

    # --- (1P) Solvable puzzle ---
    sudoku = _get_public_sudoku_solvable()
    sudoku_work = copy.deepcopy(sudoku)

    try:
        ok = mod.backtracking(sudoku_work, mod.constraints, row=0, col=0)

        # 4 subchecks, each 0.25 = 1 point
        check(ok is True,
              f"backtracking should return True on solvable puzzle, got {ok}; Points: -0.25",
              deduction=0.25)

        check(_no_zeros(sudoku_work),
              "Solved grid still contains zeros; Points: -0.25",
              deduction=0.25)

        check(_is_valid_solution(sudoku_work),
              "Grid is not a valid Sudoku solution; Points: -0.25",
              deduction=0.25)

        assignment_ctr = getattr(mod, "assignment_ctr", None)
        check(assignment_ctr is not None and assignment_ctr != 0,
              f"assignment_ctr missing or 0 (got {assignment_ctr}); Points: -0.25",
              deduction=0.25)

    except Exception as e:
        fail_section(f"Solvable backtracking test crashed: {type(e).__name__}: {e}; Points: -1",
                     deduction=1)

    # --- (1P) Unsolvable puzzle ---
    sudoku_bad = _get_public_sudoku_unsolvable()
    sudoku_bad_work = copy.deepcopy(sudoku_bad)

    try:
        ok2 = mod.backtracking(sudoku_bad_work, mod.constraints, row=0, col=0)
        check(ok2 is False,
              f"backtracking should return False on unsolvable puzzle, got {ok2}; Points: -1",
              deduction=1)
    except Exception as e:
        fail_section(f"Unsolvable backtracking test crashed: {type(e).__name__}: {e}; Points: -1",
                     deduction=1)
        

def test_select_unassigned_variable_mrv(module_name):
    """
    Public test (1P): select_unassigned_variable()
    - returns the position (row, col) of the unassigned cell
      with the smallest domain (MRV heuristic)
    """
    print("\n--- Testing select_unassigned_variable (MRV) ---")

    mod = _test_function_exists(module_name, "select_unassigned_variable")
    if mod is None:
        fail_section("select_unassigned_variable() missing; Points: -1", deduction=1)
        return

    # Sudoku: all empty
    sudoku = [[0 for _ in range(9)] for _ in range(9)]

    # Domains: default size 3 everywhere
    domains = [[{1, 2, 3} for _ in range(9)] for _ in range(9)]

    # Make one cell strictly better (MRV)
    domains[2][5] = {7}          # size 1  -> should be chosen
    domains[4][4] = {1, 2}       # size 2

    try:
        pos = mod.select_unassigned_variable(sudoku, domains)

        check(pos == (2, 5),
              f"MRV failed: expected (2,5), got {pos}; Points: -1",
              deduction=1)

    except Exception as e:
        fail_section(
            f"select_unassigned_variable test crashed: {type(e).__name__}: {e}; Points: -1",
            deduction=1
        )


def test_forward_checking_domains(module_name):
    """
    Public test: forward_checking domain updates
    Maximum deduction: 1 point total

    Checked cases:
    - returns None on valid assignment        -> -0.5
    - original domains modified (no deepcopy)-> -0.5
    - row/column propagation incorrect       -> -0.5
    """

    print("\n--- Testing forward_checking local domain updates ---")

    total_deduction = 0.0

    mod = _test_function_exists(module_name, "forward_checking")
    if mod is None:
        fail_section("forward_checking() missing; Points: -1", deduction=1)
        return

    # empty sudoku
    sudoku = [[0 for _ in range(9)] for _ in range(9)]

    # simple domains everywhere
    domains = [[{1, 2, 3} for _ in range(9)] for _ in range(9)]
    domains_before = copy.deepcopy(domains)

    row, col, value = 4, 4, 2

    try:
        new_domains = mod.forward_checking(sudoku, domains, row, col, value)

        # -------------------------
        # Case 1: returned None
        # -------------------------
        if new_domains is None:
            total_deduction += 1
            print("❌ forward_checking returned None for valid assignment (-0.5)")
        else:
            # -------------------------
            # Case 2: row / column propagation
            # -------------------------
            rc_ok = True

            for c in range(9):
                if c != col and value in new_domains[row][c]:
                    rc_ok = False

            for r in range(9):
                if r != row and value in new_domains[r][col]:
                    rc_ok = False

            if not rc_ok:
                total_deduction += 0.5
                print("❌ Value not correctly removed from row/column neighbors (-0.5)")

        # -------------------------
        # Case 3: deepcopy violated
        # -------------------------
        if domains != domains_before:
            total_deduction += 0.5
            print("❌ Original domains were modified (no deep copy) (-0.5)")

        # cap total deduction
        total_deduction = min(total_deduction, 1.0)

        if total_deduction > 0:
            fail_section(
                f"forward_checking domain test failed; Points: -{total_deduction}",
                deduction=total_deduction
            )
        else:
            print("✅ forward_checking domain test passed")

    except Exception as e:
        fail_section(
            f"forward_checking test crashed: {type(e).__name__}: {e}; Points: -1",
            deduction=1
        )




# ==== Configuration ====

# Base directory is where this script is located
TOTAL_POINTS = 5
BASE_DIR = pathlib.Path(__file__).parent
PYTHON_FILES_DIR = BASE_DIR / "python_files"

# Ensure python_files directory is in the Python path for imports
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# ==== Helper Functions ====

def convert_notebooks():
    """
    Finds all .ipynb files, converts to .py in 'python_files' dir.
    Returns list of module names.
    """
    notebook_dir = BASE_DIR
    output_dir = PYTHON_FILES_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "__init__.py").touch()

    module_list = []
    
    notebooks = list(notebook_dir.glob("*.ipynb"))
    if not notebooks:
        print("No .ipynb files found in directory!")
        return []
    
    print(f"Found {len(notebooks)} notebooks. Converting...")

    for nb_path in notebooks:
        py_filename = nb_path.with_suffix(".py").name
        py_path = output_dir / py_filename
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=Warning)
            nb = nbformat.read(nb_path, as_version=4)
        
        exporter = PythonExporter()
        (body, resources) = exporter.from_notebook_node(nb)
        
        with open(py_path, "w", encoding="utf-8") as f:
            f.write(body)
            
        module_list.append(nb_path.stem)
    
    return module_list

def load_module(module_name):
    try:
        mod = importlib.import_module(f"python_files.{module_name}")
        importlib.reload(mod)
        return mod
    except Exception:
        traceback.print_exc()
        return None
    


def check( condition, message, deduction=1):
    """
    Checks a condition. If false, deducts points and records error.
    """
    global errors
    if not condition:
        errors.append((message,deduction))
        print(f"❌ failed: {message}\n")
        return -deduction
    else:
        print(f"✅ Test passed \n")
        return 0

def fail_section( message, deduction=1):
    """
    Manually fail a section (e.g. if function is missing).
    """
    global errors
    errors.append((message,deduction))
    print(f"❌ {message}")
    return -deduction

def check_identification(module_name):
    print("\n--- Checking identification ---")
    mod = _test_function_exists(module_name, "matrikelnummer")
    if mod is None:
        fail_section("No matrikelnummer found in notebook", deduction=1)
        return
    
    matrikelnummer = getattr(mod, "matrikelnummer", None)
    name = getattr(mod, "name", None)
    
    # Check if values have been changed from defaults
    matrikelnummer_valid = matrikelnummer != 0 and matrikelnummer != "0000000"
    name_valid = name != "Max Mustermann"
    
    check(matrikelnummer_valid,
          f"matrikelnummer has not been changed from default (currently {matrikelnummer}); Points: -0.5", deduction=0.5)
    check(name_valid,
          f"name has not been changed from default (currently {name}); Points: -0.5", deduction=0.5)

def print_summary():
    global errors
    final_deduction = 0
    # Ensure score doesn't drop below 0
    final_score = max(0, current_score)
    
    print("\n" + "="*30)
    print("       GRADING RESULTS       ")
    print("="*30)
    
    if not errors:
        print("\n No errors found.")
    else:
        print("\nErrors found:")
        for error in errors:
            print(error[0], f"(-{error[1]} points)")
            final_deduction += error[1]

    final_score = max(0, max_score-final_deduction)
    print("-" * 30)
    print(f"Final Score: {final_score} / {max_score}")
    print("="*30)
    return final_score

def _path_is_valid(path, graph):
    """
    Checks that every consecutive city pair in the path is connected in the graph.
    """
    if not path:
        return False
    for src, dst in zip(path, path[1:]):
        neighbors = dict(graph.get(src, []))
        if dst not in neighbors:
            return False
    return True

def _test_function_exists(module_name, function_name):
    """
    Helper function to import the module and check if a function exists.
    Fails the test immediately if the module or function is missing.
    """
    try:
        # Attempt to import the converted python file
        mod = importlib.import_module(f"python_files.{module_name}")
        
        # invalidates caching
        importlib.reload(mod)
        
    except ImportError as e:
        print(f"Could not import module '{module_name}'. Error: {e}")
        return None
    except SyntaxError as e:
        print(f"Syntax error in student code '{module_name}'. Error: {e}")
        return None

    # Check if the specific function exists in the module
    if not hasattr(mod, function_name):
        print(f"Function '{function_name}' not found in notebook '{module_name}'.")
        return None
        
    return mod

def _path_cost(path, graph):
    """
    Computes the total edge cost of a path using the provided graph.
    """
    cost = 0
    for src, dst in zip(path, path[1:]):
        neighbors = dict(graph.get(src, []))
        if dst not in neighbors:
            print(f"Edge {src}->{dst} missing.")
        cost += neighbors[dst]
    return cost

# ==== Main Execution ====

if __name__ == "__main__":
    global errors
    modules = convert_notebooks()
    
    for mod_name in modules:
        errors = []
        current_score = TOTAL_POINTS
        max_score = TOTAL_POINTS
      
        print(f"\n{'='*10} GRADING: {mod_name}{'='*10}")
        print(f"{'_'*10} Running {mod_name} code once to check for errors.{'_'*10}")
         
        student_module = load_module(mod_name)

        if student_module:
            check_identification(mod_name)
            test_backtracking(mod_name)
            test_select_unassigned_variable_mrv(mod_name)
            test_forward_checking_domains(mod_name)
        else:
            print("CRITICAL: Could not import student code.")
            
            errors.append(("Code failed to import/run.",5))
        
        print_summary()