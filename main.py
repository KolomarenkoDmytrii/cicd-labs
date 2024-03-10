"""Start game application."""

import argparse
from game import Game
from helpers import Edges


def main():
    """Run the game."""

    background_colors = {
        'black': (0, 0, 0),
        'white': (255, 255, 255),
        'darkcyan': (32, 88, 110)
    }

    parser = argparse.ArgumentParser(
        description='The Arkanoid game. For control keys see '
            'start / pause menu text'
    )

    parser.add_argument(
        '--columns',
        help='set number of columns of the blocks',
        type=int,
        default=10
    )
    parser.add_argument(
        '--rows',
        help='set number of rows of the blocks',
        type=int,
        default=5
    )
    parser.add_argument(
        '--background',
        help='set background color. Color of font, lines etc '
            'is opposite to backround color.',
        default='black',
        choices=background_colors.keys()
    )

    arguments = parser.parse_args()
    Game(
        edges=Edges(700, 500),
        num_of_columns=arguments.columns,
        num_of_rows=arguments.rows,
        background_color=background_colors[arguments.background]
    ).run()


if __name__ == '__main__':
    main()
