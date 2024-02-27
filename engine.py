import pygame


class Entity(pygame.sprite.Sprite):
    """Base class for game objects.

    Attributes
    ----------
    image: pygame.Surface
        The image of the entity.
    rect : pygame.Rect
        The rectangle that contains position and borders of the entity.
    """
    def __init__(self, image, rect):
        """Initalizes the entity object.

        Parameters
        ----------
        image : pygame.Surface
            The image of the entity.
        rect : pygame.Rect
            The rectangle that contains position and borders of the entity.
        """
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = rect

    def is_collided_with(self, other) -> bool:
        """Checks if the entity is collided with other entity.

        Parameters
        ----------
        other : Entity
            The other entity, for which collision check is doing.

        Returns
        ------
        bool
            If there is collision between `self` and `other`, `True` will be returned.
            Otherwise `False` will be returned.
        """
        return pygame.sprite.collide_rect(self, other)


class MovableEntity(Entity):
    """Base class for movable entities
    """
    def __init__(self, image, rect, speed):
        Entity.__init__(self, image, rect)
        self.speed = speed

    def move(self):
        self.rect.move_ip(self.speed.x, self.speed.y)

    def update(self):
        self.move()


class Block(Entity):
    def __init__(self, image, rect):
        Entity.__init__(self, image, rect)
        self.is_destroyed = False

    def is_destroyed(self):
        return self.is_destroyed

    def set_is_destroyed(self):
        self.is_destroyed = True


class Ball(MovableEntity):
    def __init__(self, image, rect, speed):
        MovableEntity.__init__(self, image, rect, speed)


class Platform(MovableEntity):
    def __init__(self, image, rect, speed):
        MovableEntity.__init__(self, image, rect, speed)

    def move(self):
        self.rect.move_ip(self.speed.x, 0)


class Level:
    def __init__(self, blocks, platform, ball, width, height):
        self.blocks = blocks
        self.platform = platform
        self.ball = ball

        self.width = width
        self.height = height

        self.is_game_over = False

    def process_key_presses(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.platform.speed.x = -abs(self.platform.speed.x)
            self.platform.update()
        if keys[pygame.K_d]:
            self.platform.speed.x = abs(self.platform.speed.x)
            self.platform.update()

    def get_sprites_group(self):
        return pygame.sprite.Group(self.platform, self.ball)

    def check_collisions(self):
        # checking collision on the X axis
        self.ball.rect.x += self.ball.speed.x
        if self.ball.is_collided_with(self.platform):
            # if ball collides with platform's left side
            if self.ball.rect.right > self.platform.rect.left and self.ball.rect.right < self.platform.rect.right:
                self.ball.rect.right = self.platform.rect.left
            # otherwise ball collided with platform's right side
            else:
                self.ball.rect.left = self.platform.rect.right
            self.ball.speed.x = -self.ball.speed.x
        # if ball is out of level edges...
        #   on the right edge
        elif self.ball.rect.right > self.width:
            self.ball.rect.right = self.width
            self.ball.speed.x = -self.ball.speed.x
        #   on the left edge
        elif self.ball.rect.left < 0:
            self.ball.rect.left = 0
            self.ball.speed.x = -self.ball.speed.x

        # checking collision on the Y axis
        self.ball.rect.y += self.ball.speed.y
        if self.ball.is_collided_with(self.platform):
            self.ball.rect.y -= self.ball.speed.y
            self.ball.speed.y = -self.ball.speed.y
        # if ball is out of level edges...
        #   on the bottom edge
        elif self.ball.rect.bottom > self.height:
            self.ball.rect.bottom = self.height
            self.ball.speed.y = -self.ball.speed.y
        #   on the top edge
        elif self.ball.rect.top < 0:
            self.ball.rect.top = 0
            self.ball.speed.y = -self.ball.speed.y

        # if platform "squeezes" ball to the left or right level edge
        if (self.ball.rect.bottom < self.platform.rect.top or self.ball.rect.top < self.platform.rect.bottom) and \
            (self.ball.rect.right > self.width or self.ball.rect.left < 0):
            self.ball.rect.top = self.platform.rect.bottom

        # if platform out of level edges...
        #   on the right edge
        if self.platform.rect.right > self.width:
            self.platform.rect.right = self.width
            self.platform.speed.x = -self.platform.speed.x
        #   on the left edge
        elif self.platform.rect.left < 0:
            self.platform.rect.left = 0
            self.platform.speed.x = -self.platform.speed.x


    def update(self):
        self.process_key_presses()
        self.check_collisions()



class LevelMaker:
    def __init__(self, edges_sizes, images):
        self.edges_sizes = edges_sizes
        self.images = images

    def get_level(self):
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
            width=self.edges_sizes[0],
            height=self.edges_sizes[1]
        )


class Game:
    def __init__(self, edges):
        self.edges = edges

        self.images = {
            'platform': pygame.Surface((65, 20)),
            'ball': pygame.Surface((20, 20))
        }
        self.images['platform'].fill((0, 0, 0))
        self.images['ball'].fill((0, 0, 0))

        self.level_maker = LevelMaker(
            (self.edges[0], self.edges[1]),
            self.images
        )

    def draw(self, screen, sprites_group):
        # fill the screen with a color to wipe away anything from last frame
        screen.fill('white')
        sprites_group.draw(screen)
        # flip() the display to put your work on screen
        pygame.display.flip()

    def run(self):
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

