from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import pygame

from entity.base import BaseEntity

if TYPE_CHECKING:
    from game import Game


@dataclass
class Monster(BaseEntity):
    game: Game

    def __init__(self, height, width):
        self.image = pygame.Surface([width, height])
        self.image.fill(0xaa0000)
        pygame.draw.rect(self.image, 0xaa0000, pygame.Rect(200, 200, width, height))
        self.rect = self.image.get_rect()

    def on_touch(self):
        self.game.end_game(win=False)

    def behavior(self, x_c, y_c):
        ...

