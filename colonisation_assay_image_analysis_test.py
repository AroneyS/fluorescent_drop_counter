import cv2

input_directory = '/Users/aroney/OneDrive/PhD/Experiments/Colonisation Assay/'
experiment = '2019-04-09 Z1.1 mCherry vs YFP check/test_image_analysis/'

# merge image
r = cv2.imread(input_directory + experiment + 'image0012.tif', 0)  # red
g = cv2.imread(input_directory + experiment + 'image0013.tif', 0)  # green
merged = cv2.merge((g, g, r))
merged[:, :, 0] = 0  # remove b
cv2.imwrite(input_directory + experiment + 'merged.png', merged)

number = '17'
img = cv2.imread(input_directory + experiment + 'image00' + number + '.tif', 0)
img = cv2.GaussianBlur(img, ksize=(9, 9), sigmaX=8, sigmaY=8)

# thresh = 16 for YFP, 20 for mCherry
hello, timg = cv2.threshold(img, thresh=16, maxval=255, type=cv2.THRESH_BINARY)
cv2.imwrite(input_directory + experiment + 'threshold00' + number + '.png', timg)
cimg = cv2.cvtColor(timg, cv2.COLOR_GRAY2BGR)

# Contours
contours, hier = cv2.findContours(timg, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_NONE)
print('Number of contours: {0}'.format(len(contours)))
cv2.drawContours(cimg, contours=contours, contourIdx=-1, color=(0, 255, 0), thickness=2)
cv2.imwrite(input_directory + experiment + 'contours00' + number + '.png', cimg)

winnname = "Test"
cv2.namedWindow(winnname)
cv2.moveWindow(winnname, 1150, 30)
cv2.imshow(winnname, cimg)
cv2.waitKey()
cv2.destroyAllWindows()
