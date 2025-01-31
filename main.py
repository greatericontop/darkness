"""Main File, Loads Game"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import ClassVar

import pygame

from game import Game


__version__ = '1.0.0-dev'

WINDOW_FLAGS = pygame.RESIZABLE


@dataclass
class Main:
    TPS: ClassVar[int] = 60
    x_size: int = 1280
    y_size: int = 720

    number_tick: int = 0

    @property
    def x_center(self) -> int:
        return self.x_size // 2

    @property
    def y_center(self) -> int:
        return self.y_size // 2

    def main(self) -> None:
        pygame.init()
        pygame.display.set_caption(f'DARKNESS: THE ESCAPE | Version {__version__}')
        canvas = pygame.display.set_mode((self.x_size, self.y_size), WINDOW_FLAGS)
        clock = pygame.time.Clock()

        game = Game(self, canvas)
        game.display_menu()

        while True:
            self.number_tick += 1
            pygame.display.update()
            clock.tick(self.TPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.VIDEORESIZE:
                    self.x_size = event.w
                    self.y_size = event.h
                game.handle_event(event)
            game.tick_loop()


if __name__ == '__main__':
    Main().main()
