from threading import Thread, Lock
from tkinter import messagebox

import cv2
import time


class Video:
    def __init__(self):
        self.camera = None
        self.frame = None
        self.camera_lock = Lock()
        self.frame_lock = Lock()
        self.thread = None
        self.thread_life = False
        self.work = False
        self.closing = False

    def is_working(self):
        if self.closing or self.camera is None or self.camera.isOpened is False:
            self.work = False
        return self.work

    def set_camera(self, state):
        with self.camera_lock:
            with self.frame_lock:
                if state == 'on':
                    self.closing = False
                    self.camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # default camera : id = 0
                    self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                    self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
                    ret_, frame_ = self.camera.read()
                    if not ret_:
                        if not self.closing:
                            messagebox.showerror("Camera Error", "Failed to access camera resource")
                        return False
                    elif len(frame_[0]) != 1280 or len(frame_) != 720:
                        # TODO quality change might cause additional error for low quality hardware
                        if not self.closing:
                            messagebox.showwarning("Low Performance Camera", "Unable to get frame with 1280x720")
                    self.thread = Thread(target=self.update_frame, args=())
                    self.thread.daemon = True
                    self.thread.start()
                    return True
                else:
                    self.close(camera_lock=True)

    def update_frame(self):
        # Read the next frame from the stream in a different thread
        while self.camera is not None:
            with self.camera_lock:
                try:
                    if self.camera is not None and self.camera.isOpened():
                        _, _frame = self.camera.read()
                        _frame = cv2.flip(_frame, 1)
                        if not self.closing:
                            self.work = True
                    else:
                        self.work = False
                        if not self.closing:
                            messagebox.showerror("Camera Error", "Fail to get frame")
                        else:
                            break
                except Exception as e:
                    print(e)
                    self.work = False
                    if not self.closing:
                        messagebox.showerror("Camera Error0", "Fail to get frame")
                    else:
                        break
            with self.frame_lock:
                self.frame = _frame
            time.sleep(0.005)
        self.work = False
        if not self.closing:
            messagebox.showinfo("Camera Stop", "Stop to get frame")

    def get_frame(self):
        with self.frame_lock:
            if self.is_working() and self.frame is not None:
                return self.frame.copy()

    def close(self, camera_lock=False):
        self.work = False
        self.closing = True
        if camera_lock:
            if self.camera is not None and self.camera.isOpened():
                self.camera.release()
            self.camera = None
        else:
            with self.camera_lock:
                if self.camera is not None and self.camera.isOpened():
                    self.camera.release()
                self.camera = None


if __name__ == '__main__':
    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # default camera : id = 0
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    ret, frame = camera.read()
    print(len(frame), len(frame[0]))
    print(camera.get(cv2.CAP_PROP_FRAME_WIDTH), camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
    camera.read()
    po = Video()
    po.set_camera('on')
    while True:
        fr = po.get_frame()
        if fr is not None:
            cv2.imshow('video.py - unit test', fr)
        cv2.waitKey(3)