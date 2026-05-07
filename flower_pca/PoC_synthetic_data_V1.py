"""
Proof of Concept for the federated PCA.

This script does not implement anything with flower. It just computes the PCA on two datasets and merge the results.
At the same time the PCA on the merged dataset is computed and the results are compared.

The implementation is based on the works of Grammenos et al.: Federated Principal Component Analysis
https://proceedings.neurips.cc/paper/2020/hash/47a658229eb2368a99f1d032c8848542-Abstract.html

Version 1. 
Copy of the formulas from the original paper but some errors are present.
Inconsistency between the paper's notation (which assumes that matrices are features x samples) and the Python library's notation (which assumes that matrices are samples x features)

@author: Alberto Zancanaro (Jesus)
@organization: Luxembourg Centre for Systems Biomedicine (LCSB)
@contact : alberto.zancanaro@uni.lu
"""

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

import numpy as np
import scipy.linalg
import sklearn.decomposition

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Settings

n_samples = 220
n_features = 50

centering = True

rank = -1  # Number of principal components to keep

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Load data

# Generate synthetic datasets. The data shape is features x samples, to be consistent with the mathematical notation used in the paper
x_data_1 = np.random.rand(n_features, n_samples)
x_data_2 = np.random.rand(n_features, n_samples)
x_data_merged = np.concatenate((x_data_1, x_data_2), axis = 1)

# Set rank to the number of features if rank < 0
# Note that x_data_1, x_data_2 and x_data_merged have the same number of features
if rank < 0 : rank = x_data_1.shape[0]

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Preprocess data

if centering :
    # Center data (subtract the mean of each feature)
    mean_merged = np.mean(x_data_merged, axis = 1, keepdims = True)
    # x_data_1 = x_data_1 - mean_merged
    # x_data_2 = x_data_2 - mean_merged
    # x_data_merged = x_data_merged - mean_merged
else :
    mean_merged = 0.0

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Compute Federated PCA

# Compute SVD on local data
U_1, S_1, _ = scipy.linalg.svd(x_data_1 - mean_merged)
U_2, S_2, _ = scipy.linalg.svd(x_data_2 - mean_merged)

# Convert S from vector to diagonal matrix
S_1 = np.diag(S_1)
S_2 = np.diag(S_2)

# Keep only the top 'rank' components
U_1, S_1 = U_1[:, :rank], S_1[:rank, :rank]
U_2, S_2 = U_2[:, :rank], S_2[:rank, :rank]

# Print info (Client 1)
print("Local PCA computed.")
print("CLIENT 1")
print(f"\t x.shape = {x_data_1.shape} (samples = {x_data_1.shape[1]}, features = {x_data_1.shape[0]})")
print(f"\t U.shape = {U_1.shape}")
print(f"\t S.shape = {S_1.shape}")

# Print info (Client 2)
print("\nCLIENT 2")
print(f"\t x.shape = {x_data_2.shape} (samples = {x_data_2.shape[1]}, features = {x_data_2.shape[0]})")
print(f"\t U.shape = {U_2.shape}")
print(f"\t S.shape = {S_2.shape}")


# Concatenate matrices and compute global SVD (see section 3.1 of the paper)
US_1 = np.matmul(U_1, S_1)
US_2 = np.matmul(U_2, S_2)
US_concat = np.concatenate((US_1, US_2), axis = 1)
U_fed, S_fed, Vt_fed = scipy.linalg.svd(US_concat)

# Keep only the top 'rank' components
U_fed = U_fed[:, :rank]
S_fed = np.diag(S_fed[:rank])

# Print info (Federated)
print("\nFEDERATED")
print(f"\t US_1.shape = {US_1.shape}")
print(f"\t US_2.shape = {US_2.shape}")
print(f"\t US_concat.shape = {US_concat.shape}")
print(f"\t U_fed.shape = {U_fed.shape}")
print(f"\t S_fed.shape = {S_fed.shape}")
print(f"\t Vt_fed.shape = {Vt_fed.shape}")

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Compute Centralized PCA

# Compute SVD on merged data
U_cent, S_cent, Vt_cent = scipy.linalg.svd(x_data_merged - mean_merged)
S_cent = np.diag(S_cent)

# Keep only the top 'rank' components
U_cent = U_cent[:, :rank]
S_cent = S_cent[:rank, :rank]

# Print info (Centralized)
print("\nCENTRALIZED")
print(f"\t x_merged.shape = {x_data_merged.shape}")
print(f"\t U_cent.shape = {U_cent.shape}")
print(f"\t S_cent.shape = {S_cent.shape}")
print(f"\t Vt_cent.shape = {Vt_cent.shape}")

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Compare results
# Compare U matrices (up to a sign)
U_diff = np.abs(U_fed - U_cent)
print("\nCOMPARISON OF U MATRICES")
print(f"\t U_diff.mean() = {U_diff.mean()}")
print(f"\t U_diff.max() = {U_diff.max()}")
# Compare S matrices
S_diff = np.diag(np.abs(S_fed - S_cent))
print("\nCOMPARISON OF S MATRICES")
print(f"\t S_diff.mean() = {S_diff.mean()}")
print(f"\t S_diff.max() = {S_diff.max()}")

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Compute PCA using sklearn for validation

pca = sklearn.decomposition.PCA(n_components = rank)
x_reduced_skl = pca.fit_transform((x_data_merged - mean_merged).T).T

U_skl = pca.components_ 
S_skl = np.diag(pca.singular_values_)
print("\nSKLEARN PCA")
print(f"\t x_reduced_skl.shape = {x_reduced_skl.shape}")
print(f"\t U_skl.shape = {U_skl.shape}")
print(f"\t S_skl.shape = {S_skl.shape}")

# Compare U matrices (up to a sign)
U_diff_skl = np.abs(U_fed - U_skl)
print("\nCOMPARISON OF U MATRICES WITH SKLEARN")
print(f"\t U_diff_skl.mean() = {U_diff_skl.mean()}")
print(f"\t U_diff_skl.max() = {U_diff_skl.max()}")

# Compare S matrices
S_diff_skl = np.diag(np.abs(S_fed - S_skl))
print("\nCOMPARISON OF S MATRICES WITH SKLEARN")
print(f"\t S_diff_skl.mean() = {S_diff_skl.mean()}")
print(f"\t S_diff_skl.max() = {S_diff_skl.max()}")


# Compare U_skl with Vt_fed.T
Vt_fed_T = Vt_fed.T
U_diff_skl_fed = np.abs(U_skl - Vt_fed_T)
print("COMPARISON OF U MATRICES WITH SKLEARN AND Vt_fed.T")
print(f"\t U_diff_skl_fed.mean() = {U_diff_skl_fed.mean()}")
print(f"\t U_diff_skl_fed.max() = {U_diff_skl_fed.max()}")


Vt_fed_T = Vt_fed
U_diff_skl_fed = np.abs(U_skl - Vt_fed_T)
print("COMPARISON OF U MATRICES WITH SKLEARN AND Vt_fed")
print(f"\t U_diff_skl_fed.mean() = {U_diff_skl_fed.mean()}")
print(f"\t U_diff_skl_fed.max() = {U_diff_skl_fed.max()}")
