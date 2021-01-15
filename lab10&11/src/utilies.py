import os

TARGET_PATH = 'target.jpg'
DATASET = [
	'dataset/1.jpg',
	'dataset/2.jpg',
	'dataset/3.jpg',
	'dataset/4.jpg',
	'dataset/5.jpg'
]

def mkdir(dic):
	split = dic.split('/')
	d = ''
	for name in split:
		d = os.path.join(d, name)
		if not os.path.exists(d):
			os.mkdir(d)