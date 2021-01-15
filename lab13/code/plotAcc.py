from matplotlib import pyplot as plt

acc = [
	0.410300,
	0.539200,
	0.580000,
	0.642100,
	0.682400,
	0.684600,
	0.720900,
	0.783100,
	0.787600,
	0.785800,
	0.791600,
	0.791800,
	0.793900,
	0.794600,
	0.796100,
	0.798300
]

epoch = [i+1 for i in range(16)]

plt.plot(epoch, acc)
plt.show()