# FruitBox Solver

This auto-playing bot utilizes Python and OpenCV to automatically solve the [FruitBox](https://en.gamesaien.com/game/fruit_box/) game. The aim of the game is to surround sets of numbers with boxes such that the boxes have a total of exactly 10 inside.

## Installation/Usage

Usage requires Python 3.11. Install the requirements with

```
pip3 install requirements.txt
```

Run the program with

```
python3 main.py
```

## Troubleshooting

This program uses OpenCV to process images of the entire screen in order to isolate the game window. The game window is located by finding the largest bounding box of any contour located by OpenCV. Thus, if the program is not working, make sure the game window is as large as possible while still fitting entirely on the screen, including the green border around the playfield.
