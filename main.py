from game import Game
from helpers import Edges

Game(
    edges=Edges(700, 500),
    num_of_columns=10,
    num_of_rows=5,
    # background_color=(255, 255, 255)
    background_color=(0, 0, 0)
).run()
