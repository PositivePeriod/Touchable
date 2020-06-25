import json
import os
from tkinter import colorchooser, simpledialog, messagebox, filedialog


class Pen:
    def __init__(self, name=None, hsv=None, color=(0, 0, 0), size=5, data=None):
        if name is not None and hsv is not None:
            hsv, color, size = tuple(hsv), tuple(color), int(size)
            self.name = name
            self.hsv = hsv
            self.color = color  # RGB
            self.size = size
        elif data is not None:
            self.name, self.hsv, self.color, self.size = data
        else:
            raise Exception

    def access_hsv(self, hsv=None):
        if hsv is None:
            return self.hsv
        else:
            self.hsv = hsv

    def access_color(self, color=None, chooser=False):
        if chooser is True:
            color_ = (int(self.color[0]), int(self.color[1]), int(self.color[2]))
            rgb, web_color = colorchooser.askcolor(title='Pen color', initialcolor=color_)
            if rgb is not None:
                self.color = rgb
                return True
            else:
                return False
        elif color is None:
            return self.color
        else:
            self.color = color

    def access_size(self, size=None, chooser=False):
        if chooser is True:
            while True:
                size = simpledialog.askstring('Pen size', 'Change Pen size')
                if size is None:
                    return False
                try:
                    size = int(size)
                    if 1 <= size <= 30:
                        self.size = size
                        return True
                    else:
                        raise ValueError
                except ValueError:
                    messagebox.showwarning('Pen size', 'Enter integer between 1 to 30')
        elif size is None:
            return self.size
        else:
            self.size = size

    def data_list(self):
        return [self.name, self.hsv, self.color, self.size]


class Pens:
    def __init__(self, init_dir):
        self.init_dir = init_dir
        self.data = {}

    def make_pen(self, master):
        blacklist = self.get_pens_name()
        while True:
            name = simpledialog.askstring('Pen maker', 'Pen name')
            if name is None:
                return False
            elif name in blacklist:
                messagebox.showwarning('Pen maker', 'The pen name already exists')
            elif name == "":
                messagebox.showwarning('Pen maker', 'Write your own pen name')
            else:
                break
        self.add_pen(name=name, hsv=master.var['pick_hsv'], color=(0, 0, 0), size=5)
        self.get_pen(name).access_color(chooser=True)
        master.gui.widget['listbox_var'].set(master.pen.get_pens_name())
        master.key.event = None
        return True

    def add_pen(self, name=None, hsv=None, color=(0, 0, 0), size=5, data=None):
        if (name is None or hsv is None) and data is None:
            return [False, 'unfilled']
        elif name not in self.data.keys():
            if data is not None:
                self.data[name] = Pen(data=data)
            else:
                print(name, hsv, color, size)
                self.data[name] = Pen(name=name, hsv=hsv, color=color, size=size)
            return [True]
        else:
            return [False, 'same name']

    def get_pen(self, name=None):
        if self.is_empty():
            return None
        elif name is not None:
            if name in self.data.keys():
                return self.data[name]
        else:
            return self.data[list(self.data.keys())[0]]

    def load(self, master):
        file_name = filedialog.askopenfilename(initialdir=self.init_dir, title='Load pen data')
        if file_name == '':
            return False
        with open(file_name, 'r+') as f:
            json_data = json.load(f)
            for pen in json_data.values():
                self.add_pen(name=pen[0], hsv=pen[1], color=pen[2], size=pen[3])
        master.gui.widget['listbox_var'].set(master.pen.get_pens_name())

    def save(self):
        dir_name = filedialog.askdirectory(initialdir=self.init_dir, title='Save pen data')
        if dir_name == '':
            return False
        file_name = simpledialog.askstring('Save pen data', 'Write file name')
        if file_name is None:
            return False
        path = os.path.join(dir_name, file_name+'.json')
        json_data = {}
        for pen in self.data.values():
            json_data[pen.name] = pen.data_list()
        with open(path, "w") as json_file:
            json.dump(json_data, json_file)

    def get_pens_name(self):
        return list(self.data.keys())

    def access_pens_data(self):
        return self.data

    def is_empty(self):
        return len(self.data) == 0

    def change_color(self, master):
        print('change_color')
        print(master.function)
        if master.function == 'detect':
            pen = master.var['pen']
            print('123')
            success = pen.access_color(chooser=True)
            if success:
                master.key.event = None

    def change_size(self, master):
        if master.function == 'detect':
            pen = master.var['pen']
            success = pen.access_size(chooser=True)
            if success:
                master.key.event = None


def reset_pen_data(direc):
    # format in './data/pen_data_{ }.json'
    if direc[:15] == './data/pen_data' and direc[-5:] == '.json':
        if os.path.isfile(direc):
            os.remove(direc)


if __name__ == '__main__':
    '''test_directory = './data/pen_data_test.json'
    reset_pen_data(test_directory)
    a = Pens(test_directory)
    a.add_pen('name', [1, 3, 5], (2, 3, 5), 5)
    a.data['name'].access_color(chooser=True)
    print(a.data['name'].data_list())
    a.data['name'].access_hsv([4, 6, 8])
    a.data['name'].access_color([3, 4, 5])
    a.data['name'].access_size(8)
    print(a.data['name'].data_list())
    # a.save()
    b = Pens(test_directory)
    # b.load()
    print(b.data['name'].data_list())
    reset_pen_data(test_directory)'''