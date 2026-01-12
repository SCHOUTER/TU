import pathlib
import importlib
import nbformat
from nbconvert import PythonExporter
import sys
import traceback
import warnings

"""

Public tests for bonus exercise 1.

Usage: Put this file in the same directory as your exercise notebook.

You can run the tests by running this file. Don't use pytest from the command line.

This script will create a new folder called 'python_files' in which a python version of the exercise notebook will be generated into.

Normally running the file regenerates the python files, but if you feel like changes in your python notebook are not tested, delete that folder and run this file again.

Each failed test will cause points to be deducted from the 10 point total.

The public tests are 5 points, and the private test will also be worth 5 points.

Submit you python file with your name and matrikelnummer

  

If you have any troubles with the tests, please post them to moodle.
"""


def test_depth_first_search(module_name):
    print("\n--- Testing depth_first_search ---")
    mod = _test_function_exists(module_name, "depth_first_search")
    if mod is None:
        return
    graph_ro = get_map("romania")
    graph_de = get_map("germany") 
    graph_toy = get_map("toy")

    
    try:
        path = mod.depth_first_search(graph_ro, "Arad", "Bucharest")
        print("testing if first city is Arad")
        check(path[0] == "Arad",
               f"DFS path should start at Arad, got {path[0]}",0.1)
        
        print("testing if last city is Bucharest")
        check(path[-1] == "Bucharest",
               f"DFS path should end at Bucharest, got {path[-1]}",0.1)
        
        print("testing if cities are unique")
        check(len(path) == len(set(path)),
               "DFS should avoid revisiting cities",0.2)
        
        print("testing if path is valid")
        check(_path_is_valid(path, graph_ro),
               "DFS path contains edges that are not in the Romania map",0.2)
        
        path_de = mod.depth_first_search(graph_de, "Hamburg", "Berlin")
        print("checking germany dfs starts in Hamburg")
        check(path_de[0] == "Hamburg",
                f"DFS path should start at Hamburg, got {path_de[0]}",0.1)
        
        print("checking germany dfs ends in Berlin")
        check(path_de[-1] == "Berlin",
                f"DFS path should end at Berlin, got {path_de[-1]}",0.1)
        
        print("checking germany dfs path validity")
        check(_path_is_valid(path_de, graph_de),
                "DFS path contains edges that are not in the Germany map",0.2)

        # path_toy = mod.depth_first_search(graph_toy, "Start", "Goal")
        # print("checking toy dfs reaches Goal")
        # check(path_toy[-1] == "Goal", "Toy DFS should reach Goal",0.1)

    except Exception as e:
        fail_section(f"DFS test failed with exception: {type(e).__name__}: {e}", deduction=1)



def test_a_star_search(module_name):
    print("\n--- Testing a_star_search ---")
    mod = _test_function_exists(module_name, "a_star_search")
    if mod is None:
        return
    graph_ro = get_map("romania")
    graph_de = get_map("germany") 
    graph_toy = get_map("toy")
    heuristic_de = get_heuristic("straight_line_germany")
    heuristic_ro = get_heuristic("straight_line_romania")
    heuristic_toy = get_heuristic("toy_good")
    print(f"ro: {graph_ro==None}, de: {graph_de==None}, toy: {graph_toy==None}")
    print(f"ro: {heuristic_ro}, de: {heuristic_de==None}, toy: {heuristic_toy==None}")


    try:
        path, cost = mod.a_star_search(graph_ro, "Arad", "Bucharest", heuristic_ro)
        
        print("testing if A* path starts at Arad")
        check(path[0] == "Arad",
               f"A* path should start at Arad, got {path[0]}", 0.2)
        
        print("testing if A* path ends at Bucharest")
        check(path[-1] == "Bucharest",
               f"A* path should end at Bucharest, got {path[-1]}", 0.2)
        
        print("testing if A* path is valid")
        check(_path_is_valid(path, graph_ro),
               "A* path contains edges that are not in the Romania map", 0.2)

        calculated_cost = _path_cost(path, graph_ro)
        
        print("testing if A* cost is optimal")
        check(cost <= 419,
               f"A* should find an optimal path with cost 418 or less, got {cost}", 0.3)

        
        path_de, cost_de = mod.a_star_search(
            graph_de, "Hamburg", "Berlin", heuristic_de)
        
        print("checking A* Germany path starts at Hamburg")
        check(path_de[0] == "Hamburg",
                f"A* Germany path should start at Hamburg, got {path_de[0]}", 0.2)
        
        print("checking A* Germany path ends at Berlin")
        check(path_de[-1] == "Berlin",
                f"A* Germany path should end at Berlin, got {path_de[-1]}", 0.2)
        
        print("checking A* Germany path validity")
        check(_path_is_valid(path_de, graph_de),
                "A* Germany path contains edges not in the map", 0.2)
        calc_cost_de = _path_cost(path_de, graph_de)
        
        print("checking A* Germany reported cost matches path cost")
        check(cost_de == calc_cost_de,
                f"A* Germany reported cost {cost_de} != path cost {calc_cost_de}", 0.2)
        
        print("checking A* Germany cost is optimal")
        check(cost_de <= 290,
                f"A* Germany should find cost 290 or less, got {cost_de}", 0.3)
        
        # path_toy, cost_toy = mod.a_star_search(
        #     graph_toy, "Start", "Goal", heuristic_toy)
        
        # print("checking A* toy optimal cost")
        # check(cost_toy == 4,
        #         f"Toy A* optimal cost should be 4, got {cost_toy}", 0.2)
    except Exception as e:
        fail_section(f"A* test failed with exception: {type(e).__name__}: {e}; Points: -2", deduction=2)



def test_heuristic_checker(module_name):
    print("\n--- Testing check_heuristic ---")
    mod = _test_function_exists(module_name, "check_heuristic")
    if mod is None:
        return
    graph_ro = getattr(mod, "romania_map", None)
    heuristic_ro = getattr(mod, "straight_line_heuristic", None)
    graph_de = getattr(mod, "germany_map", None)
    heuristic_de = getattr(mod, "straight_line_heuristic_berlin", None)
    heuristic_de_bad = getattr(mod, "straight_line_heuristic_berlin_bad", None)
    graph_toy = getattr(mod, "toy_map", None)
    toy_good = getattr(mod, "toy_heuristic_good", None)
    toy_bad = getattr(mod, "toy_heuristic_bad", None)

    try:
        admissible_ro, consistent_ro = mod.check_heuristic(
            graph_ro, heuristic_ro, "Bucharest")
        
        print("checking Romania heuristic is admissible")
        check(admissible_ro is True,
               "Romania heuristic should be admissible", 0.2)
        
        print("checking Romania heuristic is consistent")
        check(consistent_ro is True,
               "Romania heuristic should be consistent", 0.2)
        
        admissible_de, consistent_de = mod.check_heuristic(
            graph_de, heuristic_de, "Berlin")
        
        print("checking Germany heuristic is admissible")
        check(admissible_de is True,
                "Germany heuristic should be admissible", 0.2)
        
        print("checking Germany heuristic is consistent")
        check(consistent_de is True,
                "Germany heuristic should be consistent", 0.2)
        
    
        admissible_bad, consistent_bad = mod.check_heuristic(
            graph_de, heuristic_de_bad, "Berlin")
        
        print("checking bad Germany heuristic is inadmissible")
        check(admissible_bad is False, "Bad Germany heuristic should be inadmissible")
        
        print("checking bad Germany heuristic is inconsistent")
        check(consistent_bad is False, "Bad Germany heuristic should be inconsistent", 0.2)

       
        adm_good, cons_good = mod.check_heuristic(graph_toy, toy_good, "Goal")
        adm_bad, cons_bad = mod.check_heuristic(graph_toy, toy_bad, "Goal")
        print("checking toy good heuristic is admissible")
        check(adm_good is True,"Toy good heuristic should be admissible", 0.2)
        
        print("checking toy good heuristic is consistent")
        check(cons_good is True,"Toy good heuristic should be consistent", 0.2)

        print("checking toy bad heuristic is inadmissible")
        check(adm_bad is False,"Toy bad heuristic should be inadmissible", 0.2)
        
        print("checking toy bad heuristic is inconsistent")
        check(cons_bad is False,"Toy bad heuristic should be inconsistent", 0.2)
    except Exception as e:
        fail_section(f"Heuristic check test failed with exception: {type(e).__name__}: {e}; Points: -2", deduction=2)



# ==== Maps =====
# these are the same as from the exercise
def get_map(name):
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


    # Toy graph for quick checks
    toy_map = {
        "Start": [("Mid", 2)],
        "Mid": [("Start", 2), ("Goal", 2)],
        "Goal": [("Mid", 2)],
    }

    maps = {
        "romania" : romania_map,
        "germany" : germany_map,
        "toy": toy_map
    }

    return maps[name]

def get_heuristic(name):

    straight_line_heuristic_Bucharest = {
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

    straight_line_heuristic_berlin = {
        "Berlin": 0,
        "Hamburg": 255,
        "Leipzig": 150,
        "Frankfurt": 424,
        "Cologne": 480,
        "Stuttgart": 510,
        "Munich": 504,
    }

    # Non-admissible on purpose
    straight_line_heuristic_berlin_bad = {
        "Berlin": 5,
        "Hamburg": 400,
        "Leipzig": 300,
        "Frankfurt": 424,
        "Cologne": 600,
        "Stuttgart": 520,
        "Munich": 700,
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

    heuristic = {
        "straight_line_romania": straight_line_heuristic_Bucharest, 
        "straight_line_germany": straight_line_heuristic_berlin,
        "straight_line_germany_bad": straight_line_heuristic_berlin_bad,
        "toy_good": toy_heuristic_good,
        "toy_bad": toy_heuristic_bad
    }

    return heuristic[name]




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
            test_depth_first_search(mod_name)
            test_a_star_search(mod_name)
            test_heuristic_checker(mod_name)
        else:
            print("CRITICAL: Could not import student code.")
            
            errors.append(("Code failed to import/run.",5))
        
        print_summary()













