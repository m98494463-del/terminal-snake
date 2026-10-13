"""Pure game logic for Terminal Snake (no terminal code, easy to test)."""
from __future__ import annotations

import random
from dataclasses import dataclass, field

UP, DOWN, LEFT, RIGHT = (-1, 0), (1, 0), (0, -1), (0, 1)
OPPOSITE = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}


@dataclass
class Game:
    height: int
    width: int
    wrap: bool = False
    seed: int | None = None
    snake: list = field(default_factory=list)
    direction: tuple = RIGHT
    food: tuple | None = None
    bonus: tuple | None = None
    bonus_ttl: int = 0
    score: int = 0
    over: bool = False

    def __post_init__(self):
        self.rng = random.Random(self.seed)
        if not self.snake:
            r, c = self.height // 2, self.width // 2
            self.snake = [(r, c), (r, c - 1), (r, c - 2)]
        self._pending = self.direction
        self.grow = 0
        if self.food is None:
            self.food = self._free_cell()

    @property
    def level(self) -> int:
        return 1 + self.score // 50

    @property
    def tick_seconds(self) -> float:
        return max(0.04, 0.15 - 0.012 * (self.level - 1))

    def _free_cell(self):
        taken = set(self.snake) | {self.food, self.bonus}
        free = [(r, c) for r in range(self.height) for c in range(self.width) if (r, c) not in taken]
        return self.rng.choice(free) if free else None

    def turn(self, d: tuple) -> None:
        if d != OPPOSITE.get(self.direction):
            self._pending = d

    def step(self) -> None:
        if self.over:
            return
        self.direction = self._pending
        hr, hc = self.snake[0]
        nr, nc = hr + self.direction[0], hc + self.direction[1]
        if self.wrap:
            nr, nc = nr % self.height, nc % self.width
        elif not (0 <= nr < self.height and 0 <= nc < self.width):
            self.over = True
            return
        head = (nr, nc)
        body = self.snake if self.grow else self.snake[:-1]
        if head in body:
            self.over = True
            return
        self.snake.insert(0, head)
        if self.grow:
            self.grow -= 1
        else:
            self.snake.pop()

        if head == self.food:
            self.score += 10
            self.grow += 1
            self.food = self._free_cell()
            if self.bonus is None and self.rng.random() < 0.25:
                self.bonus, self.bonus_ttl = self._free_cell(), 40
        elif head == self.bonus:
            self.score += 30
            self.grow += 3
            self.bonus = None
        if self.bonus is not None:
            self.bonus_ttl -= 1
            if self.bonus_ttl <= 0:
                self.bonus = None
        if self.food is None:  # board full: you win
            self.over = True
