import math
import os

import cv2
import numpy as np


def fit(img, boundary):
    xmin, ymin = boundary.min(axis=0)
    xmax, ymax = boundary.max(axis=0)

    return img[ymin:ymax, xmin:xmax]


def crop_poly(img, boundary, max_w, max_h, add_alpha=True, tight=True):
    """Args:
    img (np.array): source img to be cropped
    boundary ([(x, y)]): an array of points

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

    boundary = boundary.astype(np.int32)
    mask = np.zeros_like(img)
    mask = cv2.fillPoly(mask, [boundary], (255, 255, 255))
    img = img * mask.astype(bool)

    if add_alpha:
        alpha = np.where(mask.sum(axis=2), 255, 0)
        img = np.dstack([img, alpha])
    if tight:
        img = fit(img, boundary)

    return img


def crop_src_patch(cors, width, height, dir_path='static/data', 
                   src_name='src.png', patch_name='patch.png'):
    """Args:
    cors ([{'x': int, 'y':int}])
    width (int)
    height (int)
    dir_path (str)

    Return:
    size (int, int): width, height
    """
    img = cv2.imread(os.path.join(dir_path, src_name))
    img = cv2.resize(img, (width, height))
    bndry = np.array([[cor['x'], cor['y']] for cor in cors])
    img = crop_poly(img, bndry, width, height)
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

    return img, ps.round().astype(np.int32)


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
    tx = tar.shape[1] / info['tar_size']['width']
    ty = tar.shape[0] / info['tar_size']['height']

    src = cv2.imread(os.path.join(dir_path, src_name))
    patch = cv2.imread(os.path.join(dir_path, patch_name))

    bndry = np.array([[per['x'], per['y']] for per in info['perimeter']])
    bx = src.shape[1] / info['cavs_width']
    by = src.shape[0] / info['cavs_height']
    bndry = bndry * np.array([bx, by])

    crp_shape = bndry.max(axis=0) - bndry.min(axis=0)
    sx = info['src_size']['width'] / crp_shape[0] * tx
    sy = info['src_size']['height'] / crp_shape[1] * ty
    src = cv2.resize(src, None, fx=sx, fy=sy)

    bndry = bndry * np.array([sx, sy])
    src = fit(src, np.int32(bndry.round()))
    bndry = bndry - bndry.min(axis=0)

    bndry = np.vstack([bndry, [0, 0]])
    patch, bndry = rotate(src, bndry, -info['rot'])

    pos = np.array([info['pos']['x'], info['pos']['y']]) * [tx, ty] - bndry[-1] + \
        np.array([patch.shape[1], patch.shape[0]]) / 2
    bndry = bndry[:-1]

    patch = fit(patch, bndry)
    bndry = bndry - bndry.min(axis=0)

    return patch.astype(np.uint8), tar, bndry.astype(np.int32), pos.astype(np.int32)