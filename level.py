"""Create and manage level."""

from dataclasses import dataclass
import copy
import pygame
import entity
import helpers

class Level:
    """Class for level objects and logic.

    Attributes
    ----------
    __blocks: list[entity.Block]
        Destroyable blocks of the level.
    __platform: entity.Platform
        The movable platform object.
    __ball: entity.Ball
        The movable ball object. Contains value of the released speed. Also
        because ball before its releasing "tied" to the platform, initial
        position is ignored.
    __edges: pygame.Rect
        Rectangle that contains width and height of the level.
    __state: Level.GameState
        Game state of the level.
    """

    @dataclass
    class GameState:
        """Dataclass for containing width and height of edges.

        Attributes
        ----------
        ball_released_speed: pygame.math.Vector2
            Initial speed of the level ball.
        score: int
            Game score of the level.
        life: int
            Contains number of player tries (lifes)
        is_game_over: bool
            Indicates whether game is ended or not.
        """

        ball_released_speed: pygame.math.Vector2
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
            Contains width and height of the level.
        top_start: int
            Says where the top of game area lays. It is needed for delimeting
            game and counters areas.
        """

        self.__blocks = blocks
        self.__platform = platform
        self.__ball = ball

        self.__edges = pygame.Rect((0, top_start), (edges.width, edges.height))

        self.__state = Level.GameState(
            ball_released_speed=copy.deepcopy(self.__ball.speed),
            lifes=lifes
        )

        self.__reset_ball()

    def get_top_edge(self):
        """Return value of the top of game area.

        Returns
        ------
        int
        """

        return self.__edges.top

    def __reset_ball(self):
        """Reset state of the level ball to its initial state."""

        self.__ball.rect.bottom = self.__platform.rect.top
        self.__ball.rect.centerx = self.__platform.rect.centerx
        self.__ball.speed = pygame.math.Vector2(0, 0)
        self.__state.is_ball_released = False

    def release_ball(self):
        """Release the ball from the platform."""

        if not self.__state.is_ball_released:
            self.__state.is_ball_released = True
            self.__ball.speed = copy.deepcopy(self.__state.ball_released_speed)

    def get_game_state(self):
        """Return game state of the level.

        Returns
        -------
        Level.GameState
        """

        return self.__state

    def get_sprites_group(self):
        """Return game objects as one group.

        Returns
        -------
        pygame.sprite.Group
        """

        return pygame.sprite.Group(self.__platform, self.__ball, *self.__blocks)

    def __adjust_on_x_collision(movable_entity_1, entity_2):
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

    def __adjust_on_y_collision(movable_entity):
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

    def __process_key_presses(self):
        """Process key presses and update level objects and state
            correspondingly.
        """
        def do_update():
            self.__platform.move()
            if not self.__state.is_ball_released:
                self.__ball.rect.bottom = self.__platform.rect.top
                self.__ball.rect.centerx = self.__platform.rect.centerx


        keys = pygame.key.get_pressed()

        if keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
            self.release_ball()
        if keys[pygame.K_a]:
            self.__platform.speed.x = -abs(self.__platform.speed.x)
            do_update()
        if keys[pygame.K_d]:
            self.__platform.speed.x = abs(self.__platform.speed.x)
            # self.__platform.move()
            do_update()

    def __process_collisions(self):
        """Process collisions and update objects positions and speeds."""

        #   This function checks collision by firstly moving ball by the X axis
        # and then by Y axis. This allows accuratly determinate whether there
        # is collision with left / right or top / bottom sides of platform:
        # if while moving on the X axis there is collison, it is obvious that
        # collison occured on left or right side; the same applies to the Y
        # axis.

        # checking collision on the X axis
        self.__ball.rect.x += self.__ball.speed.x
        if self.__ball.is_collided_with(self.__platform):
            Level.__adjust_on_x_collision(self.__ball, self.__platform)
        # if ball is out of level edges...
        #   on the right edge
        elif self.__ball.rect.right > self.__edges.right:
            self.__ball.rect.right = self.__edges.right
            self.__ball.speed.x = -self.__ball.speed.x
        #   on the left edge
        elif self.__ball.rect.left < self.__edges.left:
            self.__ball.rect.left = self.__edges.left
            self.__ball.speed.x = -self.__ball.speed.x
        else:
            for block in self.__blocks:
                if self.__ball.is_collided_with(block):
                    Level.__adjust_on_x_collision(self.__ball, block)
                    block.set_is_destroyed()

        # checking collision on the Y axis
        self.__ball.rect.y += self.__ball.speed.y
        if self.__ball.is_collided_with(self.__platform):
            Level.__adjust_on_y_collision(self.__ball)
        # if ball is out of level edges...
        #   on the bottom edge
        elif self.__ball.rect.bottom > self.__edges.bottom:
            self.__reset_ball()
            self.__state.lifes -= 1
        #   on the top edge
        elif self.__ball.rect.top < self.__edges.top:
            self.__ball.rect.top = self.__edges.top
            self.__ball.speed.y = -self.__ball.speed.y
        else:
            for block in self.__blocks:
                if self.__ball.is_collided_with(block):
                    Level.__adjust_on_y_collision(self.__ball)
                    block.set_is_destroyed()

        # if platform "squeezes" ball to the left or right level edge
        is_squeezing_on_y = self.__ball.rect.bottom < self.__platform.rect.top or \
            self.__ball.rect.top < self.__platform.rect.bottom
        is_squeezing_on_x = self.__ball.rect.right > self.__edges.right or \
            self.__ball.rect.left < self.__edges.left
        if is_squeezing_on_y and is_squeezing_on_x:
            self.__ball.rect.top = self.__platform.rect.bottom

        # if platform out of level edges...
        #   on the right edge
        if self.__platform.rect.right > self.__edges.right:
            self.__platform.rect.right = self.__edges.right
            self.__platform.speed.x = -self.__platform.speed.x
        #   on the left edge
        elif self.__platform.rect.left < self.__edges.left:
            self.__platform.rect.left = self.__edges.left
            self.__platform.speed.x = -self.__platform.speed.x


    def update(self):
        """Do updates of the level's state and objects."""

        self.__process_key_presses()
        self.__process_collisions()

        # remove destroyed block and increase score correspondingly
        for block in self.__blocks:
            if block.is_destroyed():
                self.__blocks.remove(block)
                self.__state.score += 100
                self.__ball.speed *= 1.02

        if self.__state.lifes < 1:
            self.__state.is_game_over = True
        elif len(self.__blocks) == 0:
            self.__state.is_player_won = True


class LevelMaker:
    """Class for creating level's objects and other data.

    Attributes
    ----------
    __edges: helpers.Edges
        Contains width and height of the level.
    __images: dict[str, pygame.Surface]
        Dictionary that contains level's objects images.
        Object types name can be:
            - 'platform' for entity.Platform object;
            - 'ball' for entity.Ball object;
            - 'block' for entity.Block objects.
    __horizontal_alignment: int
        Horizontal alignment between blocks.
    __vertical_alignment: int
        Vertical alignment between blocks.
    __num_of_rows:
        Number of rows of blocks.
    """

    def __init__(self, edges, images, blocks_layout):
        """Initalize the LevelMaker class object.

        Parameters
        ----------
        edges: helpers.Edges
            Contains width and height of the level.
        images: dict[str, pygame.Surface]
           Dictionary that contains level's objects images.
            Object types name can be:
            - 'platform' for entity.Platform object;
            - 'ball' for entity.Ball object;
            - 'block' for entity.Block objects.
        blocks_layout: dict[str, int]
            Dictionary that contains blocks layout. Dictionary keys are follows:
                - 'horizontal_alignment': horizontal alignment between blocks;
                - 'vertical_alignment': vertical alignment between blocks;
                - 'num_of_rows': number of rows of blocks.
        """

        self.__edges = edges
        self.__images = images
        self.__horizontal_alignment = blocks_layout['horizontal_alignment']
        self.__vertical_alignment = blocks_layout['vertical_alignment']
        self.__num_of_rows = blocks_layout['num_of_rows']

    def get_level(self):
        """Get a maked and initialized level.

        Returns
        -------
        level.Level
        """

        platform = entity.Platform(
            image=self.__images['platform'],
            rect=pygame.Rect(
                (self.__edges.width / 2, self.__edges.height * 0.75),
                self.__images['platform'].get_size()
            ),
            speed=pygame.math.Vector2(5, 0)
        )
        ball = entity.Ball(
            image=self.__images['ball'],
            rect=pygame.Rect(
                (0, 0),
                self.__images['ball'].get_size()
            ),
            speed=pygame.math.Vector2(
                round(self.__edges.height * 0.005),
                -round(self.__edges.height * 0.005)
            )
        )

        # placing blocks
        x = self.__horizontal_alignment
        top_alignment = ball.rect.height * 3
        y = round(ball.rect.height * 2.2 + top_alignment)

        rainbow_colors = [
            (255, 0, 0), # red
            (255, 200, 0), # yellow
            (0, 128, 0), # green
            (0, 0, 255), # blue
            (128, 0, 200), # violet
        ]
        colored_block_images = []
        for color in rainbow_colors:
            image = self.__images['block'].copy()
            # make block colored (not completly fill solidly)
            image.fill(color, special_flags=pygame.BLEND_MULT)
            colored_block_images.append(image)

        # make the blocks "net"
        blocks = []
        for i in range(0, self.__num_of_rows):
            while x + self.__images['block'].get_size()[0] < self.__edges.width:
                blocks.append(entity.Block(
                    image=colored_block_images[i % len(colored_block_images)],
                    rect=pygame.Rect(
                        (x, y),
                        self.__images['block'].get_size()
                    )
                ))
                x += self.__images['block'].get_size()[0] + self.__horizontal_alignment

            # go to the next row
            x = self.__horizontal_alignment
            y += self.__vertical_alignment

        return Level(
            lifes=4,
            blocks=blocks,
            platform=platform,
            ball=ball,
            edges=self.__edges,
            top_start=top_alignment
        )
