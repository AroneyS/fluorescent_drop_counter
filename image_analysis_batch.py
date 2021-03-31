import cv2
import numpy as np
import os
import pandas as pd

base_directory = '/Users/aroney/OneDrive/PhD/Experiments/Colonisation Assay/'
experiment_directory = '2019-05-21 Z2.1 wt vs che1/named_images/'
directory = base_directory + experiment_directory
if not os.path.exists(directory + 'annotated/'):
    os.mkdir(directory + 'annotated/')

# Filename pattern: Z1_1_A_B_-1_1_Y.tif
# 0 = Z1: experiment number
# 1 = 1: dpi (of 1, 3, 5, 7)
# 2 = A: plant (of A, B, C, D, E)
# 3 = B: type (of B/bulk, G/grind)
# 4 = -1: dilution (of 0/10^0, -1/10^-1, -2/10^-2, -3/10^-3)
# 5 = 1: droplet (of 1, 2, 3, 4, 5, 6)
# 6 = Y: fluorescence (of Y/sYFP, C/mCherry)


data = []
winname = 'Images'
cv2.namedWindow(winname)
cv2.moveWindow(winname, 1160, 30)
for filename in os.listdir(directory):
    if filename.endswith(".tif"):
        metadata = filename.split('.')[0].split('_')
        if metadata[6] == 'Y':
            thresh = 27
            channel = 1
            color = (0, 255, 0)
        else:
            thresh = 50
            channel = 2
            color = (0, 0, 255)

        img = cv2.imread(directory + filename)
        img = img[:, :, channel]
        blur_img = cv2.GaussianBlur(img, ksize=(9, 9), sigmaX=8, sigmaY=8)
        ret, thresh_img = cv2.threshold(blur_img, thresh=thresh, maxval=255, type=cv2.THRESH_BINARY)

        # Contours
        contours, hier = cv2.findContours(thresh_img, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_NONE)
        colour_img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        cv2.drawContours(colour_img, contours=contours, contourIdx=-1, color=color, thickness=1)
        colour_img = cv2.putText(colour_img, str(len(contours)), (50, 50),
                                 cv2.FONT_HERSHEY_SIMPLEX, 1, color=color, thickness=2)
        cv2.imshow(winname, colour_img)
        cv2.waitKey(500)

        print(metadata)
        print("Correct the automatic count of {0} (additions then subtractions)".format(len(contours)))
        add = None
        while True:
            try:
                add = int(input("Add: "))
            except ValueError: # Sanitise because I'm an idiot
                continue
            else:
                break

        sub = None
        while True:
            try:
                sub = int(input("Sub: "))
            except ValueError:
                continue
            else:
                break

        value = len(contours) + add - sub
        print(value)

        colour_img = cv2.putText(colour_img, '+' + str(add) + ', -' + str(sub), (50, 100),
                                 cv2.FONT_HERSHEY_SIMPLEX, 1, color=color, thickness=2)
        cv2.imwrite(directory + 'annotated/' + filename.split('.')[0] + '.png', colour_img)

        metadata.append(value)
        data.append(metadata)

df = pd.DataFrame(data, columns=["experiment", "dpi", "plant", "type", "dilution", "droplet", "fluorescence", "value"])
print(df)
df.to_csv(directory + 'counts.csv', index=False)

cv2.destroyAllWindows()
