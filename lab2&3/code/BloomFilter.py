from Bitarray import Bitarray 
from functools import reduce
from copy import deepcopy
from GeneralHashFunctions import GeneralHashFunctions as Hash

class BloomFilter:

	# Used to generate extra BKDRHash functions when n_hash_functions > 10.
	def __extra_BKDRHash(self, factor):
		
		def BKDRHash(key):
			seed = 131 + (factor + 1) * 13			
			hash = 0
			for x in key:
				hash = (hash * seed) + ord(x)
			return hash

		return BKDRHash

	def __init__(self, n_bits, n_hash_functions):
		'''
			Create a BloomFilter which contains a Bitarray with size 'n_bits'
			and will use 'n_hash_function' different basis to compute the 
			hash function. 

			input:
				n_bits: the size of the Bitarray;
				n_hash_functions: the number of hash functions. 
			return:
				None
		'''

		# all the hash functions in GeneralHashFunctions.py 
		self.__all_hash_functions = [
			Hash.BKDRHash,
			Hash.APHash,
			Hash.BPHash,
			Hash.DEKHash,
			Hash.DJBHash,
			Hash.ELFHash,
			Hash.FNVHash,
			Hash.JSHash,
			Hash.RSHash,
			Hash.SDBMHash
		]   
               
		self.n_bits = n_bits
		self.bitArray = Bitarray(n_bits)
		if n_hash_functions < len(self.__all_hash_functions):
			self.hash_functions = self.__all_hash_functions[:n_hash_functions]
			# If n_hash_functions < 10, we use the prior n_hash_function hash_functions as hash function
		else:
			self.hash_functions = self.__all_hash_functions \
			                     + [self.__extra_BKDRHash(i) for i in range(n_hash_functions - len(self.__all_hash_functions))]
			# else: besides the 10 hash functions, we add extra BKDRHash with base=131+13*k(k > 0)
	

	def insert(self, key):
		'''
			Insert a key into the BloomFilter.
			
			input:
				key: the key you want to insert into the BloomFilter.
			return:
				None
		'''

		HASH = [hash_function(key) % self.n_bits for hash_function in self.hash_functions]
		for x in HASH:
			self.bitArray.set(x)

	
	def check(self, key):
		'''
			check whether the BloomFilter contains the key.

			input:
				key: the key you want to check.
			return:
				True/False.
		'''

		HASH = [hash_function(key) % self.n_bits for hash_function in self.hash_functions]

		return reduce(lambda x, y: x & y, 
			          map(lambda x: self.bitArray.get(x), HASH))

	def __contains__(self, key):
		return self.check(key)

if __name__ == '__main__':
	obj = BloomFilter(32000, 7)
	obj.insert('karzexcc')
	obj.insert('retyxrk')
	print(obj.check('kArzexcc'))
	print(obj.check('retyxrk'))