import cv2
import numpy as np
from adaptmesh import triangulate
import matplotlib


class MVC_Cloner:
    def __init__(self):
        self.adaptive_mesh = False

    def preprocess(self, src_image, curve):
        if self.adaptive_mesh is False:
            src_mask = np.zeros(src_image.shape, src_image.dtype)
            cv2.fillPoly(src_mask, [curve], (255, 255, 255))
            src_mask = cv2.cvtColor(src_mask, cv2.COLOR_BGR2GRAY)
            # print(src_mask.shape)
            coord = cv2.findNonZero(src_mask).squeeze(axis=1)
            print(coord.shape)
            return coord

    def solve_mvc(self, x, curve):
        vec = curve - x
        N = len(curve)
        W = np.zeros((N, 1))
        for n in range(N):
            # three vectos
            vec_pre = vec[n]
            vec_now = vec[(n+1) % N]
            vec_nxt = vec[(n+2) % N]

            dist_pre = np.linalg.norm(vec_pre)
            dist_now = np.linalg.norm(vec_now)
            dist_nxt = np.linalg.norm(vec_nxt)
            if dist_pre == 0 or dist_now == 0 or dist_nxt == 0:
                w = 0
            else:
                # cosine angle
                cosine_angle1 = np.clip(np.dot(vec_pre, vec_now) / (dist_pre * dist_now), -1.0, 1.0)
                angle1 = np.arccos(cosine_angle1)
                cosine_angle2 = np.clip(np.dot(vec_now, vec_nxt) / (dist_now * dist_nxt), -1.0, 1.0)
                angle2 = np.arccos(cosine_angle2)
                # w = [ tan(X_i-1/2) + tan(X_i/2) ] / norm(vec_now)
                w = (np.tan(angle1 / 2) + np.tan(angle2 / 2)) / np.linalg.norm(vec_now)
            W[n] = w
        # normalization
        L = W / W.sum()
        return L

    def count_diff(self, curve, translation, src_image, dst_image):
        N = len(curve)
        D = np.zeros((N, 3))
        for i, src_x in enumerate(curve):
            trg_x = src_x + translation
            f_pi = src_image[src_x[1], src_x[0]]
            g_pi = dst_image[trg_x[1], trg_x[0]]
            D[i] = g_pi - f_pi
        return D

    def process(self, src_image, dst_image, src_center, dst_center, curve):
        translation = dst_center - src_center

        coordinate_X = self.preprocess(src_image, curve)
        # contours
        src_mask = np.zeros(src_image.shape, src_image.dtype)
        cv2.fillPoly(src_mask, [curve], (255, 255, 255))
        src_mask = cv2.cvtColor(src_mask, cv2.COLOR_BGR2GRAY)
        contours, hier = cv2.findContours(src_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        contours = contours[0].squeeze(1)
        src_image = src_image.astype(np.float32) / 255
        dst_image = dst_image.astype(np.float32) / 255
        output_image = dst_image.copy()
        diff = self.count_diff(contours, translation, src_image, dst_image)
        for x in coordinate_X:
            L = self.solve_mvc(x, contours)
            trg_x = x + translation
            r_x = np.sum(L * diff, axis=0)
            output_image[int(trg_x[1]), int(trg_x[0])] = src_image[x[1], x[0]] + r_x
        # prevent overflow
        final_output = (np.clip(output_image, 0.0, 1.0) * 255).astype(np.uint8)
        return final_output


class MVC_ClonerFast:
    def __init__(self):
        self.adaptive_mesh = False

    def preprocess(self, src_img, curve, sampling=True):
        if self.adaptive_mesh is False:
            src_mask = np.zeros_like(src_img)
            cv2.fillPoly(src_mask, [curve], (255, 255, 255))
            src_mask = cv2.cvtColor(src_mask, cv2.COLOR_BGR2GRAY)

            kernel = np.ones((5, 5), np.uint8)
            src_mask = cv2.erode(src_mask, kernel, iterations=1)
            if sampling:
                flag = cv2.CHAIN_APPROX_SIMPLE
            else:
                flag = cv2.CHAIN_APPROX_NONE
            contours, hier = cv2.findContours(src_mask, cv2.RETR_TREE, flag)
            contours = contours[0].squeeze(1)
            coord = cv2.findNonZero(src_mask).squeeze(axis=1)

            return coord, contours

    def rad(self, v1, v2, norm1, norm2):
        cos = (v1 * v2).sum(axis=1) / norm1 / norm2
        return np.arccos(np.clip(cos, -1, 1))

    def solve_mvc(self, x, curve):
        """In pure python,
        for i in range(len(curve)):
            v1, v2, v3 = shift[i-2], shift[i-1], shift[i]
            norm1, norm2, norm3 = norms[i-2], norms[i-1], norms[i]
            w = (np.tan(self.rad(v2, v1, norm2, norm1)/2) +
                np.tan(self.rad(v3, v2, norm3, norm2)/2)) / norm2
            w[(norm1==0) | (norm2==0) | (norm3==0)] = 0
            mvc[:, i] = w
        """
        mvc = np.empty((len(x), len(curve)))
        shift = [cur - x for cur in curve]
        norms = [np.linalg.norm(v, axis=1) for v in shift]
        tans = [np.tan(self.rad(shift[i-1], shift[i], norms[i-1], norms[i]) / 2)
                for i in range(len(shift))]

        mvc = (np.vstack([tans[-1], tans[:-1]]) + tans) / np.vstack([norms[-1], norms[:-1]])
        true_divide_mask = np.stack([
            (norms[i-2] == 0) | (norms[i-1] == 0) | (norms[i] == 0) for i in range(len(norms))])
        mvc[true_divide_mask] = 0
        mvc = mvc.T  # (len(x), len(curve))

        return mvc / mvc.sum(axis=1, keepdims=True)

    def count_diff(self, curve, translation, src_img, dst_img):
        curve_shft = curve + translation
        D = [dst_img[trg_x[1], trg_x[0]] - src_img[src_x[1], src_x[0]]
             for src_x, trg_x in zip(curve, curve_shft)]

        return np.stack(D)

    def gen_mesh(self, contours):
        m = triangulate(contours, quality=0.99, max_refloops=30)
        vertex = np.swapaxes(m.p, 0, 1).astype(np.float32)
        face = np.swapaxes(m.t, 0, 1).astype(np.int32)
        return vertex, face

    def process(self, src_img, dst_img, src_center, dst_center, curve):
        translation = (dst_center - src_center)
        src_x, contours = self.preprocess(src_img, curve, sampling=True)

        src_img = src_img.astype(np.float) / 255
        dst_img = dst_img.astype(np.float) / 255

        diff = self.count_diff(contours, translation, src_img, dst_img)  # (contour, 3)

        mvc = self.solve_mvc(src_x, contours)  # (pixel, contour)
        r = (mvc[:, :, np.newaxis] * diff[np.newaxis, :, :]).sum(axis=1)  # (pixel, 3)
        dst_x = src_x + translation

        output = dst_img.copy()
        output[(dst_x[:, 1], dst_x[:, 0])] = src_img[(src_x[:, 1], src_x[:, 0])] + r

        return (np.clip(output, 0.0, 1.0) * 255).astype(np.uint8)

    def adaptive_process(self, src_img, dst_img, src_center, dst_center, curve):
        translation = (dst_center - src_center)
        src_x, contours = self.preprocess(src_img, curve, sampling=False)
        vertex, face = self.gen_mesh(contours)   # vertex: (N, 2) --> Y, X

        src_img = src_img.astype(np.float) / 255
        dst_img = dst_img.astype(np.float) / 255

        diff = self.count_diff(contours, translation, src_img, dst_img)  # (contour, 3)

        mvc = self.solve_mvc(vertex, contours)  # (pixel, contour)
        r = (mvc[:, :, np.newaxis] * diff[np.newaxis, :, :]).sum(axis=1)  # (pixel, 3)
        dst_x = src_x + translation

        output = dst_img.copy()
        dst_vertex = vertex + translation
        dst_color = cv2.remap(src_img, vertex[:, 0], vertex[:, 1], cv2.INTER_LANCZOS4).squeeze(1) + r
        triang = matplotlib.tri.Triangulation(dst_vertex[:, 1], dst_vertex[:, 0], face)
        for c in range(3):
            interp_lin = matplotlib.tri.LinearTriInterpolator(triang, dst_color[:, c])
            zi_lin = interp_lin(dst_x[:, 1], dst_x[:, 0])
            output[dst_x[:, 1], dst_x[:, 0], c] = zi_lin

        return (np.clip(output, 0.0, 1.0) * 255).astype(np.uint8)
