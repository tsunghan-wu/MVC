import cv2
import numpy as np


def read_image(fname):
    image = cv2.imread(fname)
    return image


def write_image(fname, image):
    cv2.imwrite(fname, image)


def get_curve(src_image):
    poly = np.array([[5, 110], [15, 140], [200, 175], [375, 150], [399, 125], [350, 60], [50, 75]], np.int32)
    return poly


def get_srcCenter(src_image):
    src_center = np.array([src_image.shape[0] // 2, src_image.shape[1] // 2])
    return src_center


def get_trgCenter(dst_image):
    trg_center = np.array([1100, 300])
    return trg_center
