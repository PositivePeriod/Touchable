import tkinter
from tkinter import messagebox, simpledialog
from Function import Inform


class GUI:
    def __init__(self, master):
        self.master = master
        self.canvas = self.master.canvas
        self.pen = self.master.pen
        self.widget = {}

        self.window = tkinter.Tk()
        self.window.configure(bg='black')
        self.window.title("Touchable")
        self.window.geometry("800x500+100+100")
        self.window.minsize(400, 250)
        self.window.resizable(True, True)
        self.window.protocol("WM_DELETE_WINDOW", self.master.exit)
        self.window.update()

    def start_gui(self):
        self.widget['canvas_frame'] = tkinter.Frame(self.window, bg='black', bd=0)
        self.widget['canvas_frame'].config(highlightthickness=0)
        self.widget['canvas_frame'].place(relwidth=0.9, relheight=1.0)
        self.widget['canvas_frame'].bind('<Configure>', lambda x: self.resize())

        self.widget['canvas'] = tkinter.Canvas(self.widget['canvas_frame'], bg='black', bd=0)
        self.widget['canvas'].config(highlightthickness=0)
        self.canvas.set_canvas(self.widget['canvas'])
        self.resize()

        self.widget['palette'] = tkinter.Canvas(self.window, bg='black', bd=0)
        self.widget['palette'].place(relx=0.9, rely=0, relwidth=0.1, relheight=0.1)

        self.widget['listbox_var'] = tkinter.StringVar(value=self.pen.get_pens_name())
        self.widget['listbox'] = tkinter.Listbox(self.window, selectmode='single', bg='white', bd=0, height=0,
                                                 listvariable=self.widget['listbox_var'], activestyle='none',
                                                 selectbackground='red', selectforeground='white', state='disabled')
        self.widget['listbox'].xview()
        self.widget['listbox'].place(relx=0.9, rely=0.1, relwidth=0.1, relheight=0.9)

        self.window.config(menu=self.make_bar())
        self.window.mainloop()

    def resize(self):
        self.widget['canvas_frame'].update()
        scale = min(self.widget['canvas_frame'].winfo_width() / 1280,
                    self.widget['canvas_frame'].winfo_height() / 720)
        width_margin = (self.widget['canvas_frame'].winfo_width() - int(1280 * scale)) // 2
        height_margin = (self.widget['canvas_frame'].winfo_height() - int(720 * scale)) // 2
        p = {'x': width_margin, 'y': height_margin, 'width': int(1280 * scale), 'height': int(720 * scale)}
        self.widget['canvas'].place(**p)

    def make_bar(self):
        bar_data = \
            [
                ['File', [['New', lambda: self.canvas.clear()], ['Open', self.master.image_manager.open],
                          ['Save', self.master.image_manager.save], None, ['Exit', self.master.exit]]],
                ['Camera', [
                     ['Start', lambda: self.master.video.set_camera('on')],
                     ['Stop', lambda: self.master.video.set_camera('off')],
                     ['Show', self.master.show_camera]]],
                ['Detection', [['Start', self.master.detect], ['Stop', self.master.stop_detect]]],
                ['Pens', [['Make', self.master.set_detect], ['Erase', self.erase_pen], ['Use', self.change_pen],
                          None, ['Save', self.pen.save], ['Load', lambda: self.pen.load(self.master)]]],
                ['Pen', [['Color', lambda: self.pen.change_color(self.master)],
                         ['Size', lambda: self.pen.change_size(self.master)]]],
                ['Help', [['Help', lambda: Inform('Help')],
                          ['About', lambda: Inform('About')]]]
            ]
        bar_widget = tkinter.Menu(self.window)
        for menu in bar_data:
            temp_menu = tkinter.Menu(bar_widget, tearoff=False, title=menu[0])
            for command in menu[1]:
                if type(command) == str:
                    temp_menu.add_command(label=command)
                elif command is None:
                    temp_menu.add_separator()
                else:
                    temp_menu.add_command(label=command[0], command=command[1])
            bar_widget.add_cascade(label=menu[0], menu=temp_menu)
        return bar_widget

    def change_pen(self):
        if self.master.function == 'detect':
            while True:
                name = simpledialog.askstring('Change pen', 'Write pen name')
                if name is None:
                    return False
                elif name in self.pen.get_pens_name():
                    if name != self.master.var['pen'].name:
                        self.master.stop_detect(reset_drawing=False)
                        self.master.detect(pen=self.pen.get_pen(name))
                        self.master.key.event = None
                    return True
                else:
                    messagebox.showwarning('Change pen', 'Invalid pen name')

    def erase_pen(self):
        if self.master.function is None or self.master.function == 'detect':
            while True:
                name = simpledialog.askstring('Change pen', 'Write pen name')
                if name is None:
                    return False
                elif name in self.pen.get_pens_name():
                    if self.master.function == 'detect' and name == self.master.var['pen'].name:
                        self.master.stop_detect(reset_drawing=False)
                        self.master.key.event = None
                    del self.pen.access_pens_data()[name]
                    self.master.gui.widget['listbox_var'].set(self.master.pen.get_pens_name())
                    return True
                else:
                    messagebox.showwarning('Change pen', 'Invalid pen name')