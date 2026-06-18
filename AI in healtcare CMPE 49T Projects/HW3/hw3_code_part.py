# @author: Ali Ayhan Gunder
# @student_id: 2021400219
# @date: 2025-11-23
# Implementation for CMPE 49T HW3: Logistic Regression from Scratch and Evaluation

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from pathlib import Path

# ------------------- CONFIG -------------------
student_id = "2021400219"  
seed = int("".join([c for c in student_id if c.isdigit()]) or "0") % (2**32 - 1)

data_path = "processed.cleveland.data"  
outdir = Path(".")
outdir.mkdir(parents=True, exist_ok=True)

# Training hyperparameters
lr = 0.05
epochs = 5000
patience = 5
train_ratio = 0.7

# Threshold grid for evaluation
thresholds_coarse = np.round(np.arange(0.0, 1.0 + 1e-9, 0.05), 2)
thresholds_fine = np.round(np.arange(0.0, 1.0 + 1e-9, 0.01), 2)

# ------------------- UTILITIES -------------------
def set_seed(s):
    rng = np.random.default_rng(s)
    return rng

def sigmoid(z):
    # numerically stable
    # for large negative values, exp(-z) overflows; clip z
    z = np.clip(z, -500, 500)
    return 1 / (1 + np.exp(-z))

def bce_loss(y_true, y_prob, eps=1e-12):
    y_prob = np.clip(y_prob, eps, 1 - eps)
    return -np.mean(y_true * np.log(y_prob) + (1 - y_true) * np.log(1 - y_prob))

def metrics_from_confusion(tp, fp, fn, tn):
    acc = (tp + tn) / (tp + fp + fn + tn) if (tp + fp + fn + tn) > 0 else np.nan
    prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0  # sensitivity
    spec = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    f1 = (2 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0
    return acc, prec, rec, spec, f1

def confusion_counts(y_true, y_prob, thr):
    y_pred = (y_prob >= thr).astype(int)
    tp = int(np.sum((y_true == 1) & (y_pred == 1)))
    fp = int(np.sum((y_true == 0) & (y_pred == 1)))
    fn = int(np.sum((y_true == 1) & (y_pred == 0)))
    tn = int(np.sum((y_true == 0) & (y_pred == 0)))
    return tp, fp, fn, tn

def trapezoid_area(x, y):
    # Assumes x sorted ascending and same length
    return np.trapz(y, x)

# ------------------- PART I: LOAD & PREP -------------------
# Column names from UCI Cleveland dataset
columns = [
    "age","sex","cp","trestbps","chol","fbs","restecg","thalach",
    "exang","oldpeak","slope","ca","thal","num"
]

raw = pd.read_csv(
    data_path, header=None, names=columns, na_values=["?"], dtype=str
)

# Convert to numeric
for c in columns:
    raw[c] = pd.to_numeric(raw[c], errors="coerce")

# Drop rows with NaNs
df = raw.dropna().copy()

# Binary target: disease present if num > 0
df["target"] = (df["num"] > 0).astype(int)
df = df.drop(columns=["num"])

# Separate features and target
X = df.drop(columns=["target"]).values.astype(float)
y = df["target"].values.astype(int)

# Train/test split (70/30) 
rng = set_seed(seed)
idx = np.arange(len(X))
rng.shuffle(idx)
split = int(train_ratio * len(X))
train_idx, test_idx = idx[:split], idx[split:]

X_train, y_train = X[train_idx], y[train_idx]
X_test, y_test = X[test_idx], y[test_idx]

# Z-score normalization using TRAIN stats only
mu = X_train.mean(axis=0)
sd = X_train.std(axis=0, ddof=0)
sd = np.where(sd == 0, 1.0, sd)  

X_train_std = (X_train - mu) / sd
X_test_std = (X_test - mu) / sd

# Summaries before/after normalization
summary_before = pd.DataFrame({
    "feature": df.drop(columns=["target"]).columns,
    "mean_before": X.mean(axis=0),
    "std_before": X.std(axis=0, ddof=0)
})

summary_after = pd.DataFrame({
    "feature": df.drop(columns=["target"]).columns,
    "mean_train_after": X_train_std.mean(axis=0),
    "std_train_after": X_train_std.std(axis=0, ddof=0),
})

# Display summaries
# import caas_jupyter_tools
# caas_jupyter_tools.display_dataframe_to_user("Feature summary — before normalization", summary_before)
# caas_jupyter_tools.display_dataframe_to_user("Feature summary — after normalization (train stats)", summary_after)

# ------------------- PART II: LOGISTIC REGRESSION (from scratch) -------------------
n, d = X_train_std.shape
rng = set_seed(seed)

# Initialize small random weights and bias
W = rng.normal(0, 0.01, size=(d,))
b = rng.normal(0, 0.01)

best_loss = np.inf
best_W = W.copy()
best_b = b
stall = 0
loss_history = []

for epoch in range(1, epochs + 1):
    # forward
    z = X_train_std @ W + b
    p = sigmoid(z)
    loss = bce_loss(y_train, p)

    loss_history.append(loss)

    # gradients
    # dL/dz = p - y ; dL/dW = X.T @ (p - y) / n ; dL/db = mean(p - y)
    diff = (p - y_train)
    grad_W = (X_train_std.T @ diff) / n
    grad_b = diff.mean()

    # update
    W -= lr * grad_W
    b -= lr * grad_b

    # early stopping on training loss
    if loss + 1e-10 < best_loss:
        best_loss = loss
        best_W = W.copy()
        best_b = b
        stall = 0
    else:
        stall += 1
        if stall >= patience:
            break

# Use best weights
W = best_W
b = best_b

# Plot and save training loss
plt.figure()
plt.plot(np.arange(1, len(loss_history) + 1), loss_history)
plt.xlabel("Epoch")
plt.ylabel("Binary Cross-Entropy Loss")
plt.title("Training Loss")
loss_png = outdir / "training_loss.png"
plt.savefig(loss_png, bbox_inches="tight")
plt.close()

# Save learned parameters and standardized test data
weights_path = outdir / f"weights_{student_id}.npy"
bias_path = outdir / f"bias_{student_id}.npy"
Xtest_path = outdir / f"X_test_{student_id}.npy"
ytest_path = outdir / f"y_test_{student_id}.npy"
mu_path = outdir / f"mu_{student_id}.npy"
sd_path = outdir / f"sd_{student_id}.npy"
cols_path = outdir / f"feature_names_{student_id}.npy"

np.save(weights_path, W)
np.save(bias_path, b)
np.save(Xtest_path, X_test_std)
np.save(ytest_path, y_test)
np.save(mu_path, mu)
np.save(sd_path, sd)
np.save(cols_path, df.drop(columns=["target"]).columns.values)

# ------------------- PART III: EVALUATION @ threshold 0.8 (manual) -------------------
# Predicted probabilities for test set
probs_test = sigmoid(X_test_std @ W + b)

thr_manual = 0.80
tp, fp, fn, tn = confusion_counts(y_test, probs_test, thr_manual)
acc, prec, rec, spec, f1 = metrics_from_confusion(tp, fp, fn, tn)

manual_table = pd.DataFrame({
    "Count": [tp, fp, fn, tn],
    "Meaning": ["True Positive", "False Positive", "False Negative", "True Negative"]
}, index=["TP", "FP", "FN", "TN"])

metrics_manual = pd.DataFrame({
    "Metric": ["Accuracy", "Precision", "Recall (Sensitivity)", "Specificity", "F1-score"],
    "Value": [acc, prec, rec, spec, f1]
})

# caas_jupyter_tools.display_dataframe_to_user("Confusion matrix counts @ threshold 0.80", manual_table)
# caas_jupyter_tools.display_dataframe_to_user("Metrics @ threshold 0.80", metrics_manual)

# ------------------- PART III (continued): sweep thresholds -------------------
records = []
for thr in thresholds_coarse:
    tp, fp, fn, tn = confusion_counts(y_test, probs_test, thr)
    acc, prec, rec, spec, f1 = metrics_from_confusion(tp, fp, fn, tn)
    records.append({
        "threshold": thr, "TP": tp, "FP": fp, "FN": fn, "TN": tn,
        "accuracy": acc, "precision": prec, "recall": rec, "specificity": spec, "f1": f1
    })
metrics_table = pd.DataFrame.from_records(records)

# caas_jupyter_tools.display_dataframe_to_user("Metrics across thresholds (step 0.05)", metrics_table)

# ------------------- PART IV: ROC, PR, AUC, Youden J -------------------
# For ROC: TPR vs FPR at fine thresholds
roc_records = []
pr_records = []

for thr in thresholds_fine:
    tp, fp, fn, tn = confusion_counts(y_test, probs_test, thr)
    tpr = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    rec = tpr
    roc_records.append({"threshold": thr, "TPR": tpr, "FPR": fpr})
    pr_records.append({"threshold": thr, "Precision": prec, "Recall": rec})

roc_df = pd.DataFrame(roc_records).sort_values("FPR")
pr_df = pd.DataFrame(pr_records).sort_values("Recall")

# AUC with trapezoid rule
auc_roc = trapezoid_area(roc_df["FPR"].values, roc_df["TPR"].values)
auc_pr = trapezoid_area(pr_df["Recall"].values, pr_df["Precision"].values)

# Youden's J = Sensitivity + Specificity - 1
youden_records = []
for thr in thresholds_fine:
    tp, fp, fn, tn = confusion_counts(y_test, probs_test, thr)
    sens = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    spec = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    j = sens + spec - 1
    youden_records.append({"threshold": thr, "Sensitivity": sens, "Specificity": spec, "J": j})
youden_df = pd.DataFrame(youden_records)
j_best_row = youden_df.iloc[youden_df["J"].argmax()]
j_best_thr = float(j_best_row["threshold"])
j_best_val = float(j_best_row["J"])

# Plot ROC
plt.figure()
plt.plot(roc_df["FPR"].values, roc_df["TPR"].values, label=f"AUC={auc_roc:.3f}")
plt.plot([0,1], [0,1], linestyle="--")
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.title("ROC Curve")
roc_png = outdir / "roc_curve.png"
plt.savefig(roc_png, bbox_inches="tight")
plt.close()

# Plot PR
plt.figure()
plt.plot(pr_df["Recall"].values, pr_df["Precision"].values, label=f"AUC={auc_pr:.3f}")
plt.xlabel("Recall")
plt.ylabel("Precision")
plt.title("Precision–Recall Curve")
pr_png = outdir / "pr_curve.png"
plt.savefig(pr_png, bbox_inches="tight")
plt.close()

# ------------------- PART V: COST-SENSITIVE EVALUATION -------------------
cost_records = []
for thr in thresholds_fine:
    tp, fp, fn, tn = confusion_counts(y_test, probs_test, thr)
    total_cost = 50000 * fn + 2000 * fp
    cost_records.append({"threshold": thr, "FP": fp, "FN": fn, "TotalCost": total_cost})
cost_df = pd.DataFrame(cost_records)

# Plot total cost vs threshold
plt.figure()
plt.plot(cost_df["threshold"].values, cost_df["TotalCost"].values)
plt.xlabel("Threshold")
plt.ylabel("Total cost ($)")
plt.title("Total Cost vs Threshold (FN=$50k, FP=$2k)")
cost_png = outdir / "total_cost.png"
plt.savefig(cost_png, bbox_inches="tight")
plt.close()

min_cost_row = cost_df.loc[cost_df["TotalCost"].idxmin()]

# ------------------- PART VI: CLASS IMBALANCE SIMULATION -------------------
# Add 10 additional healthy individuals to the TEST SET (simulate)
extra_negatives = 10
if extra_negatives > 0:
    # Sample (with replacement) from observed negative class in X_test_std
    neg_mask = (y_test == 0)
    if neg_mask.sum() > 0:
        idx_neg = np.where(neg_mask)[0]
        # If not enough negatives exist, sample with replacement
        extra_idx = rng.choice(idx_neg, size=extra_negatives, replace=True)
        X_test_imb = np.vstack([X_test_std, X_test_std[extra_idx]])
        y_test_imb = np.concatenate([y_test, np.zeros(extra_negatives, dtype=int)])
    else:
        # If no negatives present, just append zeros of right dimensionality (rare case)
        X_test_imb = np.vstack([X_test_std, np.tile(X_test_std.mean(axis=0), (extra_negatives, 1))])
        y_test_imb = np.concatenate([y_test, np.zeros(extra_negatives, dtype=int)])
else:
    X_test_imb, y_test_imb = X_test_std.copy(), y_test.copy()

probs_test_imb = sigmoid(X_test_imb @ W + b)

# Recalculate metrics across thresholds
imb_records = []
for thr in thresholds_coarse:
    tp, fp, fn, tn = confusion_counts(y_test_imb, probs_test_imb, thr)
    acc, prec, rec, spec, f1 = metrics_from_confusion(tp, fp, fn, tn)
    imb_records.append({
        "threshold": thr, "TP": tp, "FP": fp, "FN": fn, "TN": tn,
        "accuracy": acc, "precision": prec, "recall": rec, "specificity": spec, "f1": f1
    })
metrics_table_imb = pd.DataFrame.from_records(imb_records)

# Save all key tables to CSV for your report
summary_before.to_csv(outdir / "summary_before.csv", index=False)
summary_after.to_csv(outdir / "summary_after.csv", index=False)
metrics_table.to_csv(outdir / "metrics_by_threshold.csv", index=False)
metrics_table_imb.to_csv(outdir / "metrics_by_threshold_imbalanced.csv", index=False)
roc_df.to_csv(outdir / "roc_points.csv", index=False)
pr_df.to_csv(outdir / "pr_points.csv", index=False)
youden_df.to_csv(outdir / "youden_j.csv", index=False)
cost_df.to_csv(outdir / "cost_by_threshold.csv", index=False)

# Bundle a quick text summary
summary_text = f"""
CMPE 49T HW3 — Auto Summary
===========================

Student ID: {student_id}
Seed used: {seed}

Training examples: {len(X_train_std)}, Test examples: {len(X_test_std)}

Best (lowest) training loss: {best_loss:.6f}
AUC-ROC: {auc_roc:.4f}
AUC-PR: {auc_pr:.4f}

Youden's J best threshold: {j_best_thr:.2f} (J={j_best_val:.4f})

Cost-minimizing threshold (FN=$50k, FP=$2k): {float(min_cost_row['threshold']):.2f}
Minimum expected cost: ${int(min_cost_row['TotalCost'])}

Saved Files:
- {loss_png.name}
- {roc_png.name}
- {pr_png.name}
- {cost_png.name}
- {weights_path.name}, {bias_path.name}, {Xtest_path.name}, {ytest_path.name}
- summary_before.csv, summary_after.csv
- metrics_by_threshold.csv, metrics_by_threshold_imbalanced.csv
- roc_points.csv, pr_points.csv, youden_j.csv, cost_by_threshold.csv
""".strip()

with open(outdir / "SUMMARY.txt", "w") as f:
    f.write(summary_text)

summary_text
