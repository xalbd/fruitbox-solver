# Fruitbox Solver

This bot utilizes Python and OpenCV to automatically solve the [Fruitbox](https://en.gamesaien.com/game/fruit_box/) game. The aim of the game is to surround sets of numbers with boxes such that the boxes have a total of exactly 10 inside.

## Game Notes

The bot can filter for possibly higher scoring games by noting the sum of all apples on the board. The game is generated such that the total is always a multiple of 10, meaning that we can use the simple heuristic that lower total score boards will generally lead to higher score games.

Given the size of the board (10x17), the average total apple sum is 850, with an estimated standard deviation of roughly 34 (assuming each apple is independently placed). Filtering out boards with a sum higher than 780 (roughly Z = -2) is an easy way to get a score of 140+ with this bot.

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
