import pygame
from dataclasses import dataclass

@dataclass
class Edges:
    """Dataclass for containing width and height of edges.

    Attributes
    ----------
    width: int
        Width of top and bottom sides of the edges.
    height: int
        Height of left and right sides of the edges.
    """
    width: int
    height: int


class Label:
    """Class for drawing text strings.

    Attributes
    ----------
    __font: pygame.font.Font
        Font of the text.
    __position: pygame.Vector2
        Position where the text label is placed.
    __text: str
        Actual text of the label.
    __color: tuple[int, int, int]
        Color of a text font.
    __text_image: pygame.Surface
        Rendered image of text label.
    __text_image_rect: pygame.Rect
        Rectangle with position and width and lenght of rendered image
        of text label.
    """
    def __init__(self, font, position, text='', color=(0, 0, 0)):
        """Initalize the Label class object.

        Parameters
        ----------
        font: pygame.font.Font
            Font of the text.
        position: pygame.Vector2
            Position where the text label is placed.
        text: str
            Actual text of the label.
        color: tuple[int, int, int]
            Color of a text font.
        """
        self.__font = font
        self.__position = position
        self.__text = text
        self.color = color

        self.__text_image = None
        self.__text_image_rect = None
        self.__render()

    def get_rendered(self):
        """Return a rendered image of the text and its rectangle.

        Returns
        -------
        tuple[pygame.Surface, pygame.Rect]
        """
        return (self.__text_image, self.__text_image_rect)

    def set_text(self, text):
        """Update text of the label and update its rendered image and
            placementing rectangle.
        """
        self.__text = text
        self.__render()

    def __render(self):
        """Render an image of the label text and get its placementing
            rectangle.
        """
        self.__text_image = self.__font.render(self.__text, True, self.color)
        self.__text_image_rect = \
            self.__text_image.get_rect(x=self.__position.x, y=self.__position.y)
