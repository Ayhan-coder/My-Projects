import random
import math
# Step 1: Define the mean vector and covariance matrix
mean_vector = [20, 0.3, 0.8]
cov_matrix = [
    [4, 0.5, 0.2],
    [0.5, 0.7, 0.2],
    [0.2, 0.2, 0.1]
]
# Function to generate correlated random variables
def generate_correlated_samples(mean_vector, cov_matrix, n_samples):
    samples = []
    # Cholesky decomposition to get lower triangular matrix
    L = cholesky_decomposition(cov_matrix)
    for _ in range(n_samples):
        # Generate independent standard normal random variables
        z = [random.gauss(0, 1) for _ in range(len(mean_vector))]

        # Create correlated variables
        x = [mean_vector[i] + sum(L[i][j] * z[j] for j in range(len(z))) for i in range(len(mean_vector))]
        samples.append(x)
    return samples
# Function for Cholesky decomposition of a positive-definite matrix
def cholesky_decomposition(matrix):
    n = len(matrix)
    L = [[0.0]*n for _ in range(n)]
    for i in range(n):
        for j in range(i+1):
            sum_temp = sum(L[i][k]*L[j][k] for k in range(j))
            if i == j:
                L[i][j] = math.sqrt(matrix[i][i] - sum_temp)
            else:
                L[i][j] = (1.0 / L[j][j] * (matrix[i][j] - sum_temp))
    return L
# Step 2: Define the failure function g(x)
def failure_function(x):
    temp, load, cooling_eff = x
    return 0.1 * temp ** 2 + 12.5 * load ** 2 - 7.5 * cooling_eff ** 2
# Step 3: Monte Carlo sampling to estimate E[g(x)]
def monte_carlo_simulation(n_samples, mean_vector, cov_matrix):
    # Generate multivariate normal samples
    samples = generate_correlated_samples(mean_vector, cov_matrix, n_samples)
    # Calculate the failure values for each sample
    failures = [failure_function(sample) for sample in samples]
    # Calculate the mean failure value and confidence interval
    mean_failure = sum(failures) / n_samples
    variance_failure = sum((x - mean_failure) ** 2 for x in failures) / (n_samples - 1)
    std_failure = math.sqrt(variance_failure)
    confidence_interval = 1.96 * (std_failure / math.sqrt(n_samples))
    return mean_failure, confidence_interval, std_failure
# Step 4: Run simulations for different sample sizes
sample_sizes = [50, 100, 1000, 10000]
for n in sample_sizes:
    mean_failure, confidence_interval, _ = monte_carlo_simulation(n, mean_vector, cov_matrix)
    print(f"Samples: {n}, Mean Failure: {mean_failure:.4f}, 95% Confidence Interval: ±{confidence_interval:.4f}")
# Step 5: Hypothesis testing to compare two sample estimates
def hypothesis_test(mean_1, mean_2, std_1, std_2, n1, n2, alpha=0.05):
    # Calculate the combined standard deviation
    pooled_std = math.sqrt((std_1 ** 2) / n1 + (std_2 ** 2) / n2)
    # Compute the test statistic (z-score)
    z_score = (mean_1 - mean_2) / pooled_std
    # Critical z-value for two-tailed test
    critical_z = 1.96  # For alpha=0.05
    # Decision based on the z-score
    if abs(z_score) > critical_z:
        print(f"Reject the null hypothesis. Difference between the two means is significant (z = {z_score:.4f}).")
    else:
        print(f"Fail to reject the null hypothesis. No significant difference (z = {z_score:.4f}).")

# Example hypothesis test between n = 50 and n = 10000 estimates
mean_50, _, std_50 = monte_carlo_simulation(50, mean_vector, cov_matrix)
mean_10000, _, std_10000 = monte_carlo_simulation(10000, mean_vector, cov_matrix)

# Perform the hypothesis test

if __name__ == "__main__":
    hypothesis_test(mean_50, mean_10000, std_50, std_10000, 50, 10000)