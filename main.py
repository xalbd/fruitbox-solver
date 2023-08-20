import cv2
import pytesseract
import numpy as np

# Load image
image = cv2.imread("img/game.png")

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

# Grab game window and resize to multiple of known canvas dimension
gameplay = gray[
    largest_contour[1] : largest_contour[1] + largest_contour[3],
    largest_contour[0] : largest_contour[0] + largest_contour[2],
]
resize_factor = 2.2
gameplay = cv2.resize(
    gameplay, (int(720 * resize_factor), int(470 * resize_factor)), interpolation=cv2.INTER_CUBIC
)
gameplay = gameplay[
    int(70 * resize_factor) : int(415 * resize_factor),
    int(69 * resize_factor) : int(632 * resize_factor),
]
char_width = gameplay.shape[1] // 17
char_height = gameplay.shape[0] // 10


# Process game window image to get black numbers over white background
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

# Process by individual character
# for i in range(10):
#     for j in range(17):
#         height_offset = int(0.1 * char_height)
#         width_offset = int(0.1 * char_width)
#         single = thresh[
#             i * char_height + height_offset : (i + 1) * char_height - 2 * height_offset,
#             j * char_width + width_offset : (j + 1) * char_width - 2 * width_offset,
#         ]
#         result = pytesseract.image_to_data(
#             single,
#             config="--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789",
#             output_type=pytesseract.Output.DICT,
#         )
#         print(result)

#         number_boxes = len(result["text"])
#         print(number_boxes)
#         for k in range(number_boxes):
#             (x, y, width, height) = (
#                 result["left"][k],
#                 result["top"][k],
#                 result["width"][k],
#                 result["height"][k],
#             )
#             single = cv2.rectangle(single, (x, y), (x + width, y + height), (0, 255, 0), 2)
#             single = cv2.putText(
#                 single,
#                 result["text"][k],
#                 (x, y + height + 20),
#                 cv2.FONT_HERSHEY_SIMPLEX,
#                 0.7,
#                 (0, 255, 0),
#                 2,
#             )
#             cv2.imshow(f"{i}, {j}", single)
#         cv2.waitKey(0)

contours, hierarchy = cv2.findContours(thresh, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
opt = [[[" "] for i in range(17)] for j in range(10)]
loc = 0
for i, cnt in enumerate(contours[1:]):
    if hierarchy[0][i][3] < 0:
        continue
    i += 1
    x, y, w, h = cv2.boundingRect(cnt)
    print(h)
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
    print(output)


# OCR for text (apple data)
result = pytesseract.image_to_data(
    thresh,
    config="--psm 6 --oem 3 -c tessedit_char_whitelist=0123456789",
    output_type=pytesseract.Output.DICT,
)
print(result)

number_boxes = len(result["text"])
for i in range(number_boxes):
    if True:
        (x, y, width, height) = (
            result["left"][i],
            result["top"][i],
            result["width"][i],
            result["height"][i],
        )
        thresh = cv2.rectangle(thresh, (x, y), (x + width, y + height), (0, 255, 0), 2)
        thresh = cv2.putText(
            thresh,
            result["text"][i],
            (x, y + height + 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2,
        )

cv2.imshow("image", thresh)
cv2.waitKey(0)
