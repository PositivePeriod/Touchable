import cv2
import numpy as np
# https://wikidocs.net/48925
# https://rosia.tistory.com/243


class Tracker:
    def __init__(self):
        self.tracker = cv2.TrackerMOSSE_create()

    def reset(self):
        self.tracker = cv2.TrackerMOSSE_create()

    def set(self, set_img, set_rect):  # x, y, w, h
        # print(set_img, set_img.shape, set_rect)
        self.tracker.init(set_img.copy(), set_rect)  # ERROR

    def track(self, image):
        success, box = self.tracker.update(image)
        if success:
            return [box[0], box[1], box[0]+box[2], box[1]+box[3]]  # x, y, w, h -> x1, y1, x2, y2


if __name__ == '__main__':
    # open video file
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # default camera : id = 0
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    tracker = Tracker()
    ret, img = cap.read()
    if not ret:
        print('error')
        exit()
    rect = cv2.selectROI('Select Window', img, fromCenter=False, showCrosshair=True)
    cv2.destroyWindow('Select Window')
    tracker.set(img, rect)
    capture = True
    while True:
        ret, img = cap.read()
        if not ret:
            print('error')
            break
        import time
        p = time.time()
        rect = tracker.track(img)
        cv2.imshow('img', img)
        if rect is not None:
            cv2.rectangle(img, (int(rect[0]), int(rect[1])), (int(rect[2]), int(rect[3])), (255, 255, 255), 3)
            cv2.imshow('result', img)
        else:
            capture = False

        if cv2.waitKey(1) == ord('q'):
            break
    # release everything
    cap.release()
    cv2.destroyAllWindows()
