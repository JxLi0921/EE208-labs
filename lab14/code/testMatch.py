import numpy as np
import torch
import torchvision.transforms as transforms
from torchvision.datasets.folder import default_loader

def normalize(x):
	return x / np.linalg.norm(x)

def compute_similarity(feat_1, feat_2):
	dist = np.linalg.norm(feat_1 - feat_2)
	angle = np.arccos(np.minimum(1, np.maximum(feat_1 @ feat_2, -1)))
	return dist, angle

normalizeImage = transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                      std=[0.229, 0.224, 0.225])
trans = transforms.Compose([
    transforms.ToTensor(),
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    normalizeImage,
])

normalize = lambda x: x / np.linalg.norm(x)
preprocessImage = lambda img: torch.unsqueeze(trans(img), 0)
readAndPreprocessImage = lambda path: preprocessImage(default_loader(path))

model = torch.hub.load('pytorch/vision', 'resnet50', pretrained=True)

def features(x):
    x = model.conv1(x)
    x = model.bn1(x)
    x = model.relu(x)
    x = model.maxpool(x)
    x = model.layer1(x)
    x = model.layer2(x)
    x = model.layer3(x)
    x = model.layer4(x)
    x = model.avgpool(x)

    return x

all_features = np.load('../features_final.npy')
test_image = readAndPreprocessImage('../testdata/phone.jpg')
test_feature = features(test_image).detach().numpy().reshape((-1, ))
test_feature = normalize(test_feature)

angles = np.dot(all_features, test_feature)
print(angles.argsort()[-5:][::-1])