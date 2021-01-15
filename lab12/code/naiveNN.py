import numpy as np
import cv2
import time
import copy
from matcher import matcher

class nnMatcher(matcher):
	def __init__(self, imgs):
		self.features = [self.computeFeature(img) for img in imgs]
		self.imgs = copy.copy(imgs)

	def match(self, target, threhold=0.1):
		featureOfTarget = self.computeFeature(target)
		minimal = 114514
		minimalImage = None

		for i, (feature, img) in enumerate(zip(self.features, self.imgs)):
			norm = np.linalg.norm(feature - featureOfTarget)
			if norm < minimal:
				minimal = norm
				minimalImage = img
		
		return None if minimal > threhold else minimalImage

def NNTest():
	imagePath = [f'../dataset_12/{i+1}.jpg' for i in range(40)]
	targetPath = '../target.jpg'
	
	images = [cv2.imread(path) for path in imagePath]
	target = cv2.imread(targetPath)
	
	nn = nnMatcher(images)
	img = nn.match(target)
	cv2.imshow('show.png', img)
	cv2.waitKey()
	cv2.destroyAllWindows()

if __name__ == '__main__':
	NNTest()