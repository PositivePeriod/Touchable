from scipy import interpolate
from Function import *


class Canvas:
    def __init__(self):
        self.to_draw = []
        self.to_draw_image = None
        self.canvas = None

    def clear(self):
        self.to_draw.clear()

    def erase(self):
        if len(self.to_draw):
            self.to_draw.pop()

    def new_draw(self, command):
        self.to_draw.append(command)

    def set_canvas(self, canvas):
        self.canvas = canvas

    def pop(self):
        return self.to_draw.pop()

    def draw(self, scale, width_margin, height_margin):
        if self.to_draw_image is not None:
            self.canvas.create_image()  # TODO

        for obj in self.to_draw:
            color = color_type(obj[1], 'rgb', 'hex')
            size = obj[2]
            if obj[0] == 'interpolate':
                try:
                    tck = interpolate.splprep([numpy.array(obj[3]), numpy.array(obj[4])], s=0)[0]
                    u_new = numpy.arange(0, 1.001, 0.001)
                    out = interpolate.splev(u_new, tck)
                    inp = []
                    for i in range(len(out[0])):
                        x, y = convert_pos(scale, width_margin, height_margin, x=out[0][i], y=out[1][i])
                        inp.extend([x, y])
                    self.canvas.create_line(*inp, fill=color, width=obj[2])
                except TypeError as e:
                    points = []
                    for i in range(len(obj[3])):
                        point = convert_pos(scale, width_margin, height_margin, x=obj[3][i], y=obj[4][i])
                        points.extend(point)
                    self.canvas.create_line(*points, fill=color, width=obj[2])
                    if str(e) != 'm > k must hold':
                        print(e)
                finally:
                    continue
            elif obj[0] == 'line':
                p = tuple(obj[3][i] * scale + (width_margin if i % 2 == 0 else height_margin) for i in range(len(obj[3])))
                self.canvas.create_line(*p, fill=color, width=size)
                continue
            x1, y1 = convert_pos(scale, width_margin, height_margin, x=obj[3][0], y=obj[3][1])
            if obj[0] == 'point':
                self.canvas.create_oval(x1 - 1, y1 - 1, x1 + 1, y1 + 1, fill=color, outline=color, width=size)
                continue
            x2, y2 = convert_pos(scale, width_margin, height_margin, x=obj[4][0], y=obj[4][1])
            if obj[0] == 'rectangle':
                if x1 != x2 and y1 != y2:
                    x1_, y1_, x2_, y2_ = min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)
                    self.canvas.create_rectangle(x1_, y1_, x2_, y2_, outline=color, width=size)
            elif obj[0] == 'line':
                if obj[3] != obj[4]:
                    self.canvas.create_line(x1, y1, x2, y2, fill=color, width=size)
            elif obj[0] == 'circle':
                r = int(square_distance((x1, y1), (x2, y2), root=True))
                if r != 0:
                    self.canvas.create_oval(x1 - r, y1 - r, x1 + r, y1 + r, outline=color, width=size)
            else:
                print(f'Error; draw; {obj}')
