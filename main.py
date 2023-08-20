import cv2
import pytesseract
import numpy as np

# Load image
image = cv2.imread("img/game_big.png")

# Crop image slightly to remove edges of screen (may cause erroneous detection)
image_h, image_w = image.shape[0], image.shape[1]
crop = image[int(0.02 * image_h) : int(0.98 * image_h), int(0.02 * image_w) : int(0.98 * image_w)]

# Detect edges & contours
gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
edged = cv2.Canny(gray, 50, 270)
contours, hierarchy = cv2.findContours(edged, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

# Find the largest contour (should be game window)
largest_contour = [0, 0, 0, 0]
for contour in contours:
    (x, y, w, h) = cv2.boundingRect(contour)
    if w * h > largest_contour[2] * largest_contour[3]:
        largest_contour = [x, y, w, h]


# Offset game window to only see apples (no scoreboard)
x_offset, y_offset = int(0.09 * largest_contour[2]), int(0.12 * largest_contour[3])
largest_contour[0] += x_offset
largest_contour[1] += y_offset
largest_contour[2] -= 2 * x_offset
largest_contour[3] -= 2 * y_offset
gameplay = gray[
    largest_contour[1] : largest_contour[1] + largest_contour[3],
    largest_contour[0] : largest_contour[0] + largest_contour[2],
]

# Process game window image
ret, thresh = cv2.threshold(gameplay, 160, 255, cv2.THRESH_BINARY_INV)

num_components, labels, stats, centroids = cv2.connectedComponentsWithStats(~thresh, connectivity=4)
sizes = stats[:, cv2.CC_STAT_AREA]
max_label, max_size = 0, sizes[0]
for i in range(1, num_components):
    if sizes[i] > max_size:
        max_size = sizes[i]
        max_label = i

mask = np.zeros(labels.shape, dtype=np.uint8)
mask[labels == max_label] = 255
thresh = cv2.bitwise_xor(thresh, mask)
thresh = cv2.dilate(thresh, np.ones((3, 3), dtype=np.uint8))

contours, hierarchy = cv2.findContours(thresh, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
opt = [[[" "] for i in range(17)] for j in range(10)]
loc = 0
for i, cnt in enumerate(contours[1:]):
    if hierarchy[0][i][3] < 0:
        continue
    i += 1
    x, y, w, h = cv2.boundingRect(cnt)
    x_offset = int(w * 0.2)
    y_offset = int(h * 0.2)
    x -= x_offset
    y -= y_offset
    w += 2 * x_offset
    h += 2 * y_offset
    roi = thresh[y : y + h, x : x + w]
    output = pytesseract.image_to_string(
        roi,
        config="--psm 10 --oem 1 -c tessedit_char_whitelist=0123456789",
    )
    opt[loc // 17][loc % 17] = output
    loc += 1
    # print(output)
print(opt)
cv2.imshow("img", thresh)
cv2.waitKey(0)


# OCR for text (apple data)
result = pytesseract.image_to_string(
    thresh,
    config="--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789 -c preserve_interword_spaces=1",
)
print(result)

cv2.imshow("image", thresh)
cv2.waitKey(0)
