import copy

import pytest
import pygame

from ..src import level
from ..src import entity


@pytest.fixture(autouse=True)
def dummy_key_presses(monkeypatch):
    monkeypatch.setattr(
        "pygame.key.get_pressed",
        lambda: {
            pygame.K_a: False,
            pygame.K_RCTRL: False,
            pygame.K_LCTRL: False,
            pygame.K_a: False,
            pygame.K_d: False,
        },
    )


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

    # realising the ball from the platform
    assert not tested_level.get_game_state().is_ball_released
    tested_level.update()
    assert tested_level.get_game_state().is_ball_released

    speed_x = platform.speed.x
    tested_level.update()
    assert tested_level._Level__platform.speed.x == -abs(speed_x)

    tested_level.update()
    assert tested_level._Level__platform.speed.x == abs(speed_x)


def test_block_logic():
    block = entity.Block(None, pygame.Rect(10, 10, 10, 10))
    initial_ball_speed = pygame.Vector2(10, 10)
    ball = entity.Ball(
        None, pygame.Rect(5, 15, 5, 5), copy.deepcopy(initial_ball_speed)
    )

    platform = entity.Platform(None, pygame.Rect(5, 15, 15, 5), pygame.Vector2(0, 0))
    platform.rect.centerx = ball.rect.centerx
    platform.rect.top = ball.rect.bottom

    tested_level = level.Level(
        lifes=4,
        blocks=[block],
        platform=platform,
        ball=ball,
        edges=pygame.Rect(0, 0, 100, 100),
        top_start=0,
    )

    previous_state = copy.deepcopy(tested_level.get_game_state())

    assert not block.is_destroyed()

    tested_level.release_ball()
    tested_level.update()

    assert block.is_destroyed()
    assert tested_level.get_game_state().score > previous_state.score
    # if ball speed is increased
    assert abs(ball.speed.x) > abs(initial_ball_speed.x) and abs(ball.speed.y) > abs(
        initial_ball_speed.y
    )


def test_victory_after_destroying_all_blocks():
    block = entity.Block(None, pygame.Rect(10, 10, 10, 10))
    ball = entity.Ball(None, pygame.Rect(5, 15, 5, 5), pygame.Vector2(10, 10))

    platform = entity.Platform(None, pygame.Rect(5, 15, 15, 5), pygame.Vector2(0, 0))
    platform.rect.centerx = ball.rect.centerx
    platform.rect.top = ball.rect.bottom

    tested_level = level.Level(
        lifes=4,
        blocks=[block],
        platform=platform,
        ball=ball,
        edges=pygame.Rect(0, 0, 100, 100),
        top_start=0,
    )

    tested_level.release_ball()
    tested_level.update()

    assert tested_level.get_game_state().is_player_won


def test_ball_is_out_of_bottom_edge_logic():
    block = entity.Block(None, pygame.Rect(0, 0, 1, 1))
    ball = entity.Ball(None, pygame.Rect(5, 2, 5, 5), pygame.Vector2(15, 15))

    platform = entity.Platform(
        None, pygame.Rect(5, ball.rect.bottom, 10, 5), pygame.Vector2(0, 0)
    )
    platform.rect.centerx = ball.rect.centerx
    platform.rect.top = ball.rect.bottom

    tested_level = level.Level(
        lifes=1,
        blocks=[block],
        platform=platform,
        ball=ball,
        edges=pygame.Rect(0, 0, 100, 15),
        top_start=0,
    )

    previous_state = copy.deepcopy(tested_level.get_game_state())

    tested_level.release_ball()
    tested_level.update()

    assert previous_state.lifes - tested_level.get_game_state().lifes == 1
    assert tested_level.get_game_state().is_game_over
