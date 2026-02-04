import pathlib
import importlib
import nbformat
from nbconvert import PythonExporter
import sys
import traceback
import warnings
import math
import numpy as np

"""

Public tests for bonus exercise 4.

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

# ==== Configuration ====

TOTAL_POINTS = 10
BASE_DIR = pathlib.Path(__file__).parent
PYTHON_FILES_DIR = BASE_DIR / "python_files"

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# ==== Helper Functions ====

def convert_notebooks():
    """
    Finds all .ipynb files, converts to .py in 'python_files' dir.
    Returns list of module names.
    """
    output_dir = PYTHON_FILES_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "__init__.py").touch()

    module_list = []

    notebooks = list(BASE_DIR.glob("*.ipynb"))
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
        (body, _resources) = exporter.from_notebook_node(nb)

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
    global errors
    if not condition:
        errors.append((message, deduction))
        print(f"❌ failed: {message}\n")
        return -deduction
    else:
        print("✅ Test passed \n")
        return 0


def fail_section(message, deduction=1):
    global errors
    errors.append((message, deduction))
    print(f"❌ {message}")
    return -deduction


def _test_var_exists(mod, name):
    if not hasattr(mod, name):
        fail_section(f"Missing required variable: {name}", deduction=0.5)
        return False
    return True


def _test_function_exists(module_name, function_name):
    try:
        mod = importlib.import_module(f"python_files.{module_name}")
        importlib.reload(mod)
    except Exception as e:
        print(f"Could not import module '{module_name}'. Error: {e}")
        return None
    if not hasattr(mod, function_name):
        print(f"Function or variable '{function_name}' not found in {module_name}.")
        return None
    return mod


def check_identification(module_name):
    print("\n--- Checking identification ---")
    mod = _test_function_exists(module_name, "matrikelnummer")
    if mod is None:
        fail_section("No matrikelnummer found in notebook", deduction=1)
        return

    matrikelnummer = getattr(mod, "matrikelnummer", None)
    name = getattr(mod, "name", None)

    matrikelnummer_valid = matrikelnummer != 0 and matrikelnummer != "0000000"
    name_valid = name != "Max Mustermann"

    check(matrikelnummer_valid,
          f"matrikelnummer has not been changed from default (currently {matrikelnummer}); Points: -0.5",
          deduction=0.5)
    check(name_valid,
          f"name has not been changed from default (currently {name}); Points: -0.5",
          deduction=0.5)


# ===== Test Functions =====


def test_dataset(module_name):
    """Task 0: Test get_sample function (budget 1.0 points)"""
    print("\n--- Testing Task 0: Dataset & get_sample ---")
    mod = _test_function_exists(module_name, "get_sample")
    if mod is None:
        fail_section("Could not import module or get_sample missing", deduction=1.0)
        return
    
    if not hasattr(mod, "X_train") or not hasattr(mod, "y_train"):
        fail_section("Missing X_train or y_train in module", deduction=1.0)
        return
    
    try:
        x0, y0 = mod.get_sample(mod.X_train, mod.y_train, 0)
    except Exception as e:
        fail_section(f"Error calling get_sample: {type(e).__name__}: {e}", deduction=1.0)
        return
    
    print("Checking x0[0][-1] is approximately 0")
    check(abs(float(x0[0, -1]) - 0.0) <= 1e-6,
          f"x0[0][-1] should be 0.0, got {x0[0, -1]}", deduction=0.5)
    
    print("Checking y0 == 5")
    check(int(y0) == 5,
          f"y0 should be 5, got {y0}", deduction=0.5)


def test_task1_forward(module_name):
    """Task 1: Test forward_pass function (budget 2.0 points)"""
    print("\n--- Testing Task 1: Forward Pass ---")
    mod = _test_function_exists(module_name, "forward_pass")
    if mod is None:
        fail_section("forward_pass missing or module import failed", deduction=2.0)
        return
    
    # Ensure get_sample and data exist
    if not hasattr(mod, "get_sample") or not hasattr(mod, "X_train") or not hasattr(mod, "y_train"):
        fail_section("Missing get_sample, X_train, or y_train for forward_pass test", deduction=2.0)
        return
    
    try:
        # Reinitialize weights to original state (module execution may have modified them)
        input_dim = mod.X_train.shape[1]
        rng = np.random.default_rng(1)
        mod.W1 = rng.normal(scale=0.1, size=(input_dim, 64))
        mod.b1 = np.zeros(64)
        mod.W2 = rng.normal(scale=0.1, size=(64, 10))
        mod.b2 = np.zeros(10)
        
        # Prepare sample
        x0, y0 = mod.get_sample(mod.X_train, mod.y_train, 0)
        mod.x0 = x0
        mod.y0 = y0
    except Exception as e:
        fail_section(f"Error preparing sample for forward_pass: {type(e).__name__}: {e}", deduction=2.0)
        return
    
    try:
        z1, a1, logits, probs, loss, pred = mod.forward_pass()
    except Exception as e:
        fail_section(f"Error in forward_pass: {type(e).__name__}: {e}", deduction=2.0)
        return
    
    # Reference values (fresh weights): pred: 1, loss: 2.1027, z1: -0.4291, a1: 0.0000, logits: -0.4046, probs: 0.0588
    print("Checking predicted class == 1")
    check(int(pred) == 1,
          f"pred should be 1, got {pred}", deduction=0.5)
    
    print("Checking loss value")
    check(abs(float(loss) - 2.1027) <= 5e-2,
          f"loss should be ~2.1027, got {loss}", deduction=0.5)
    
    print("Checking z1[0,0] and a1[0,0] values")
    z1_ok = abs(round(float(z1[0, 0]), 4) - (-0.4291)) <= 5e-4
    a1_ok = abs(round(float(a1[0, 0]), 4) - 0.0000) <= 5e-4  # ReLU(-0.4291) = 0
    check(z1_ok and a1_ok,
          f"z1[0,0] should be ~-0.4291 (got {z1[0,0]:.4f}), a1[0,0] should be ~0.0000 (got {a1[0,0]:.4f})", deduction=0.5)
    
    print("Checking logits[0,0] and probs[0,0] values")
    logits_ok = abs(round(float(logits[0, 0]), 4) - (-0.4046)) <= 5e-4
    probs_ok = abs(round(float(probs[0, 0]), 4) - 0.0588) <= 5e-4
    check(logits_ok and probs_ok,
          f"logits[0,0] should be ~-0.4046 (got {logits[0,0]:.4f}), probs[0,0] should be ~0.0588 (got {probs[0,0]:.4f})", deduction=0.5)


def test_task2_backprop(module_name):
    """Task 2: Test update_step function (budget 2.0 points)"""
    print("\n--- Testing Task 2: Backpropagation (update_step) ---")
    mod = _test_function_exists(module_name, "update_step")
    if mod is None:
        fail_section("update_step missing or module import failed", deduction=2.0)
        return
    
    # Ensure required functions and variables exist
    required = ["get_sample", "forward_pass", "W1", "b1", "W2", "b2", "X_train", "y_train"]
    for req in required:
        if not hasattr(mod, req):
            fail_section(f"Missing {req} for update_step test", deduction=2.0)
            return
    
    try:
        # Reinitialize weights to original state
        input_dim = mod.X_train.shape[1]
        rng = np.random.default_rng(1)
        mod.W1 = rng.normal(scale=0.1, size=(input_dim, 64))
        mod.b1 = np.zeros(64)
        mod.W2 = rng.normal(scale=0.1, size=(64, 10))
        mod.b2 = np.zeros(10)
        
        # Prepare inputs
        x0, y0 = mod.get_sample(mod.X_train, mod.y_train, 0)
        mod.x0 = x0
        mod.y0 = y0
        z1, a1, logits, probs, loss, pred = mod.forward_pass()
    except Exception as e:
        fail_section(f"Error preparing inputs for update_step: {type(e).__name__}: {e}", deduction=2.0)
        return
    
    try:
        # Use copies to avoid side effects
        W1_new, b1_new, W2_new, b2_new = mod.update_step(
            probs, y0, a1, z1, x0,
            mod.W1.copy(), mod.b1.copy(), mod.W2.copy(), mod.b2.copy(),
            lr=0.1
        )
    except Exception as e:
        fail_section(f"Error in update_step: {type(e).__name__}: {e}", deduction=2.0)
        return
    
    # Reference values (fresh weights after one update): w1: 0.0346 b1: 0.0000 w2: -0.0417 b2: -0.0059
    print("Checking W1[0,0] and b1[0] after update")
    w1_ok = abs(round(float(W1_new[0, 0]), 4) - 0.0346) <= 5e-4
    b1_ok = abs(round(float(b1_new[0]), 4) - 0.0000) <= 5e-4
    check(w1_ok and b1_ok,
          f"W1[0,0] should be ~0.0346 (got {W1_new[0,0]:.4f}), b1[0] should be ~0.0000 (got {b1_new[0]:.4f})", deduction=1.0)
    
    print("Checking W2[0,0] and b2[0] after update")
    w2_ok = abs(round(float(W2_new[0, 0]), 4) - (-0.0417)) <= 5e-4
    b2_ok = abs(round(float(b2_new[0]), 4) - (-0.0059)) <= 5e-4
    check(w2_ok and b2_ok,
          f"W2[0,0] should be ~-0.0417 (got {W2_new[0,0]:.4f}), b2[0] should be ~-0.0059 (got {b2_new[0]:.4f})", deduction=1.0)


def test_task3_pytorch(module_name):
    """Task 3: Test pytorch_forward_backward function (budget 2.0 points)"""
    print("\n--- Testing Task 3: PyTorch Forward/Backward ---")
    mod = _test_function_exists(module_name, "pytorch_forward_backward")
    if mod is None:
        fail_section("pytorch_forward_backward missing or module import failed", deduction=2.0)
        return
    
    # Ensure required functions and variables exist
    required = ["get_sample", "forward_pass", "update_step", "W1", "b1", "W2", "b2", "X_train", "y_train"]
    for req in required:
        if not hasattr(mod, req):
            fail_section(f"Missing {req} for pytorch_forward_backward test", deduction=2.0)
            return
    
    try:
        # Reinitialize weights to original state
        input_dim = mod.X_train.shape[1]
        rng = np.random.default_rng(1)
        mod.W1 = rng.normal(scale=0.1, size=(input_dim, 64))
        mod.b1 = np.zeros(64)
        mod.W2 = rng.normal(scale=0.1, size=(64, 10))
        mod.b2 = np.zeros(10)
        
        # Reconstruct the same state as after Task 2
        x0, y0 = mod.get_sample(mod.X_train, mod.y_train, 0)
        mod.x0 = x0
        mod.y0 = y0
        z1, a1, logits, probs, loss, pred = mod.forward_pass()
        W1_u, b1_u, W2_u, b2_u = mod.update_step(
            probs, y0, a1, z1, x0,
            mod.W1.copy(), mod.b1.copy(), mod.W2.copy(), mod.b2.copy(),
            lr=0.1
        )
    except Exception as e:
        fail_section(f"Error preparing inputs for pytorch_forward_backward: {type(e).__name__}: {e}", deduction=2.0)
        return
    
    try:
        W1_t, b1_t, W2_t, b2_t, loss_t = mod.pytorch_forward_backward(x0, y0, W1_u, b1_u, W2_u, b2_u)
    except Exception as e:
        fail_section(f"Error in pytorch_forward_backward (PyTorch missing or error): {type(e).__name__}: {e}", deduction=2.0)
        return
    
    # Reference values: W1 grad: 0.0000 b1 grad: 0.0000 W2 grad: 0.0000 b2 grad: 0.0131 loss: 0.2373
    print("Checking gradients (W1, b1, W2 should be ~0, b2 may vary)")
    try:
        gW1 = float(W1_t.grad[0, 0])
        gb1 = float(b1_t.grad[0])
        gW2 = float(W2_t.grad[0, 0])
        gb2 = float(b2_t.grad[0])
        # W1, b1, W2 grads at [0,0] or [0] should be ~0 (due to ReLU killing gradient path)
        grads_ok = (abs(gW1) <= 5e-4 and abs(gb1) <= 5e-4 and abs(gW2) <= 5e-4)
        check(grads_ok,
              f"W1, b1, W2 gradients should be ~0.0000, got W1:{gW1:.4f}, b1:{gb1:.4f}, W2:{gW2:.4f}", deduction=1.0)
    except Exception as e:
        fail_section(f"Error accessing gradients: {type(e).__name__}: {e}", deduction=1.0)
    
    print("Checking loss value")
    try:
        loss_val = float(loss_t.item())
        check(abs(round(loss_val, 4) - 0.2373) <= 5e-2,
              f"loss should be ~0.2373, got {loss_val:.4f}", deduction=1.0)
    except Exception as e:
        fail_section(f"Error accessing loss: {type(e).__name__}: {e}", deduction=1.0)


def test_task4_training(module_name):
    """Task 4: Test training_loop function with 2 epochs (budget 2.0 points)"""
    print("\n--- Testing Task 4: Training Loop (2 epochs) ---")
    mod = _test_function_exists(module_name, "training_loop")
    if mod is None:
        fail_section("training_loop missing or module import failed", deduction=2.0)
        return
    
    # Ensure required variables exist
    required = ["X_train", "y_train", "X_test", "y_test"]
    for req in required:
        if not hasattr(mod, req):
            fail_section(f"Missing {req} for training_loop test", deduction=2.0)
            return
    
    # Reconstruct initial weights exactly as in the notebook for reproducibility
    try:
        input_dim = mod.X_train.shape[1]
        rng = np.random.default_rng(1)
        W1_init = rng.normal(scale=0.1, size=(input_dim, 64))
        b1_init = np.zeros(64)
        W2_init = rng.normal(scale=0.1, size=(64, 10))
        b2_init = np.zeros(10)
    except Exception as e:
        fail_section(f"Error initializing weights for training_loop test: {type(e).__name__}: {e}", deduction=2.0)
        return
    
    try:
        W1_tr, b1_tr, W2_tr, b2_tr, loss_last, test_acc_last = mod.training_loop(
            mod.X_train, mod.y_train, mod.X_test, mod.y_test,
            W1_init, b1_init, W2_init, b2_init,
            lr=0.1, epochs=2, batch_size=128, seed=42
        )
    except Exception as e:
        fail_section(f"Error in training_loop: {type(e).__name__}: {e}", deduction=2.0)
        return
    
    # Reference values for 2 epochs:
    # W1[0,0]: 0.0346 b1[0]: 0.0319 W2[0,0]: -0.1148 b2[0]: -0.0383
    # Final loss: 1.2845, Final test accuracy: 0.646
    print("Checking final parameters after 2 epochs")
    w1_ok = abs(round(float(W1_tr[0, 0]), 4) - 0.0346) <= 5e-4
    b1_ok = abs(round(float(b1_tr[0]), 4) - 0.0319) <= 5e-4
    w2_ok = abs(round(float(W2_tr[0, 0]), 4) - (-0.1148)) <= 5e-4
    b2_ok = abs(round(float(b2_tr[0]), 4) - (-0.0383)) <= 5e-4
    check(w1_ok and b1_ok and w2_ok and b2_ok,
          f"Final params incorrect: W1[0,0]={W1_tr[0,0]:.4f} (exp 0.0346), b1[0]={b1_tr[0]:.4f} (exp 0.0319), "
          f"W2[0,0]={W2_tr[0,0]:.4f} (exp -0.1148), b2[0]={b2_tr[0]:.4f} (exp -0.0383)", deduction=1.0)
    
    print("Checking final loss and test accuracy")
    loss_ok = abs(round(float(loss_last), 4) - 1.2845) <= 5e-4
    acc_ok = abs(round(float(test_acc_last), 3) - 0.646) <= 5e-3
    check(loss_ok and acc_ok,
          f"Final metrics incorrect: loss={loss_last:.4f} (exp 1.2845), test_acc={test_acc_last:.3f} (exp 0.646)", deduction=1.0)


def print_summary():
    global errors
    final_deduction = 0
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


# ==== Main Execution ====

if __name__ == "__main__":
    max_score = TOTAL_POINTS
    current_score = TOTAL_POINTS
    errors = []

    module_list = convert_notebooks()

    for module_name in module_list:
        check_identification(module_name)
        test_dataset(module_name)
        test_task1_forward(module_name)
        test_task2_backprop(module_name)
        test_task3_pytorch(module_name)
        test_task4_training(module_name)

    print_summary()
