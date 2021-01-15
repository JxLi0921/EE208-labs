import numpy as np
import matplotlib.pyplot as plt

def compute_gradient(img):
	'''
		compute the corresponding gradient of a grayscale image.
		Input:
			a grayscale image, which is represented with a numpy array.
		Output:
			a tuple of numpy array, (I_x, I_y), 
			the gradient in the x, y directions of the input image.
	'''
	I_x = np.zeros_like(img, dtype=np.float32)
	I_x[:-1, :] += img[1:, :]
	I_x[1:, :] -= img[:-1, :]
	
	I_y = np.zeros_like(img, dtype=np.float32)
	I_y[:, :-1] += img[:, 1:]
	I_y[:, 1:] -= img[:, :-1]
	return I_x, I_y

def compute_intensity(I_x, I_y):
	'''
		Compute the Intensity of an image whose gradient 
		is I_x and I_y.

		Input: 
			the two gradient: I_x and I_y.
		Output:
			the Intensity M of the image.
	'''
	return np.sqrt(np.power(I_x, 2) + np.power(I_y, 2))

def compute_color_histogram(img):
	'''
		Compute a color histogram of a given image.
		Input:
			a image with K channels, 
			which is represented with a (N, M, K) numpy array.
		Output:
			a (K, ) numpy array, which is it's color histogram.
	'''
	E = np.sum(img, axis=(0, 1)) # total energy of each channel.
	return E / np.sum(E)         


def comput_grayscale_histogram(img):
	'''
		Compute a grayscale histogram of a given image.
		Input: 
			a grayscale image, represented with a (N, M) numpy array.
		Output:
			a (256, ) numpy array.
	'''
	N = np.array([np.sum(img == i) for i in range(256)])
	return N / np.sum(N)

def compute_gradient_histogram(img):
	'''
		compute the grayscale if a given image.
		Input:
			an K channel img, which is represented with a numpy.array
			with shape (N, M, K)
		Output:
			the gradient histogram.
	'''

	I_x, I_y = compute_gradient(img)
	M = compute_intensity(I_x, I_y)
	B = np.floor(M)
	N = np.array([np.sum(B == i) for i in range(361)])
	return N / np.sum(N)	

def draw_color_histogram(img, img_name, file_path, show=False) -> None:
	'''
		draw the color histogram of a BGR image,
		save the image to the file_path.

		Input:
			img: an (N, M, K) image, represented with an numpy array.
			file_path: the path where to save the color histogram image.
			show: bool, whether to show the image with plt.show()
		Return:
			None
	'''
	plt.title('color histogram of {}'.format(img_name))
	color_histogram = compute_color_histogram(img)
	name_list = ['R', 'G', 'B']
	color_list = 'bgr'
	plt.xlabel('color')
	plt.ylabel('ratio')
	plt.bar(x=name_list, height=color_histogram, color=['r', 'g', 'b'], tick_label=name_list)
	plt.savefig(file_path)
	if show:
		plt.show()
	plt.clf()

def draw_grayscale_histogram(img, img_name, file_path, show=False) -> None:
	'''
		draw the grayscale histogram of a BGR image,
		save the image to the file_path.

		Input:
			img: an (N, M, K) image, represented with an numpy array.
			file_path: the path where to save the grayscale histogram image.
			show: bool, whether to show the image with plt.show()
		Return:
			None
	'''
	plt.title('grayscale histogram of {}'.format(img_name))
	grayscale_histogram = comput_grayscale_histogram(img)
	plt.bar(range(256), grayscale_histogram)
	plt.savefig(file_path)
	if show:
		plt.show()
	plt.clf()

def draw_gradient_histogram(img, img_name, file_path, show=False) -> None:
	'''
		draw the gradient histogram of a BGR image,
		save the image to the file_path.

		Input:
			img: an (N, M, K) image, represented with an numpy array.
			file_path: the path where to save the gradient histogram image.
			show: bool, whether to show the image with plt.show()
		Return:
			None
	'''
	plt.title('gradient histogram of {}'.format(img_name))
	gradient_histogram = compute_gradient_histogram(img)
	plt.bar(range(361), gradient_histogram)
	plt.savefig(file_path)
	if show:
		plt.show()
	plt.clf()