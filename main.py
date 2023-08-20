import cv2
import numpy as np
import pyautogui
import time
import pyscreeze
import PIL

# Fix for pyscreeze bug, TODO: remove once bug is fixed
__PIL_TUPLE_VERSION = tuple(int(x) for x in PIL.__version__.split("."))
pyscreeze.PIL__version__ = __PIL_TUPLE_VERSION

# Pause program to allow user to start game/switch windows and take screenshot
# time.sleep(2)
# image = cv2.cvtColor(np.array(pyautogui.screenshot()), code=cv2.COLOR_RGB2GRAY)

# Test with static image
image = cv2.imread("img/test_2.png", flags=cv2.IMREAD_GRAYSCALE)

# Detect edges & contours
edge_detection = cv2.Canny(image, 50, 270)
contours = cv2.findContours(edge_detection, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[0]

# Find the largest contour (should be game window)
largest_contour = cv2.boundingRect(
    sorted(contours, key=lambda x: cv2.boundingRect(x)[2] * cv2.boundingRect(x)[3])[-1]
)

# Crop apples from game window
game_window_x_offset, game_window_y_offset = int(0.09 * largest_contour[2]), int(
    0.12 * largest_contour[3]
)
game_window = [
    largest_contour[0] + game_window_x_offset,
    largest_contour[1] + game_window_y_offset,
    largest_contour[2] - 2 * game_window_x_offset,
    largest_contour[3] - 2 * game_window_y_offset,
]
gameplay = image[
    game_window[1] : game_window[1] + game_window[3],
    game_window[0] : game_window[0] + game_window[2],
]

# Process apples to get black numbers over white background
thresh = cv2.threshold(gameplay, 160, 255, cv2.THRESH_BINARY_INV)[1]
cv2.floodFill(thresh, None, seedPoint=(0, 0), newVal=255)

# Form rows using morphological open and floodfill to number 1-10
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

# Form columns using morphological open and floodfill to number 1-17
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

    # Grab selected number from bounding rectangle and resize to match sample images
    x, y, w, h = cv2.boundingRect(contour)
    grab = cv2.resize(thresh[y : y + h, x : x + w], (25, 35))

    decision = min(range(9), key=lambda x: np.min(cv2.matchTemplate(grab, data[x], cv2.TM_SQDIFF)))
    values[rows[y + h // 2][x + w // 2] - 1][cols[y + h // 2][x + w // 2] - 1] = decision + 1

print(values)
