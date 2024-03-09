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
    """

    def __init__(self, edges, num_of_columns, num_of_rows):
        """Initalize the game application object.

        Parameters
        ----------
        edges: helpers.Edges
            Contains width and height of the level.
        num_of_columns: int
            Number of columns of blocks.
        num_of_rows: int
            Number of rows of blocks.
        """
        self.__edges = edges

        horizontal_margin = round(self.__edges.width * 0.03)

        block_width = round(
            (self.__edges.width - horizontal_margin * 2 - horizontal_margin * num_of_columns) /
                num_of_columns
        )

        self.__images = {
            'platform': pygame.Surface((65, 20)),
            'ball': pygame.Surface((15, 15)),
            'block': pygame.Surface( (block_width, 20) )
        }
        self.__images['platform'].fill((0, 0, 0))
        self.__images['ball'].fill((100, 100, 60))
        self.__images['block'].fill((0, 0, 0))

        self.__level_maker = level.LevelMaker(
            edges=self.__edges,
            images=self.__images,
            blocks_layout={
                'horizontal_margin': horizontal_margin,
                'vertical_margin': round(self.__edges.height * 0.06),
                'num_of_rows': num_of_rows
            }
        )

    def __draw(self, screen, sprites_group, labels, y_of_delimiter):
        """Update the image of the game.

        Parameters
        ----------
        screen: pygame.Surface
            A `Surface` object (created using ``pygame.display.set_mode()``)
            which contains the final rendered image that is putted on
            the screen.
        sprites_group: pygame.sprite.Group
            Game objects that needed to be drawn. Pass `None` if no sprites
            needed to be drawn.
        labels: list[helpers.Label]
            Text label that needed to be drawn.
        y_of_delimiter: int
            Says where on Y axis draw the line that delimiters game area and
            game counters.
        """
        # fill the screen with a color to wipe away anything from last frame
        screen.fill('white')
        if sprites_group: sprites_group.draw(screen)

        for label in labels:
            screen.blit(*label.get_rendered())

        pygame.draw.line(
            screen,
            (0, 0, 0),
            (0, y_of_delimiter), (self.__edges.width, y_of_delimiter)
        )

        # flip() the display to put work on screen
        pygame.display.flip()

    def __render_menu(screen, font, menu_text, start_position):
        """Renders text label of the start / pause game menu text.

        Returns
        -------
        list[helpers.Label]
        """
        menu_labels = []
        for line in menu_text.splitlines():
            menu_labels.append(helpers.Label(font, start_position, line))
            start_position += (0, menu_labels[-1].get_rendered()[1].height)

        return menu_labels

    def run(self):
        """Run the game application."""
        # pygame setup
        pygame.init()
        screen = pygame.display.set_mode((self.__edges.width, self.__edges.height))
        clock = pygame.time.Clock()
        font = pygame.font.SysFont('roboto', 20)

        # creating text labels
        score_count = helpers.Label(
            font, pygame.Vector2(screen.get_width() / 1.5, 10), 'Score: 0'
        )
        lifes_count = helpers.Label(
            font, pygame.Vector2(screen.get_width() / 4, 10), 'Lifes: ?'
        )
        game_over_label = helpers.Label(
            font,
            pygame.Vector2(screen.get_width() * 0.45, screen.get_height() / 2),
            'GAME OVER'
        )
        victory_label = helpers.Label(
            font,
            pygame.Vector2(screen.get_width() * 0.45, screen.get_height() / 2),
            'YOU WIN!'
        )
        paused_label = helpers.Label(
            font,
            pygame.Vector2(screen.get_width() * 0.45, screen.get_height() / 2),
            'PAUSE'
        )

        menu_text = \
            "Press SPACE to start the game or for resume / pause the game\n" \
            "Q for exit\n" \
            "DELETE for reset the game\n" \
            "CTRL for release the ball\n" \
            "A for moving platform to left\n" \
            "D for moving platform to right"
        menu_labels = Game.__render_menu(
            screen,
            font,
            menu_text,
            pygame.Vector2(screen.get_width() / 6, screen.get_height() / 4)
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
                self.__draw(screen, None, menu_labels, level.get_top_edge())
            else:
                self.__draw(screen, level.get_sprites_group(), labels, level.get_top_edge())

            # limit FPS to 60
            clock.tick(60)

        pygame.quit()

