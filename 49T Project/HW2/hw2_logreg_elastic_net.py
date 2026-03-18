# CMPE49T - HW2
# @author: Ali Ayhan Gunder
# @id: 2021400219

# Logistic Regression with Elastic Net Regularization
# Implements proximal gradient descent with L1 soft-thresholding for true sparsity.




import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt
import csv
from pathlib import Path

def sigmoid(z):
    """Numerically stable sigmoid function."""
    out = np.empty_like(z, dtype=float)
    pos = z >= 0
    neg = ~pos
    out[pos] = 1.0 / (1.0 + np.exp(-z[pos]))
    expz = np.exp(z[neg])
    out[neg] = expz / (1.0 + expz)
    return out

def expand_features(X):
    """Return 9D polynomial feature map: [x1,x2,x3,x1^2,x2^2,x3^2,x1x2,x1x3,x2x3]."""
    x1 = X[:, 0]; x2 = X[:, 1]; x3 = X[:, 2]
    return np.column_stack([
        x1, x2, x3,
        x1**2, x2**2, x3**2,
        x1*x2, x1*x3, x2*x3
    ])

def standardize_train_test(X_train, X_val):
    """Standardize using train mean/std only; if a feature has zero std, set std=1.0."""
    mean = X_train.mean(axis=0, keepdims=True)
    std = X_train.std(axis=0, keepdims=True)
    std = np.where(std == 0, 1.0, std)
    return (X_train - mean) / std, (X_val - mean) / std, (mean, std)

def compute_loss_and_grad_without_l1(X, y, w, b, lmbda, alpha):
    """Compute CE loss + L2 penalty (without L1) and gradients for the gradient step."""
    N = X.shape[0]
    z = X @ w + b
    p = sigmoid(z)
    eps = 1e-12
    # Cross-entropy loss
    ce = - (y * np.log(p + eps) + (1 - y) * np.log(1 - p + eps)).mean()
    # L2 penalty only (L1 handled separately in proximal step)
    l2_penalty = lmbda * (1.0 - alpha) * np.sum(w**2)
    loss = ce + l2_penalty

    error = (p - y)
    grad_w = (X.T @ error) / N
    grad_b = error.mean()
    # Add L2 gradient (no L1 here)
    grad_w += 2.0 * lmbda * (1.0 - alpha) * w

    return loss, grad_w, grad_b, p

def compute_full_loss(X, y, w, b, lmbda, alpha):
    """Compute full Elastic Net loss: CE + lambda * [alpha * L1 + (1-alpha) * L2]."""
    z = X @ w + b
    p = sigmoid(z)
    eps = 1e-12
    ce = - (y * np.log(p + eps) + (1 - y) * np.log(1 - p + eps)).mean()
    penalty = lmbda * (alpha * np.sum(np.abs(w)) + (1 - alpha) * np.sum(w**2))
    return ce + penalty

def accuracy_from_probs(p, y, thresh=0.5):
    """Compute classification accuracy at given threshold."""
    yhat = (p >= thresh).astype(int)
    return (yhat == y).mean()

def train_logreg_elastic_net(
    X_train, y_train, X_val, y_val,
    lmbda, alpha=0.5, eta=0.1, tol=1e-6, max_iter=3000, seed=42,
    grad_clip=10.0, b_clip=10.0, patience=50
):
    """
    Train logistic regression with elastic net using proximal gradient descent.

    Sparsity method: Proximal gradient with L1 soft-thresholding.
    After each gradient step, apply: w := sign(w) * max(|w| - eta*lambda*alpha, 0)
    This induces exact zeros for true sparsity.

    Includes early stopping on validation loss (patience).
    """
    rng = np.random.default_rng(seed)
    d = X_train.shape[1]
    w = rng.uniform(-0.01, 0.01, size=d)
    b = float(rng.uniform(-0.01, 0.01, size=1)[0])  # Extract scalar before converting to float

    history = {"iter": [], "train_loss": [], "val_loss": []}
    last_loss = np.inf
    best_val = float("inf")
    bad = 0

    for it in range(1, max_iter + 1):
        # Compute gradient (without L1; L1 handled in proximal step)
        train_loss, grad_w, grad_b, _ = compute_loss_and_grad_without_l1(X_train, y_train, w, b, lmbda, alpha)

        # Clip gradient norm
        gn = np.linalg.norm(grad_w)
        if gn > grad_clip:
            grad_w *= (grad_clip / (gn + 1e-12))
        grad_b = float(np.clip(grad_b, -b_clip, b_clip))

        # Gradient step
        w -= eta * grad_w
        b -= eta * grad_b

        # Proximal step: L1 soft-thresholding for true sparsity
        threshold = eta * lmbda * alpha
        w = np.sign(w) * np.maximum(np.abs(w) - threshold, 0.0)

        # Compute full loss for reporting (including L1)
        full_train_loss = compute_full_loss(X_train, y_train, w, b, lmbda, alpha)
        val_loss = compute_full_loss(X_val, y_val, w, b, lmbda, alpha)

        history["iter"].append(it)
        history["train_loss"].append(float(full_train_loss))
        history["val_loss"].append(float(val_loss))

        # Early stopping on validation loss
        if val_loss < best_val - 1e-8:
            best_val = val_loss
            bad = 0
        else:
            bad += 1
        if bad >= patience:
            break

        if not np.isfinite(full_train_loss):
            break
        if abs(last_loss - full_train_loss) < tol:
            break
        last_loss = full_train_loss

    train_probs = sigmoid(X_train @ w + b)
    val_probs = sigmoid(X_val @ w + b)
    return {
        "w": w, "b": b,
        "train_acc": float(accuracy_from_probs(train_probs, y_train)),
        "val_acc": float(accuracy_from_probs(val_probs, y_val)),
        "final_train_loss": float(history["train_loss"][-1]) if history["train_loss"] else np.inf,
        "final_val_loss": float(history["val_loss"][-1]) if history["val_loss"] else np.inf,
        "iters": len(history["iter"]),
        "ok": np.isfinite(history["train_loss"][-1]) if history["train_loss"] else False,
        "history": history,  # Return history for plotting
    }

# ===============================
# Data
# ===============================
dataset = np.array([
[-2, 0, 2, 1],
[ 1, -1, 1, 0],
[-1, -1, 0, 0],
[-1, -1, -2, 1],
[ 0, 2, 2, 0],
[ 0, 0, 0, 0],
[-1, -2, 0, 0],
[-2, -2, -1, 1],
[ 0, -1, 0, 0],
[ 1, 0, 0, 0],
[-2, -1, 0, 1],
[ 1, 0, 2, 0],
[ 1, 2, -2, 1],
[-2, 0, -2, 0],
[ 1, 0, 0, 0],
[-1, -2, 0, 0],
[ 0, 1, 0, 0],
[-2, 0, 1, 1],
[-1, 1, 1, 0],
[ 2, -2, -1, 0],
[ 0, -1, -2, 1],
[ 2, 1, 0, 0],
[ 2, 1, -2, 1],
[-2, 0, -1, 0],
[ 2, -2, 0, 0],
[ 0, -2, 1, 0],
[ 1, 1, 2, 1],
[-2, -1, 0, 1],
[ 1, -2, 2, 1],
[ 1, 0, -1, 0],
[ 2, 1, -2, 1],
[ 0, 2, 1, 0],
[ 0, 1, 0, 0],
[ 1, -2, 0, 0],
[-1, 0, 0, 0],
[ 2, -1, 1, 0],
[ 1, 1, 2, 1],
[-2, 0, 0, 1],
[-1, 1, 1, 0],
[ 1, 2, -2, 1],
[ 0, 0, -2, 0],
[ 0, 0, -2, 0],
[ 0, -2, 2, 1],
[ 1, 1, 1, 1],
[ 2, 0, 0, 1],
[-1, 1, 1, 0],
[ 1, 2, -2, 1],
[ 0, 0, 1, 1],
[ 1, 1, 1, 1],
[-2, 0, -1, 0],
[ 0, -1, 2, 1],
[ 0, 0, 1, 1],
[-1, -1, -1, 1],
[ 0, -2, 1, 0],
[-1, 0, 0, 0],
[ 2, 1, -2, 1],
[ 1, 1, 1, 1],
[ 2, 1, 2, 1],
[ 2, 2, 1, 1],
[ 1, 1, 1, 1]
], dtype=float)

X_raw = dataset[:, :3]
y = dataset[:, 3].astype(int)
X_exp = expand_features(X_raw)

# Fixed seed for reproducibility
rng = np.random.default_rng(49)
idx = np.arange(len(X_exp))
rng.shuffle(idx)
train_idx = idx[:50]
val_idx = idx[50:60]
X_train = X_exp[train_idx]
y_train = y[train_idx]
X_val = X_exp[val_idx]
y_val = y[val_idx]

# Standardize using train mean/std only
X_train_std, X_val_std, (mu, sigma) = standardize_train_test(X_train, X_val)

# ===============================
# Training across lambdas
# ===============================
lambdas = [0.01, 0.1, 1.0, 10.0, 50.0]
results = []
weights_rows = []  # Collect learned weights across lambdas
feature_names = ["x1","x2","x3","x1^2","x2^2","x3^2","x1x2","x1x3","x2x3"]

for lmbda in lambdas:
    res = train_logreg_elastic_net(
        X_train_std, y_train, X_val_std, y_val,
        lmbda=lmbda, alpha=0.5, eta=0.1, tol=1e-6, max_iter=3000, seed=42, patience=50
    )
    res["lambda"] = lmbda
    results.append(res)

    # Save learned parameters for this lambda
    w = res["w"]
    b = res["b"]
    weights_rows.append([lmbda, *w.tolist(), b])

    # Save convergence plot for this lambda
    history = res["history"]
    if history["train_loss"]:
        plt.figure(figsize=(8, 5))
        plt.plot(history["iter"], history["train_loss"], label="train loss", linewidth=2)
        if len(history["val_loss"]) == len(history["train_loss"]):
            plt.plot(history["iter"], history["val_loss"], label="val loss", linewidth=2)
        plt.xlabel("Iteration")
        plt.ylabel("Loss (CE + penalty)")
        plt.title(f"Convergence (λ={lmbda})")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(f"convergence_lambda_{lmbda}.png", dpi=150)
        plt.close()

    # Save feature ranking for this lambda
    abs_order = np.argsort(-np.abs(w))
    with open(f"feature_ranking_lambda_{lmbda}.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["rank", "feature", "feature_index", "abs_weight", "weight"])
        for rank, idx_feat in enumerate(abs_order, 1):
            writer.writerow([rank, feature_names[idx_feat], idx_feat + 1, abs(w[idx_feat]), w[idx_feat]])

# Save all learned weights/parameters
with open("learned_weights.csv", "w", newline="") as f:
    writer = csv.writer(f)
    header = ["lambda"] + [f"w{i+1}" for i in range(len(results[0]["w"]))] + ["b"]
    writer.writerow(header)
    writer.writerows(weights_rows)

# ===============================
# Summary table
# ===============================
summary_rows = []
for r in results:
    w = r["w"]
    # Use exact zeros from proximal step: count nonzeros directly
    num_nonzero_exact = int(np.count_nonzero(w))

    summary_rows.append({
        "lambda": r["lambda"],
        "train_loss": r["final_train_loss"],
        "val_loss": r["final_val_loss"],
        "train_acc": r["train_acc"],
        "val_acc": r["val_acc"],
        "num_nonzero_weights": num_nonzero_exact,
        "avg_|w|": float(np.mean(np.abs(w))),
        "iterations": r["iters"],
        "ok": bool(r["ok"]),
    })
summary_df = pd.DataFrame(summary_rows).sort_values(by="lambda")

# Pick best by val_acc then lower val_loss
best = sorted(results, key=lambda r: (-r["val_acc"], r["final_val_loss"]))[0]

# Feature ranking for best model
rank_idx = np.argsort(-np.abs(best["w"]))
feature_ranking = pd.DataFrame({
    "feature": np.array(feature_names)[rank_idx],
    "|w|": np.abs(best["w"])[rank_idx],
    "w": best["w"][rank_idx],
})

# ===============================
# Predictions for unseen points
# ===============================
unseen = np.array([
    [ 1, 0, 1],
    [-1,-1, 1],
    [ 2, 0,-2],
    [ 0, 2,-1],
    [-2, 1, 0],
], dtype=float)

unseen_exp = expand_features(unseen)
unseen_std = (unseen_exp - mu) / sigma

pred_rows = []
for r in results:
    w = r["w"]
    b = r["b"]
    probs = sigmoid(unseen_std @ w + b)
    labels = (probs >= 0.5).astype(int)
    for i in range(unseen.shape[0]):
        pred_rows.append({
            "lambda": r["lambda"],
            "point": i+1,
            "x1": unseen[i,0], "x2": unseen[i,1], "x3": unseen[i,2],
            "prob_lesion": float(probs[i]),
            "pred_label@0.5": int(labels[i])
        })
pred_df = pd.DataFrame(pred_rows)

# ===============================
# Save artifacts
# ===============================
summary_df.to_csv("hw2_summary.csv", index=False)
pred_df.to_csv("hw2_predictions.csv", index=False)

# Save "best model" artifacts for quick access
pd.DataFrame({"w": best["w"]}).to_csv("best_weights.csv", index=False)
feature_ranking.to_csv("best_feature_ranking.csv", index=False)

# Save run meta for reproducibility
run_meta = {"alpha": 0.5, "eta": 0.1, "patience": 50, "tol": 1e-6, "seed": 42, "split_seed": 49}
pd.DataFrame([run_meta]).to_csv("run_meta.csv", index=False)

# ===============================
# Console report
# ===============================
print("=" * 70)
print("HW2 Summary (by λ)")
print("=" * 70)
print(summary_df.to_string(index=False))
print("\n" + "=" * 70)
print("Best Model Feature Ranking (|w| desc)")
print("=" * 70)
print(feature_ranking.to_string(index=False))
print("\n" + "=" * 70)
print("Predictions on Unseen Points (all λ)")
print("=" * 70)
print(pred_df.to_string(index=False))
print("\n" + "=" * 70)
print("Files saved:")
print("  - hw2_summary.csv")
print("  - hw2_predictions.csv")
print("  - learned_weights.csv")
print("  - best_weights.csv")
print("  - best_feature_ranking.csv")
print("  - run_meta.csv")
print("  - convergence_lambda_*.png (for each λ)")
print("  - feature_ranking_lambda_*.csv (for each λ)")
print("=" * 70)
print("\nNOTE: Sparsity method used: Proximal gradient with L1 soft-thresholding.")
print("This induces exact zeros in the learned weights, enabling true L1 sparsity.")
print("Feature rankings and convergence plots saved for each λ value.")
print("=" * 70)
