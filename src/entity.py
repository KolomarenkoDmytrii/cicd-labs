import pygame
from pygame.sprite import Sprite
from pygame.math import Vector2


class Entity(Sprite):
    """Base class for game objects."""

    def __init__(self, image: pygame.Surface, rect: pygame.Rect):
        """Initialize the entity object.

        Parameters
        ----------
        image : pygame.Surface
            The image of the entity.
        rect : pygame.Rect
            The rectangle that contains position and borders of the entity.
        """
        super().__init__()
        self.image = image
        self.rect = rect

    def is_collided_with(self, other: "Entity") -> bool:
        """Check if the entity is collided with another entity.

        Parameters
        ----------
        other : Entity
            The other entity, for which collision check is done.

        Returns
        -------
        bool
            Returns True if there is a collision between self and other, False otherwise.
        """
        return pygame.sprite.collide_rect(self, other)


class MovableEntity(Entity):
    """Base class for movable entities."""

    def __init__(self, image: pygame.Surface, rect: pygame.Rect, speed: Vector2):
        """Initialize the movable entity object.

        Parameters
        ----------
        image : pygame.Surface
            The image of the entity.
        rect : pygame.Rect
            The rectangle that contains position and borders of the entity.
        speed : Vector2
            The speed vector of the entity.
        """
        super().__init__(image, rect)
        self.speed = speed

    def move(self):
        """Move the entity."""
        self.rect.move_ip(self.speed.x, self.speed.y)


class Block(Entity):
    """Class for destroyable blocks."""

    def __init__(self, image: pygame.Surface, rect: pygame.Rect):
        """Initialize the block object.

        Parameters
        ----------
        image : pygame.Surface
            The image of the block.
        rect : pygame.Rect
            The rectangle that contains position and borders of the block.
        """
        super().__init__(image, rect)
        self.__is_destroyed = False

    def is_destroyed(self) -> bool:
        """Return whether the block is destroyed or not.

        Returns
        -------
        bool
            Returns True if the block is destroyed, False otherwise.
        """
        return self.__is_destroyed

    def set_is_destroyed(self):
        """Mark the block as destroyed."""
        self.__is_destroyed = True


class Ball(MovableEntity):
    """Class for ball entity."""

    def __init__(self, image: pygame.Surface, rect: pygame.Rect, speed: Vector2):
        """Initialize the ball object.

        Parameters
        ----------
        image : pygame.Surface
            The image of the ball.
        rect : pygame.Rect
            The rectangle that contains position and borders of the ball.
        speed : Vector2
            The speed vector of the ball.
        """
        super().__init__(image, rect, speed)


class Platform(MovableEntity):
    """Class for platform entity.

    Note: Platform moves only left or right, so vertical speed is ignored.
    """

    def __init__(self, image: pygame.Surface, rect: pygame.Rect, speed: Vector2):
        """Initialize the platform object.

        Parameters
        ----------
        image : pygame.Surface
            The image of the platform.
        rect : pygame.Rect
            The rectangle that contains position and borders of the platform.
        speed : Vector2
            The speed vector of the platform.
        """
        super().__init__(image, rect, speed)

    def move(self):
        """Move the platform left or right."""
        self.rect.move_ip(self.speed.x, 0)


def adjust_on_x_collision(movable_entity: MovableEntity, entity: Entity) -> None:
    """Process collisions on X axis between movable entity and other entity and update their positions and
    speeds.

    Parameters
    ----------
    movable_entity : entity.MovableEntity
        Movable entity which has collision on X axis.
    entity : entity.Entity
        Any other entity with which movable entity has collided.
    """
    # if collides on the left side
    if entity.rect.left < movable_entity.rect.right < entity.rect.right:
        movable_entity.rect.right = entity.rect.left
    # if collides on the right side
    else:
        movable_entity.rect.left = entity.rect.right

    movable_entity.speed.x = -movable_entity.speed.x


def adjust_on_y_collision(movable_entity: MovableEntity, entity: Entity) -> None:
    """Process collisions on Y axis between movable entity and other entity and
        update their positions and speeds.

    Parameters
    ----------
    movable_entity : entity.MovableEntity
        Movable entity which has collision on Y axis.
    entity : entity.Entity
        Any other entity with which movable entity has collided.
    """
    # if collides on the top side
    if movable_entity.rect.top < entity.rect.top < movable_entity.rect.bottom:
        movable_entity.rect.bottom = entity.rect.top
    # if collides on the bottom side
    else:
        movable_entity.rect.top = entity.rect.bottom

    movable_entity.speed.y = -movable_entity.speed.y
