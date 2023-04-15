from __future__ import annotations

import abc
from dataclasses import dataclass
import math

import pygame.sprite


@dataclass
class BaseEntity:
    game: Game
    _x: float
    _y: float

    @property
    def x(self) -> int:
        return math.floor(self._x)

    @property
    def y(self) -> int:
        return math.floor(self._y)

    @property
    def display_x(self) -> int:
        return math.floor(self.x + self.game.alignment_x)

    @property
    def display_y(self) -> int:
        return math.floor(self.y + self.game.alignment_y)

    @abc.abstractmethod
    def on_touch(self) -> None:
        pass

    @abc.abstractmethod
    def behavior(self) -> None:
        pass

    @abc.abstractmethod
    def draw(self, canvas: pygame.Surface) -> None:
        pass

    @abc.abstractmethod
    def tick(self) -> None:
        pass
