import pathlib
import importlib
import nbformat
from nbconvert import PythonExporter
import sys
import traceback
import warnings
import math

"""

Public tests for bonus exercise 1.

Usage: Put this file in the same directory as your exercise notebook.

You can run the tests by running this file. Don't use pytest from the command line.

This script will create a new folder called 'python_files' in which a python version
of the exercise notebook will be generated into.

Normally running the file regenerates the python files, but if you feel like changes
in your python notebook are not tested, delete that folder and run this file again.

Each failed test will cause points to be deducted from the 10 point total.

The public tests are 5 points, and the private test will also be worth 5 points.

Submit you python file with your name and matrikelnummer

If you have any troubles with the tests, please post them to moodle.
"""


# ===== Test Functions =====

def test_joint_probability(module_name):
    print("\n--- Testing joint_probability ---")
    mod = _test_function_exists(module_name, "joint_probability")
    if mod is None:
        return

    bn = getattr(mod, "burglary_bn", None)
    order = getattr(mod, "burglary_order", None)
    if bn is None or order is None:
        fail_section("burglary_bn or burglary_order not found in notebook", deduction=1)
        return

    assignment = {"B": True, "E": False, "A": True, "J": True, "M": False}
    expected = 0.0002532924

    try:
        prob = mod.joint_probability(bn, assignment, order)
        check(
            math.isclose(prob, expected, rel_tol=1e-6, abs_tol=1e-8),
            f"joint_probability expected {expected}, got {prob}",
            0.5,
        )
    except Exception as e:
        fail_section(f"joint_probability failed with exception: {type(e).__name__}: {e}", deduction=1)



def test_markov_blanket(module_name):
    print("\n--- Testing markov_blanket ---")
    mod = _test_function_exists(module_name, "markov_blanket")
    if mod is None:
        return

    bn = getattr(mod, "burglary_bn", None)
    if bn is None:
        fail_section("burglary_bn not found in notebook", deduction=1)
        return

    try:
        mb_b = mod.markov_blanket(bn, "B")
        check(isinstance(mb_b, set), "markov_blanket should return a set", 0.2)
        check(mb_b == {"A", "E"}, f"Markov blanket of B should be {{'A','E'}}, got {mb_b}", 0.4)

        mb_a = mod.markov_blanket(bn, "A")
        check(mb_a == {"B", "E", "J", "M"},
              f"Markov blanket of A should be {{'B','E','J','M'}}, got {mb_a}", 0.4)
    except Exception as e:
        fail_section(f"markov_blanket failed with exception: {type(e).__name__}: {e}", deduction=1.5)



def test_rejection_sampling(module_name):
    print("\n--- Testing rejection_sampling ---")
    mod = _test_function_exists(module_name, "rejection_sampling")
    if mod is None:
        return

    bn = getattr(mod, "sprinkler_bn", None)
    order = getattr(mod, "sprinkler_order", None)
    if bn is None or order is None:
        fail_section("sprinkler_bn or sprinkler_order not found in notebook", deduction=1)
        return

    expected_true = 0.7079276773296247
    try:
        dist = mod.rejection_sampling("R", {"W": True}, bn, order, n=5000, seed=0)
        check(isinstance(dist, dict), "rejection_sampling should return a dict", 0.2)
        check(True in dist and False in dist, "distribution must have True/False keys", 0.2)
        if isinstance(dist, dict) and True in dist and False in dist:
            total = dist[True] + dist[False]
            check(math.isclose(total, 1.0, rel_tol=1e-2, abs_tol=1e-2),
                  f"distribution not normalized (sum={total})", 0.2)
            check(abs(dist[True] - expected_true) < 0.05,
                  f"P(R=True | W) expected about {expected_true}, got {dist[True]}", 0.4)
    except Exception as e:
        fail_section(f"rejection_sampling failed with exception: {type(e).__name__}: {e}", deduction=1.5)


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



def check(condition, message, deduction=1):
    """
    Checks a condition. If false, deducts points and records error.
    """
    global errors
    if not condition:
        errors.append((message, deduction))
        print(f"❌ failed: {message}\n")
        return -deduction
    else:
        print("✅ Test passed \n")
        return 0


def fail_section(message, deduction=1):
    """
    Manually fail a section (e.g. if function is missing).
    """
    global errors
    errors.append((message, deduction))
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

    check(
        matrikelnummer_valid,
        f"matrikelnummer has not been changed from default (currently {matrikelnummer}); Points: -0.5",
        deduction=0.5,
    )
    check(
        name_valid,
        f"name has not been changed from default (currently {name}); Points: -0.5",
        deduction=0.5,
    )


def print_summary():
    global errors
    final_deduction = 0
    # Ensure score doesn't drop below 0
    final_score = max(0, current_score)

    print("\n" + "=" * 30)
    print("       GRADING RESULTS       ")
    print("=" * 30)

    if not errors:
        print("\n No errors found.")
    else:
        print("\nErrors found:")
        for error in errors:
            print(error[0], f"(-{error[1]} points)")
            final_deduction += error[1]

    final_score = max(0, max_score - final_deduction)
    print("-" * 30)
    print(f"Final Score: {final_score} / {max_score}")
    print("=" * 30)
    return final_score



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


# ==== Main Runner ====

if __name__ == "__main__":
    max_score = TOTAL_POINTS
    current_score = max_score
    errors = []

    module_list = convert_notebooks()

    if not module_list:
        print("No notebooks to test. Exiting.")
        sys.exit(0)

    for module_name in module_list:
        print(f"\n=== Testing {module_name} ===")
        check_identification(module_name)
        test_joint_probability(module_name)
        test_markov_blanket(module_name)
        test_rejection_sampling(module_name)

    print_summary()
