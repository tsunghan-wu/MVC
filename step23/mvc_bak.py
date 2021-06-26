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
        translation = (dst_center - src_center)

        coordinate_X = self.preprocess(src_image, curve)
        # contours
        src_mask = np.zeros(src_image.shape, src_image.dtype)
        cv2.fillPoly(src_mask, [curve], (255, 255, 255))
        src_mask = cv2.cvtColor(src_mask, cv2.COLOR_BGR2GRAY)
        contours, hier = cv2.findContours(src_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = contours[0].squeeze(1)

        img = src_image.copy()
        for p in contours:
            img = cv2.circle(img, p, radius=1, color=(0, 0, 255))
        cv2.imwrite('con.png', img)

        src_image = src_image.astype(np.float32) / 255
        dst_image = dst_image.astype(np.float32) / 255
        output_image = dst_image.copy()
        diff = self.count_diff(contours, translation, src_image, dst_image)

        mvc = np.empty((len(contours), len(coordinate_X)))

        for x in coordinate_X:
            L = self.solve_mvc(x, contours)
            trg_x = x + translation
            r_x = np.sum(L * diff, axis=0)
            output_image[int(trg_x[1]), int(trg_x[0])] = src_image[x[1], x[0]] + r_x
        # prevent overflow
        final_output = (np.clip(output_image, 0.0, 1.0) * 255).astype(np.uint8)
        return final_output

    def rad(self, v1, v2):
        norm1 = np.linalg.norm(v1, axis=1)
        norm2 = np.linalg.norm(v2, axis=1)
        cos = (v1 * v2).sum(axis=1) / norm1 / norm2
        
        return np.arccos(np.clip(cos, -1, 1))
