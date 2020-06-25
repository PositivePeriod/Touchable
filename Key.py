from function import square_distance, color_type


class Key:
    def __init__(self, master, canvas):
        self.canvas = canvas
        self.master = master
        self.window = master.gui.window
        self.function = None
        self.event = None
        self.pos = None
        self.mark = None

    def key_map(self, function):
        self.function = function
        if self.function == 'set_detect':
            self.window.bind('<space>', self.key)
            self.window.bind('<c>', self.key)
        elif self.function == 'detect':
            self.window.bind('<p>', self.key)
            self.window.bind('<c>', self.key)
            self.window.bind('<i>', self.key)
            self.window.bind('<l>', self.key)
            self.window.bind('<r>', self.key)
            self.window.bind('<z>', self.key)
            self.window.bind('<e>', self.key)
            self.window.bind('<space>', self.key)

    def access_event(self, event=None):
        if event is None:
            return self.event
        self.event = event

    def access_pos(self, pos=None):
        if pos is None:
            return self.pos
        self.pos = pos

    def key(self, event):
        print(event, self.function)
        if self.function == 'set_detect':
            if event.keysym == 'space' and self.master.var['clicked']:
                self.master.var['pick_hsv'] = self.master.var['hsv']
                self.master.var['pick_roi'] = self.master.var['roi']
            elif event.keysym == 'c':
                self.master.var['run'] = False

        elif self.function == 'detect':
            if event.keysym == 'z':
                self.canvas.erase()
                self.event = None
            elif event.keysym == 'e':
                self.canvas.clear()
                self.event = None
            elif event.keysym == 'space':
                self.event = None
            if self.pos is not None:
                try:
                    pen = self.master.var['pen']
                    color = pen.access_color()
                    size = pen.access_size()
                    if event.keysym == 'p':
                        self.canvas.new_draw(['point', color, size, self.pos])
                        self.event = None

                    elif square_distance(self.pos, self.mark) != 0:
                        if event.keysym == 'c':
                            if self.event == '_c':
                                self.canvas.new_draw(['circle', color, size, self.mark, self.pos])
                                self.event = None
                            else:
                                self.event = '_c'
                        elif event.keysym == 'i':
                            if self.event == '__i':
                                inter = self.canvas.pop()
                                inter[3].append(self.pos[0])
                                inter[4].append(self.pos[1])
                                self.canvas.new_draw(inter)
                            elif self.event == '_i':
                                x = [self.mark[0], self.pos[0]]
                                y = [self.mark[1], self.pos[1]]
                                self.canvas.new_draw(['interpolate', color, size, x, y])
                                self.event = '__i'
                            else:
                                self.event = '_i'
                        elif event.keysym == 'l':
                            if self.event == '__l':
                                inter = self.canvas.pop()
                                inter[3].extend(self.pos)
                                self.canvas.new_draw(inter)
                            elif self.event == '_l':
                                p = self.mark + self.pos
                                self.canvas.new_draw(['line', color, size, p])
                                self.event = '__l'
                            else:
                                self.event = '_l'

                        elif event.keysym == 'r':
                            if self.event == '_r':
                                self.canvas.new_draw(['rectangle', color, size, self.mark, self.pos])
                                self.event = None
                            else:
                                self.event = '_r'
                    self.mark = self.pos
                except AttributeError as e:
                    print('AttributeError; key', e)
                    return False
