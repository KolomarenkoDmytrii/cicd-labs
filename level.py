from dataclasses import dataclass
import copy
import pygame
import entity
import helpers

class Level:
    """Class for level objects and logic.

    Attributes
    ----------
    blocks: list[entity.Block]
        Destroyable blocks of the level.
    platform: entity.Platform
        The movable platform object.
    ball: entity.Ball
        The movable ball object. Contains speed of the released speed. Also
        because ball before its releasing "tied" to platform, initial position
        is ignored.
    edges: pygame.Rect
        Rectangle that contains width and height of the level
    state: GameState
        Game state of the level.
    """

    @dataclass
    class GameState:
        """Dataclass for containing width and height of edges.

        Attributes
        ----------
        ball_proto_rect: pygame.Rect
            Initial rectangle of the level ball.
        ball_released_speed: pygame.Vector2
            Initial speed of the level ball.
        score: int
            Game score of the level.
        life: int
            Contains number of player tries (lifes)
        is_game_over: bool
            Indicates whether game is ended or not.
        """
        ball_released_speed: pygame.Vector2
        score: int = 0
        lifes: int = 4
        is_game_over: bool = False
        is_ball_released: bool = False
        is_player_won: bool = False

    def __init__(self, lifes, blocks, platform, ball, edges, top_start):
        """Initalize the level object.

        Parameters
        ----------
        blocks: list[entity.Block]
            Destroyable blocks of the level.
        platform: entity.Platform
            The movable platform object.
        ball: entity.Ball
            The movable ball object.
        edges: helpers.Edges
            Tulpe that contains width and height of the level in this format:
            (width: int, height: int)
        top_start: int
            Says where the top of game area lays.
        """
        self.blocks = blocks
        self.platform = platform
        self.ball = ball

        self.edges = pygame.Rect((0, top_start), (edges.width, edges.height))

        self.state = Level.GameState(
            ball_released_speed=copy.deepcopy(self.ball.speed),
            lifes=lifes
        )

        self.reset_ball()


    def reset_ball(self):
        """Reset state of the level ball to its initial state."""
        # self.ball.rect = copy.deepcopy(self.state.ball_proto_rect)
        self.ball.rect.bottom = self.platform.rect.top
        self.ball.rect.centerx = self.platform.rect.centerx
        self.ball.speed = pygame.Vector2(0, 0)
        self.state.is_ball_released = False

    def release_ball(self):
        if not self.state.is_ball_released:
            self.state.is_ball_released = True
            self.ball.speed = copy.deepcopy(self.state.ball_released_speed)
            print('ball is released')

    def get_game_state(self):
        """Return game state of the level.

        Returns
        -------
            Level.GameState
        """
        return self.state

    def get_sprites_group(self):
        """Return game objects as one group.

        Returns
        -------
            pygame.sprite.Group
        """
        return pygame.sprite.Group(self.platform, self.ball, *self.blocks)

    def adjust_on_x_collision(movable_entity_1, entity_2):
        """Process collisions on X axis bewtween movable entity and other (any)
            entity and update their positions and speeds.

        Parameters
        ----------
        movable_entity_1: entity.MovableEntity
            A movable entity.
        entity_2: entity.Entity
            Another entity that can be movable or not.
        """
        # if movable_entity_1 collides with entity_2's left side
        if movable_entity_1.rect.right > entity_2.rect.left and \
            movable_entity_1.rect.right < entity_2.rect.right:
            movable_entity_1.rect.right = entity_2.rect.left
        # otherwise movable_entity_1 collided with entity_2's right side
        else:
            movable_entity_1.rect.left = entity_2.rect.right

        movable_entity_1.speed.x = -movable_entity_1.speed.x

    def adjust_on_y_collision(movable_entity):
        """Process collisions on Y axis bewtween movable entity and other (any)
            entity and update their positions and speeds.

        Parameters
        ----------
        movable_entity_1: entity.MovableEntity
            A movable entity.
        entity_2: entity.Entity
            Another entity that can be movable or not.
        """
        movable_entity.rect.y -= movable_entity.speed.y
        movable_entity.speed.y = -movable_entity.speed.y

    def process_key_presses(self):
        """Process key presses and update level objects and state
            correspondingly.
        """
        def update():
            self.platform.move()
            if not self.state.is_ball_released:
                self.ball.rect.bottom = self.platform.rect.top
                self.ball.rect.centerx = self.platform.rect.centerx


        keys = pygame.key.get_pressed()

        if keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
            self.release_ball()
        if keys[pygame.K_a]:
            self.platform.speed.x = -abs(self.platform.speed.x)
            update()
        if keys[pygame.K_d]:
            self.platform.speed.x = abs(self.platform.speed.x)
            # self.platform.move()
            update()

    def process_collisions(self):
        """Process collisions and update objects positions and speeds."""

        #   This function checks collision by firstly moving ball by the X axis
        # and then by Y axis. This allows accuratly determinate whether there
        # is collision with left / right or top / bottom sides of platform:
        # if while moving on the X axis there is collison, it is obvious that
        # collison occured on left or right side; the same applies to the Y
        # axis.

        # checking collision on the X axis
        self.ball.rect.x += self.ball.speed.x
        if self.ball.is_collided_with(self.platform):
            Level.adjust_on_x_collision(self.ball, self.platform)
        # if ball is out of level edges...
        #   on the right edge
        elif self.ball.rect.right > self.edges.right:
            self.ball.rect.right = self.edges.right
            self.ball.speed.x = -self.ball.speed.x
        #   on the left edge
        elif self.ball.rect.left < self.edges.left:
            self.ball.rect.left = self.edges.left
            self.ball.speed.x = -self.ball.speed.x
        else:
            for block in self.blocks:
                if self.ball.is_collided_with(block):
                    Level.adjust_on_x_collision(self.ball, block)
                    block.set_is_destroyed()

        # checking collision on the Y axis
        self.ball.rect.y += self.ball.speed.y
        if self.ball.is_collided_with(self.platform):
            Level.adjust_on_y_collision(self.ball)
        # if ball is out of level edges...
        #   on the bottom edge
        elif self.ball.rect.bottom > self.edges.bottom:
            # # # self.ball.rect.bottom = self.edges.bottom
            # # # self.ball.speed.y = -self.ball.speed.y
            self.reset_ball()
            self.state.lifes -= 1
            print('Lifes:', self.state.lifes)
        #   on the top edge
        # elif self.ball.rect.top < 0:
        elif self.ball.rect.top < self.edges.top:
            self.ball.rect.top = self.edges.top
            self.ball.speed.y = -self.ball.speed.y
        else:
            for block in self.blocks:
                if self.ball.is_collided_with(block):
                    Level.adjust_on_y_collision(self.ball)
                    block.set_is_destroyed()

        # if platform "squeezes" ball to the left or right level edge
        is_squeezing_on_y = self.ball.rect.bottom < self.platform.rect.top or \
            self.ball.rect.top < self.platform.rect.bottom
        is_squeezing_on_x = self.ball.rect.right > self.edges.right or \
            self.ball.rect.left < self.edges.left
        if is_squeezing_on_y and is_squeezing_on_x:
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

        # remove destroyed block and increase score correspondingly
        for block in self.blocks:
            if block.is_destroyed:
                self.blocks.remove(block)
                self.state.score += 100
                print('Score:', self.state.score)
                # self.ball.speed += self.state.ball_released_speed * 0.1
                self.ball.speed *= 1.02

        if self.state.lifes < 1:
            self.state.is_game_over = True
        elif len(self.blocks) == 0:
            self.state.is_player_won = True


class LevelMaker:
    """Class for creating level's objects and other data.

    Attributes
    ----------
    edges: tuple[int, int]
        Tulpe that contains width and height of the level in this format:
        (width: int, height: int)
    images: dict[str, pygame.Surface]
        Dictionary that contains level's objects images in this format:
        'object type name, `str`' : 'image, `pygame.Surface`'
        Object types name can be:
            - 'platform' for entity.Platform object;
            - 'ball' for entity.Ball object;
            - 'block' for entity.Block objects.
    horizontal_margin: int
        Horizontal margin between blocks.
    vertical_margin: int
        Vertical margin between blocks.
    num_of_rows:
        Number of rows of blocks.
    """

    def __init__(self, edges, images, blocks_layout):
        """Initalize the LevelMaker class object.

        Parameters
        ----------
        edges: tuple[int, int]
            Tulpe that contains width and height of the level in this format:
            (width: int, height: int)
        images: dict[str, pygame.Surface]
            Dictionary that contains level's objects images in this format:
            'object type name, `str`' : 'image, `pygame.Surface`'
            Object types name can be:
                - 'platform' for entity.Platform object;
                - 'ball' for entity.Ball object;
                - 'block' for entity.Block objects.
        blocks_layout: dict[str, int]
            Dictionary that contains blocks layout. Dictionary keys are follows:
                - 'horizontal_margin': horizontal margin between blocks;
                - 'vertical_margin': vertical margin between blocks;
                - 'num_of_rows': number of rows of blocks.
        """
        self.edges = edges
        self.images = images
        self.horizontal_margin = blocks_layout['horizontal_margin']
        self.vertical_margin = blocks_layout['vertical_margin']
        self.num_of_rows = blocks_layout['num_of_rows']

    def get_level(self):
        """Get a maked and initialized level."""
        platform = entity.Platform(
            image=self.images['platform'],
            rect=pygame.Rect(
                (self.edges.width / 2, self.edges.height * 0.75),
                self.images['platform'].get_size()
            ),
            speed=pygame.Vector2(5, 0)
        )
        ball = entity.Ball(
            image=self.images['ball'],
            rect=pygame.Rect(
                (0, 0),
                self.images['ball'].get_size()
            ),
            speed=pygame.Vector2(
                round(self.edges.height * 0.005),
                -round(self.edges.height * 0.005)
            )
        )

        # placing blocks
        blocks = []

        x = self.horizontal_margin

        top_margin = ball.rect.height * 3
        y = round(ball.rect.height * 2.2 + top_margin)

        rainbow_colors = [
            (255, 0, 0), # red
            (255, 200, 0), # yellow
            (0, 128, 0), # green
            (0, 0, 255), # blue
            (128, 0, 200), # violet
        ]
        colored_block_images = []
        for color in rainbow_colors:
            image = self.images['block'].copy()
            image.fill(color)
            colored_block_images.append(image)

        for i in range(0, self.num_of_rows):
            while x + self.images['block'].get_size()[0] < self.edges.width:
                blocks.append(entity.Block(
                    image=colored_block_images[i % len(colored_block_images)],
                    rect=pygame.Rect(
                        (x, y),
                        self.images['block'].get_size()
                    )
                ))
                x += self.images['block'].get_size()[0] + self.horizontal_margin

            x = self.horizontal_margin
            y += self.vertical_margin

        return Level(
            lifes=4,
            blocks=blocks,
            platform=platform,
            ball=ball,
            edges=self.edges,
            top_start=top_margin
        )
