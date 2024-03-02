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
    """Class for destroyble blocks."""

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


class Level:
    """Class for level objects and logic.

    Attributes
    ----------
    blocks: list[Block]
        Destroyble blocks of the level.
    platform: Platform
        The movable platform object.
    ball: Ball
        The movable ball object.
    edges: pygame.Rect
        Rectangle that contains width and height of the level
    is_game_over: bool
        This variable indicates whether game ended or not
    """

    def __init__(self, blocks, platform, ball, edges):
        """Initalize the level object.

        Parameters
        ----------
        blocks: list[Block]
            Destroyble blocks of the level.
        platform: Platform
            The movable platform object.
        ball: Ball
            The movable ball object.
        edges: tuple
            Tulpe that contains width and height of the level in this format:
            (width: int, height: int)
        """
        self.blocks = blocks
        self.platform = platform
        self.ball = ball

        self.edges = pygame.Rect((0, 0), edges)

        self.is_game_over = False

    def process_key_presses(self):
        """Process key presses and update level objects and state
            correspondingly.
        """
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.platform.speed.x = -abs(self.platform.speed.x)
            self.platform.move()
        if keys[pygame.K_d]:
            self.platform.speed.x = abs(self.platform.speed.x)
            self.platform.move()

    def get_sprites_group(self):
        """Return game objects as one group.

        Returns
        -------
            pygame.sprite.Group
        """
        return pygame.sprite.Group(self.platform, self.ball)

    def process_collisions(self):
        """Process collisions and update objects positions and speeds."""

        #   This function checks collision by firstly moving ball by the X axis
        # and then by Y axis. This allows accuratly determinate whether there is
        # collision wit left / right or top / bottom sides of platform:
        # if while moving on the X axis there is collison, it is obvious that
        # collison occured on left or right side; the same applies to the Y
        # axis.

        # checking collision on the X axis
        self.ball.rect.x += self.ball.speed.x
        if self.ball.is_collided_with(self.platform):
            # if ball collides with platform's left side
            if self.ball.rect.right > self.platform.rect.left and \
                self.ball.rect.right < self.platform.rect.right:
                self.ball.rect.right = self.platform.rect.left
            # otherwise ball collided with platform's right side
            else:
                self.ball.rect.left = self.platform.rect.right
            self.ball.speed.x = -self.ball.speed.x
        # if ball is out of level edges...
        #   on the right edge
        elif self.ball.rect.right > self.edges.right:
            self.ball.rect.right = self.edges.right
            self.ball.speed.x = -self.ball.speed.x
        #   on the left edge
        elif self.ball.rect.left < self.edges.left:
            self.ball.rect.left = self.edges.left
            self.ball.speed.x = -self.ball.speed.x

        # checking collision on the Y axis
        self.ball.rect.y += self.ball.speed.y
        if self.ball.is_collided_with(self.platform):
            self.ball.rect.y -= self.ball.speed.y
            self.ball.speed.y = -self.ball.speed.y
        # if ball is out of level edges...
        #   on the bottom edge
        elif self.ball.rect.bottom > self.edges.bottom:
            self.ball.rect.bottom = self.edges.bottom
            self.ball.speed.y = -self.ball.speed.y
        #   on the top edge
        # elif self.ball.rect.top < 0:
        elif self.ball.rect.top < self.edges.top:
            self.ball.rect.top = self.edges.top
            self.ball.speed.y = -self.ball.speed.y

        # if platform "squeezes" ball to the left or right level edge
        if (self.ball.rect.bottom < self.platform.rect.top or self.ball.rect.top < self.platform.rect.bottom) and \
            (self.ball.rect.right > self.edges.right or self.ball.rect.left < self.edges.left):
            self.ball.rect.top = self.platform.rect.bottom

        # if platform out of level edges...
        #   on the right edge
        if self.platform.rect.right > self.edges.right:
            self.platform.rect.right = self.edges.right
            self.platform.speed.x = -self.platform.speed.x
        #   on the left edge
        elif self.platform.rect.left < self.edges.left:
            self.platform.rect.left = self.edges.left
            self.platform.speed.x = -self.platform.speed.x


    def update(self):
        """Do updates of the level's state and objects"""
        self.process_key_presses()
        self.process_collisions()


class LevelMaker:
    """Class for creating level's objects and other data.

    Attributes
    ----------
    edges_sizes: tuple[int, int]
        Tulpe that contains width and height of the level in this format:
        (width: int, height: int)
    images: dict[str, pygame.Surface]
        Dictionary that contains level's objects images in this format:
        'object type name, `str`' : 'image, `pygame.Surface`'
    """

    def __init__(self, edges_sizes, images):
        """Initalize the LevelMaker class object.

        Parameters
        ----------
        edges_sizes: tuple[int, int]
            Tulpe that contains width and height of the level in this format:
            (width: int, height: int)
        images: dict[str, pygame.Surface]
            Dictionary that contains level's objects images in this format:
            'object type name, `str`' : 'image, `pygame.Surface`'
        """
        self.edges_sizes = edges_sizes
        self.images = images

    def get_level(self):
        """Get a maked and initialized level."""
        platform = Platform(
            image=self.images['platform'],
            rect=pygame.Rect(
                (self.edges_sizes[0] / 2, self.edges_sizes[1] * 0.6),
                self.images['platform'].get_size()
            ),
            speed=pygame.Vector2(5, 0)
        )
        ball = Ball(
            image=self.images['ball'],
            rect=pygame.Rect(
                (self.edges_sizes[0] / 2, self.edges_sizes[1] * 0.4),
                self.images['ball'].get_size()
            ),
            speed=pygame.Vector2(1, 1)
        )
        blocks = None

        return Level(
            blocks=blocks,
            platform=platform,
            ball=ball,
            edges=self.edges_sizes
        )


class Game:
    """Game application class.

    Attributes
    ----------
    edges: tuple[int, int]
        Tulpe that contains width and height of the level in this format:
        (width: int, height: int)
    images: dict[str, pygame.Surface]
        Dictionary that contains level's objects images in this format:
        'object type name, `str`' : 'image, `pygame.Surface`'
    level_maker: LevelMaker
        The LevelMaker object that do initializeing of the level
    """

    def __init__(self, edges):
        """Initalize the game application object.

        Parameters
        ----------
        edges: list[int, int]
            Tulpe that contains width and height of the level in this format:
            (width: int, height: int)
        """
        self.edges = edges

        self.images = {
            'platform': pygame.Surface((65, 20)),
            'ball': pygame.Surface((20, 20))
        }
        self.images['platform'].fill((0, 0, 0))
        self.images['ball'].fill((0, 0, 0))

        self.level_maker = LevelMaker(
            self.edges,
            self.images
        )

    def draw(self, screen, sprites_group):
        """Update image of the game.

        Parameters
        ----------
        screen: Surface
            A `Surface` object (created using ``pygame.display.set_mode()``)
            which contains the final rendered image that is putted on the screen

        sprites_group: pygame.sprite.Group
            Game objects that needed to be drawn
        """
        # fill the screen with a color to wipe away anything from last frame
        screen.fill('white')
        sprites_group.draw(screen)
        # flip() the display to put your work on screen
        pygame.display.flip()

    def run(self):
        """Run the game application."""
        # pygame setup
        pygame.init()
        screen = pygame.display.set_mode(self.edges)
        clock = pygame.time.Clock()

        # game setup
        running = True
        level = self.level_maker.get_level()

        while running:
            # poll for events
            # pygame.QUIT event means the user clicked X to close your window
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.draw(screen, level.get_sprites_group())

            level.update()

            # limits FPS to 60
            clock.tick(60)

        pygame.quit()

