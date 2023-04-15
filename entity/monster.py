from __future__ import annotations

import dataclasses
import random
from dataclasses import dataclass
from typing import TYPE_CHECKING

import pygame

import game
import util
from entity.base import BaseEntity

if TYPE_CHECKING:
    from game import Game


@dataclass
class Monster(BaseEntity):
    next_target_x: int = dataclasses.field(init=False)
    next_target_y: int = dataclasses.field(init=False)

    def __post_init__(self):
        self._x = random.randrange(game.BOARD_SIZE)*game.CELL_SIZE + game.CELL_SIZE//2
        self._y = random.randrange(game.BOARD_SIZE)*game.CELL_SIZE + game.CELL_SIZE//2
        self.find_next_path()

    def on_touch(self) -> None:
        self.game.end_game(win=False)

    def find_next_path(self) -> None:
        """Finds a next cell that we should pathfind towards. Tries to BFS to the player."""
        target_x = self.game.player_x // game.CELL_SIZE
        target_y = self.game.player_y // game.CELL_SIZE
        board = self.game.board.board
        visited = [[False for _ in range(game.BOARD_SIZE)] for _ in range(game.BOARD_SIZE)]
        queue = [[board[self.x // game.CELL_SIZE][self.y // game.CELL_SIZE]]]
        while queue:
            path = queue.pop(0)
            node = path[-1]
            if node.x == target_x and node.y == target_y:
                break
            for i in range(4):
                if not node.connections[i]:
                    continue
                new_node = board[node.x+util.D_X[i]][node.y+util.D_Y[i]]
                if visited[new_node.x][new_node.y]:
                    continue
                visited[new_node.x][new_node.y] = True
                queue.append(path + [new_node])
        if len(path) == 1:
            print(f'path for dfs: {path=}')
            self.next_target_x = path[0].x
            self.next_target_y = path[0].y
            return
        self.next_target_x = path[1].x
        self.next_target_y = path[1].y

    def behavior(self) -> None:
        target_x_c = self.next_target_x * game.CELL_SIZE + game.CELL_SIZE//2
        target_y_c = self.next_target_y * game.CELL_SIZE + game.CELL_SIZE//2
        direction_x = target_x_c - self.x
        direction_y = target_y_c - self.y
        normalize = (direction_x**2 + direction_y**2) ** 0.5
        # the coefficient is the speed
        direction_x *= 2.6 / normalize
        direction_y *= 2.6 / normalize
        self._x += direction_x
        self._y += direction_y
        if abs(self.x - target_x_c) < 5.0 and abs(self.y - target_y_c) < 5.0:
            self._x = target_x_c
            self._y = target_y_c
            self.find_next_path()

    def draw(self, canvas: pygame.Surface) -> None:
        pygame.draw.rect(canvas, 0xaa0000, pygame.Rect(self.display_x-60, self.display_y-60, 120, 120))

    def tick(self) -> None:
        self.behavior()
        self.draw(self.game.canvas)
        rect = pygame.Rect(self.x-game.CELL_SIZE//2, self.y-game.CELL_SIZE//2, game.CELL_SIZE, game.CELL_SIZE)
        if rect.collidepoint(self.game.player_x, self.game.player_y):
            self.on_touch()

