import cv2
import os
import pandas as pd
import tkinter as tk
import PIL.Image
import PIL.ImageTk

# Filename pattern: Z1_1_A_B_-1_1_Y.tif
# 0 = Z1: experiment number
# 1 = 1: dpi (of 1, 3, 5, 7)
# 2 = A: plant (of A, B, C, D, E)
# 3 = B: type (of B/bulk, G/grind)
# 4 = -1: dilution (of 0/10^0, -1/10^-1, -2/10^-2, -3/10^-3)
# 5 = 1: droplet (of 1, 2, 3, 4, 5, 6)
# 6 = Y: fluorescence (of Y/sYFP, C/mCherry)


class AnalysisGui:
    def __init__(self, directory):
        self.data = []
        self.currentMetadata = []
        self.currentFile = ""
        self.colour_img = []
        self.contours = []
        self.initial_threshold = 100
        self.channel = 1
        self.color = (255, 255, 255)

        self.directory = directory
        self.fileList = os.listdir(self.directory)

        self.root = tk.Tk()
        self.canvas = tk.Canvas(self.root, width=1392, height=1040)
        self.canvas.pack()
        self._job = None
        self.slider = tk.Scale(self.root, from_=0, to=255,
                               length=1400,
                               orient="horizontal",
                               command=self.updateValue)
        self.slider.pack()
        self.button = tk.Button(self.root, text='Done',
                                command=self.saveNext)
        self.button.pack()
        self.button2 = tk.Button(self.root, text='Increase Contrast',
                                 command=self.changeContrastBrightness)
        self.button2.pack()
        self.button2.place(x=1200, y=1085)

        self.nextImage()
        self.root.mainloop()

    def updateValue(self, *_):
        if self._job:
            self.root.after_cancel(self._job)
        self._job = self.root.after(500, self._calculate_threshold)

    def _calculate_threshold(self):
        self._job = None
        threshold = int(self.slider.get())
        ret, thresh_img = cv2.threshold(self.blur_img, thresh=threshold, maxval=255, type=cv2.THRESH_BINARY)
        self.contours, _ = cv2.findContours(thresh_img, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_NONE)
        self.colour_img = cv2.cvtColor(self.img, cv2.COLOR_GRAY2BGR)
        cv2.drawContours(self.colour_img, contours=self.contours, contourIdx=-1, color=self.color, thickness=1)
        self.colour_img = cv2.putText(self.colour_img, str(len(self.contours)), (50, 50),
                                      cv2.FONT_HERSHEY_SIMPLEX, 1, color=self.color, thickness=2)
        self._display_image()

    def _display_image(self):
        self.tk_img = cv2.cvtColor(self.colour_img, cv2.COLOR_BGR2RGB)
        self.tk_img = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(self.tk_img))
        self.canvas.create_image(0, 0, image=self.tk_img, anchor=tk.NW)

    def saveNext(self):
        print(self.currentMetadata)
        print("Correct the automatic count of {0} (additions then subtractions)".format(len(self.contours)))
        add = self._getInt("Add: ")
        sub = self._getInt("Sub: ")
        value = len(self.contours) + add - sub
        print(value)

        threshold = self.slider.get()
        self.colour_img = cv2.putText(self.colour_img, 'Threshold = ' + str(threshold), (50, 100),
                                      cv2.FONT_HERSHEY_SIMPLEX, 1, color=self.color, thickness=2)

        self.colour_img = cv2.putText(self.colour_img, '+' + str(add) + ', -' + str(sub), (50, 150),
                                      cv2.FONT_HERSHEY_SIMPLEX, 1, color=self.color, thickness=2)
        cv2.imwrite(directory + 'annotated/' + self.currentFile.split('.')[0] + '.png', self.colour_img)

        self.currentMetadata.append(value)
        self.data.append(self.currentMetadata)
        self.nextImage()

    def _getInt(self, text):
        while True:
            try:
                int_input = int(input(text))
            except ValueError:
                continue
            else:
                return int_input

    def changeContrastBrightness(self):
        contrast = 1.2
        brightness = 0
        self.colour_img = cv2.addWeighted(self.colour_img, contrast, self.colour_img, 0, brightness)
        self._display_image()

    def nextImage(self):
        if not self.fileList:
            self._finish_list()
        else:
            self.currentFile = self.fileList.pop(0)
            if not self.currentFile.endswith(".tif"):
                self.nextImage()
            else:
                self._metadata_import()
                self.slider.set(self.initial_threshold)
                self._initialise_image()
                self._calculate_threshold()

    def _metadata_import(self):
        self.currentMetadata = self.currentFile.split('.')[0].split('_')
        if self.currentMetadata[6] == 'Y':
            self.initial_threshold = 27
            self.channel = 1
            self.color = (0, 255, 0)
        else:
            self.initial_threshold = 50
            self.channel = 2
            self.color = (0, 0, 255)

    def _initialise_image(self):
        self.img = cv2.imread(self.directory + self.currentFile)
        self.img = self.img[:, :, self.channel]
        self.blur_img = cv2.GaussianBlur(self.img, ksize=(9, 9), sigmaX=8, sigmaY=8)

    def _finish_list(self):
        df = pd.DataFrame(self.data, columns=["experiment", "dpi", "plant", "type", "dilution",
                                              "droplet", "fluorescence", "value"])
        print(df)
        df.to_csv(self.directory + 'counts.csv', index=False)

        self.root.destroy()


if __name__ == '__main__':
    base_directory = '/Users/aroney/OneDrive/PhD/Experiments/Colonisation Assay/'
    experiment_directory = '2019-07-01 Z3.1 wt vs che2/named_images/'
    directory = base_directory + experiment_directory
    if not os.path.exists(directory + 'annotated/'):
        os.mkdir(directory + 'annotated/')
    analysisgui = AnalysisGui(directory)
