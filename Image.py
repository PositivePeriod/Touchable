from tkinter import filedialog, messagebox
import cv2


class ImageManager:
    def __init__(self, master, init_dir):
        self.master = master
        self.init_dir = init_dir

    def screenshot(self, area=None):
        print('having problem')  # TODO
        '''
        # monitor = {"top": 0, "left": 0, "width": 500, "height": 100}
        with mss.mss() as sct:
            if area is None:
                image = sct.shot()
            else:
                image = np.array(sct.grab(area))
        return image
        '''

    def save(self, path=None):
        messagebox.showinfo('Image save', 'Just do screen capture :)')
        '''
        if self.master.function == 'detect':
            if path is None:
                tm = time.localtime(time.time())
                name = time.strftime('%Y-%m-%d %I:%M:%S', tm)
                counter = 0
                while os.path.isfile(self.directory+name+f'_{counter}.png'):
                    counter += 1
                path = self.directory+name+f'_{counter}.png'
            img = Image.fromarray(array) 
            img.save(self.directory+name+f'_{counter}.png')'''

    def open(self):
        if not self.master.pen.is_empty():
            file_name = filedialog.askopenfilename(initialdir=self.init_dir, title='Open image')
            if file_name == '':
                return False
            image = cv2.imread(file_name)
            self.master.detect(pen=None, color_reflect=0.01, back_image=image)