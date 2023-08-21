import cv2
import numpy as np
import pyautogui
import time
import pyscreeze
import PIL

# Fix for pyscreeze bug, TODO: remove once bug is fixed
__PIL_TUPLE_VERSION = tuple(int(x) for x in PIL.__version__.split("."))
pyscreeze.PIL__version__ = __PIL_TUPLE_VERSION

# Pytautogui failsafe
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.15

while True:
    # Pause program and grab image
    time.sleep(1)
    image = cv2.cvtColor(np.array(pyautogui.screenshot()), code=cv2.COLOR_RGB2GRAY)

    # Test with static image
    # image = cv2.imread("img/game.png", flags=cv2.IMREAD_GRAYSCALE)

    # Detect edges & contours
    edge_detection = cv2.Canny(image, 50, 270)
    contours = list(
        cv2.findContours(edge_detection, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_SIMPLE)[0]
    )
    contours.sort(key=lambda x: cv2.boundingRect(x)[2] * cv2.boundingRect(x)[3], reverse=True)

    # Loop through contours biggest -> smallest while trying to find game window
    for contour in contours:
        bounding = cv2.boundingRect(contour)

        # Crop apples from bounding box, assuming we've found the game window
        game_window_x_offset, game_window_y_offset = int(0.09 * bounding[2]), int(
            0.12 * bounding[3]
        )
        game_window = [
            bounding[0] + game_window_x_offset,
            bounding[1] + game_window_y_offset,
            bounding[2] - 2 * game_window_x_offset,
            bounding[3] - 2 * game_window_y_offset,
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

        # Form columns using morphological open and floodfill to number 1-17
        col_structuring_element = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1000))
        cols = cv2.morphologyEx(thresh, op=cv2.MORPH_OPEN, kernel=col_structuring_element)
        col_count = 0
        for c in range(rows.shape[1]):
            if cols[rows.shape[0] // 2][c] == 0:
                col_count += 1
                cv2.floodFill(cols, None, seedPoint=(c, rows.shape[0] // 2), newVal=col_count)

        # Assumes that if the processed image has 10 rows and 17 columns, we have located the game window successfully
        if row_count == 10 and col_count == 17:
            print("located game window, beginning analysis")
            break
    else:
        continue
    break

# Load images of numbers 1-9
data = [cv2.imread(f"data/{i}.png", flags=cv2.IMREAD_GRAYSCALE) for i in range(1, 10)]

# Grab contours of numbers
contours, hierarchy = cv2.findContours(thresh, mode=cv2.RETR_CCOMP, method=cv2.CHAIN_APPROX_SIMPLE)

# Process each number and locate/store using pre-calculated rows/cols
pixel_ratio = pyautogui.screenshot().size[0] / pyautogui.size().width
values = np.zeros((10, 17, 3), dtype=np.uint16)
for i, contour in enumerate(contours):
    # Skip contours that are inside other contours (may grab hole of an 8, for instance)
    if hierarchy[0][i][3] < 0:
        continue

    # Grab selected number from bounding rectangle and resize to match sample images
    x, y, w, h = cv2.boundingRect(contour)
    grab = cv2.resize(thresh[y : y + h, x : x + w], (25, 35))

    decision = min(
        range(9), key=lambda x: np.min(cv2.matchTemplate(grab, templ=data[x], method=cv2.TM_SQDIFF))
    )
    values[rows[y + h // 2][x + w // 2] - 1][cols[y + h // 2][x + w // 2] - 1] = [
        decision + 1,
        (game_window[0] + x + w // 2) // pixel_ratio,
        (game_window[1] + y + h // 2) // pixel_ratio,
    ]

print(values)

unique, counts = np.unique(values[:, :, 0], return_counts=True)
print(dict(zip(unique, counts)))
