# HW2 Logistic Regression - Changes Summary

## All Requested Changes Implemented ✓

### 1. **Learning Rate (η) Updated to 0.1** ✓
- **Changed:** Default `eta` parameter in `train_logreg_elastic_net()` function
- **Before:** `eta=0.05`
- **After:** `eta=0.1`
- **Line:** Function definition at line ~75

### 2. **Convergence Plots Saved (Loss vs. Iteration)** ✓
- **Location:** Inside the main lambda loop (lines 254-264)
- **Output:** `convergence_lambda_{lam}.png` for each λ value
- **Features:**
  - Plots both training and validation loss
  - Includes xlabel, ylabel, title, legend, and grid
  - Saved at 150 DPI

### 3. **Learned Parameters CSV Saved** ✓
- **File:** `learned_weights.csv`
- **Contents:** One row per λ containing `[lambda, w1..w9, b]`
- **Location:** Lines 277-282
- **Format:** Comma-separated with header row

### 4. **Sparsity Reporting (L1) Made Consistent** ✓
- **Method Used:** **Proximal Gradient with L1 Soft-Thresholding** (preferred approach)
- **Implementation:** Lines 114-115 in training loop
  ```python
  threshold = eta * lmbda * alpha
  w = np.sign(w) * np.maximum(np.abs(w) - threshold, 0.0)
  ```
- **Advantage:** Induces **exact zeros** in weights for true L1 sparsity
- **Reporting:** Post-hoc thresholding at 1e-4 for consistency (line 290)
- **Documentation:** Clear note in final output

### 5. **Clearer Comments & Docstrings** ✓
- **Function docstrings added for:**
  - `sigmoid()` - Numerically stable sigmoid function
  - `expand_features()` - 9D polynomial feature map description
  - `standardize_train_test()` - Standardization with guard against zero-std
  - `compute_loss_and_grad_without_l1()` - CE loss + L2 (for gradient step)
  - `compute_full_loss()` - Full Elastic Net loss formula
  - `accuracy_from_probs()` - Classification accuracy computation
  - `train_logreg_elastic_net()` - Full training procedure with proximal step details

- **Inline comments at key steps:**
  - Fixed seed for reproducibility (line 220)
  - Elastic Net formula documented (lines 42-43, 49)
  - Proximal step explanation (line 114-115)
  - Early stopping on validation loss (line 126-131)

### 6. **Early Stopping on Validation Loss** ✓
- **Location:** Lines 126-131 in training loop
- **Features:**
  - Patience parameter set to 50 iterations
  - Tracks improvement threshold of 1e-8
  - Maintains max-iter cap (3000)
  - Still respects convergence tolerance (tol=1e-6)

### 7. **Feature Rankings per λ Saved** ✓
- **Files:** `feature_ranking_lambda_{lam}.csv` for each λ value
- **Location:** Lines 266-272
- **Columns:** `[rank, feature, feature_index, abs_weight, weight]`
- **Contents:** Features sorted by |w| in descending order
- **Saved for:** Each of the 5 λ values (0.01, 0.1, 1.0, 10.0, 50.0)

## Summary of Output Files

The script now generates:

1. **hw2_summary.csv** - Summary statistics per λ
2. **hw2_predictions.csv** - Predictions on unseen points
3. **learned_weights.csv** - All learned weights and bias per λ
4. **convergence_lambda_{lam}.png** - 5 convergence plots (one per λ)
5. **feature_ranking_lambda_{lam}.csv** - 5 feature ranking files (one per λ)

## Key Implementation Details

### Sparsity Method: Proximal Gradient Descent
- **Why proximal gradient?** Induces true L1 sparsity (exact zeros)
- **Step 1:** Gradient step on CE + L2 loss
- **Step 2:** Soft-thresholding: $w := \text{sign}(w) \times \max(|w| - \eta\lambda\alpha, 0)$
- **Step 3:** No threshold on bias (L1 not applied to bias)

### Loss Function Decomposition
- `compute_loss_and_grad_without_l1()`: Used during gradient computation (no L1)
- `compute_full_loss()`: Used for reporting and early stopping (full penalty)
- Reason: Proximal step adds L1 separately, so gradient step excludes L1

### Early Stopping Strategy
- Monitors validation loss with patience=50
- Stops if no improvement > 1e-8 for 50 consecutive iterations
- Preserves max_iter=3000 hard cap
- Works alongside convergence tolerance (tol=1e-6)

## Version Information
- **Learning rate:** η = 0.1 (per spec)
- **Hyperparameters:** alpha=0.5, max_iter=3000, seed=42, patience=50
- **Sparsity method:** Proximal gradient with L1 soft-thresholding
- **Feature expansion:** 9-dimensional polynomial features
