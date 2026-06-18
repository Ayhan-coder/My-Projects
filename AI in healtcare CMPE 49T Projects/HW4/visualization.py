import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import confusion_matrix, roc_curve

def visualize_samples(images, labels, class_names=['Normal', 'Pneumonia'], num_samples=5, save_path=None, show=True):
    # show some example images from each class
    fig = plt.figure(figsize=(10, 4))
    for i in range(len(class_names)):
        # find all images of this class
        idx = np.where(labels == i)[0]
        # pick random samples
        samples = np.random.choice(idx, num_samples, replace=False)
        
        # plot them in a grid
        for j, s in enumerate(samples):
            plt.subplot(len(class_names), num_samples, i * num_samples + j + 1)
            plt.imshow(images[s], cmap='gray')
            plt.title(class_names[i])
            plt.axis('off')
    plt.tight_layout()
    if save_path:
        fig.savefig(save_path)
    if show:
        plt.show()
    else:
        plt.close(fig)

def plot_histograms(images, labels, class_names=['Normal', 'Pneumonia'], save_path=None, show=True):
    # plot pixel intensity distributions for each class
    # helps see if there's visual difference between normal and pneumonia
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    colors = ['blue', 'red']
    for i in range(len(class_names)):
        idx = np.where(labels == i)[0]
        # flatten all images and plot histogram
        axes[i].hist(images[idx].ravel(), bins=50, color=colors[i], alpha=0.7)
        axes[i].set_title(f'Pixel Intensity Histogram - {class_names[i]}')
        axes[i].set_xlabel('Pixel Intensity')
        axes[i].set_ylabel('Frequency')
    plt.tight_layout()
    if save_path:
        fig.savefig(save_path)
    if show:
        plt.show()
    else:
        plt.close(fig)

def plot_loss(train_losses, val_losses, save_path=None, show=True):
    plt.figure(figsize=(10, 5))
    plt.plot(train_losses, label='Train Loss')
    plt.plot(val_losses, label='Validation Loss')
    plt.title('Training and Validation Loss')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.legend()
    if save_path:
        plt.savefig(save_path)
    if show:
        plt.show()
    else:
        plt.close()

def plot_metrics(val_acc, val_prec, val_rec, val_f1, save_path=None, show=True):
    plt.figure(figsize=(10, 5))
    plt.plot(val_acc, label='Accuracy')
    plt.plot(val_prec, label='Precision')
    plt.plot(val_rec, label='Recall')
    plt.plot(val_f1, label='F1 Score')
    plt.title('Validation Metrics over Epochs')
    plt.xlabel('Epochs')
    plt.ylabel('Score')
    plt.legend()
    if save_path:
        plt.savefig(save_path)
    if show:
        plt.show()
    else:
        plt.close()

def plot_confusion_matrix(y_true, y_pred_binary, class_names=['Normal', 'Pneumonia'], save_path=None, show=True):
    cm = confusion_matrix(y_true, y_pred_binary)
    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
    ax.set_title('Confusion Matrix')
    fig.colorbar(im, ax=ax)
    ticks = np.arange(len(class_names))
    ax.set_xticks(ticks)
    ax.set_yticks(ticks)
    ax.set_xticklabels(class_names)
    ax.set_yticklabels(class_names)
    ax.set_xlabel('Predicted Label')
    ax.set_ylabel('True Label')
    
    thresh = cm.max() / 2.0
    for i, j in np.ndindex(cm.shape):
        ax.text(j, i, format(cm[i, j], 'd'), ha="center",
                color="white" if cm[i, j] > thresh else "black")
    if save_path:
        fig.savefig(save_path)
    if show:
        plt.show()
    else:
        plt.close(fig)

def plot_roc_curve(y_true, y_pred_prob, auc_score, save_path=None, show=True):
    fpr, tpr, _ = roc_curve(y_true, y_pred_prob)
    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (area = {auc_score:.2f})')
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver Operating Characteristic (ROC)')
    plt.legend(loc="lower right")
    if save_path:
        plt.savefig(save_path)
    if show:
        plt.show()
    else:
        plt.close()
