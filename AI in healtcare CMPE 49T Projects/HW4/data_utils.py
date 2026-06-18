import numpy as np
import os
import urllib.request

def download_data(url, filename):
    if not os.path.exists(filename):
        print(f"Downloading {filename}...")
        urllib.request.urlretrieve(url, filename)
        print("Download complete.")
    else:
        print(f"{filename} already exists.")

def load_data(filename):
    # load the npz file with all the data
    data = np.load(filename)
    train_imgs = data['train_images']
    train_lbls = data['train_labels']
    val_imgs = data['val_images']
    val_lbls = data['val_labels']
    test_imgs = data['test_images']
    test_lbls = data['test_labels']
    
    # images might have extra channel dimension, remove it
    if train_imgs.ndim == 4:
        train_imgs = train_imgs[..., 0]
        val_imgs = val_imgs[..., 0]
        test_imgs = test_imgs[..., 0]

    return train_imgs, train_lbls, val_imgs, val_lbls, test_imgs, test_lbls

def normalize_data(images):
    # convert pixel values from 0-255 to 0-1 range
    return images.astype('float32') / 255.0

def save_normalized_data(save_dir, train_images, train_labels, val_images, val_labels, test_images, test_labels):
    # save all the normalized arrays to disk
    os.makedirs(save_dir, exist_ok=True)
    np.save(os.path.join(save_dir, "train_images.npy"), train_images)
    np.save(os.path.join(save_dir, "train_labels.npy"), train_labels)
    np.save(os.path.join(save_dir, "val_images.npy"), val_images)
    np.save(os.path.join(save_dir, "val_labels.npy"), val_labels)
    np.save(os.path.join(save_dir, "test_images.npy"), test_images)
    np.save(os.path.join(save_dir, "test_labels.npy"), test_labels)
    print(f"Normalized data saved to {save_dir}/")

def report_distribution(labels, set_name):
    # check how many samples we have for each class
    unique, counts = np.unique(labels, return_counts=True)
    dist = dict(zip(unique, counts))
    print(f"{set_name} Distribution: {dist}")
    return dist

def calculate_class_weights(train_labels):
    # calculate weights to balance the classes during training
    # gives more weight to underrepresented class
    unique, counts = np.unique(train_labels, return_counts=True)
    total = len(train_labels)
    n_classes = len(unique)
    weights = {}
    for cls, cnt in zip(unique, counts):
        weights[cls] = total / (n_classes * cnt)
    return weights
