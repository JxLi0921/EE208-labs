from utilies import *
import cv2
import os, sys
import numpy as np
import random

def build_image_pyramid(image):
    '''
        Compute a grayscale image's image pyramid.
        Constrains: Width and Height both larger than 32. 
    '''
    x, y = image.shape
    pyramid = [image]
    ratio = 0.5
    while True:
        _x, _y = int(x * ratio), int(y * ratio)
        if _x > 32 and _y > 32:
            new_image = cv2.resize(image, (_y, _x))
            pyramid.append(new_image)
            ratio /= 2.0
        else:
            break
    
    return pyramid

def find_kps(pyramid):
    '''
        Find the keypoints from a image's image pyramid.
        Algorithm: cv2.cornerHarris.

        Return: a list of numpy.array with shape (N_0, 2), (N_1, 2), ......
        for the i_th entry in the list, it corresponding to the keypoints find
        from the i_th image in the image pyramid.

        For the numpy.array, N_i represents the number of keypoints in the 
        i_th image in the pyramid, 2 simply means the point has two dimensions. 
    '''
    kps = []
    for image_gray in pyramid:
        dest = cv2.cornerHarris(np.float32(image_gray), 2, 3, 0.18)
        keyPoints = np.argwhere(dest > 0.01 * dest.max())
        kps.append(keyPoints)
    return kps

def Gradient(img):
    '''
        Compute the Gradient of a given image.
        
        Formula: I_x[i][j] = img[i+1][j] - img[i-1][j]
                 I_y[i][j] = img[i][j+1] - img[i][j-1]

        This procedure was accelerates with numpy's vectorilize operations.

        return: I_x and I_y, the Gradient on the x and y directions.
    '''
    I_x = np.zeros_like(img, dtype=np.float32)
    I_x[:-1, :] += img[1:, :]
    I_x[1:, :] -= img[:-1, :]
    
    I_y = np.zeros_like(img, dtype=np.float32)
    I_y[:, :-1] += img[:, 1:]
    I_y[:, 1:] -= img[:, :-1]
    return I_x, I_y

def Intensity(I_x, I_y):
    '''
        Return the Intensity of the Gradient.
    '''
    return np.sqrt(np.power(I_x, 2) + np.power(I_y, 2))

def find_descriptors(pyramid, Kps):
    '''
        Find the SIFT descriptors from the image pyramid and the KeyPoints.
    '''
    descriptors = []
    print('compute descriptor...')
    RADIUS = 8

    ratio = 1
    img = pyramid[0].astype('float32')
    I_x, I_y = Gradient(img)                            # gradient in x, y directions
    M = Intensity(I_x, I_y)                             # Gradient Intensity
    theta = np.rad2deg(np.arctan2(-I_y, I_x)) + 180.0   # direction of the gradient
    x_max, y_max = img.shape

    for _, kps in enumerate(Kps):
        for i, kp in enumerate(kps):
            x_kp, y_kp = kp * ratio  # recover the position of the keypoint.
            if x_kp < RADIUS - 1 or y_kp < RADIUS - 1 or x_kp >  x_max - RADIUS or y_kp > y_max - RADIUS:
                continue
    
            N_BINS = 36                
            
            bin_vote = np.zeros(N_BINS)                         # the total Intensity of the 36 bins.

            for offset_x in range(-RADIUS, RADIUS):             # compute the the total Intensity of the 36 bins. from
                bx = x_kp + offset_x                            # nearby [-8~8, -8~8) region.
                for offset_y in range(-RADIUS, RADIUS):
                    by = y_kp + offset_y
                    bin_belong = int(np.floor(theta[bx][by] / 10.0)) % N_BINS
                    bin_vote[bin_belong] += M[bx][by]

            main_theta = np.argwhere(bin_vote == bin_vote.max())[0]  
            main_theta = int(main_theta) * 10.0 + 5.0           # find the angle of the keypoint.
            new_theta = theta - main_theta                      # rotate the gradient

            ANGLE = 45.0
            N_BINS = 8

            Cos = np.cos(np.deg2rad(-main_theta))               
            Sin = np.sin(np.deg2rad(-main_theta))
            descriptor = np.zeros((16, 8)).astype(np.float32)

            for offset_x in range(-RADIUS, RADIUS):            # divide the [-8~8, -8~8) region into 16 4*4 subregions.
                _idx = (offset_x + RADIUS) // 4
                for offset_y in range(-RADIUS, RADIUS):
                    _id = _idx * 4 + (offset_y + RADIUS) // 4  # find the id of the subregion (0-15)
                    
                    x_rotated = int(round(offset_x * Cos - offset_y * Sin)) + x_kp  # rotate the point.
                    y_rotated = int(round(offset_y * Cos + offset_x * Sin)) + y_kp
                    
                    if 0 <= x_rotated < x_max and 0 <= y_rotated < y_max:
                        t = int(new_theta[x_rotated][y_rotated] / ANGLE) % N_BINS   # add to the descriptor
                        descriptor[_id][t] += M[x_rotated][y_rotated]

            descriptor /= np.linalg.norm(descriptor + 1e-7)  # add a very small number to avoid division by 0 error.
            
            descriptors.append(descriptor.flatten()) 
            # compress the descriptor from an(16, 8) array to a (128, ) vector, and add it to the descriptors
        ratio *= 2
    return np.array(descriptors).astype(np.float32)

def convert_to_cv2_keypoints(kps):
    '''
        Convert the keypoints to a list of cv2.KeyPoint.
    '''
    kp = kps[0]
    res = []
    r = 1.0
    for kp in kps:
        for n in kp:
            keypoint = cv2.KeyPoint()
            keypoint.pt = (n[1] * r, n[0] * r)
            res.append(keypoint)
        r *= 2
    return res

############# Ransac Algorithm Implement: 
############# Reference: https://blog.csdn.net/meteoraki/article/details/104732922
############# I saw the implement of Ransac Algorithm from the blog and modify it to 
############# fit my SIFT. I compared the result with and without Ransac in the report.

def compute_fundamental(x1, x2):
    n = x1.shape[1]
    if x2.shape[1] != n:
        raise ValueError("Number of points don't match.")

    A = np.zeros((n, 9))
    for i in range(n):
        A[i] = [x1[0, i] * x2[0, i], x1[0, i] * x2[1, i], x1[0, i] * x2[2, i],
                x1[1, i] * x2[0, i], x1[1, i] * x2[1, i], x1[1, i] * x2[2, i],
                x1[2, i] * x2[0, i], x1[2, i] * x2[1, i], x1[2, i] * x2[2, i]]

    U, S, V = np.linalg.svd(A)
    F = V[-1].reshape(3, 3)
    U, S, V = np.linalg.svd(F)
    S[2] = 0
    F = np.dot(U, np.dot(np.diag(S), V))

    return F / F[2, 2]


def compute_fundamental_normalized(x1, x2):
    n = x1.shape[1]
    x1 = x1 / x1[2]
    mean_1 = np.mean(x1[:2], axis=1)
    S1 = np.sqrt(2) / np.std(x1[:2])
    T1 = np.array([[S1, 0, -S1 * mean_1[0]], [0, S1, -S1 * mean_1[1]], [0, 0, 1]])
    x1 = np.dot(T1, x1)
    x2 = x2 / x2[2]
    mean_2 = np.mean(x2[:2], axis=1)
    S2 = np.sqrt(2) / np.std(x2[:2])
    T2 = np.array([[S2, 0, -S2 * mean_2[0]], [0, S2, -S2 * mean_2[1]], [0, 0, 1]])
    x2 = np.dot(T2, x2)
    F = compute_fundamental(x1, x2)
    F = np.dot(T1.T, np.dot(F, T2))
    return F / F[2, 2]


def randSeed(good, num=8):
    return random.sample(good, num)

def PointCoordinates(eight_points, keypoints1, keypoints2):
    x1 = []
    x2 = []
    tuple_dim = (1.,)

    for i in eight_points:
        tuple_x1 = keypoints1[i[0].queryIdx].pt + tuple_dim
        tuple_x2 = keypoints2[i[0].trainIdx].pt + tuple_dim
        x1.append(tuple_x1)
        x2.append(tuple_x2)

    return np.array(x1, dtype=float), np.array(x2, dtype=float)

def computeReprojError(x1, x2, F):
    ww = 1.0 / (F[2, 0] * x1[0] + F[2, 1] * x1[1] + F[2, 2])
    dx = (F[0, 0] * x1[0] + F[0, 1] * x1[1] + F[0, 2]) * ww - x2[0]
    dy = (F[1, 0] * x1[0] + F[1, 1] * x1[1] + F[1, 2]) * ww - x2[1]
    return dx * dx + dy * dy


def inlier(F, good, keypoints1, keypoints2, confidence):
    num = 0
    ransac_good = []
    x1, x2 = PointCoordinates(good, keypoints1, keypoints2)

    for i in range(len(x2)):
        line = F.dot(x1[i].T)
        line_v = np.array([-line[1], line[0]])
        err = h = np.linalg.norm(np.cross(x2[i, :2], line_v) / np.linalg.norm(line_v))


        if abs(err) < confidence:
            ransac_good.append(good[i])
            num += 1

    return num, ransac_good

def Ransac(betterMatch, kps1, kps2, confidence=40, iter_num=500):
    Max_num = 0
    good_F = np.zeros([3, 3])
    inlier_points = []

    for i in range(iter_num):
        eight_points = randSeed(betterMatch)
        x1, x2 = PointCoordinates(eight_points, kps1, kps2)
        F = compute_fundamental_normalized(x1.T, x2.T)
        num, ransac_good = inlier(F, betterMatch, kps1, kps2, confidence)

        if num > Max_num:
            Max_num = num
            good_F = F
            inlier_points = ransac_good

    return Max_num, good_F, inlier_points

########## end of Ransac Algorithm Implement.


def Main():
    target = cv2.imread(TARGET_PATH)
    target_gray = cv2.cvtColor(target, cv2.COLOR_BGR2GRAY)
    target_pyramid = build_image_pyramid(target_gray)
    target_kps = find_kps(target_pyramid)
    target_desp = find_descriptors(target_pyramid, target_kps)

    target_kps = convert_to_cv2_keypoints(target_kps)
    target_with_kps = cv2.drawKeypoints(target, target_kps, np.array([]), color=(140,23,255))
    cv2.imwrite('output/naive/target_with_kps.jpg', target_with_kps)
    cv2.imwrite('output/naive/target_gray.jpg', target_gray)

    flann = cv2.FlannBasedMatcher (           # initialize matcher.
        {
            'algorithm': 0,
            'trees': 5
        },
        {
            'checked': 50
        }
    )

    for i, img_path in enumerate(DATASET):
        print(f'image {i+1}: ')
        img = cv2.imread(img_path)
        image_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        pyramid = build_image_pyramid(image_gray)
        kps = find_kps(pyramid)
        desp = find_descriptors(pyramid, kps)                         # find keyPoints and descriptors
        
        kps = convert_to_cv2_keypoints(kps)
        match = flann.knnMatch(desp, target_desp, 2)  
                                                                       # find match results.
        better_match = []
        for m, n in match:
            if m.distance <  0.94 * n.distance:
                better_match.append([m])

        _, _, better_match = Ransac(better_match, kps, target_kps)

        image_with_kps = cv2.drawKeypoints(img, kps, np.array([]), color=(140,23,255))
        cv2.imwrite(f'output/naive/{i+1}_with_kps.jpg', image_with_kps)

        image_match_kps = cv2.drawMatchesKnn(image_with_kps, kps, target_with_kps, \
                                             target_kps, better_match, None, flags=2)       # draw match results.
        cv2.imwrite(f'output/naive/{i+1}_match_kps.jpg', image_match_kps)

        cv2.imwrite(f'output/naive/{i+1}_gray.jpg', image_gray)

if __name__ == '__main__':
    Main()