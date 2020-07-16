from Canvas import Canvas
from Detector import Detector
from GUI import GUI
from Tracker import Tracker
from Function import *
from Video import Video
from Pen import Pens
from Key import Key
from Image import ImageManager

import tkinter
import tkinter.messagebox
import tkinter.font
import tkinter.simpledialog
import time

import cv2
import os


class Touchable:
    def __init__(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        to_dir = [r'./data/', r'./data/pen_data/', r'./data/image_save/', r'./data/source/']
        for dir_ in to_dir:
            if not os.path.isdir(dir_):
                os.mkdir(dir_)
        self.pen = Pens(r'./data/pen_data/')
        self.video = Video()
        self.detector = Detector()
        self.tracker = Tracker()
        self.image_manager = ImageManager(self, r'./data/source/')
        self.function = None
        self.var = None
        self.stop = None

        self.canvas = Canvas()
        self.gui = GUI(self)
        self.key = Key(self, self.canvas)
        self.gui.start_gui()

    def show_camera(self):
        if not self.video.is_working():
            return False
        top_level = tkinter.Toplevel(self.gui.window)
        top_level.title('Touchable - Camera')
        top_level.geometry('320x180')
        canvas = tkinter.Canvas(top_level, bg='black')
        canvas.place(x=0, y=0, relwidth=1, relheight=1)
        top_level.update()
        canvas.update()
        try:
            while True:
                if self.video.is_working():
                    img = self.video.get_frame()
                    if img is not None:
                        width, height = canvas.winfo_width(), canvas.winfo_height()
                        scale, width_margin, height_margin = fit_resize(1280, 720, width, height)
                        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                        img_resize = cv2.resize(img_rgb, dsize=(int(1280 * scale), int(720 * scale)), interpolation=cv2.INTER_AREA)
                        photo = pil_to_tkinter(img_resize)
                        canvas.create_image(width // 2, height // 2, image=photo, anchor=tkinter.CENTER)
                        canvas.update()
                else:
                    top_level.destroy()
                    break
        except Exception as e:
            print(f'Error in show_camera; {e}')
            raise e

    def set_detect(self):
        if not self.video.is_working():
            success = self.video.set_camera('on')
            if not success:
                print('Video is not working; cannot enter set_detect')
                return False
        self.var = {'run': True, 'hsv': (0, 0, 0), 'pick_hsv': (0, 0, 255), 'roi': None, 'pick_roi': None, 'clicked': False}
        self.enter('set_detect')
        ret_counter = 0
        while True:
            while self.var['run']:  # determine detect color
                try:
                    img = self.video.get_frame()  # get image from camera; type(img) = numpy.nd array
                    if img is None:
                        ret_counter += 1
                        if ret_counter == 20:
                            return self.exit('set_detect')
                        time.sleep(0.1)
                        continue
                    else:
                        ret_counter = 0
                except AttributeError as e:
                    print('AttributeError; set_detect', e)
                    return self.exit('set_detect')

                self.detector.bg_subtract(img)

                width, height = self.gui.widget['canvas'].winfo_width(), self.gui.widget['canvas'].winfo_height()
                scale, width_margin, height_margin = fit_resize(1280, 720, width, height)
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                img_resize = cv2.resize(img_rgb, dsize=(int(1280 * scale), int(720 * scale)),
                                        interpolation=cv2.INTER_AREA)
                photo = pil_to_tkinter(img_resize)
                self.gui.widget['canvas'].create_image(width // 2, height // 2, image=photo, anchor=tkinter.CENTER)

                roi_size = [150, 150]
                roi = img[720 // 2 - roi_size[0]:720 // 2 + roi_size[0], 1280 // 2 - roi_size[1]:1280 // 2 + roi_size[1]]
                circles = self.detector.find_circle(roi, set_detect=True, roi=roi_size)

                d, u = convert_pos(scale, width_margin, height_margin, x=720 // 2 - roi_size[0],
                                   y=720 // 2 + roi_size[1])
                l, r = convert_pos(scale, width_margin, height_margin, x=1280 // 2 - roi_size[0],
                                   y=1280 // 2 + roi_size[1])
                self.gui.widget['canvas'].create_rectangle(l, d, r, u, width=2, outline='red')

                if circles is None:
                    w, h = convert_pos(scale, width_margin, height_margin, relx=0.5, rely=0.9)
                    self.gui.widget['canvas'].create_rectangle(w - 100, h - 20, w + 100, h + 20, fill='red',
                                                               outline='red')
                    self.gui.widget['canvas'].create_text((w, h), font=tkinter.font.Font(size=15), fill='white',
                                                          text='Adjust the distance')
                else:
                    x, y, max_rad = 0, 0, 0
                    for circle in circles:  # for every circle
                        if circle[2] > max_rad:  # circle[2] == radius
                            x, y, max_rad = circle[0], circle[1], circle[2]  # circle center 좌표
                    self.var['roi'] = (img, (x, y), max_rad)
                    self.var['clicked'] = True
                    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
                    hsv = center_color(img_hsv, x, y, int(max_rad * 0.5))
                    self.var['hsv'] = hsv
                    x, y = convert_pos(scale, width_margin, height_margin, x=x, y=y)
                    max_rad = int(max_rad * scale)
                    self.gui.widget['canvas'].create_line(x - 5, y, x + 5, y, fill='white')
                    self.gui.widget['canvas'].create_line(x, y - 5, x, y + 5, fill='white')
                    self.gui.widget['canvas'].create_oval(x - max_rad - 3, y - max_rad - 3, x + max_rad + 3,
                                                          y + max_rad + 3, outline=color_type(hsv, 'hsv', 'hex'),
                                                          width=6)
                    self.gui.widget['canvas'].create_oval(x - max_rad, y - max_rad, x + max_rad, y + max_rad,
                                                          outline='white', width=3)

                self.gui.widget['palette'].delete('all')
                self.gui.widget['palette'].create_rectangle(0, 0, self.gui.widget['palette'].winfo_width(),
                                                            self.gui.widget['palette'].winfo_height(),
                                                            fill=color_type(self.var['pick_hsv'], 'hsv', 'hex'))
                self.gui.widget['canvas'].update()
                self.gui.widget['palette'].update()
                self.gui.widget['canvas'].delete('all')
            if self.pen.make_pen(self):
                break
            else:
                self.var['run'] = True
        # TODO
        # self.detector.set_backprojection(image=self.var['pick_roi'][0], pos=self.var['pick_roi'][1]
        time.sleep(0.05)
        self.detector.set_backprojection(image=self.var['pick_roi'][0], pos=self.var['pick_roi'][1],
                                         rad=self.var['pick_roi'][2])
        return self.exit('set_detect', True)

    def detect(self, pen=None, color_reflect=0.01, back_image=None):
        if self.pen.is_empty():
            new_pen = self.set_detect()
            if not new_pen:
                print('No new pen; cannot enter detect')
                return False
        if not self.video.is_working():
            print('Video is not working; cannot enter detect')
            return False
        if pen is None:
            pen = self.pen.get_pen()
        self.var = {'run': True, 'pen': pen, 'pos': None, 'target': None, 'mark': None, 'event': None, 'scale': 1}
        self.enter('detect')
        backup_pen_hsv = pen.access_hsv()
        no_circle = 0
        ret_counter = 0
        self.gui.widget['canvas'].configure(bg='white')
        self.detector.reset_bg_subtract()

        last_result = None
        tracked = False
        tracker_roi = None
        tracker_result = None
        roi_size = 2
        self.stop = False

        while self.var['run']:  # determine detect color # TODO turn off
            try:
                img = self.video.get_frame()  # get image from camera; type(img) = numpy.nd array
                if img is None:
                    ret_counter += 1
                    if ret_counter == 20:
                        print('Cannot get frame for long time; leave detect')
                        return self.exit('detect')
                    time.sleep(0.1)
                    continue
                else:
                    ret_counter = 0
            except AttributeError as e:
                print('AttributeError; detect', e)
                return self.exit('detect')
            if no_circle > 20:  # hard-coding / 20 can be change / for initialize color
                print('No circle; reset color')
                no_circle = 0
                pen.access_hsv(backup_pen_hsv)
                self.gui.widget['palette'].create_rectangle(0, 0, self.gui.widget['palette'].winfo_width(),
                                                            self.gui.widget['palette'].winfo_height(),
                                                            fill=color_type(pen.access_color(), 'hsv', 'rgb'))

            width, height = self.gui.widget['canvas'].winfo_width(), self.gui.widget['canvas'].winfo_height()

            if back_image is not None:  # TODO
                height_, width_, _ = back_image.shape
                scale_, width_margin_, height_margin_ = fit_resize(width_, height_, width, height)
                img_cvt = cv2.cvtColor(back_image, cv2.COLOR_BGR2RGB)
                img_res = cv2.resize(img_cvt, dsize=(int(width_ * scale_), int(height_ * scale_)), interpolation=cv2.INTER_AREA)
                photo = pil_to_tkinter(img_res)
                self.gui.widget['canvas'].create_image(width // 2, height // 2, image=photo, anchor=tkinter.CENTER)

            scale, width_margin, height_margin = fit_resize(1280, 720, width, height)
            self.canvas.draw(scale, width_margin, height_margin)

            result = None

            # 0. Preprocessing
            img_subtract = self.detector.bg_subtract(img)
            '''
            if self.stop:
                time.sleep(0.01)
                continue
            '''
            img_color = self.detector.backprojection(img_subtract)
            img_color = cv2.bilateralFilter(img_color, 9, 75, 75)
            img_color = self.detector.morph(img_color)

            # 1. Contour
            contours = self.detector.contour(img_color)
            answer = self.detector.contour_process(contours)
            if answer is not None:
                contour, x, y, rad = answer
                contour_color = self.detector.contour_color(img, contour)
                if hsv_square_distance(pen.access_hsv(), contour_color, only_h=True) < 0.6 and rad > 10:
                    result = [[x, y], int(0.7*rad)]  # calibration
                    cv2.circle(img, (x, y), rad, (255, 0, 0))

            if result is None:
                # 2. Tracker
                if tracked:
                    pos, rad = tracker_roi
                    r1 = int(max(pos[1]-roi_size*rad, 0))
                    r2 = int(min(pos[1]+roi_size*rad, int(img.shape[0])))
                    r3 = int(max(pos[0]-roi_size*rad, 0))
                    r4 = int(min(pos[0]+roi_size*rad, int(img.shape[1])))
                    roi = img[r1:r2, r3:r4].copy()
                    rect = self.tracker.track(roi)
                    if rect is None:
                        tracked = False
                        tracker_result = None
                    else:
                        rect = [int(rect[0]+r3), int(rect[1]+r1), int(rect[2]+r3), int(rect[3]+r1)]
                        pos_ = [int((rect[0]+rect[2])/2), int((rect[1]+rect[3])/2)]
                        rad_ = min(int((-rect[0]+rect[2])/2), int((-rect[1]+rect[3])/2))
                        tracker_result = [pos_, rad_]
                        cv2.rectangle(img, (rect[0], rect[1]), (rect[2], rect[3]), (0, 0, 255), 3)

                # 3. Detector
                circles = self.detector.find_circle(img_color, blob=True)  # TODO ROI
                if circles is None:
                    no_circle += 1
                    tracked = False
                    self.tracker.reset()
                if circles is not None:
                    no_circle = 0
                    temp_pos, temp_rad = [0, 0], 0
                    priority_ = 2  # small is good
                    if tracked:
                        for circle in circles:  # for every circle
                            x, y, rad = circle
                            if rad < 10:
                                continue
                            in_rect = -int(rect[0] <= x <= rect[2] and rect[1] <= y <= rect[3])
                            center_hsv = center_color(img, x, y, int(rad*0.9))
                            hsv_distance = hsv_square_distance(center_hsv, pen.access_hsv(), only_h=True)
                            priority = hsv_distance-in_rect
                            if priority > 0.3:
                                continue
                            elif priority < priority_:
                                temp_pos, temp_rad, priority_ = [x, y], rad, priority
                    else:
                        for circle in circles:  # for every circle
                            x, y, rad = circle
                            if rad < 10:
                                continue
                            center_hsv = center_color(img, x, y, int(rad * 0.9))
                            priority = hsv_square_distance(center_hsv, pen.access_hsv(), only_h=True)
                            if priority > 0.3:
                                continue
                            elif priority < priority_:
                                temp_pos, temp_rad, priority_ = [x, y], rad, priority

                    if priority_ != 2:
                        result = [temp_pos, int(temp_rad*0.7)]  # calibration
                        cv2.circle(img, tuple(result[0]), result[1], (0, 0, 255))

            if result is None:
                # TODO - not needed
                if tracker_result is not None:
                    if (not (0 < tracker_result[0][0] < 1280)) or (not(0 < tracker_result[0][1] < 720)):
                        outside = True
                elif last_result is not None:
                    if (not (0 < last_result[0][0] < 1280)) or (not(0 < last_result[0][1] < 720)):
                        outside = True
                tracked = False
            else:
                pos, rad = result
                if last_result is None or square_distance(last_result[0], result[0], root=True) < 50:
                    last_result = result
                tracked = True
                self.tracker.reset()
                if tracker_result is not None:
                    track_rad = max(rad, tracker_result[1], 50)
                else:
                    track_rad = max(rad, 50)
                tracker_roi = [pos, track_rad]
                y1 = int(max(pos[1]-roi_size*track_rad, 0))
                y2 = int(min(pos[1]+roi_size*track_rad, int(img.shape[0])))
                x1 = int(max(pos[0]-roi_size*track_rad, 0))
                x2 = int(min(pos[0]+roi_size*track_rad, int(img.shape[1])))
                self.tracker.set(img, (x1, y1, x2-x1, y2-y1))
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255))
                # self.detector.set_backprojection(image=img, pos=pos, rad=int(rad * 0.7 * 0.3))  # MIGHT ERROR - calibration
                self.key.access_pos(pos)

                img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
                temp_hsv = center_color(img_hsv, pos[0], pos[1], int(rad * 0.3))
                pen.access_hsv([int(pen.access_hsv()[i_] * (1 - color_reflect) + temp_hsv[i_] * color_reflect) for i_ in range(3)])
                width, height = self.gui.widget['canvas'].winfo_width(), self.gui.widget['canvas'].winfo_height()
                scale, width_margin, height_margin = fit_resize(1280, 720, width, height)
                x_, y_ = convert_pos(scale, width_margin, height_margin, x=pos[0], y=pos[1])
                if self.key.access_event() is not None and self.key.access_event()[0] == '_':
                    cross_color = 'red'
                else:
                    cross_color = 'black'
                self.gui.widget['canvas'].create_line(x_ - 5, y_, x_ + 5, y_, fill=cross_color, width=1)
                self.gui.widget['canvas'].create_line(x_, y_ - 5, x_, y_ + 5, fill=cross_color, width=1)

            cv2.imshow('ori', img)

            self.gui.widget['palette'].delete('all')
            w, h = self.gui.widget['palette'].winfo_width(), self.gui.widget['palette'].winfo_height()
            self.gui.widget['palette'].create_rectangle(0, 0, w, h, fill=color_type(pen.access_color(), 'hsv', 'hex'))

            self.gui.widget['canvas'].update()
            self.gui.widget['palette'].update()
            self.gui.widget['canvas'].delete('all')
        return self.exit('detect')

    def stop_detect(self, reset_drawing=True):
        if self.function == 'detect':
            self.var['run'] = False
        if reset_drawing:
            self.canvas.clear()

    def enter(self, command):
        self.function = command
        print(f'Enter {command}')
        self.key.key_map(command)

    def exit(self, command="all", success=False):
        self.function = None
        print(f'Leave {command}')
        if not success:
            if command == 'set_detect':
                self.gui.widget['canvas'].delete('all')
                self.gui.widget['palette'].delete('all')
            elif command == 'detect':
                self.gui.widget['canvas'].delete('all')
                self.gui.widget['palette'].delete('all')
                self.gui.widget['canvas'].configure(bg='black')
            elif command == 'all':
                self.video.close()
                cv2.destroyAllWindows()
                self.gui.window.destroy()
                exit()
            self.gui.widget['canvas'].update()
            self.gui.widget['palette'].update()
            return False
        else:
            return True


main = Touchable()
