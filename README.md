# About
The Arkanoid game. For more info about the game read 
[Wikipedia -- Arkanoid](https://en.wikipedia.org/wiki/Arkanoid).
For avaible command line argumets run `python main.py -h`.

# Controls
- *SPACE* to start the game or for resume / pause the game;
- *Q* for exit;
- *DELETE* for reset the game;
- *CTRL* for release the ball;
- *A* for moving platform to left;
- *D* for moving platform to right.

# Project structure
- `README.md`: this file.
- `main.py`: main exutable which start the game
- `game.py`: main game routine.
- `level.py`: create and manage level.
- `entity.py`: module for game objects.
- `helpers.py`: various helpers for other modules.
- `assets`: ddd
    + `ball.png`: image of the ball.
    + `platform.png`: image of the platform.
    + `block.png`: image of destroyable blocks.
    + `font.ttf`: font used for rendering text.

# Notes
Images of game objects are resized accordingly to app window resolution. Images
of blocks is colored in rainbow colors, so it is better that the basic block 
image has greyish color.

Also color of text font and top line which delimeters game counters and level
areas (and other similar drawings) is opposite to the background color, thus is
is equal to (in RGB): (255, 255, 255) - "background color value".
