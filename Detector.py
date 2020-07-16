import math
import cv2
import numpy


class Detector:
    def __init__(self):
        # param 2 : accuracy - Hough
        self.subtract = cv2.createBackgroundSubtractorKNN(history=500, dist2Threshold=400, detectShadows=False)
        self.kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        params = cv2.SimpleBlobDetector_Params()
        params.minThreshold, params.maxThreshold = 40, 200  # Change thresholds
        params.filterByArea, params.minArea = True, 300  # Filter by Area
        params.filterByCircularity, params.minCircularity = False, 0.1  # Filter by Circularity
        params.filterByConvexity, params.minConvexity = False, 0.2  # Filter by Convexity
        params.filterByInertia, params.minInertiaRatio = False, 0.1  # Filter by Inertia
        self.blob_detector = cv2.SimpleBlobDetector_create(params)
        self.roihist = None
        self.morph_kernel = numpy.ones((9, 9), numpy.uint8)

    def reset_bg_subtract(self):
        self.subtract = cv2.createBackgroundSubtractorKNN(history=500, dist2Threshold=400, detectShadows=False)

    def bg_subtract(self, image):
        mask_sub = self.subtract.apply(image)
        mask_sub = cv2.morphologyEx(mask_sub, cv2.MORPH_CLOSE, self.kernel)
        image_sub = cv2.bitwise_and(image, image, mask=mask_sub)
        return image_sub

    def set_backprojection(self, roi=None, image=None, pos=None, rad=None, ratio=0.9):
        if roi is None and image is None and pos is None and rad is None:
            return None
        elif image is not None and pos is not None and rad is not None:
            rad_ = int(rad / 2 ** 0.5 * ratio)

            r1 = int(max(pos[1] - rad, 0))
            r2 = int(min(pos[1] + rad, int(image.shape[0])))
            r3 = int(max(pos[0] - rad, 0))
            r4 = int(min(pos[0] + rad, int(image.shape[1])))
            roi = image[r1:r2, r3:r4].copy()
        if roi is not None and roi.shape != [] and roi.shape != () and len(roi) != 0:
            # TODO
            # ERROR OCCUR BECAREFUL
            hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            self.roihist = cv2.calcHist([hsv], [0, 1], None, [180, 256], [0, 180, 0, 256], accumulate=False)  # TODO change
            cv2.normalize(self.roihist, self.roihist, 0, 255, cv2.NORM_MINMAX)

    def backprojection(self, image):
        image_ = image.copy()
        hsvt = cv2.cvtColor(image_, cv2.COLOR_BGR2HSV)
        dst = cv2.calcBackProject([hsvt], [0, 1], self.roihist, [0, 180, 30, 256], 1)

        disc = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        cv2.filter2D(dst, -1, disc, dst)

        ret, thr = cv2.threshold(dst, 50, 255, 0)
        thr = cv2.merge((thr, thr, thr))
        res = cv2.bitwise_and(image_, thr)
        return res

    def find_circle(self, image, set_detect=False, blob=False, roi=None):  # need bgr input
        img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        if blob:
            points = self.blob_detector.detect(img_gray)
            if points is not None:
                result = []
                if roi is None:
                    for point in points:
                        result.append([int(point.pt[0]), int(point.pt[1]), int(point.size)])  # x, y, rad
                else:
                    for point in points:
                        result.append([int(point.pt[0]) + 1280 // 2 - roi, int(point.pt[1]) + 720 // 2 - roi,
                                       int(point.size)])  # x, y, rad
                if len(result):
                    return result
                else:
                    return None
            else:
                return None
        elif set_detect:
            circles = cv2.HoughCircles(img_gray, cv2.HOUGH_GRADIENT, dp=1, minDist=500, param1=50, param2=25,
                                       minRadius=80, maxRadius=160)
        else:
            circles = cv2.HoughCircles(img_gray, cv2.HOUGH_GRADIENT, dp=1, minDist=600,
                                       param1=100, param2=10, minRadius=20, maxRadius=120)
        if circles is not None:
            circles = numpy.uint16(numpy.around(circles))[0, :]
            if roi is None:
                new_circles = [[int(circle[0]), int(circle[1]), int(circle[2])] for circle in circles]  # x, y, rad
            else:
                new_circles = [[int(circle[0]) + 1280 // 2 - roi[0], int(circle[1]) + 720 // 2 - roi[1], int(circle[2])]
                               for circle in circles]  # x, y, rad
            if len(new_circles):
                return new_circles

    def contour(self, image):
        img_result = image.copy()
        imgray = cv2.cvtColor(img_result, cv2.COLOR_BGR2GRAY)
        ret, thr = cv2.threshold(imgray, 30, 255, 0)
        contours, hierarchy = cv2.findContours(thr, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(img_result, contours, -1, (0, 255, 0), 1)
        cv2.imshow('thr', thr)
        cv2.imshow('contour', img_result)
        return contours

    def contour_process(self, contours):
        area_ = 0
        contour_ = None
        for contour in contours:
            area = cv2.contourArea(contour)
            if area_ < area:
                area_ = area
                contour_ = contour
        if contour_ is None:
            return None
        if not cv2.isContourConvex(contour_):
            contour_ = cv2.convexHull(contour_)
        mmt = cv2.moments(contour_)
        cx = int(mmt['m10']/mmt['m00'])
        cy = int(mmt['m01']/mmt['m00'])
        contour_area = cv2.contourArea(contour_)
        rad = int((4*contour_area/math.pi)**0.5)
        # TODO ?!
        # contour - better result than contour_
        return contour, cx, cy, rad

    def contour_color(self, image, contour):
        img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        mask = numpy.zeros(img_gray.shape, numpy.uint8)
        cv2.drawContours(mask, [contour], 0, 255, -1)
        # pixels = cv2.findNonZero(mask)
        mean_color = cv2.mean(image, mask=mask)
        return mean_color

    def morph(self, image):
        closing = cv2.morphologyEx(image, cv2.MORPH_CLOSE, self.morph_kernel)
        return closing


if __name__ == '__main__':
    a = Detector()
    for i in range(3):
        s = f'./prac/blob{i + 1}.png'
        img = cv2.imread(s, cv2.IMREAD_COLOR)
        img_small = cv2.resize(img, (0, 0), fx=0.5, fy=0.5)
        points_ = a.find_circle(img, blob=True)
        for point_ in points_:
            img_small = cv2.circle(img_small, (point_[0] // 2, point_[1] // 2), point_[2] // 2, (0, 0, 255), 3)
        cv2.imshow(s, img_small)
    print('restart')
    cv2.waitKey(0)
