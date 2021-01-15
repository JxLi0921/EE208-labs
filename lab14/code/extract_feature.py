# SJTU EE208

import time

import numpy as np
import torch

from utilities import readAndPreprocessImage, normalize
from torchvision.datasets.folder import default_loader

print('Load model: ResNet50')
model = torch.hub.load('pytorch/vision', 'resnet50', pretrained=True)

print('Prepare image data!')

input_images = [readAndPreprocessImage(f'../dataset/{i}.jpg') for i in range(1005)]

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

all_features = np.zeros((1005, 2048))

for i, input_image in enumerate(input_images):
    print(f'Extract features: {i+1}/{len(input_images)}')
    image_feature = features(input_image)
    image_feature = image_feature.detach().numpy().reshape(-1)
    all_features[i] = normalize(image_feature)
    if i % 100 == 0:
        print('Save features!')
        np.save(f'features_{i}.npy', all_features)

np.save(f'features_final.npy', all_features)