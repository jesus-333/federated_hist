"""
Proof of Concept for the federated PCA.

This script does not implement anything with flower. It just computes the PCA on two datasets and merge the results.
At the same time the PCA on the merged dataset is computed and the results are compared.

The implementation is based on the works of Grammenos et al.: Federated Principal Component Analysis
https://proceedings.neurips.cc/paper/2020/hash/47a658229eb2368a99f1d032c8848542-Abstract.html

Version 2.
Rewriting the paper's formulas to use library notation for matrices (samples x features)

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
use_local_mean_for_centering = False

rank = 50 # Number of principal components to keep

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Load data

# Generate synthetic datasets. The data shape is features x samples, to be consistent with the mathematical notation used in the paper
x_data_1 = np.random.rand(n_samples, n_features)
x_data_2 = np.random.rand(n_samples, n_features)
x_data_merged = np.concatenate((x_data_1, x_data_2), axis = 0)

# Set rank to the number of features if rank < 0
# Note that x_data_1, x_data_2 and x_data_merged have the same number of features
if rank < 0 : rank = x_data_1.shape[1]

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Preprocess data

if centering :
    # Center data (subtract the mean of each feature)
    mean_merged = np.mean(x_data_merged, axis = 0)
    if use_local_mean_for_centering :
        mean_data_1 = np.mean(x_data_1, axis = 0)
        mean_data_2 = np.mean(x_data_2, axis = 0)
    else :
        mean_data_1, mean_data_2 = mean_merged, mean_merged
else :
    mean_data_1, mean_data_2, mean_merged = 0.0, 0.0, 0.0

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Compute Federated PCA

# Compute SVD on local data
U_1, S_1, Vt_1 = scipy.linalg.svd(x_data_1 - mean_data_1)
U_2, S_2, Vt_2 = scipy.linalg.svd(x_data_2 - mean_data_2)

# Convert S from vector to diagonal matrix
S_1 = np.diag(S_1)
S_2 = np.diag(S_2)

# Note that the matrix S has dimension min(n_samples, n_features) x min(n_samples, n_features).
# I.e. if n_samples < n_features, S will be a n_samples x n_samples matrix, otherwise it will be a n_features x n_features matrix.
# This comes from the fact that the SVD of a matrix X of dimension m x n is defined as X = U @ S @ Vt, where :
# - U is a m x m orthogonal matrix
# - S is a m x n diagonal matrix (with non-negative real numbers on the diagonal
# - Vt is a n x n orthogonal matrix (transpose of V)
# But the matrix S has only min(m, n) non-zero elements on the diagonal. So it is saved as a min(m, n) vector.
# In our case m = n_samples and n = n_features

# Keep only the top 'rank' components
U_1, S_1 = U_1[:, :rank], S_1[:rank, :rank]
U_2, S_2 = U_2[:, :rank], S_2[:rank, :rank]

# Note that if we want to keep all components, we just need to select that specific number of columns from U (i.e. U[:, :rank]).
# If you need a proof just run the snippet of code at the end of this script called "Test for debugging".

# Print info (Client 1)
print("Local PCA computed.")
print("CLIENT 1")
print(f"\t x.shape = {x_data_1.shape} (samples = {x_data_1.shape[0]}, features = {x_data_1.shape[1]})")
print(f"\t U.shape = {U_1.shape}")
print(f"\t S.shape = {S_1.shape}")

# Print info (Client 2)
print("\nCLIENT 2")
print(f"\t x.shape = {x_data_2.shape} (samples = {x_data_2.shape[0]}, features = {x_data_2.shape[1]})")
print(f"\t U.shape = {U_2.shape}")
print(f"\t S.shape = {S_2.shape}")

# Concatenate matrices and compute global SVD (see section 3.1 of the paper)
# Note that the SVD of a matrix X is defined as X = U @  S @ Vt (where Vt is the transpose of V)
# The basic idea of the PCA is to find the directions (principal components) where the data varies the most, and then project the data onto these directions
# This cant be obtained by computing the matrix X @ V (where V contains the principal components as columns). It can be also computed as U @ S.
# X_pca = X @ V = U @ S  Vt @ V = U @ S (where Vt is the transpose of V)
# The federated PCA computed the projection of the local dataset and then concatenate these projections. In this way it still obtained some kind of global dataset.
# After that the SVD is computed on this concatenated matrix to obtain the global principal components.
US_1 = np.matmul(U_1, S_1)
US_2 = np.matmul(U_2, S_2)
US_concat = np.concatenate((US_1, US_2), axis = 0)
U_fed, S_fed, Vt_fed = scipy.linalg.svd(US_concat)
U_fed, S_fed = U_fed[:, :rank], np.diag(S_fed[:rank])

# Print info (Federated)
print("\nFEDERATED")
print(f"\t US_1.shape = {US_1.shape}")
print(f"\t US_2.shape = {US_2.shape}")
print(f"\t US_concat.shape = {US_concat.shape}")
print(f"\t U_fed.shape = {U_fed.shape}")
print(f"\t S_fed.shape = {S_fed.shape}")

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Compute Centralized PCA

# Compute SVD on merged data
U_cent, S_cent, Vt_cent = scipy.linalg.svd(x_data_merged - mean_merged)

# Keep only the top 'rank' components
U_cent, S_cent = U_cent[:, :rank], np.diag(S_cent[:rank])

# Print info (Centralized)
print("\nCENTRALIZED")
print(f"\t x_merged.shape = {x_data_merged.shape}")
print(f"\t U_cent.shape  = {U_cent.shape}")
print(f"\t S_cent.shape  = {S_cent.shape}")
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
# Compare Vt matrices (up to a sign)
Vt_diff = np.abs(Vt_fed - Vt_cent)
print("\nCOMPARISON OF Vt MATRICES")
print(f"\t Vt_diff.mean() = {Vt_diff.mean()}")
print(f"\t Vt_diff.max() = {Vt_diff.max()}")
 
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Test for debugging
# n_samples = 200
# n_features = 80
# x_data = np.random.rand(n_samples, n_features)
# x_data = x_data - np.mean(x_data, axis = 0)
# rank = n_features
# U_1, S_1, Vt_1 = scipy.linalg.svd(x_data)
# a = np.matmul(U_1[:, :rank], np.diag(S_1[:rank]))
# S_1_extended = np.zeros((n_samples, n_features))
# S_1_extended[:rank, :rank] = np.diag(S_1[:rank])
# b = np.matmul(U_1, S_1_extended)
#
# print("Debug Test")
# print(f"x_data.shape = {x_data.shape}")
# print(f"U_1.shape = {U_1.shape}")
# print(f"S_1.shape = {S_1.shape}")
# print(f"Vt_1.shape = {Vt_1.shape}")
# print(f"S_1_extended.shape = {S_1_extended.shape}")
# print(f"rank = {rank}")
# print("Comparing a (U[:, :rank] @ S[:rank, :rank]) and b (U @ S_extended):")
# print(f"a.shape = {a.shape}")
# print(f"b.shape = {b.shape}")
# print(f"Difference mean = {np.abs(a - b).mean()}")
# print(f"Difference max  = {np.abs(a - b).max()}")
# raise Exception("Debug STOP")
