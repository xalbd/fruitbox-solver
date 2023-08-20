# FruitBox Solver

This bot utilizes Python and OpenCV to automatically solve the [FruitBox](https://en.gamesaien.com/game/fruit_box/) game. The aim of the game is to surround sets of numbers with boxes such that the boxes have a total of exactly 10 inside.

## Installation/Usage

Usage requires Python 3.11. Install the requirements with

```
pip3 install -r requirements.txt
```

Make the game window as large as possible while making sure the entire green border of the playfield is visible on screen.

Run the bot with

```
python3 main.py
```

You may need to allow your terminal/IDE/etc to capture the contents of your display.

## Troubleshooting

#### An erronous number of rows/columns of apples is detected even though the game is open

This program processes images of the entire screen and assumes the largest bounding box of any contour detected by OpenCV is the game window. Detecting the wrong number of rows/columns of apples could indicate this process is generating an incorrect location for the game window.

To fix, make the game window as large as possible while making sure the entire green border of the playfield is visible on screen.

This is most easily accomplished by opening the game in a full-screen browser window, hitting the play button, alt-tabbing to run the program, and immediately alt-tabbing back.
