import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from snake_engine import DOWN, LEFT, RIGHT, UP, Game


def test_moves_forward():
    g = Game(10, 10, seed=1)
    head = g.snake[0]
    g.step()
    assert g.snake[0] == (head[0], head[1] + 1) and len(g.snake) == 3


def test_cannot_reverse():
    g = Game(10, 10, seed=1)
    g.turn(LEFT)
    g.step()
    assert not g.over and g.direction == RIGHT


def test_eat_food_grows_and_scores():
    g = Game(10, 10, seed=1)
    r, c = g.snake[0]
    g.food = (r, c + 1)
    g.step(); g.step()
    assert g.score == 10 and len(g.snake) == 4


def test_bonus_food():
    g = Game(10, 10, seed=1)
    r, c = g.snake[0]
    g.bonus, g.bonus_ttl = (r, c + 1), 10
    g.food = (0, 0)
    g.step()
    assert g.score == 30 and g.bonus is None


def test_wall_kills_without_wrap():
    g = Game(5, 5, seed=1)
    for _ in range(5):
        g.step()
    assert g.over


def test_wrap_mode():
    g = Game(5, 5, wrap=True, seed=1, food=(0, 0))
    for _ in range(5):
        g.step()
    assert not g.over


def test_self_collision():
    g = Game(10, 10, seed=1, snake=[(5, 5), (5, 4), (5, 3), (5, 2), (5, 1)], food=(0, 0))
    for d in (DOWN, LEFT, UP):
        g.turn(d); g.step()
    assert g.over


def test_level_speeds_up():
    g = Game(10, 10, seed=1)
    slow = g.tick_seconds
    g.score = 200
    assert g.level == 5 and g.tick_seconds < slow
