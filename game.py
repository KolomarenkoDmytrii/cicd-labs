"""Main game routine."""

import os
import pygame
import helpers
import level


class Game:
    """Game application class.

    Attributes
    ----------
    __edges: helpers.Edges
        Contains width and height of the level.
    __images: dict[str, pygame.Surface]
        Dictionary that contains level's objects images.
    __level_maker: level.LevelMaker
        The level.LevelMaker object that do initializing of the level
    __font: pygame.font.Font
        Font which used for rendering text.
    __screen: pygame.Surface
        Contains the final rendered image that is putted on
        the screen.
    __background_color: tuple[int, int, int]
            Color of the background.
    __accent_color: tuple[int, int, int]
        Color of font, lines etc. It is opposite to backround color thus is it
        equals to "(255, 255, 255) - `background_color`"
    """

    def __init__(self, edges, num_of_columns, num_of_rows, background_color=(0, 0, 0)):
        """Initalize the game application object.

        Parameters
        ----------
        edges: helpers.Edges
            Contains width and height of the level.
        num_of_columns: int
            Number of columns of blocks.
        num_of_rows: int
            Number of rows of blocks.
        background_color: tuple[int, int, int]
            Color of the background. Accent color (color of font, lines etc) is
            opposite to backround color thus is it equals to
            "(255, 255, 255) - `background_color`"
        """

        pygame.init()

        self.__edges = edges

        self.__screen = \
            pygame.display.set_mode((self.__edges.width, self.__edges.height))

        self.__background_color = background_color
        self.__accent_color = tuple(
            pygame.math.Vector3(255, 255, 255) - \
                pygame.math.Vector3(self.__background_color)
        )

        horizontal_alignment = round(self.__edges.width * 0.03)

        # make game objects images
        #   Because blocks placementing is as follows:
        # alignment block alignment block ... block alignment,
        # formula for calculating block width is as follows
        block_width = round(
            (self.__edges.width - horizontal_alignment * 2 - horizontal_alignment * num_of_columns) /
                num_of_columns
        )
        ball_size = round(self.__edges.height * 0.03)

        ball_image = pygame.image.load(
            os.path.join(os.getcwd(), 'assets', 'ball.png')
        ).convert_alpha(self.__screen)
        ball_image = pygame.transform.scale(ball_image, (ball_size, ball_size))

        platform_image = pygame.image.load(
            os.path.join(os.getcwd(), 'assets', 'platform.png')
        ).convert_alpha(self.__screen)
        platform_image = pygame.transform.scale(platform_image, (round(self.__edges.width * 0.092), ball_size))

        block_image = pygame.image.load(
            os.path.join(os.getcwd(), 'assets', 'block.png')
        ).convert_alpha(self.__screen)
        block_image = pygame.transform.scale(block_image, (block_width, block_width * 0.45))

        self.__images = {
            'platform': platform_image,
            'ball': ball_image,
            'block': block_image
        }

        self.__level_maker = level.LevelMaker(
            edges=self.__edges,
            images=self.__images,
            blocks_layout={
                'horizontal_alignment': horizontal_alignment,
                'vertical_alignment': round(self.__edges.height * 0.06),
                'num_of_rows': num_of_rows
            }
        )

        self.__font = pygame.font.Font(
            os.path.join(os.getcwd(), 'assets', 'font.ttf'), 20
        )

    def __draw(self, sprites_group, labels, y_of_delimiter):
        """Update the image of the game.

        Parameters
        ----------
        sprites_group: pygame.sprite.Group
            Game objects that needed to be drawn. Pass `None` if no sprites
            needed to be drawn.
        labels: list[helpers.Label]
            Text label that needed to be drawn.
        y_of_delimiter: int
            Says where on Y axis draw the line that delimiters game area and
            game counters.
        """

        self.__screen.fill(self.__background_color)
        if sprites_group: sprites_group.draw(self.__screen)

        for label in labels:
            self.__screen.blit(*label.get_rendered())

        pygame.draw.line(
            self.__screen,
            self.__accent_color,
            (0, y_of_delimiter), (self.__edges.width, y_of_delimiter)
        )

        # flip() the display to put work on screen
        pygame.display.flip()

    def __render_menu(screen, font, color, menu_text, start_position):
        """Renders text label of the start / pause game menu text.

        Returns
        -------
        list[helpers.Label]
        """

        menu_labels = []
        for line in menu_text.splitlines():
            menu_labels.append(
                helpers.Label(font, start_position, line, color)
            )
            start_position += (0, menu_labels[-1].get_rendered()[1].height)

        return menu_labels

    def run(self):
        """Run the game application."""

        clock = pygame.time.Clock()

        # creating text labels
        text_color = self.__accent_color
        score_count = helpers.Label(
            self.__font, pygame.math.Vector2(self.__screen.get_width() / 1.5, 10), 'Score: 0', text_color
        )
        lifes_count = helpers.Label(
            self.__font, pygame.math.Vector2(self.__screen.get_width() / 4, 10), 'Lifes: ?', text_color
        )
        game_over_label = helpers.Label(
            self.__font,
            pygame.math.Vector2(self.__screen.get_width() * 0.45, self.__screen.get_height() / 2),
            'GAME OVER',
            text_color
        )
        victory_label = helpers.Label(
            self.__font,
            pygame.math.Vector2(self.__screen.get_width() * 0.45, self.__screen.get_height() / 2),
            'YOU WIN!',
            text_color
        )

        menu_text = \
            "Press SPACE to start the game or for resume / pause the game\n" \
            "Q for exit\n" \
            "DELETE for reset the game\n" \
            "CTRL for release the ball\n" \
            "A for moving platform to left\n" \
            "D for moving platform to right"
        menu_labels = Game.__render_menu(
            self.__screen,
            self.__font,
            self.__accent_color,
            menu_text,
            pygame.math.Vector2(self.__screen.get_width() / 6, self.__screen.get_height() / 4)
        )

        # game setup
        running = True
        is_paused = False
        level = self.__level_maker.get_level()
        is_menu_showing = True

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
                    if event.key == pygame.K_DELETE: # reset a game
                        level = self.__level_maker.get_level()
                        is_paused = False
                        is_menu_showing = True

            score_count.set_text(f'Score: {level.get_game_state().score}')
            lifes_count.set_text(f'Lifes: {level.get_game_state().lifes}')
            labels = [score_count, lifes_count]

            if level.get_game_state().is_game_over:
                labels.append(game_over_label)
            # if all blocks are cleared, player wins
            elif level.get_game_state().is_player_won:
                labels.append(victory_label)
            elif not is_paused:
                level.update()

            if is_menu_showing or is_paused:
                self.__draw(None, menu_labels, level.get_top_edge())
            else:
                self.__draw(level.get_sprites_group(), labels, level.get_top_edge())

            # limit FPS to 60
            clock.tick(60)

        pygame.quit()

