import cv2
import numpy as np


class MVC_Cloner:
    def __init__(self):
        self.adaptive_mesh = False

    def preprocess(self, src_image, curve):
        if self.adaptive_mesh is False:
            src_mask = np.zeros(src_image.shape, src_image.dtype)
            cv2.fillPoly(src_mask, [curve], (255, 255, 255))
            src_mask = cv2.cvtColor(src_mask, cv2.COLOR_BGR2GRAY)
            coord = cv2.findNonZero(src_mask).squeeze(axis=1)
            return coord

    def rad(self, v1, v2, norm1, norm2):
        cos = (v1 * v2).sum(axis=1) / norm1 / norm2
        return np.arccos(np.clip(cos, -1, 1))

    def solve_mvc(self, x, curve):
        mvc = np.empty((len(x), len(curve)))
        shift = [cur - x for cur in curve]
        norms = [np.linalg.norm(v, axis=1) for v in shift]
        for i in range(len(curve)):
            v1 = shift[i-2]
            v2 = shift[i-1]
            v3 = shift[i]
            norm1 = norms[i-2]
            norm2 = norms[i-1]
            norm3 = norms[i]

            w = (np.tan(self.rad(v2, v1, norm2, norm1)/2) + 
                 np.tan(self.rad(v3, v2, norm3, norm2)/2)) / norm2
            w[(norm1 == 0) | (norm2 == 0) | (norm3 == 0)] = 0
            mvc[:,i] = w

        return mvc / mvc.sum(axis=1, keepdims=True)


    def count_diff(self, curve, translation, src_image, dst_image):
        curve_shft = curve + translation
        D = [dst_image[trg_x[1], trg_x[0]] - src_image[src_x[1], src_x[0]] \
            for src_x, trg_x in zip(curve, curve_shft)]
        
        return np.stack(D)

    def process(self, src_img, dst_img, src_center, dst_center, curve):
        translation = (dst_center - src_center)
        src_x = self.preprocess(src_img, curve)

        # contours
        src_mask = np.zeros(src_img.shape, src_img.dtype)
        cv2.fillPoly(src_mask, [curve], (255, 255, 255))
        src_mask = cv2.cvtColor(src_mask, cv2.COLOR_BGR2GRAY)
        contours, hier = cv2.findContours(src_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = contours[0].squeeze(1)
        print('Contours:', contours.shape)

        src_img = src_img.astype(np.float) / 255
        dst_img = dst_img.astype(np.float) / 255

        diff = self.count_diff(contours, translation, src_img, dst_img) # (contour, 3)

        mvc = self.solve_mvc(src_x, contours) # (pixel, contour)
        r = (mvc[:, :, np.newaxis] * diff[np.newaxis, :, :]).sum(axis=1) # (pixel)
        dst_x = src_x + translation

        output = dst_img.copy()
        output[(dst_x[:, 1], dst_x[:, 0])] = src_img[(src_x[:, 1], src_x[:, 0])] + r

        return (np.clip(output, 0.0, 1.0) * 255).astype(np.uint8)

