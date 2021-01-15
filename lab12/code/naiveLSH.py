import numpy as np
import cv2
from matcher import matcher

class LSHMatcher(matcher):
	def __init__(self, imgs, L=10, threhold=0.05):
		self.map = {}
		self.L = L
		self.subSets = self.generateSubSets()
		self.threhold = threhold

		for img in imgs:
			code, feat = self.getLSHCode(img)
			code = tuple(code)
			if code not in self.map:
				self.map[code] = []
			self.map[code].append((img, feat))

	def generateSubSets(self):
		result = []
		baseArray = np.linspace(1, 24, 24).astype('int')

		while len(result) < self.L:
			randomSubSet = sorted(np.random.choice(baseArray, 12, replace=False))
			if randomSubSet not in result:
				result.append(randomSubSet)
		return result

	def furthurMatch(self, d, featOfTarget):
		for img, feat in d:
			if np.linalg.norm(feat - featOfTarget) < self.threhold: 
				return img
		return None

	def __getitem__(self, image):
		code, feat = self.getLSHCode(image)
		code = tuple(code)
		if code in self.map:
			return self.furthurMatch(self.map[code], feat)
		return None

	def __contains__(self, image):
		code, feat = self.getLSHCode(image)
		code = tuple(code)
		if code in self.map:
			return self.furthurMatch(self.map[code], feat) is not None
		return None

	def listVector2BinaryVector(self, x) -> int:
		result = 0
		for y in reversed(x.tolist()):
			result = (result << 1) + y
		return result

	def computeEigenVector(self, img):
		colorHistograms = self.computeFeature(img)

		Select = lambda p: \
			0 if 0 <= p < 0.38 \
			else \
				1 if 0.38 <=p < 0.72 \
				else 2

		result = np.zeros(12, dtype='int')
		
		for j, p in enumerate(colorHistograms):
			result[j] = Select(p)

		return result, colorHistograms

	def getLSHCode(self, target):
		eigenVector, colorHistograms = self.computeEigenVector(target)
		L = self.L

		arrayLength = L // 5 if L % 5 == 0 else L // 5 + 1
		finalVectors = np.zeros(shape=(arrayLength, ), dtype=np.int64)
		index = 0
		
		for j, I in enumerate(self.subSets):
			vectorOfI = 0
			for i in range(1, 12 + 1):
				T = 0
				for x in filter(lambda x: (i-1)*2 < x <= i*2, I):
					T <<= 1
					if x - (i-1)*2 <= eigenVector[i-1]:
						T |= 1
				vectorOfI = (vectorOfI << 1) | T
			finalVectors[index] = (finalVectors[index] << 12) | vectorOfI
			if j % 5 == 4:
				index += 1
		
		return finalVectors, colorHistograms


def showImage(x, name):
	cv2.imshow(name, x)
	cv2.waitKey(0)
	cv2.destroyAllWindows()
		

def testLSH():
	imagePath = [f'../dataset_12/{i+1}.jpg' for i in range(40)]
	targetPath = '../target.jpg'
	
	images = [cv2.imread(path) for path in imagePath]
	target = cv2.imread(targetPath)
	
	hashset = LSHMatcher(images, L=10)
	x = hashset[target]
	showImage(x, 'dx.jpg')
	
if __name__ == '__main__':
	testLSH()