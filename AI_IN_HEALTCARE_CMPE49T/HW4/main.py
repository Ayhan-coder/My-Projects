import argparse
import os
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix

import data_utils
import neural_net

np.random.seed(42)

DATA_URL = "https://zenodo.org/record/10519652/files/pneumoniamnist.npz?download=1"
DATA_FILE = "pneumoniamnist.npz"
SAVE_DIR = "chatgpt_data_normalized"

def main(show_plots=False, save_plots=False):
    print("--- Data Preparation ---")
    # if not showing plots, use non-interactive backend
    if not show_plots:
        os.environ.setdefault("MPLBACKEND", "Agg")
    import visualization
    
    # download dataset if needed
    data_utils.download_data(DATA_URL, DATA_FILE)
    train_images, train_labels, val_images, val_labels, test_images, test_labels = data_utils.load_data(DATA_FILE)

    # see how many samples in each class
    data_utils.report_distribution(train_labels, "Train")
    data_utils.report_distribution(val_labels, "Validation")
    data_utils.report_distribution(test_labels, "Test")
    print(f"Train images shape: {train_images.shape}")
    
    # normalize to 0-1 range
    train_norm = data_utils.normalize_data(train_images)
    val_norm = data_utils.normalize_data(val_images)
    test_norm = data_utils.normalize_data(test_images)
    
    # save normalized data as requested in assignment
    data_utils.save_normalized_data(SAVE_DIR, train_norm, train_labels, val_norm, val_labels, test_norm, test_labels)
    
    # generate some visualizations
    plots_dir = "plots"
    if save_plots:
        os.makedirs(plots_dir, exist_ok=True)
    if show_plots or save_plots:
        sp = os.path.join(plots_dir, "sample_images.png") if save_plots else None
        hp = os.path.join(plots_dir, "pixel_histograms.png") if save_plots else None
        visualization.visualize_samples(train_images, train_labels, save_path=sp, show=show_plots)
        visualization.plot_histograms(train_norm, train_labels, save_path=hp, show=show_plots)
    
    # calculate class weights to handle imbalanced data
    class_weights = data_utils.calculate_class_weights(train_labels)
    print("Class Weights:", class_weights)
    w0, w1 = class_weights[0], class_weights[1]
    
    print("\n--- Feature Extraction ---")
    # create model and extract features using conv layers
    model = neural_net.SimpleCNN()
    
    X_train = model.extract_features(train_norm, show_progress=True, desc="training set")
    X_val = model.extract_features(val_norm, show_progress=True, desc="validation set")
    X_test = model.extract_features(test_norm, show_progress=True, desc="test set")
    
    print(f"Features shape: {X_train.shape}")
    
    print("\n--- Training ---")
    # training hyperparameters
    epochs = 50
    lr = 0.01  # learning rate
    batch_size = 32
    patience = 5  # for early stopping
    
    # track metrics during training
    train_losses, val_losses = [], []
    val_acc, val_prec, val_rec, val_f1 = [], [], [], []
    
    # for early stopping - save best model
    best_loss = float('inf')
    patience_cnt = 0
    best_weights = {}
    
    for epoch in range(epochs):
        # shuffle data each epoch
        idx = np.arange(X_train.shape[0])
        np.random.shuffle(idx)
        X_shuffled = X_train[idx]
        y_shuffled = train_labels[idx]
        
        epoch_loss = 0
        num_batches = 0
        
        # train in mini batches
        for i in range(0, X_train.shape[0], batch_size):
            X_batch = X_shuffled[i:i+batch_size]
            y_batch = y_shuffled[i:i+batch_size]
            
            # one training step
            loss = model.train_step(X_batch, y_batch, lr, w0, w1)
            epoch_loss += loss
            num_batches += 1
        
        avg_loss = epoch_loss / num_batches
        train_losses.append(avg_loss)
        
        val_preds = model.predict(X_val)
        vloss = neural_net.weighted_bce_loss(val_labels, val_preds, w0, w1)
        val_losses.append(vloss)
        
        val_pred_bin = (val_preds > 0.5).astype(int)
        vacc = accuracy_score(val_labels, val_pred_bin)
        vprec = precision_score(val_labels, val_pred_bin, zero_division=0)
        vrec = recall_score(val_labels, val_pred_bin, zero_division=0)
        vf1 = f1_score(val_labels, val_pred_bin, zero_division=0)
        
        val_acc.append(vacc)
        val_prec.append(vprec)
        val_rec.append(vrec)
        val_f1.append(vf1)
        
        print(f"Epoch {epoch+1}/{epochs} - Train Loss: {avg_loss:.4f} - Val Loss: {vloss:.4f} - Val Acc: {vacc:.4f}")
        
        if vloss < best_loss:
            best_loss = vloss
            patience_cnt = 0
            best_weights = {
                'W1': model.W1.copy(),
                'b1': model.b1.copy(),
                'W2': model.W2.copy(),
                'b2': model.b2.copy()
            }
        else:
            patience_cnt += 1
            if patience_cnt >= patience:
                print("Early stopping triggered.")
                break
    
    # Restore best weights
    if best_weights:
        model.W1 = best_weights['W1']
        model.b1 = best_weights['b1']
        model.W2 = best_weights['W2']
        model.b2 = best_weights['b2']
    
    print("Training complete.")
    
    # 4. Evaluation
    print("\n--- Evaluation ---")
    if show_plots or save_plots:
        lp = os.path.join(plots_dir, "training_loss.png") if save_plots else None
        mp = os.path.join(plots_dir, "validation_metrics.png") if save_plots else None
        cp = os.path.join(plots_dir, "confusion_matrix.png") if save_plots else None
        rp = os.path.join(plots_dir, "roc_curve.png") if save_plots else None
        visualization.plot_loss(train_losses, val_losses, save_path=lp, show=show_plots)
        visualization.plot_metrics(val_acc, val_prec, val_rec, val_f1, save_path=mp, show=show_plots)
    
    test_pred = model.predict(X_test)
    test_pred_bin = (test_pred > 0.5).astype(int)
    
    tacc = accuracy_score(test_labels, test_pred_bin)
    tprec = precision_score(test_labels, test_pred_bin, zero_division=0)
    trec = recall_score(test_labels, test_pred_bin, zero_division=0)
    tf1 = f1_score(test_labels, test_pred_bin)
    tauc = roc_auc_score(test_labels, test_pred)
    
    tn, fp, fn, tp = confusion_matrix(test_labels, test_pred_bin).ravel()
    spec = tn / (tn + fp)
    
    print(f"Test Accuracy: {tacc:.4f}")
    print(f"Test Precision: {tprec:.4f}")
    print(f"Test Recall: {trec:.4f}")
    print(f"Test F1 Score: {tf1:.4f}")
    print(f"Test AUC: {tauc:.4f}")
    print(f"Test Specificity: {spec:.4f}")
    
    if show_plots or save_plots:
        visualization.plot_confusion_matrix(test_labels, test_pred_bin, save_path=cp, show=show_plots)
        visualization.plot_roc_curve(test_labels, test_pred, tauc, save_path=rp, show=show_plots)

def parse_args():
    parser = argparse.ArgumentParser(description="Run the PneumoniaMNIST NumPy pipeline")
    parser.add_argument("--show-plots", action="store_true", help="Display the visualization windows during evaluation")
    parser.add_argument("--save-plots", action="store_true", help="Save the generated plots under the plots/ directory")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    main(args.show_plots, args.save_plots)
