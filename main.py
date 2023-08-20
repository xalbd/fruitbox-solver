import cv2
import numpy as np

# Load image
image = cv2.imread("img/test.png")

# Detect edges & contours
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
edged = cv2.Canny(gray, 50, 270)
contours, hierarchy = cv2.findContours(edged, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

# Find the largest contour (should be game window)
largest_contour = [0, 0, 0, 0]
for contour in contours:
    (x, y, w, h) = cv2.boundingRect(contour)
    if w * h > largest_contour[2] * largest_contour[3]:
        largest_contour = [x, y, w, h]

# Crop only apples from game window
x_offset, y_offset = int(0.09 * largest_contour[2]), int(0.12 * largest_contour[3])
game_window = [
    largest_contour[0] + int(0.09 * largest_contour[2]),
    largest_contour[1] + int(0.12 * largest_contour[3]),
    largest_contour[2] - 2 * int(0.09 * largest_contour[2]),
    largest_contour[3] - 2 * int(0.12 * largest_contour[3]),
]
gameplay = gray[
    game_window[1] : game_window[1] + game_window[3],
    game_window[0] : game_window[0] + game_window[2],
]

# Process apples to get black numbers over white background
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

# Form rows using morphological open and floodfill for numbering
row_structuring_element = cv2.getStructuringElement(cv2.MORPH_RECT, (1000, 1))
rows = cv2.morphologyEx(thresh, op=cv2.MORPH_OPEN, kernel=row_structuring_element)
row_count = 0
for r in range(rows.shape[0]):
    if rows[r][rows.shape[1] // 2] == 0:
        row_count += 1
        cv2.floodFill(rows, None, seedPoint=(rows.shape[1] // 2, r), newVal=row_count)
if row_count != 10:
    print(f"{row_count} rows found instead of 10, exiting")
    exit(1)

# Form columns using morphological open and floodfill for numbering
col_structuring_element = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1000))
cols = cv2.morphologyEx(thresh, op=cv2.MORPH_OPEN, kernel=col_structuring_element)
col_count = 0
for c in range(rows.shape[1]):
    if cols[rows.shape[0] // 2][c] == 0:
        col_count += 1
        cv2.floodFill(cols, None, seedPoint=(c, rows.shape[0] // 2), newVal=col_count)
if col_count != 17:
    print(f"{col_count} cols found instead of 17, exiting")
    exit(1)

# Load images of numbers 1-9
data = [cv2.imread(f"data/{i}.png", cv2.IMREAD_GRAYSCALE) for i in range(1, 10)]

# Grab contours of numbers
contours, hierarchy = cv2.findContours(thresh, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)

# Process each number and locate/store using pre-calculated rows/cols
values = np.zeros((10, 17))
for i, contour in enumerate(contours):
    # Skip contours that are inside other contours (may grab hole of an 8, for instance)
    if hierarchy[0][i][3] < 0:
        continue

    x, y, w, h = cv2.boundingRect(contour)
    grab = cv2.resize(thresh[y : y + h, x : x + w], (25, 35))

    decision, min_diff = 0, float("inf")
    for num in range(1, 10):
        matching_result = cv2.matchTemplate(grab, data[num - 1], cv2.TM_SQDIFF)
        min_val = cv2.minMaxLoc(matching_result)[0]
        if min_val < min_diff:
            min_diff = min_val
            decision = num

    values[rows[y + h // 2][x + w // 2] - 1][cols[y + h // 2][x + w // 2] - 1] = decision

print(values)
