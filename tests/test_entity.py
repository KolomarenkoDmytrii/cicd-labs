import copy

import pytest
import pygame

from .. import entity


@pytest.mark.parametrize(
    "one,other",
    [
        # check collision on the left side
        (
            entity.Entity(None, pygame.Rect(5, 5, 10, 10)),
            entity.Entity(None, pygame.Rect(12, 5, 10, 10)),
        ),
        # check collision on the right side
        (
            entity.Entity(None, pygame.Rect(5, 5, 10, 10)),
            entity.Entity(None, pygame.Rect(-4, 5, 10, 10)),
        ),
        # check collision on the top side
        (
            entity.Entity(None, pygame.Rect(5, 5, 10, 10)),
            entity.Entity(None, pygame.Rect(5, 14, 10, 10)),
        ),
        # check collision on the bottom side
        (
            entity.Entity(None, pygame.Rect(5, 5, 10, 10)),
            entity.Entity(None, pygame.Rect(5, -4, 10, 10)),
        ),
        # check if entities do not collide
        pytest.param(
            entity.Entity(None, pygame.Rect(5, 5, 10, 10)),
            entity.Entity(None, pygame.Rect(5, 40, 10, 10)),
            marks=pytest.mark.xfail,
        ),
    ],
)
def test_entities_collision(one: entity.Entity, other: entity.Entity):
    assert one.is_collided_with(other) == True


def test_moving_of_movable_entity():
    initial = entity.MovableEntity(
        None, pygame.Rect(5, 5, 5, 10), pygame.Vector2(3, -2)
    )
    moved = entity.Entity(
        None, pygame.Rect(8, 3, initial.rect.width, initial.rect.height)
    )

    initial.move()
    assert initial.rect == moved.rect


@pytest.mark.parametrize(
    "platform,expected",
    [
        # check horizontal movement
        (
            entity.Platform(None, pygame.Rect(5, 5, 10, 10), pygame.Vector2(10, 0)),
            entity.Platform(None, pygame.Rect(15, 5, 10, 10), pygame.Vector2(10, 0)),
        ),
        # check if paddle do not moves vertically
        pytest.param(
            entity.Platform(None, pygame.Rect(5, 5, 10, 10), pygame.Vector2(0, 5)),
            entity.Platform(None, pygame.Rect(5, 10, 10, 10), pygame.Vector2(0, 5)),
            marks=pytest.mark.xfail,
        ),
    ],
)
def test_moving_of_platform(platform: entity.Platform, expected: entity.Platform):
    platform.move()
    assert platform.rect == expected.rect


def test_adjusting_on_x_collision(monkeypatch):
    monkeypatch.setattr(
        "pygame.key.get_pressed",
        lambda: {
            pygame.K_a: False,
            pygame.K_RCTRL: False,
            pygame.K_LCTRL: False,
            pygame.K_d: False,
        },
    )

    static_entity = entity.Block(None, pygame.Rect(10, 5, 10, 10))

    speed = pygame.Vector2(10, 0)
    left_movable_entity = entity.Ball(
        None, pygame.Rect(5, 5, 10, 10), copy.deepcopy(speed)
    )
    right_movable_entity = entity.Platform(
        None, pygame.Rect(19, 5, 10, 10), copy.deepcopy(speed)
    )

    entity.adjust_on_x_collision(left_movable_entity, static_entity)
    assert left_movable_entity.rect.right == static_entity.rect.left
    assert left_movable_entity.speed.x == -speed.x

    entity.adjust_on_x_collision(right_movable_entity, static_entity)
    assert right_movable_entity.rect.left == static_entity.rect.right
    assert right_movable_entity.speed.x == -speed.x
