import cv2

imgPaths = [(s, 'imgs/politics/' + s) for s in os.listdir('imgs/politics')]
imgPaths.extend([(s, 'imgs/technology/' + s) for s in os.listdir('imgs/technology')])

labeledImages = [] # 有人脸的图片们

for (s, imagePath) in imgPaths:
	image = cv2.imread(imagePath)
	face_model=cv2.CascadeClassifier('plugins/opencv/haarcascade_frontalcatface.xml')
	gray = cv2.cvtColor(image,cv2.COLOR_RGB2GRAY)
	faces = face_model.detectMultiScale(gray)
	if faces: 
		labeledImages.append(int(x[:-4]))

