import numpy as np
import matplotlib.pyplot as plt

dist_matrix = np.load('../distMatrix.npy')
angle_matrix = np.load('../angleMatrix.npy')

N, _ = dist_matrix.shape

x = []
y = []

for i in range(N):
	print(i)
	for j in range(i + 1, N):
		x.append(dist_matrix[i][j])
		y.append(angle_matrix[i][j])

plt.scatter(x, y, s=6)
plt.xlabel('dist')
plt.ylabel('angle')
plt.savefig('a.png')