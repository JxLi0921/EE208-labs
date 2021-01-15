from BloomFilter import *
import random
import math
from matplotlib import pyplot as plt


def process_words():
	words = None
	with open('partC/cet6-words.txt', 'r', encoding='utf-8') as f:
		words = f.readlines()
		for _ in range(2109 * 9):
			index = random.randint(0, 2109)
			words.append(words[index])
	return words


def process_data():
	data = []
	with open('/workspaces/code/index.txt', 'r', encoding='utf-8') as f:
		p_data = f.readlines()
		for x in p_data:
			data.extend(x.split())
	return data


def test():

	ms = [12000, 22000,  32000, 42000, 52000, 62000, 72000]
	logfps = []
	
	for m in ms:
		# words = process_words()
		data = process_data()
		n = len(data)
		print(n)
		Filter = BloomFilter(m, int(0.7 * m / n))
		std = set()
		
		n_correct = 0

		run = 0

		for item in data:
			print(run + 1, item)
			res_filter = Filter.check(item)
			res_std = item in std
			if res_filter == res_std:
				n_correct += 1
			Filter.insert(item)
			std.add(item)
			run += 1
			
		fp = 1 - n_correct / n
		logfp = math.log(fp + 0.1)
		logfps.append(logfp)
		print(f'All test: {n}, correct: {n_correct}, FP rate: {fp}')

	plt.plot(ms, logfps, color='blue')
	plt.title('Relationship Between m and False Positive Rate')
	plt.xlabel('m')
	plt.ylabel('log(False Positive + 0.1)')
	plt.savefig('fig.png')

test()