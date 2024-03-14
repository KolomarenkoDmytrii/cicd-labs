import pygame
from dataclasses import dataclass
from pygame.math import Vector2


@dataclass
class Edges:
    """Dataclass for containing width and height of edges."""

    width: int
    height: int


class Label:
    """Class for drawing text strings."""

    def __init__(self, font: pygame.font.Font, position: Vector2, text: str = '', color: tuple = (0, 0, 0)):
        """Initialize the Label class object.

        Parameters
        ----------
        font : pygame.font.Font
            Font of the text.
        position : Vector2
            Position where the text label is placed.
        text : str, optional
            Actual text of the label, by default ''.
        color : tuple[int, int, int], optional
            Color of the text font, by default (0, 0, 0).
        """

        self.__font: pygame.font.Font = font
        self.__position: Vector2 = position
        self.__text: str = text
        self.color: tuple = color

        self.__text_image: pygame.Surface = None
        self.__text_image_rect: pygame.Rect = None
        self.__render()

    def get_rendered(self) -> tuple[pygame.Surface, pygame.Rect]:
        """Return a rendered image of the text and its rectangle.

        Returns
        -------
        tuple[pygame.Surface, pygame.Rect]
            Rendered image of the text and its rectangle.
        """

        return (self.__text_image, self.__text_image_rect)

    def set_text(self, text: str):
        """Update text of the label and update its rendered image and placement rectangle.

        Parameters
        ----------
        text : str
            New text for the label.
        """

        self.__text = text
        self.__render()

    def __render(self):
        """Render an image of the label text and get its placement rectangle."""

        self.__text_image: pygame.Surface = self.__font.render(self.__text, True, self.color)
        self.__text_image_rect: pygame.Rect = \
            self.__text_image.get_rect(x=self.__position.x, y=self.__position.y)
