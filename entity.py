import pygame


class Entity(pygame.sprite.Sprite):
    """Base class for game objects.

    Attributes
    ----------
    image: pygame.Surface
        The image of the entity.
    rect: pygame.Rect
        The rectangle that contains position and borders of the entity.
    """

    def __init__(self, image, rect):
        """Initalize the entity object.

        Parameters
        ----------
        image: pygame.Surface
            The image of the entity.
        rect: pygame.Rect
            The rectangle that contains position and borders of the entity.
        """
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = rect

    def is_collided_with(self, other):
        """Check if the entity is collided with other entity.

        Parameters
        ----------
        other: Entity
            The other entity, for which collision check is doing.

        Returns
        ------
        bool
            If there is collision between `self` and `other`,
            `True` will be returned. Otherwise `False` will be returned.
        """
        return pygame.sprite.collide_rect(self, other)


class MovableEntity(Entity):
    """Base class for movable entities.

    Attributes
    ----------
    speed: pygame.Vector2
        The speed vector of the entity
    """

    def __init__(self, image, rect, speed):
        """Initalize the movable entity object.

        Parameters
        ----------
        image: pygame.Surface
            The image of the entity.
        rect: pygame.Rect
            The rectangle that contains position and borders of the entity.
        speed: pygame.Vector2
            The speed vector of the entity.
        """
        Entity.__init__(self, image, rect)
        self.speed = speed

    def move(self):
        """Move the entity."""
        self.rect.move_ip(self.speed.x, self.speed.y)


class Block(Entity):
    """Class for destroyable blocks."""

    def __init__(self, image, rect):
        Entity.__init__(self, image, rect)
        self.is_destroyed = False

    def is_destroyed(self):
        """Return whether the block is destroyed or not."""
        return self.is_destroyed

    def set_is_destroyed(self):
        """Mark the block destroyed."""
        self.is_destroyed = True


class Ball(MovableEntity):
    """Class for ball entity."""

    def __init__(self, image, rect, speed):
        """Initalize the ball object.

        Parameters
        ----------
        image: pygame.Surface
            The image of the ball.
        rect: pygame.Rect
            The rectangle that contains position and borders of the ball.
        speed: pygame.Vector2
            The speed vector of the ball.
        """
        MovableEntity.__init__(self, image, rect, speed)


class Platform(MovableEntity):
    """Class for platform entity.

    Note: Platform moves only to left or right, so vertical speed is ignored.
    """

    def __init__(self, image, rect, speed):
        """Initalize the platform object.

        Parameters
        ----------
        image: pygame.Surface
            The image of the platform.
        rect: pygame.Rect
            The rectangle that contains position and borders of the platform.
        speed: pygame.Vector2
            The speed vector of the platform.
        """
        MovableEntity.__init__(self, image, rect, speed)

    def move(self):
        """Move platform to left or right"""
        self.rect.move_ip(self.speed.x, 0)
