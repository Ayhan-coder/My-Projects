import numpy as np
from tqdm import tqdm

def convolve2d(image, kernel):
    # get image and kernel sizes
    H, W = image.shape
    kH, kW = kernel.shape
    # figure out output size (shrinks because no padding)
    out_H = H - kH + 1
    out_W = W - kW + 1
    
    output = np.zeros((out_H, out_W))
    # slide kernel across image and multiply
    for i in range(out_H):
        for j in range(out_W):
            output[i, j] = np.sum(image[i:i+kH, j:j+kW] * kernel)
    return output

def max_pooling2d(img, pool_size=2, stride=2):
    # this reduces image size by taking max value in each pool
    h, w = img.shape
    out_h = h // pool_size
    out_w = w // pool_size
    output = np.zeros((out_h, out_w))
    
    # go through each pool region
    for i in range(out_h):
        for j in range(out_w):
            hs = i * stride
            ws = j * stride
            # pick the biggest value in this pool
            output[i, j] = np.max(img[hs:hs+pool_size, ws:ws+pool_size])
    return output

# using emboss filter to detect edges and texture
emboss_kernel = np.array([[-2, -1, 0],
                          [-1, 1, 1],
                          [0, 1, 2]])

# sobel filter finds vertical edges in images
sobel_kernel = np.array([[-1, 0, 1],
                         [-2, 0, 2],
                         [-1, 0, 1]])

def relu(x):
    # simple activation - anything negative becomes zero
    return np.maximum(0, x)

def relu_derivative(x):
    # gradient is 1 where x positive, 0 otherwise
    return (x > 0).astype(float)

def sigmoid(x):
    # squash values between 0 and 1 for probability
    # clipping to avoid overflow issues
    return 1 / (1 + np.exp(-np.clip(x, -500, 500)))

def sigmoid_derivative(x):
    s = sigmoid(x)
    return s * (1 - s)

def weighted_bce_loss(y_true, y_pred, w0, w1):
    # binary cross entropy but with class weights to handle imbalance
    eps = 1e-15
    y_pred = np.clip(y_pred, eps, 1 - eps)  # don't let it hit exactly 0 or 1
    loss = -(w1 * y_true * np.log(y_pred) + w0 * (1 - y_true) * np.log(1 - y_pred))
    return np.mean(loss)

class SimpleCNN:
    def __init__(self, input_shape=(28, 28)):
        # after running conv and pool twice the size shrinks
        # 28->26->13->11->5, so we get 5*5=25 features per image
        self.flatten_size = 25
        self.hidden_units = 16
        self.output_units = 1
        
        # initialize weights randomly (He initialization works better for ReLU)
        self.W1 = np.random.randn(self.flatten_size, self.hidden_units) * np.sqrt(2.0 / self.flatten_size)
        self.b1 = np.zeros((1, self.hidden_units))
        
        # output layer uses Xavier init (better for sigmoid)
        self.W2 = np.random.randn(self.hidden_units, self.output_units) * np.sqrt(1.0 / self.hidden_units)
        self.b2 = np.zeros((1, self.output_units))
        
        # dropout helps prevent overfitting
        self.dropout_rate = 0.5
        
    def extract_features(self, X, show_progress=False, desc=None):
        # run each image through convolution and pooling to extract features
        features = []
        loop = tqdm(range(X.shape[0]), desc=desc) if show_progress else range(X.shape[0])
        for i in loop:
            img = X[i]
            # first conv layer with emboss filter
            c1 = convolve2d(img, emboss_kernel)
            p1 = max_pooling2d(c1)  # make it smaller
            # second conv layer with sobel filter
            c2 = convolve2d(p1, sobel_kernel)
            p2 = max_pooling2d(c2)  # make it smaller again
            # flatten to 1D vector for dense layers
            features.append(p2.flatten())
        return np.array(features)

    def train_step(self, features, y, lr, w0, w1):
        N = features.shape[0]
        
        # forward pass through network
        z3 = np.dot(features, self.W1) + self.b1
        a3 = relu(z3)  # activation for hidden layer
        
        # randomly drop some neurons to prevent overfitting
        mask = (np.random.rand(*a3.shape) > self.dropout_rate) / (1.0 - self.dropout_rate)
        a3_drop = a3 * mask
        
        # output layer
        z4 = np.dot(a3_drop, self.W2) + self.b2
        a4 = sigmoid(z4)  # get probability
        
        # calculate loss with class weights
        loss = weighted_bce_loss(y, a4, w0, w1)
        
        # now calculate gradients (backpropagation)
        delta_out = a4 * (w1 * y + w0 * (1 - y)) - w1 * y
        
        # gradients for output layer
        dW2 = np.dot(a3_drop.T, delta_out) / N
        db2 = np.sum(delta_out, axis=0, keepdims=True) / N
        
        # propagate error back to hidden layer
        delta_h = np.dot(delta_out, self.W2.T) * mask * relu_derivative(z3)
        
        # gradients for hidden layer
        dW1 = np.dot(features.T, delta_h) / N
        db1 = np.sum(delta_h, axis=0, keepdims=True) / N
        
        # update weights using gradient descent
        self.W1 -= lr * dW1
        self.b1 -= lr * db1
        self.W2 -= lr * dW2
        self.b2 -= lr * db2
        
        return loss

    def predict(self, features):
        # just forward pass, no dropout during inference
        z3 = np.dot(features, self.W1) + self.b1
        a3 = relu(z3)
        z4 = np.dot(a3, self.W2) + self.b2
        return sigmoid(z4)  # returns probability of pneumonia
