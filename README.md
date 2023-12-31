# Fruitbox Solver

This bot utilizes Python and OpenCV to automatically solve the [Fruitbox](https://en.gamesaien.com/game/fruit_box/) game. The aim of the game is to surround sets of numbers with boxes such that the boxes have a total of exactly 10 inside.

## Game Notes

The bot can filter for possibly higher scoring games by noting the sum of all apples on the board. The game is generated such that the total is always a multiple of 10, meaning that we can use the simple heuristic that lower total score boards will generally lead to higher score games.

Given the size of the board (10x17), the average total apple sum is 850, with an estimated standard deviation of roughly 34 (assuming each apple is independently placed). Filtering out boards with a sum higher than 780 (roughly Z = -2) is an easy way to get a score of 140+ with this bot.

## Sample Run

This run filtered for a total less than or equal to 780. Total score was 140 at the end.

https://github.com/xalbd/fruitbox-solver/assets/119540449/03ad6846-4f5d-46e3-bb9f-3894514a3b80

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

## Troubleshooting

### Nothing happens/the game window is not detected.

You may need to run your Terminal/IDE/etc in administrator mode in order to allow control of the mouse/the ability to take screenshots. In addition, check that the entire game field is visible on screen when the program is running, including the green borders.

Finally, the usage of two monitors may hinder the bot's functionality due to screenshot limitations. Use one monitor only.
