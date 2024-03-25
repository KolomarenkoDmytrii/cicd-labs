"""Create and manage level."""

from dataclasses import dataclass
import copy
import pygame
import entity
import helpers
from typing import List


class Level:
    """Class for level objects and logic.

    Attributes:
        __blocks (List[entity.Block]): Destroyable blocks of the level.
        __platform (entity.Platform): The movable platform object.
        __ball (entity.Ball): The movable ball object. Contains value of the released speed. Also
            because ball before its releasing "tied" to the platform, initial
            position is ignored.
        __edges (pygame.Rect): Rectangle that contains width and height of the level.
        __state (Level.GameState): Game state of the level.
    """

    @dataclass
    class GameState:
        """Dataclass for containing width and height of edges.

        Attributes:
            ball_released_speed (pygame.math.Vector2): Initial speed of the level ball.
            score (int): Game score of the level.
            lifes (int): Contains number of player tries (lifes)
            is_game_over (bool): Indicates whether game is ended or not.
        """

        ball_released_speed: pygame.math.Vector2
        score: int = 0
        lifes: int = 4
        is_game_over: bool = False
        is_ball_released: bool = False
        is_player_won: bool = False

    def __init__(
            self,
            lifes: int,
            blocks: List[entity.Block],
            platform: entity.Platform,
            ball: entity.Ball,
            edges: pygame.Rect,
            top_start: int,
    ):
        """Initialize the level object.

        Parameters:
            lifes (int): Number of player lives.
            blocks (List[entity.Block]): List of destroyable blocks.
            platform (entity.Platform): The platform object.
            ball (entity.Ball): The ball object.
            edges (pygame.Rect): The rectangle containing width and height of the level.
            top_start (int): Indicates where the top of game area lies. Needed for delimiting
                game and counters areas.
        """
        self.__blocks = blocks
        self.__platform = platform
        self.__ball = ball

        self.__edges = pygame.Rect((0, top_start), (edges.width, edges.height))

        self.__state = Level.GameState(
            ball_released_speed=copy.deepcopy(self.__ball.speed), lifes=lifes
        )

        self.__reset_ball()

    def get_top_edge(self) -> int:
        """Return value of the top of game area.

        Returns:
            int: The top edge value.
        """
        return self.__edges.top

    def __reset_ball(self) -> None:
        """Reset state of the level ball to its initial state."""
        self.__ball.rect.bottom = self.__platform.rect.top
        self.__ball.rect.centerx = self.__platform.rect.centerx
        self.__ball.speed = pygame.math.Vector2(0, 0)
        self.__state.is_ball_released = False

    def release_ball(self) -> None:
        """Release the ball from the platform."""
        if not self.__state.is_ball_released:
            self.__state.is_ball_released = True
            self.__ball.speed = copy.deepcopy(self.__state.ball_released_speed)

    def get_game_state(self) -> GameState:
        """Return game state of the level.

        Returns:
            Level.GameState: The game state.
        """
        return self.__state

    def get_sprites_group(self) -> pygame.sprite.Group:
        """Return game objects as one group.

        Returns:
            pygame.sprite.Group: The group containing all game objects.
        """
        return pygame.sprite.Group(self.__platform, self.__ball, *self.__blocks)

    @staticmethod
    def __adjust_on_x_collision(
            movable_entity_1: entity.MovableEntity, entity_2: entity.Entity
    ) -> None:
        """Process collisions on X axis between movable entity and other entity and update their positions and
        speeds."""
        if (
                entity_2.rect.left < movable_entity_1.rect.right < entity_2.rect.right
        ):
            movable_entity_1.rect.right = entity_2.rect.left
        else:
            movable_entity_1.rect.left = entity_2.rect.right
        movable_entity_1.speed.x = -movable_entity_1.speed.x

    @staticmethod
    def __adjust_on_y_collision(movable_entity: entity.MovableEntity) -> None:
        """Process collisions on Y axis between movable entity and other entity and update their positions and
        speeds."""
        movable_entity.rect.y -= movable_entity.speed.y
        movable_entity.speed.y = -movable_entity.speed.y

    def __process_key_presses(self) -> None:
        """Process key presses and update level objects and state correspondingly."""

        def do_update() -> None:
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
            do_update()

    def __process_collisions(self) -> None:
        """Process collisions and update objects positions and speeds."""
        # Checking collision on the X axis
        self.__ball.rect.x += self.__ball.speed.x
        if self.__ball.is_collided_with(self.__platform):
            self.__adjust_on_x_collision(self.__ball, self.__platform)

        elif self.__ball.rect.right > self.__edges.right:
            self.__ball.rect.right = self.__edges.right
            self.__ball.speed.x = -self.__ball.speed.x

        elif self.__ball.rect.left < self.__edges.left:
            self.__ball.rect.left = self.__edges.left
            self.__ball.speed.x = -self.__ball.speed.x
        else:
            for block in self.__blocks:
                if self.__ball.is_collided_with(block):
                    self.__adjust_on_x_collision(self.__ball, block)
                    block.set_is_destroyed()

        self.__ball.rect.y += self.__ball.speed.y
        if self.__ball.is_collided_with(self.__platform):
            self.__adjust_on_y_collision(self.__ball)

        elif self.__ball.rect.bottom > self.__edges.bottom:
            self.__reset_ball()
            self.__state.lifes -= 1

        elif self.__ball.rect.top < self.__edges.top:
            self.__ball.rect.top = self.__edges.top
            self.__ball.speed.y = -self.__ball.speed.y
        else:
            for block in self.__blocks:
                if self.__ball.is_collided_with(block):
                    self.__adjust_on_y_collision(self.__ball)
                    block.set_is_destroyed()

        is_squeezing_on_y = (
                self.__ball.rect.bottom < self.__platform.rect.top
                or self.__ball.rect.top < self.__platform.rect.bottom
        )
        is_squeezing_on_x = (
                self.__ball.rect.right > self.__edges.right
                or self.__ball.rect.left < self.__edges.left
        )
        if is_squeezing_on_y and is_squeezing_on_x:
            self.__ball.rect.top = self.__platform.rect.bottom

        if self.__platform.rect.right > self.__edges.right:
            self.__platform.rect.right = self.__edges.right
            self.__platform.speed.x = -self.__platform.speed.x

        elif self.__platform.rect.left < self.__edges.left:
            self.__platform.rect.left = self.__edges.left
            self.__platform.speed.x = -self.__platform.speed.x

    def update(self) -> None:
        """Do updates of the level's state and objects."""
        self.__process_key_presses()
        self.__process_collisions()

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

    Attributes:
        __edges (helpers.Edges): Contains width and height of the level.
        __images (dict[str, pygame.Surface]): Dictionary that contains level's objects images.
            Object types name can be:
            - 'platform' for entity.Platform object;
            - 'ball' for entity.Ball object;
            - 'block' for entity.Block objects.
        __horizontal_alignment (int): Horizontal alignment between blocks.
        __vertical_alignment (int): Vertical alignment between blocks.
        __num_of_rows (int): Number of rows of blocks.
    """

    def __init__(self, edges: helpers.Edges, images: dict, blocks_layout: dict) -> None:
        """Initialize the LevelMaker class object.

        Parameters:
            edges (helpers.Edges): Contains width and height of the level.
            images (dict[str, pygame.Surface]): Dictionary that contains level's objects images.
                Object types name can be:
                - 'platform' for entity.Platform object;
                - 'ball' for entity.Ball object;
                - 'block' for entity.Block objects.
            blocks_layout (dict[str, int]): Dictionary that contains blocks layout. Dictionary keys are follows:
                - 'horizontal_alignment': horizontal alignment between blocks;
                - 'vertical_alignment': vertical alignment between blocks;
                - 'num_of_rows': number of rows of blocks.
        """
        self.__edges = edges
        self.__images = images
        self.__horizontal_alignment = blocks_layout["horizontal_alignment"]
        self.__vertical_alignment = blocks_layout["vertical_alignment"]
        self.__num_of_rows = blocks_layout["num_of_rows"]

    def get_level(self, lifes: int = 4) -> Level:
        """Get a maked and initialized level.

        Returns:
            Level: The created level.
        """
        platform = entity.Platform(
            image=self.__images["platform"],
            rect=pygame.Rect(
                (self.__edges.width / 2, self.__edges.height * 0.75),
                self.__images["platform"].get_size(),
            ),
            speed=pygame.math.Vector2(5, 0),
        )
        ball = entity.Ball(
            image=self.__images["ball"],
            rect=pygame.Rect((0, 0), self.__images["ball"].get_size()),
            speed=pygame.math.Vector2(
                round(self.__edges.height * 0.005), -round(self.__edges.height * 0.005)
            ),
        )

        x = self.__horizontal_alignment
        top_alignment = ball.rect.height * 3
        y = round(ball.rect.height * 2.2 + top_alignment)

        rainbow_colors = [
            (255, 0, 0),  # Red
            (255, 200, 0),  # Yellow
            (0, 128, 0),  # Green
            (0, 0, 255),  # Blue
            (128, 0, 200),  # Violet
        ]
        colored_block_images = []
        for color in rainbow_colors:
            image = self.__images["block"].copy()
            image.fill(color, special_flags=pygame.BLEND_MULT)
            colored_block_images.append(image)

        blocks = []
        for i in range(0, self.__num_of_rows):
            while x + self.__images["block"].get_size()[0] < self.__edges.width:
                blocks.append(
                    entity.Block(
                        image=colored_block_images[i % len(colored_block_images)],
                        rect=pygame.Rect((x, y), self.__images["block"].get_size()),
                    )
                )
                x += self.__images["block"].get_size()[0] + self.__horizontal_alignment

            x = self.__horizontal_alignment
            y += self.__vertical_alignment

        return Level(
            lifes=lifes,
            blocks=blocks,
            platform=platform,
            ball=ball,
            edges=self.__edges,
            top_start=top_alignment,
        )
