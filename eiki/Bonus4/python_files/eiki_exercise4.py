#!/usr/bin/env python
# coding: utf-8

# # Exercise 4
# In this exercise you will implement a forward pass and backpropagation **by hand**, then do the same with **PyTorch**. <br>
# You will build a tiny neural network for digit classification and see how the loss changes after an update step. <br>
# **Requirements:** You need `torch` (for MNIST + PyTorch) and `scikit-learn` (fallback dataset). If MNIST download fails, the notebook will use sklearn's digits dataset instead. <br>
# First enter your name and matrikelnummer. Without those we can't give you points.
# 

# In[1]:


#TODO: Enter your matriculation number and name
matrikelnummer = 3602227
name = "Niclas Kusenbach"


# The required imports for this exercise are as follows:
# numpy
# nbformat
# nbconvert
# torch
# torchvision
# scikit-learn

# # MNIST Classification (NumPy + PyTorch)
# You will start from the **MNIST** dataset and implement a tiny neural network for classification.
# 
# - Use the provided dataset loader and initial weights.
# - Keep variable names unchanged so the results are comparable.
# - **Important:** store intermediate results with the variable names listed in each task.
# 

# ## Helper functions (provided)
# These helpers are available for the tasks. Feel free to use or ignore them.
# 

# In[2]:


import numpy as np

def relu(x):
    return np.maximum(0, x)

def softmax(x):
    x = x - x.max(axis=1, keepdims=True)
    exp = np.exp(x)
    return exp / exp.sum(axis=1, keepdims=True)

def one_hot(y, num_classes):
    oh = np.zeros((len(y), num_classes), dtype=np.float32)
    oh[np.arange(len(y)), y] = 1.0
    return oh

def accuracy(y_pred, y_true):
    return (y_pred == y_true).mean()


# ## Dataset & initialization (provided)
# We try to load MNIST. If MNIST is not available, we fall back to the sklearn digits dataset.
# 

# In[3]:


def load_mnist_or_digits():
    # Try torchvision MNIST
    try:
        import torch  # pytorch>=2.5.1
        from torchvision import datasets, transforms
        transform = transforms.ToTensor()
        train_ds = datasets.MNIST(root=".", train=True, download=True, transform=transform)
        test_ds = datasets.MNIST(root=".", train=False, download=True, transform=transform)

        X_train = train_ds.data.numpy().astype(np.float32) / 255.0
        y_train = train_ds.targets.numpy().astype(np.int64)
        X_test = test_ds.data.numpy().astype(np.float32) / 255.0
        y_test = test_ds.targets.numpy().astype(np.int64)

        X_train = X_train.reshape(len(X_train), -1)
        X_test = X_test.reshape(len(X_test), -1)

        # Use small subsets for speed
        X_train = X_train[:2000]
        y_train = y_train[:2000]
        X_test = X_test[:500]
        y_test = y_test[:500]
        return X_train, y_train, X_test, y_test
    except Exception:
        pass

    # Fallback: sklearn digits (8x8)
    try:
        from sklearn.datasets import load_digits
        digits = load_digits()
        X = digits.data.astype(np.float32) / 16.0
        y = digits.target.astype(np.int64)
        # simple split
        n = len(X)
        split = int(0.8 * n)
        X_train, X_test = X[:split], X[split:]
        y_train, y_test = y[:split], y[split:]
        return X_train, y_train, X_test, y_test
    except Exception as e:
        raise RuntimeError("Could not load MNIST or digits dataset") from e

X_train, y_train, X_test, y_test = load_mnist_or_digits()
input_dim = X_train.shape[1]
num_classes = 10

# Tiny 2-layer network parameters (seeded for reproducibility)
rng = np.random.default_rng(1)
W1 = rng.normal(scale=0.1, size=(input_dim, 64))
b1 = np.zeros(64)
W2 = rng.normal(scale=0.1, size=(64, num_classes))
b2 = np.zeros(num_classes)


# ## Task 0: Dataset preview
# Print the shape of `X_train` and the first 3 labels. This helps you verify the input size.
# Look at a few samples to understand the inputs and labels.
# Then lets take the first sample from our training set
# 

# In[ ]:


# TODO: print the shape of X_train and the first 3 labels
print(X_train.shape)
print(y_train[:3])

# TODO: implement get_sample function
def get_sample(X_train,Y_train,index):
    x = X_train[index:index+1]
    y = Y_train[index]
    return x, y

#Has to be wrapped in a method for grading purposes
xb, yb_batch = get_sample(X_train, y_train, 0)


# ## Task 1: One forward pass (NumPy)
# Pick a single image `x0` and compute:
# 
# - hidden layer with ReLU (`z1`, `a1`)
# - logits (`logits`)
# - softmax probabilities (`probs`)
# - cross-entropy loss for the true label (`loss`)
# 
# **Required variable names:** `x0`, `y0`, `z1`, `a1`, `logits`, `probs`, `loss`, `pred`.
# Print the predicted class and the loss.
# 

# In[6]:


# TODO: forward pass for a single example
def forward_pass():
    x0 = X_train[0:1]
    y0 = y_train[0]
    z1 = np.dot(x0, W1) + b1  #pre-activation
    a1 = relu(z1) #activation function
    logits = np.dot(a1, W2) + b2
    probs = softmax(logits)
    loss = -1 * np.log(probs[0, y0])
    pred = np.argmax(probs)
    return z1, a1, logits, probs, loss, pred


z1, a1, logits, probs, loss, pred = forward_pass()
print(f"pred: {pred}, loss: {loss}")


# ## Task 2: One update step (NumPy)
# Compute gradients for the **single example** and do one SGD update.
# 
# Hints:
# - `dlogits = probs; dlogits[0, y0] -= 1`
# - Backprop through ReLU and the two linear layers.
# 
# **Required variable names:** `dlogits`, `dW2`, `db2`, `da1`, `dz1`, `dW1`, `db1`.
# 

# In[ ]:


# TODO: one update step
def update_step(probs, y0, a1, z1, x0, W1, b1, W2, b2, lr=0.1):
    dlogits = probs.copy()
    dlogits[0, y0] -= 1
    dW2 = np.dot(a1.T, dlogits)
    db2 = dlogits.squeeze()
    da1 = dlogits@W2.T
    dz1 = da1.copy()
    dz1[z1 <= 0] = 0
    dW1 = np.dot(x0.T, dz1)
    db1 = dz1.squeeze()
    W1 -= lr * dW1
    b1 -= lr * db1
    W2 -= lr * dW2
    b2 -= lr * db2
    return W1, b1, W2, b2


W1, b1, W2, b2 = update_step(probs, yb_batch, a1, z1, xb, W1, b1, W2, b2, lr=0.1)


# ## Task 3: PyTorch autograd
# Re-implement the same single-example forward/backward pass in [PyTorch](https://pytorch.org/get-started/locally/). The goal is to reproduce the same forward pass as in Task 1/2, and then let PyTorch compute gradients. If you want you can compare these PyTorch gradients with your NumPy gradients to see they match (up to small numerical differences).
# 
# 
# **Required variable names:** `W1_t`, `b1_t`, `W2_t`, `b2_t`, `loss_t`.
# Call `loss_t.backward()` so the gradients are stored in `.grad`.
# 

# In[ ]:


def pytorch_forward_backward(x0, y0, W1, b1, W2, b2):
    import torch
    x0_t = torch.from_numpy(x0).float()
    y0_t = torch.tensor([y0], requires_grad=False)
    W1_t = torch.tensor(W1, requires_grad=True, dtype=torch.float32)
    b1_t = torch.tensor(b1, requires_grad=True, dtype=torch.float32)
    W2_t = torch.tensor(W2, requires_grad=True, dtype=torch.float32)
    b2_t = torch.tensor(b2, requires_grad=True, dtype=torch.float32)

    z1_t = torch.matmul(x0_t, W1_t) + b1_t
    a1_t = torch.relu(z1_t)
    logits_t = torch.matmul(a1_t, W2_t) + b2_t
    loss_t = torch.nn.functional.cross_entropy(logits_t, y0_t)
    loss_t.backward()

    print(W1_t.grad.shape, b1_t.grad.shape, W2_t.grad.shape, b2_t.grad.shape)

    return W1_t, b1_t, W2_t, b2_t, loss_t


W1_t, b1_t, W2_t, b2_t, loss_t = pytorch_forward_backward(xb, yb_batch, W1, b1, W2, b2)


# ## Task 4: Mini training loop (NumPy)
# Train for a few epochs on a small subset and report accuracy on the test set. You can experiment with lr, epochs, and batch_size to see how they affect convergence.
# 
# !!!Warning!!!
# The public test only works with the default values, and the given seed.
# 
# 
# At the end, store:
# - `loss_last` (the most recent batch loss)
# - `test_acc_last` (the most recent test accuracy computed on the full test set)
# 
# Hint for test accuracy:
# - After each epoch, run a forward pass on `X_test` using your current `W1`, `b1`, `W2`, `b2`.
# - Compute logits for all test examples, turn them into predicted classes with `np.argmax(logits_t, axis=1)`
#   and then call `accuracy(preds, y_test)` to get a single scalar test accuracy.
# - Store this value in `test_acc_last` so it reflects the accuracy of the last epoch.

# In[28]:


# TODO: training loop
def training_loop(
    X_train,
    y_train,
    X_test,
    y_test,
    W1,
    b1,
    W2,
    b2,
    lr=0.1,
    epochs=5,
    batch_size=128,
    seed=42,
):
    np.random.seed(seed)
    loss_last = None
    test_acc_last = None
    for epoch in range(1, epochs + 1):
        perm = np.random.permutation(len(X_train))  # shuffle
        Xb = X_train[perm]
        yb = y_train[perm]
        for i in range(0, len(Xb), batch_size):
            # TODO: inside this minibatch loop
            xb = Xb[i : i + batch_size]
            yb_batch = yb[i : i + batch_size]
            # 1) forward pass: z1, a1, logits, probs for xb
            z1 = np.dot(xb, W1) + b1  # pre-activation
            a1 = relu(z1)  # activation function
            logits = np.dot(a1, W2) + b2
            probs = softmax(logits)

            # 2) calculate cross-entropy loss over yb
            loss = -1 * np.mean(np.log(probs[np.arange(len(xb)), yb_batch]))

            # 3) backprop: dlogits, dW2, db2, da1, dz1, dW1, db1 (similar to Task 2 but batched)
            dlogits = probs.copy()
            dlogits[np.arange(len(xb)), yb_batch] -= 1

            dW2 = np.dot(a1.T, dlogits) / len(xb)
            db2 = np.sum(dlogits, axis=0) / len(xb)
            da1 = dlogits @ W2.T
            dz1 = da1.copy()
            dz1[z1 <= 0] = 0
            dW1 = np.dot(xb.T, dz1) / len(xb)
            db1 = np.sum(dz1, axis=0) / len(xb)

            pred = np.argmax(probs)
            # 4) SGD update of W1, b1, W2, b2
            W1 -= lr * dW1
            b1 -= lr * db1
            W2 -= lr * dW2
            b2 -= lr * db2
            # 5) set loss_last = loss for this minibatch
            loss_last = loss
        # After finishing all minibatches for this epoch, compute test accuracy.
        # Hint: reuse the forward pass on the full test set:
        #   [...]

        z1_test = np.dot(X_test, W1) + b1
        a1_test = relu(z1_test)
        logits_test = np.dot(a1_test, W2) + b2

        preds = np.argmax(logits_test, axis=1)
        test_acc_last = accuracy(preds, y_test)
    # Also keep loss_last as the loss from the last minibatch of this epoch.

    return W1, b1, W2, b2, loss_last, test_acc_last


W1, b1, W2, b2, loss_last, test_acc_last = training_loop(
    X_train, y_train, X_test, y_test, W1, b1, W2, b2
)

print(f"Final loss: {loss_last:.4f}, Final test accuracy: {test_acc_last:.3f}")


# Note: <br>
# 
# If you have an implementation that you believe is correct but that does not pass the public test, please contact us via the forum. There is some numerical leeway built into the tests, but we have not tested all possible implementations.
