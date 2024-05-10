import os
import pygame
import helpers
import level
from pygame.math import Vector2
from typing import List


class Game:
    """Game application class."""

    def __init__(
        self,
        edges: helpers.Edges,
        num_of_columns: int,
        num_of_rows: int,
        background_color: tuple = (0, 0, 0),
        lifes: int = 4,
    ):
        """Initialize the game application object.

        Parameters
        ----------
        edges : helpers.Edges
            Contains width and height of the level.
        num_of_columns : int
            Number of columns of blocks.
        num_of_rows : int
            Number of rows of blocks.
        background_color : tuple[int, int, int], optional
            Color of the background. Accent color (color of font, lines etc) is
            opposite to background color thus it equals to
            "(255, 255, 255) - `background_color`", by default (0, 0, 0).
        lifes: int, Contains number of lives from which the game should begin
        """
        pygame.init()
        pygame.mixer.init()
        self.lifes = lifes
        self.music = pygame.mixer.Sound(
            os.path.join(os.getcwd(), "assets", "game-music.mp3")
        )
        self.music.play(-1)

        self.__edges: helpers.Edges = edges

        self.__screen: pygame.Surface = pygame.display.set_mode(
            (self.__edges.width, self.__edges.height)
        )

        self.__background_color: tuple[int, int, int] = background_color
        self.__accent_color: tuple[int, int, int] = tuple(
            pygame.math.Vector3(255, 255, 255)
            - pygame.math.Vector3(self.__background_color)
        )

        horizontal_alignment: int = round(self.__edges.width * 0.03)

        block_width: int = round(
            (
                self.__edges.width
                - horizontal_alignment * 2
                - horizontal_alignment * num_of_columns
            )
            / num_of_columns
        )
        ball_size: int = round(self.__edges.height * 0.03)

        ball_image: pygame.Surface = pygame.image.load(
            os.path.join(os.getcwd(), "assets", "ball.png")
        ).convert_alpha(self.__screen)
        ball_image = pygame.transform.scale(ball_image, (ball_size, ball_size))

        platform_image: pygame.Surface = pygame.image.load(
            os.path.join(os.getcwd(), "assets", "platform.png")
        ).convert_alpha(self.__screen)
        platform_image = pygame.transform.scale(
            platform_image, (round(self.__edges.width * 0.092), ball_size)
        )

        block_image: pygame.Surface = pygame.image.load(
            os.path.join(os.getcwd(), "assets", "block.png")
        ).convert_alpha(self.__screen)
        block_image = pygame.transform.scale(
            block_image, (block_width, block_width * 0.45)
        )

        self.__images: dict[str, pygame.Surface] = {
            "platform": platform_image,
            "ball": ball_image,
            "block": block_image,
        }

        self.__level_maker: level.LevelMaker = level.LevelMaker(
            edges=self.__edges,
            images=self.__images,
            blocks_layout={
                "horizontal_alignment": horizontal_alignment,
                "vertical_alignment": round(self.__edges.height * 0.06),
                "num_of_rows": num_of_rows,
            },
        )

        self.__font: pygame.font.Font = pygame.font.Font(
            os.path.join(os.getcwd(), "assets", "font.ttf"), 20
        )

    def __draw(
        self,
        sprites_group: pygame.sprite.Group | None,
        labels: List[helpers.Label],
        y_of_delimiter: int,
    ):
        """Update the image of the game.

        Parameters
        ----------
        sprites_group : pygame.sprite.Group
            Game objects that need to be drawn. Pass `None` if no sprites
            needed to be drawn.
        labels : List[helpers.Label]
            Text label that needs to be drawn.
        y_of_delimiter : int
            Says where on Y axis to draw the line that delimiters game area and
            game counters.
        """

        self.__screen.fill(self.__background_color)
        if sprites_group:
            sprites_group.draw(self.__screen)

        for label in labels:
            self.__screen.blit(*label.get_rendered())

        pygame.draw.line(
            self.__screen,
            self.__accent_color,
            (0, y_of_delimiter),
            (self.__edges.width, y_of_delimiter),
        )

        pygame.display.flip()

    @staticmethod
    def __render_menu(
        font: pygame.font.Font,
        color: tuple,
        menu_text: str,
        start_position: Vector2,
    ) -> List[helpers.Label]:
        """Renders text label of the start / pause game menu text.

        Returns
        -------
        List[helpers.Label]
        """

        menu_labels = []
        for line in menu_text.splitlines():
            menu_labels.append(helpers.Label(font, start_position, line, color))
            start_position += (0, menu_labels[-1].get_rendered()[1].height)

        return menu_labels

    def run(self):
        """Run the game application."""

        clock = pygame.time.Clock()

        text_color = self.__accent_color
        score_count = helpers.Label(
            self.__font,
            pygame.math.Vector2(self.__screen.get_width() / 1.5, 10),
            "Score: 0",
            text_color,
        )
        lifes_count = helpers.Label(
            self.__font,
            pygame.math.Vector2(self.__screen.get_width() / 4, 10),
            "Lifes: ?",
            text_color,
        )
        game_over_label = helpers.Label(
            self.__font,
            pygame.math.Vector2(
                self.__screen.get_width() * 0.45, self.__screen.get_height() / 2
            ),
            "GAME OVER",
            text_color,
        )
        victory_label = helpers.Label(
            self.__font,
            pygame.math.Vector2(
                self.__screen.get_width() * 0.45, self.__screen.get_height() / 2
            ),
            "YOU WIN!",
            text_color,
        )

        menu_text = (
            "Press SPACE to start the game or for resume / pause the game\n"
            "Q for exit\n"
            "DELETE for reset the game\n"
            "CTRL for release the ball\n"
            "A for moving platform to left\n"
            "D for moving platform to right\n"
            "Press ALT to set the game with hardcore mode[1 life]\n"
            "Press F1 to play or stop music"
        )
        menu_labels = Game.__render_menu(
            self.__font,
            self.__accent_color,
            menu_text,
            pygame.math.Vector2(
                self.__screen.get_width() / 6, self.__screen.get_height() / 4
            ),
        )

        running: bool = True
        is_paused: bool = False
        lvl = self.__level_maker.get_level(lifes=self.lifes)
        is_menu_showing: bool = True
        is_music_paused: bool = False

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        is_paused = not is_paused
                        is_menu_showing = False
                    if event.key == pygame.K_q:
                        running = False
                    if event.key == pygame.K_DELETE:
                        lvl = self.__level_maker.get_level()
                        is_paused = not is_paused
                        is_menu_showing = True
                    if event.key == pygame.K_RALT or event.key == pygame.K_LALT:
                        lvl = self.__level_maker.get_level(lifes=1)
                        is_paused = not is_paused
                        is_menu_showing = False
                    if event.key == pygame.K_F1:
                        is_music_paused = not is_music_paused
                        if is_music_paused:
                            self.music.stop()
                        else:
                            self.music.play(-1)

            score_count.set_text(f"Score: {lvl.get_game_state().score}")
            lifes_count.set_text(f"Lifes: {lvl.get_game_state().lifes}")

            labels = [score_count, lifes_count]

            if lvl.get_game_state().is_game_over:
                labels.append(game_over_label)

            elif lvl.get_game_state().is_player_won:
                labels.append(victory_label)
            elif not is_paused:
                lvl.update()

            if is_menu_showing or is_paused:
                self.__draw(None, menu_labels, lvl.get_top_edge())
            else:
                self.__draw(lvl.get_sprites_group(), labels, lvl.get_top_edge())

            clock.tick(60)

        pygame.quit()
