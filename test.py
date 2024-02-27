import engine

# # # Example file showing a circle moving on screen
import pygame

# engine.Game((700, 500)).run()
engine.Game((200, 200)).run()


# # pygame setup
# pygame.init()
# screen = pygame.display.set_mode((400, 500))
# clock = pygame.time.Clock()
# running = True
# dt = 0
#
# images = {'platform': pygame.Surface( (65, 20) ), 'ball': pygame.Surface( (20, 20) ) }
# images['platform'].fill( (0, 0, 0) )
# images['ball'].fill( (0, 0, 0) )
# level = engine.LevelMaker(
#     (400, 500),
#     images
# ).get_level()
#
# player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)
#
# while running:
#     # poll for events
#     # pygame.QUIT event means the user clicked X to close your window
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             running = False
#
#     # fill the screen with a color to wipe away anything from last frame
#     screen.fill("white")
#
#     level.get_sprites_group().draw(screen)
#     # level.process_key_presses()
#     level.update()
#
#     # pygame.draw.circle(screen, "red", player_pos, 40)
#
#     # keys = pygame.key.get_pressed()
#     # if keys[pygame.K_w]:
#     #     player_pos.y -= 300 * dt
#     # if keys[pygame.K_s]:
#     #     player_pos.y += 300 * dt
#     # if keys[pygame.K_a]:
#     #     player_pos.x -= 300 * dt
#     # if keys[pygame.K_d]:
#     #     player_pos.x += 300 * dt
#
#     # flip() the display to put your work on screen
#     pygame.display.flip()
#
#     # limits FPS to 60
#     # dt is delta time in seconds since last frame, used for framerate-
#     # independent physics.
#     # dt = clock.tick(60) / 1000
#     dt = clock.tick(60) / 1000
#
# pygame.quit()
