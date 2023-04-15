from __future__ import annotations

import abc
from dataclasses import dataclass
import math

import pygame.sprite


@dataclass
class BaseEntity:
    sprite: pygame.sprite.Sprite
    _x: int
    _y: int

    @property
    def x(self) -> int:
        return math.floor(self._x)

    @property
    def y(self) -> int:
        return math.floor(self._y)

    @abc.abstractmethod
    def on_touch(self):
        pass
