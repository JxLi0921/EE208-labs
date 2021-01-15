import numpy as np
from functools import reduce

class matcher:
	def computeColorHistogram(self, img):
		E = np.sum(img, axis=(0, 1))
		return E / np.sum(E)        

	def computeFeature(self, img):
		R, C, _ = img.shape
		halfR, halfC = R // 2, C // 2

		H = [
			img[:halfR, :halfC],
			img[halfR:, :halfC],
			img[:halfR, halfC:],
			img[halfR:, halfC:]
		]

		features = [self.computeColorHistogram(h) for h in H]
		return reduce(lambda x, y: np.hstack((x, y)), features)