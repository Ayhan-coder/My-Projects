import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math
def calculate_probability(x, mean, std_dev):
    """
    This method calculates the probability of "x" for a given mean and standard deviation using
    the Gaussian probability density function.
    Also, computes the likelihood of a given data point, assuming
    the data follows a normal distribution characterized by its mean and standard
    deviation.
    :param x: The data point for which the probability is to be calculated.
    :type x: float
    :param mean: The mean of the normal distribution.
    :type mean: float
    :param std_dev: The standard deviation of the normal distribution.
    :type std_dev: float
    :return: The probability value calculated using the Gaussian distribution.
    :rtype: float
    """
    exponent = np.exp(-0.5 * ((x-mean) /std_dev) ** 2)
    probability = (1 / (std_dev * np.sqrt(2 * np.pi))) * exponent
    return probability
def calculate_joint_probability(amplitude, distance, mean_amp, std_dev_amp, mean_dist, std_dev_dist):
    """
    This method calculates the joint probability of two independent events, amplitude and
    distance, based on their respective means and standard deviations. The joint
    probability is determined by combining the individual probabilities calculated
    for amplitude and distance using the normal distribution.
    """
    prob_amp = calculate_probability(amplitude, mean_amp, std_dev_amp)
    prob_dist = calculate_probability(distance, mean_dist, std_dev_dist)
    return prob_amp * prob_dist
# Main of the code
if __name__ == "__main__":
    # Load the dataset using pandas
    file_path = input("Please enter the data file: ")
    #file_path = 'detection_data.csv'
    #file_path =  'detection_data_extra.csv'
    try:
        data = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        exit()

    # Split data into detection and non-detection cases
    detect_data = data[data['Detection'] == 'Detect']
    no_detect_data = data[data['Detection'] == 'No Detect']

    # Calculate means and standard deviations for detection cases
    mean_detect_distance = detect_data['Distance'].mean()
    mean_detect_amplitude = detect_data['Amplitude'].mean()
    std_dev_detect_distance = detect_data['Distance'].std()
    std_dev_detect_amplitude = detect_data['Amplitude'].std()

    # Calculate means and standard deviations for non-detection cases
    mean_no_detect_distance = no_detect_data['Distance'].mean()
    mean_no_detect_amplitude = no_detect_data['Amplitude'].mean()
    std_dev_no_detect_distance = no_detect_data['Distance'].std()
    std_dev_no_detect_amplitude = no_detect_data['Amplitude'].std()

    # Print the calculated means and standard deviations
    print("Mean and Standard Deviation for Detection Cases:")
    print(f"Distance Mean: {mean_detect_distance}, Std Dev: {std_dev_detect_distance}")
    print(f"Amplitude Mean: {mean_detect_amplitude}, Std Dev: {std_dev_detect_amplitude}")
    print("\nMean and Standard Deviation for No Detection Cases:")
    print(f"Distance Mean: {mean_no_detect_distance}, Std Dev: {std_dev_no_detect_distance}")
    print(f"Amplitude Mean: {mean_no_detect_amplitude}, Std Dev: {std_dev_no_detect_amplitude}")

    # Evaluate prediction accuracy
    correct_predictions = 0
    total_samples = len(data)

    for _, row in data.iterrows():
        amplitude = row['Amplitude']
        distance = row['Distance']

        # Calculate probabilities
        prob_detect = calculate_joint_probability(
            amplitude, distance, mean_detect_amplitude, std_dev_detect_amplitude,
            mean_detect_distance, std_dev_detect_distance
        )
        prob_no_detect = calculate_joint_probability(
            amplitude, distance, mean_no_detect_amplitude, std_dev_no_detect_amplitude,
            mean_no_detect_distance, std_dev_no_detect_distance
        )

        # Normalize probabilities
        total_prob = prob_detect + prob_no_detect
        prob_detect_normalized = prob_detect / total_prob
        prob_no_detect_normalized = prob_no_detect / total_prob

        # Make a prediction
        predicted_detection = 'Detect' if prob_detect_normalized > prob_no_detect_normalized else 'No Detect'

        # Compare with actual detection
        if predicted_detection == row['Detection']:
            correct_predictions +=1

    # Calculate and print the accuracy
    accuracy = (correct_predictions /total_samples) *100
    print(f"Correct Predictions: {correct_predictions} / {total_samples}")
    print(f"\nPrediction Accuracy: {accuracy:.2f}%")

    # Visualize data distributions
    plt.figure(figsize=(10, 6))
    plt.hist(detect_data['Distance'], bins=20, alpha=0.7, label='Detect - Distance', color='blue', density=True)
    plt.hist(no_detect_data['Distance'], bins=20, alpha=0.7, label='No Detect - Distance', color='red', density=True)
    plt.title('Distance Distribution')
    plt.xlabel('Distance')
    plt.ylabel('Density')
    plt.legend()
    plt.grid()
    plt.show()
    plt.figure(figsize=(10, 6))
    plt.hist(detect_data['Amplitude'], bins= 20, alpha=0.7, label='Detect - Amplitude', color='purple', density=True)
    plt.hist(no_detect_data['Amplitude'], bins= 20, alpha=0.7, label='No Detect - Amplitude', color='cyan', density=True)
    plt.title('Amplitude Distribution')
    plt.xlabel('Amplitude')
    plt.ylabel('Density')
    plt.legend()
    plt.grid()
    plt.show()
