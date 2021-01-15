import numpy as np 
from math import pi
from utilities import normalize, compute_similarity

features = np.load('../features_final.npy')
N, W = features.shape

dist_matrix = np.zeros((N, N))
angle_matrix = np.zeros((N, N))

for i in range(N):
	print(i)
	for j in range(i, N):
		dist_matrix[i][j], angle_matrix[i][j] = compute_similarity(features[i], features[j])
		dist_matrix[j][i], angle_matrix[j][i] = dist_matrix[i][j], angle_matrix[i][j]

np.save('distMatrix.npy', dist_matrix)
np.save('angleMatrix.npy', angle_matrix)