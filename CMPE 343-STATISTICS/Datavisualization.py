import pandas as pd
import matplotlib.pyplot as plt

# Load the datasets
detection_data_path = 'detection_data.csv'  # Replace with the path to detection_data.csv
detection_data_extra_path = 'detection_data_extra.csv'  # Replace with the path to detection_data_extra.csv

# Read the CSV files into DataFrames
data_original = pd.read_csv(detection_data_path)
data_extra = pd.read_csv(detection_data_extra_path)

# Compute basic statistics for comparison
print("Original Dataset Statistics:")
print(data_original.describe())
print("\nExtra Dataset Statistics:")
print(data_extra.describe())

# Class balance comparison
class_balance_original = data_original['Detection'].value_counts(normalize=True)
class_balance_extra = data_extra['Detection'].value_counts(normalize=True)

print("\nClass Balance - Original Dataset:")
print(class_balance_original)
print("\nClass Balance - Extra Dataset:")
print(class_balance_extra)

# Histograms for Distance
plt.figure(figsize=(10, 6))
plt.hist(data_original['Distance'], bins=20, alpha=0.7, label='Original Data', color='blue', density=True)
plt.hist(data_extra['Distance'], bins=20, alpha=0.7, label='Extra Data', color='orange', density=True)
plt.title('Comparison of Distance Distributions')
plt.xlabel('Distance')
plt.ylabel('Density')
plt.legend()
plt.grid()
plt.show()

# Histograms for Amplitude
plt.figure(figsize=(10, 6))
plt.hist(data_original['Amplitude'], bins=20, alpha=0.7, label='Original Data', color='blue', density=True)
plt.hist(data_extra['Amplitude'], bins=20, alpha=0.7, label='Extra Data', color='orange', density=True)
plt.title('Comparison of Amplitude Distributions')
plt.xlabel('Amplitude')
plt.ylabel('Density')
plt.legend()
plt.grid()
plt.show()

# Boxplots for Distance
plt.figure(figsize=(10, 6))
plt.boxplot(
    [data_original['Distance'], data_extra['Distance']],
    labels=['Original Data', 'Extra Data'],
    patch_artist=True,
    boxprops=dict(facecolor='blue', alpha=0.5),
    medianprops=dict(color='black')
)
plt.title('Boxplot of Distance')
plt.ylabel('Distance')
plt.grid()
plt.show()

# Boxplots for Amplitude
plt.figure(figsize=(10, 6))
plt.boxplot(
    [data_original['Amplitude'], data_extra['Amplitude']],
    labels=['Original Data', 'Extra Data'],
    patch_artist=True,
    boxprops=dict(facecolor='orange', alpha=0.5),
    medianprops=dict(color='black')
)
plt.title('Boxplot of Amplitude')
plt.ylabel('Amplitude')
plt.grid()
plt.show()
