import torchvision.transforms as transforms
from torchvision.datasets.folder import default_loader
import torch
import numpy as np

def normalize(x):
	return x / np.linalg.norm(x)

def compute_similarity(feat_1, feat_2):
	dist = np.linalg.norm(feat_1 - feat_2)
	angle = np.arccos(np.minimum(1, np.maximum(feat_1 @ feat_2, -1)))
	return dist, angle

normalizeImage = transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                      std=[0.229, 0.224, 0.225])
trans = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    normalizeImage,
])

normalize = lambda x: x / np.linalg.norm(x)
preprocessImage = lambda img: torch.unsqueeze(trans(img), 0)
readAndPreprocessImage = lambda path: preprocessImage(default_loader(path))