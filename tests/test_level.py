import copy

import pytest

# import pytest.monkeypatch
import pygame

from .. import level
from .. import entity


def test_release_ball():
    platform = entity.Platform(None, pygame.Rect(40, 50, 15, 5), pygame.Vector2(5, 0))
    ball = entity.Ball(None, pygame.Rect(5, 5, 10, 10), pygame.Vector2(10, 10))
    ball_speed = pygame.Vector2(10, 10)

    tested_level = level.Level(
        lifes=4,
        blocks=[],
        platform=platform,
        ball=ball,
        edges=pygame.Rect(0, 0, 100, 100),
        top_start=0,
    )

    # initial state
    assert ball.rect.centerx == platform.rect.centerx
    assert ball.rect.bottom == platform.rect.top
    assert ball.speed == pygame.Vector2(0, 0)

    assert not tested_level.get_game_state().is_ball_released

    # after ball release
    tested_level.release_ball()
    assert ball.speed == ball_speed
    assert tested_level.get_game_state().is_ball_released


def test_processing_key_presses(monkeypatch):
    keys_set = [
        # releasing the ball
        {
            pygame.K_a: True,
            pygame.K_RCTRL: True,
            pygame.K_LCTRL: True,
            pygame.K_d: False,
        },
        # moving the platform to left
        {
            pygame.K_a: False,
            pygame.K_RCTRL: False,
            pygame.K_LCTRL: True,
            pygame.K_a: True,
            pygame.K_d: False,
        },
        # moving the platform to right
        {
            pygame.K_a: False,
            pygame.K_RCTRL: False,
            pygame.K_LCTRL: True,
            pygame.K_a: False,
            pygame.K_d: True,
        },
    ]
    index = (i for i in range(len(keys_set)))

    def get_pygame_presses():
        return keys_set[next(index)]

    monkeypatch.setattr("pygame.key.get_pressed", get_pygame_presses)

    platform = entity.Platform(None, pygame.Rect(40, 50, 15, 5), pygame.Vector2(5, 0))

    tested_level = level.Level(
        lifes=4,
        blocks=[],
        platform=platform,
        ball=entity.Ball(None, pygame.Rect(5, 5, 10, 10), pygame.Vector2(10, 10)),
        edges=pygame.Rect(0, 0, 100, 100),
        top_start=0,
    )

    assert tested_level.get_game_state().is_ball_released == False
    tested_level.update()
    assert tested_level.get_game_state().is_ball_released == True

    speed_x = platform.speed.x
    tested_level.update()
    assert tested_level._Level__platform.speed.x == -abs(speed_x)

    tested_level.update()
    assert tested_level._Level__platform.speed.x == abs(speed_x)
