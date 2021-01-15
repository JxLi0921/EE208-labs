import time
import numpy as np
import torch
from utilities import readAndPreprocessImage, normalize
from torchvision.datasets.folder import default_loader

model = torch.hub.load('pytorch/vision', 'resnet50', pretrained=True)
print(model)