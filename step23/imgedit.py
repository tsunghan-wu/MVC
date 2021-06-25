import math
import os

import cv2
import numpy as np

from config import *


def crop_poly(img, boundaries, max_w=JPOLY_WIDTH, max_h=JPOLY_HEIGHT, fit=True):
    """Args:
    img (np.array): source img to be cropped
    boundaries ([(x, y)]): a list of coordinates

    Return:
    img (np.array): cropped img
    """
    if len(img.shape) != 3 or img.shape[2] != 3:
        raise ValueError(f'Received input img with shape {img.shape}')
    h, w = img.shape[:2]
    if w > max_w:
        img = cv2.resize(img, (max_w, int(max_w/w*h)))
    if h > max_h:
        img = cv2.resize(img, (int(max_h/h*w), max_h))

    bndry = boundaries

    xmin, xmax = boundaries[:, 0].min(), boundaries[:, 0].max()
    ymin, ymax = boundaries[:, 1].min(), boundaries[:, 1].max()
    mask = np.zeros_like(img)
    mask = cv2.fillPoly(mask, [np.int32(bndry)], (255, 255, 255))
    alpha = np.where(mask.sum(axis=2), 255, 0)
    img = img * mask.astype(bool)
    img = np.dstack([img, alpha])

    if fit:
        img = img[ymin:ymax, xmin:xmax]

    return img


def crop_src_patch(cors, dir_path='static/data', src_name='src.png', patch_name='patch.png'):
    """Args:
    dir_path (str)
    cors ([{'x': int, 'y':int}])

    Return:
    size (int, int): width, height
    """
    img = cv2.imread(os.path.join(dir_path, src_name))
    bndry = np.array([[cor['x'], cor['y']] for cor in cors])
    img = crop_poly(img, bndry)
    cv2.imwrite(os.path.join(dir_path, patch_name), img)


def rotate(src, points, angle, scale=1.):
    """Args:
    src (np.array)
    points (np.array): shape (n, 2)
    angle (float): degree
    scale (float)
    """
    w = src.shape[1]
    h = src.shape[0]
    rangle = np.deg2rad(angle)  # angle in radians
    
    # Calculate new image width and height
    nw = (abs(np.sin(rangle)*h) + abs(np.cos(rangle)*w)) * scale
    nh = (abs(np.cos(rangle)*h) + abs(np.sin(rangle)*w)) * scale

    rot_mat = cv2.getRotationMatrix2D((nw*0.5, nh*0.5), angle, scale)
    rot_move = np.dot(rot_mat, np.array([(nw-w)*0.5, (nh-h)*0.5, 0]))
    
    # Update the translation
    rot_mat[0, 2] += rot_move[0]
    rot_mat[1, 2] += rot_move[1]
    
    # Rotate image
    img = cv2.warpAffine(src, rot_mat, (int(math.ceil(nw)), int(math.ceil(nh))))
    
    # Rotate points
    if points.shape[1] != 2:
        raise ValueError(points.shape)
    ps = points - np.array([w*0.5, h*0.5])
    ps = np.matmul(ps, rot_mat[:,:2].T) + np.array([nw/2, nh/2])

    return img, ps.astype(int)


def prepare(info, dir_path='static/data', src_name='src.png', 
            patch_name='patch.png', tar_name='tar.png'):
    """Args:
    info (dict):
        perimter: boundaries ([{'x': int, 'y': int}])
        pos: position ({'x': float, 'y': float})
        rot: clockwise rotation (float)
        src_size: src patch size ({'width': float, 'height': float})
        tar_size: tar patch size ({'width': int, 'height': int})
    """
    tar = cv2.imread(os.path.join(dir_path, tar_name))
    sx = tar.shape[1] / info['src_size']['width']
    sy = tar.shape[0] / info['src_size']['height']

    src = cv2.imread(os.path.join(dir_path, src_name))
    patch = cv2.imread(os.path.join(dir_path, patch_name))
    bndry = np.array([[per['x'], per['y']] for per in info['perimeter']])
    bndry = bndry * (src.shape[0]/patch.shape[0], src.shape[1]/patch.shape[1])
    patch = crop_poly(src, bndry, src.shape[1], src.shape[0])
    bndry = bndry - bndry.min(axis=0)

    src_width, src_height = info['src_size']['width'], info['src_size']['height']
    sw = src_width * sx
    sh = src_height * sy
    patch = cv2.resize(patch, (int(sw), int(sh)))
    bndry = bndry * np.array([sw/patch.shape[1], sh/patch.shape[0]])

    patch, bndry = rotate(patch, bndry, -info['rot'])
    # src = crop_poly(src, bndry, src.shape[1], src.shape[0], fit=False)

    
    # tar = cv2.resize(tar, (info['tar_size']['width'], info['tar_size']['height']))

    pos = np.array([info['pos']['x'], info['pos']['y']]) + \
        np.array([src.shape[1], src.shape[0]]) // 2
    return patch[:,:,:3].astype(np.uint8), tar, bndry, pos.astype(int)
