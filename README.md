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

You may need to allow your terminal/IDE/etc to capture the contents of your display and control your computer, especially if on Mac.

## Troubleshooting

### Nothing happens.

You may need to run your Terminal/IDE/etc in administrator mode in order to allow control of the mouse/the ability to take screenshots. In addition, check that the entire game field is visible on screen when the program is running, including the green borders.
