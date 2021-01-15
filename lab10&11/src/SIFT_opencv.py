from utilies import *
import cv2
import os
import numpy as np

target = cv2.imread(TARGET_PATH)
sift = cv2.xfeatures2d.SIFT_create()
kp_target, dest_target = sift.detectAndCompute(cv2.cvtColor(target, cv2.COLOR_BGR2GRAY), None)
flann = cv2.FlannBasedMatcher(
	{
		'algorithm': 0,
		'trees': 5
	},
	{'checked': 50}
)

mkdir('output/opencv')

for i, input_img_path in enumerate(DATASET):
	image = cv2.imread(input_img_path)
	image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	key_points, dest = sift.detectAndCompute(image_gray, None)
	image_with_kps = cv2.drawKeypoints(image, key_points, np.array([]), color=(140,23,255))
	cv2.imwrite(f'output/opencv/{i+1}_withkps.jpg', image_with_kps)
	match = flann.knnMatch(dest, dest_target, k=2)

	better_match = []
	for m, n in match:
		if m.distance < 0.5 * n.distance:
			better_match.append([m])

	image_match = cv2.drawMatchesKnn(image, key_points, target, \
									 kp_target, better_match, None, flags=2)
	cv2.imwrite(f'output/opencv/{i+1}_match.jpg', image_match)
	image_match_kps = cv2.drawMatchesKnn(image_with_kps, key_points, target, \
	                                     kp_target, better_match, None, flags=2)
	cv2.imwrite(f'output/opencv/{i+1}_match_kps.jpg', image_match_kps)