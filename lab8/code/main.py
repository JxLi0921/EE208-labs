import numpy as np
import matplotlib.pyplot as plt
from utilies import *
import cv2
import os

if not os.path.exists('Outputs'):
    os.mkdir('Outputs')

for i in range(1, 3 + 1):
    input_image_name = 'img{}.jpg'.format(i)
    input_image_path = 'images/{}'.format(input_image_name)

    print('now processing: {} ......'.format(input_image_path))

    img_bgr = cv2.imread(input_image_path)
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    draw_color_histogram(img_rgb, input_image_name, f'Outputs/img{i}_color_histogram.jpg')

    img_grayscale = cv2.imread(input_image_path, cv2.IMREAD_GRAYSCALE)
    cv2.imwrite(f'Outputs/img{i}_grayscale.jpg', img_grayscale)
    
    draw_grayscale_histogram(img_grayscale, input_image_name, f'Outputs/img{i}_grayscale_histogram.jpg')
    draw_gradient_histogram(img_grayscale, input_image_name, f'Outputs/img{i}_gradient_histogram.jpg')

print('finished.')

