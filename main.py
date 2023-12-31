import cv2
import numpy as np
import pyautogui
import pyscreeze
import PIL

# Fix for pyscreeze bug
__PIL_TUPLE_VERSION = tuple(int(x) for x in PIL.__version__.split("."))
pyscreeze.PIL__version__ = __PIL_TUPLE_VERSION

# Pytautogui failsafe
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1

# Constants
ROWS = 10
COLS = 17

print("this tool can auto-reset for a good board")
print(
    "possible board scores come in jumps of 10, 850 is mean and std dev ~= 34, so <= 780 is good (Z ~= -2)"
)

while True:
    try:
        fruit_input = input(
            f"ENTER for no resetting or type a desired score ({ROWS * COLS} - {ROWS * COLS * 9}):"
        )
        fruit_limit = 0 if fruit_input == "" else int(fruit_input)
    except KeyboardInterrupt:
        exit()
    except:
        print("invalid input")
    else:
        if fruit_limit != 0 and (fruit_limit < ROWS * COLS or fruit_limit > ROWS * COLS * 9):
            print(f"out of range ({ROWS * COLS} - {ROWS * COLS * 9})")
        else:
            break

while True:
    while True:
        # Grab image
        print("grabbing image")
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
            # This means that rows array holds, for each pixel that could be part of an apple, the number of the row it is in
            row_structuring_element = cv2.getStructuringElement(cv2.MORPH_RECT, (1000, 1))
            rows = cv2.morphologyEx(thresh, op=cv2.MORPH_OPEN, kernel=row_structuring_element)
            row_count = 0
            for r in range(rows.shape[0]):
                if rows[r, rows.shape[1] // 2] == 0:
                    row_count += 1
                    cv2.floodFill(rows, None, seedPoint=(rows.shape[1] // 2, r), newVal=row_count)

            # Form columns using morphological open and floodfill to number 1-17
            col_structuring_element = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1000))
            cols = cv2.morphologyEx(thresh, op=cv2.MORPH_OPEN, kernel=col_structuring_element)
            col_count = 0
            for c in range(rows.shape[1]):
                if cols[rows.shape[0] // 2, c] == 0:
                    col_count += 1
                    cv2.floodFill(cols, None, seedPoint=(c, rows.shape[0] // 2), newVal=col_count)

            # Assumes that if the processed image has 10 rows and 17 columns, we have located the game window successfully
            if row_count == ROWS and col_count == COLS:
                print("located game window, beginning analysis")
                break
        else:
            print("game window not found")
            continue
        break

    # Load images of numbers 1-9
    data = [cv2.imread(f"data/{i}.png", flags=cv2.IMREAD_GRAYSCALE) for i in range(1, 10)]

    # Grab contours of numbers
    contours, hierarchy = cv2.findContours(
        thresh, mode=cv2.RETR_CCOMP, method=cv2.CHAIN_APPROX_SIMPLE
    )

    # Process each number and locate/store using pre-calculated rows/cols
    pixel_ratio = pyautogui.screenshot().size[0] / pyautogui.size().width
    values = np.zeros((ROWS, COLS, 3), dtype=np.uint16)
    for i, contour in enumerate(contours):
        # Skip contours that are inside other contours (may grab hole of an 8, for instance)
        if hierarchy[0, i, 3] < 0:
            continue

        # Grab selected number from bounding rectangle and resize to match sample images
        x, y, w, h = cv2.boundingRect(contour)
        grab = cv2.resize(thresh[y : y + h, x : x + w], (25, 35))

        decision = min(
            range(9),
            key=lambda x: np.min(cv2.matchTemplate(grab, templ=data[x], method=cv2.TM_SQDIFF)),
        )
        values[rows[y + h // 2][x + w // 2] - 1, cols[y + h // 2][x + w // 2] - 1] = [
            decision + 1,
            (game_window[0] + x + w // 2) // pixel_ratio,
            (game_window[1] + y + h // 2) // pixel_ratio,
        ]

    # Output generated data
    print(values)
    unique, counts = np.unique(values[:, :, 0], return_counts=True)
    print(dict(zip(unique, counts)))
    print(f"total: {np.sum(counts * unique)}")

    # Activate gameplay window
    pyautogui.leftClick(values[0, 0, 1], values[0, 0, 2])

    if fruit_limit == 0 or np.sum(counts * unique) <= fruit_limit:
        break
    else:
        print("resetting")
        pyautogui.leftClick(values[9, 0, 1], values[9, 0, 2] + 2 * h)  # reset button
        pyautogui.leftClick(values[5, 4, 1], values[5, 4, 2])  # play button
        pyautogui.moveTo(10, 10)  # avoid pyautogui failsafe while remaining out of screenshot

# Loop, selecting boxes that use the smallest number of apples possible
drag_x_offset, drag_y_offset = int(0.3 * w), int(0.3 * h)
score, target_number_apples = 0, 2
while True:
    found_selection = False
    print(f"\ntarget: {target_number_apples} apples")
    for r in range(ROWS):
        for c in range(COLS):
            for r_size in range(1, ROWS - r + 1):
                for c_size in range(1, COLS - c + 1):
                    if found_selection and target_number_apples > 2:
                        break

                    section = values[r : r + r_size, c : c + c_size, 0]
                    if np.count_nonzero(section) > target_number_apples or np.sum(section) > 10:
                        break

                    elif (
                        np.count_nonzero(section) == target_number_apples
                        and np.sum(section) == 10
                        and np.count_nonzero((section[0, :])) != 0
                        and np.count_nonzero((section[:, 0])) != 0
                    ):
                        print(np.matrix(section))
                        section.fill(0)
                        pyautogui.moveTo(
                            values[r, c, 1] - drag_x_offset, values[r, c, 2] - drag_y_offset
                        )
                        pyautogui.dragTo(
                            values[r + r_size - 1, c + c_size - 1, 1] + drag_x_offset,
                            values[r + r_size - 1, c + c_size - 1, 2] + drag_y_offset,
                            duration=0.2,
                            button="left",
                        )
                        score += target_number_apples
                        found_selection = True

    if not found_selection:
        print(f"could not find selection with {target_number_apples} apples")
        target_number_apples += 1

    if found_selection and target_number_apples > 2:
        print(f"found selection with {target_number_apples}, dropping to 2")
        target_number_apples = 2

    if target_number_apples == 11:
        print(f"can't find any more selections\nscore: {score}")
        break
