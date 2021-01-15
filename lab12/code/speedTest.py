import numpy as np
from functools import reduce
import cv2
from naiveLSH import LSHMatcher
from naiveNN import nnMatcher
import time

class testUsedLSHMatcher(LSHMatcher):
	def __init__(self, imgs, L=10, threhold=0.05):
		LSHMatcher.__init__(self, imgs, L, threhold)
		self.getCodeTime = 0

	def __getitem__(self, image):
		tic = time.time()
		code, feat = self.getLSHCode(image)
		self.getCodeTime += time.time() - tic
		code = tuple(code)
		if code in self.map:
			return self.furthurMatch(self.map[code], feat)
		return None

class testUsedNNMatcher(nnMatcher):
	def __init__(self, imgs):
		nnMatcher.__init__(self, imgs)
		self.computeFeatureTime = 0

	def match(self, target, threhold=0.1):
		anot = time.time()
		featureOfTarget = self.computeFeature(target)
		self.computeFeatureTime += time.time() - anot
		minimal = 114514
		minimalImage = None

		for i, (feature, img) in enumerate(zip(self.features, self.imgs)):
			norm = np.linalg.norm(feature - featureOfTarget)
			if norm < minimal:
				minimal = norm
				minimalImage = img
		
		return None if minimal > threhold else minimalImage

if __name__ == '__main__':
	imagePath = [f'../dataset_12/{i+1}.jpg' for i in range(40)]
	targetPath = '../target.jpg'

	images = [cv2.imread(path) for path in imagePath]
	target = cv2.imread(targetPath)

	lsh = testUsedLSHMatcher(images, L=5)
	nn = testUsedNNMatcher(images)

	tic_lsh = time.time()

	for i in range(1000):
		lsh[target]

	toc_lsh = time.time()

	tic_nn = time.time()

	for i in range(1000):
		nn.match(target)
	
	toc_nn = time.time()

	print(lsh.getCodeTime, nn.computeFeatureTime)

	print('lsh: {} \nnn: {}'.format(toc_lsh - tic_lsh - lsh.getCodeTime, toc_nn - tic_nn - nn.computeFeatureTime))