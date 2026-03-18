import numpy as np

# Summary
# 
# In this part of the homework, a convolutional neural network (CNN) was implemented
# manually using only NumPy operations. Each layer, including convolution, padding,
# pooling, batch normalization, and activation, was built from scratch to demonstrate
# a clear understanding of the mathematical foundations of CNNs. The obtained results
# were consistent with the theoretical calculations from Part 1, confirming the
# correctness of the implementation.
# 
# The experiment also illustrated how parameters such as filter size, stride, and
# padding influence the output dimensions and data flow through the network. Batch
# normalization improved the stability of feature values, while the tanh activation
# function effectively constrained them within a specific range. The final softmax
# outputs and loss values indicated a properly functioning model. Overall, this
# exercise provided valuable insight into the internal mechanisms of CNNs and the
# importance of each processing step.

# Configure numpy printing for consistent formatting (3 decimal places)
np.set_printoptions(precision=3, suppress=True)

# ----- Given Data (from assignment) -----
X = np.array([
    [ 1, -1,  0,  2, -2],
    [ 2,  0, -1,  1,  1],
    [-2,  1,  2, -1,  3],
    [ 1, -2,  1,  2, -1],
    [ 3,  0, -1,  1,  1],
], dtype=float)

F1 = np.array([
    [ 1, 0, -2],
    [ 0, 1,  0],
    [-2, 0,  1],
], dtype=float)

F2 = np.array([
    [ 1, -1],
    [ 0,  1],
], dtype=float)

F3 = np.array([
    [0, 1, 0],
    [1,-2, 1],
    [0, 1, 0],
], dtype=float)

ALPHA = 0.1
EPS = 1e-2
GAMMA = 1.0
BETA = 0.0

w1 = np.array([ 0.5, -0.4,  0.3,  0.2, -0.1], dtype=float)
b1 = 0.1
w2 = np.array([-0.2,  0.6, -0.5,  0.4,  0.2], dtype=float)
b2 = -0.2


# ----- Utility: padding -----
def pad2d(x, pad_h, pad_w):
    return np.pad(x, ((pad_h, pad_h), (pad_w, pad_w)), mode='constant', constant_values=0.0)


# ----- Implemented primitives -----
def conv2d(input, kernel, stride=1, padding='same'):
    """2D Convolution using cross-correlation (kernel NOT flipped, standard CNN practice).
    
    Args:
        input: 2D array of shape (H, W)
        kernel: 2D array of shape (kH, kW)
        stride: int, stride for convolution
        padding: str, 'same' or 'valid' padding mode
    
    Returns:
        2D array of shape (out_H, out_W) where:
        - out_H = (H + 2*pad_h - kH) // stride + 1  (for 'same' padding)
        - out_W = (W + 2*pad_w - kW) // stride + 1  (for 'same' padding)
    """
    kH, kW = kernel.shape
    H, W = input.shape
    if padding == 'same':
        pad_h = (kH - 1) // 2
        pad_w = (kW - 1) // 2
        x = pad2d(input, pad_h, pad_w)
    elif padding == 'valid':
        x = input
    else:
        raise ValueError("padding must be 'same' or 'valid'")
    out_h = (x.shape[0] - kH) // stride + 1
    out_w = (x.shape[1] - kW) // stride + 1
    out = np.zeros((out_h, out_w), dtype=float)
    for i in range(out_h):
        for j in range(out_w):
            patch = x[i*stride:i*stride+kH, j*stride:j*stride+kW]
            out[i, j] = np.sum(patch * kernel)
    return out


def leaky_relu(x, alpha=0.1):
    """Leaky ReLU activation function.
    
    Args:
        x: 2D or 1D array of shape (...,)
        alpha: float, slope for negative values
    
    Returns:
        Array of same shape as input
    """
    return np.where(x >= 0, x, alpha * x)


def avg_pool2d(x, kernel_size=2, stride=1):
    """Average pooling over 2D feature maps.
    
    Args:
        x: 2D array of shape (H, W)
        kernel_size: int, pooling window size (kH, kW both = kernel_size)
        stride: int, stride for pooling
    
    Returns:
        2D array of shape (out_H, out_W) where:
        - out_H = (H - kernel_size) // stride + 1
        - out_W = (W - kernel_size) // stride + 1
    
    Raises:
        AssertionError if H < kernel_size or W < kernel_size
    """
    H, W = x.shape
    k = kernel_size
    assert H >= k and W >= k, f"Input spatial dims ({H}, {W}) must be >= kernel_size ({k})"
    out_h = (H - k) // stride + 1
    out_w = (W - k) // stride + 1
    out = np.zeros((out_h, out_w), dtype=float)
    for i in range(out_h):
        for j in range(out_w):
            patch = x[i*stride:i*stride+k, j*stride:j*stride+k]
            out[i, j] = np.mean(patch)
    return out


def min_pool2d(x, kernel_size=2, stride=1):
    """Minimum pooling over 2D feature maps.
    
    Args:
        x: 2D array of shape (H, W)
        kernel_size: int, pooling window size (kH, kW both = kernel_size)
        stride: int, stride for pooling
    
    Returns:
        2D array of shape (out_H, out_W) where:
        - out_H = (H - kernel_size) // stride + 1
        - out_W = (W - kernel_size) // stride + 1
    
    Raises:
        AssertionError if H < kernel_size or W < kernel_size
    """
    H, W = x.shape
    k = kernel_size
    assert H >= k and W >= k, f"Input spatial dims ({H}, {W}) must be >= kernel_size ({k})"
    out_h = (H - k) // stride + 1
    out_w = (W - k) // stride + 1
    out = np.zeros((out_h, out_w), dtype=float)
    for i in range(out_h):
        for j in range(out_w):
            patch = x[i*stride:i*stride+k, j*stride:j*stride+k]
            out[i, j] = np.min(patch)
    return out


def batch_norm(x, gamma=1.0, beta=0.0, eps=1e-2):
    """Batch normalization (per-feature statistics, unbiased=False).
    
    Args:
        x: 2D or 1D array of shape (...,)
        gamma: float, scale parameter (default 1.0)
        beta: float, shift parameter (default 0.0)
        eps: float, numerical stability constant (default 1e-2)
    
    Returns:
        Tuple of (normalized_output, mean, variance) where:
        - normalized_output: array of same shape as x
        - mean: float, E[x]
        - variance: float, Var[x] (computed with unbiased=False, matching np.var default)
    """
    mu = np.mean(x)
    var = np.var(x)  # unbiased=False by default
    x_hat = (x - mu) / np.sqrt(var + eps)
    return gamma * x_hat + beta, mu, var


def tanh(x):
    """Hyperbolic tangent activation function.
    
    Args:
        x: array of any shape
    
    Returns:
        Array of same shape as input, values in [-1, 1]
    """
    return np.tanh(x)


def flatten(arrays):
    """Flatten and concatenate multiple 2D arrays into a 1D vector.
    
    Args:
        arrays: list/tuple of 2D arrays, or single 2D/1D array
    
    Returns:
        1D array of shape (total_elements,)
    """
    if isinstance(arrays, (list, tuple)):
        return np.concatenate([a.flatten() for a in arrays], axis=0)
    return arrays.flatten()


def fully_connected(x, W, b):
    """Fully connected (linear) layer.
    
    Args:
        x: 1D array of shape (D,)
        W: 1D array of shape (D,) - weight vector
        b: scalar - bias term
    
    Returns:
        Scalar output: W @ x + b
    """
    return W @ x + b


def softmax(z):
    """Softmax function for probability distribution.
    
    Args:
        z: 1D array or list of logits of shape (C,)
    
    Returns:
        1D array of probabilities of shape (C,), sums to 1
    """
    z = np.array(z, dtype=float)
    z = z - np.max(z)  # stability
    e = np.exp(z)
    return e / np.sum(e)


def main():
    # Step 1: First Convolution (same, stride=1)
    s1 = conv2d(X, F1, stride=1, padding='same')
    print("Step 1 shape:", s1.shape, "\n", s1)

    # Step 2: Leaky ReLU
    s2 = leaky_relu(s1, alpha=ALPHA)
    print("\nStep 2 shape:", s2.shape, "\n", s2)

    # Step 3: Average Pooling (2x2, stride=1)
    s3 = avg_pool2d(s2, kernel_size=2, stride=1)
    print("\nStep 3 shape:", s3.shape, "\n", s3)

    # Step 4: Second Layer
    # Branch A: F2 (valid, stride=1)
    A = conv2d(s3, F2, stride=1, padding='valid')
    print("\nStep 4A shape:", A.shape, "\n", A)

    # Branch B: F3 (same, stride=2)
    B = conv2d(s3, F3, stride=2, padding='same')
    print("\nStep 4B shape:", B.shape, "\n", B)

    # Step 5: Pooling
    A_pool = min_pool2d(A, kernel_size=2, stride=1)
    print("\nStep 5A (MinPool) shape:", A_pool.shape, "\n", A_pool)

    # For 2x2 map, avg pool with 2x2 stride 1 yields 1x1
    B_pool = avg_pool2d(B, kernel_size=2, stride=1)
    print("\nStep 5B (AvgPool) shape:", B_pool.shape, "\n", B_pool)

    # Step 6: Batch Norm (per-feature-map)
    A_bn, A_mu, A_var = batch_norm(A_pool, gamma=GAMMA, beta=BETA, eps=EPS)
    B_bn, B_mu, B_var = batch_norm(B_pool, gamma=GAMMA, beta=BETA, eps=EPS)
    print(f"\nStep 6A BN: mu={A_mu:.4f}, var={A_var:.4f}, shape={A_bn.shape}\n", A_bn)
    print(f"\nStep 6B BN: mu={B_mu:.4f}, var={B_var:.4f}, shape={B_bn.shape}\n", B_bn)

    # Step 7: tanh
    A_t = tanh(A_bn)
    B_t = tanh(B_bn)
    print("\nStep 7A tanh shape:", A_t.shape, "\n", A_t)
    print("\nStep 7B tanh shape:", B_t.shape, "\n", B_t)

    # Step 8: Flatten to 5D vector (A_t has 2x2=4, B_t has 1x1=1 -> total 5)
    x_flat = flatten([A_t, B_t])
    print("\nStep 8 Flatten shape:", x_flat.shape, "\n", x_flat)

    # FC: 2 logits
    z1 = fully_connected(x_flat, w1, b1)
    z2 = fully_connected(x_flat, w2, b2)
    print("\nStep 8 logits:", z1, z2)

    # Step 9: Softmax + losses
    probs = softmax([z1, z2])
    p1, p2 = probs[0], probs[1]
    print(f"\nStep 9 Softmax: p1={p1:.6f}, p2={p2:.6f}")
    ce = -np.log(max(p1, 1e-12))
    mse = 0.5 * ((1 - p1)**2 + (0 - p2)**2)
    print(f"Cross-Entropy (Class 0): {ce:.6f}\nMSE: {mse:.6f}")


if __name__ == "__main__":
    main()




