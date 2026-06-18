# Pneumonia Detection using a Neural Network from Scratch
## CMPE 49T: Fall 25 - Homework 4

This project implements a complete pipeline for binary classification of chest X-ray images to detect pneumonia using a custom-built neural network implemented in NumPy.

### Files
- `pneumonia_detection.ipynb`: The Jupyter Notebook containing all the code, from data loading to evaluation.
- `main.py`: The main Python script to run the pipeline.
- `data_utils.py`: Helper functions for data loading and processing.
- `neural_net.py`: The neural network implementation and helper functions.
- `visualization.py`: Functions for plotting and visualization.
- `chatgpt_data_normalized/`: Directory where normalized data is saved (created by the notebook).
- `pneumoniamnist.npz`: The dataset file (downloaded by the notebook).

### Instructions
1. Open `pneumonia_detection.ipynb` in VS Code or Jupyter Notebook.
2. Run all cells sequentially.
   - The notebook will automatically download the `pneumoniamnist.npz` dataset.
   - It will preprocess the data, train the model, and display evaluation metrics and plots.
3. Alternatively, you can run the Python script:
   ```bash
   python main.py [--show-plots] [--save-plots]
   ```
   - `--show-plots` displays the evaluation figures.
   - `--save-plots` writes the loss/metrics/confusion/ROC plots to the `plots/` directory.
4. To generate the PDF report, you can export the notebook as PDF or copy the relevant outputs and explanations into a document.

### Requirements
- Python 3
- NumPy
- Matplotlib
- tqdm
- scikit-learn

### Architecture
The network consists of:
1. **Conv Layer 1**: 3x3 Emboss kernel (Fixed)
2. **Max Pooling 1**: 2x2
3. **Conv Layer 2**: 3x3 Sobel kernel (Fixed)
4. **Max Pooling 2**: 2x2
5. **Flatten Layer**
6. **Dense Layer**: 16 units, ReLU activation
7. **Dropout**: Rate = 0.5
8. **Output Layer**: 1 unit, Sigmoid activation

The model is trained using Stochastic Gradient Descent (SGD) with Weighted Binary Cross-Entropy loss.
