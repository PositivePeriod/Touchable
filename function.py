from tkinter import messagebox
from PIL import ImageTk, Image
from cv2 import cvtColor, COLOR_BGR2HSV, COLOR_HSV2BGR
from numpy import uint8, sum
from Constant import message
import numpy


def color_type(data, before, after):
    if before == 'bgr' and after == 'hsv':
        return [int(cvtColor(uint8([[data]]), COLOR_BGR2HSV)[0][0][i]) for i in range(3)]
    elif before == 'bgr' and after == 'hex':  # rgb hex
        return '#%02x%02x%02x' % (data[2], data[1], data[0])
    elif before == 'hsv' and after == 'bgr':
        return [int(cvtColor(uint8([[data]]), COLOR_HSV2BGR)[0][0][i]) for i in range(3)]
    elif before == 'hsv' and after == 'hex':
        bgr = [int(cvtColor(uint8([[data]]), COLOR_HSV2BGR)[0][0][i]) for i in range(3)]
        return '#%02x%02x%02x' % (bgr[2], bgr[1], bgr[0])
    elif before == 'rgb' and after == 'hex':  # rgb hex
        return '#%02x%02x%02x' % (int(data[0]), int(data[1]), int(data[2]))
    else:
        print(f'Error; color_type; {before} {after}')


def create_circular_mask(h, w, center=None, radius=None):
    if center is None:  # use the middle of the image
        center = (int(w/2), int(h/2))
    if radius is None:  # use the smallest distance between the center and image walls
        radius = min(center[0], center[1], w-center[0], h-center[1])

    y, x = numpy.ogrid[:h, :w]
    square_dist_from_center = (x - center[0])**2 + (y-center[1])**2
    mask = square_dist_from_center <= radius ** 2
    return mask


def center_color(image, x, y, rad):  # TODO need circle not rectangle but not important
    try:
        x1 = max(x-rad, 0)
        x2 = min(x+rad+1, image.shape[1])
        y1 = max(y - rad, 0)
        y2 = min(y + rad+1, image.shape[0])
        try:
            color = [int((sum(image[y1:y2, x1:x2, i]))/(x2-x1)/(y2-y1)) for i in range(3)]
            return color
        except TypeError as e:
            return image[y, x, :]
    except TypeError as e:
        print(f'AttributeError; center_color; {e}')
        return None


def square_distance(p1, p2, root=False):
    try:
        distance = (p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2
        if root:
            distance = distance**0.5
        return distance
    except TypeError as e:
        print(e)
        return -1


def update_hsv(hsv, hsv_range):
    lower_range = numpy.array([min(max(hsv[0] - hsv_range[0], 0), 179), min(max(hsv[1] - hsv_range[1], 70), 255), min(max(30, 0), 255)])
    upper_range = numpy.array([max(min(hsv[0] + hsv_range[0], 179), 0), max(min(255, 255), 0), max(min(255, 255), 0)])
    return lower_range, upper_range


def difference_weight(p1, p2, r1, r2, coor_dif, rad_dif):  # TODO change as priority function
    if abs(p1[0] - p2[0]) < coor_dif and abs(p1[1] - p2[1]) < coor_dif and abs(r1-r2) < rad_dif:
        pass


def fit_resize(w_img, h_img, w_frame, h_frame):
    scale = min(w_frame / w_img, h_frame / h_img)
    w_margin, h_margin = (w_frame - int(w_img * scale)) // 2, (h_frame - int(h_img * scale)) // 2
    # interpolation method can be changed but cv2.INTER_AREA is good when the image gets smaller
    return scale, w_margin, h_margin


def convert_pos(scale, width_margin, height_margin, x=None, y=None, relx=None, rely=None):
    if x is not None and y is not None:
        x, y = int(x * scale + width_margin), int(y * scale + height_margin)
        return x, y
    elif relx is not None and rely is not None:
        w, h = int(1280 * scale * relx + width_margin), int(720 * scale * rely + height_margin)
        return w, h


def pil_to_tkinter(pil_image):
    tkinter_image = ImageTk.PhotoImage(image=Image.fromarray(pil_image))
    return tkinter_image


def hsv_square_distance(color1, color2, only_h=False):
    dh = min(abs(color1[0] - color2[0]), 255 - abs(color1[0] - color2[0])) / (255.0/2)
    if only_h:
        return dh
    ds = abs(color1[1] - color2[1]) / 255.0
    dv = abs(color1[2] - color2[2]) / 255.0
    return dh**2+ds**2+dv**2


class Inform:
    def __init__(self, msg):
        messagebox.showinfo(title=msg, message=message[msg])
        '''
        self.root = root
        self.inform = Toplevel(self.root)
        self.inform.title(msg)
        self.inform.overrideredirect(False)
        self.inform.geometry(f'220x80+{self.root.winfo_width()//2-150}+{self.root.winfo_height()//2-50}')
        self.inform.resizable(False, False)
        textbox = Text(self.inform, height=6)
        textbox.place(relwidth=1, relheight=1)
        textbox.insert('1.0', message[msg])
        textbox.config(state='disabled', bg='black', fg='white')
        self.inform.mainloop()
        '''