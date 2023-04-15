"""Game class."""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass
import enum
import sys
from typing import TYPE_CHECKING

import pygame

from mazegen import generator
from mazegen.game_structures import Board
from util import clear_board, draw_centered_text

if TYPE_CHECKING:
    from main import Main


TITLE_W = 240
TITLE_H = 35
BOARD_SIZE = 10
CELL_SIZE = 240


class Playing(enum.Enum):
    MENU = 0
    GAME = 1
    ENDING_WIN = 2
    ENDING_LOSE = 3


@dataclass
class Game:
    main: Main
    canvas: pygame.Surface
    playing: Playing = dataclasses.field(init=False, default=Playing.MENU)

    board: Board = dataclasses.field(init=False)

    player_x: float = dataclasses.field(init=False, default=0.0)
    player_y: float = dataclasses.field(init=False, default=0.0)
    x_velocity: float = dataclasses.field(init=False, default=0.0)
    y_velocity: float = dataclasses.field(init=False, default=0.0)

    font_42: pygame.font.Font = dataclasses.field(init=False)
    font_60: pygame.font.Font = dataclasses.field(init=False)

    def __post_init__(self):
        self.font_42 = pygame.font.Font('assets/liberationserif.ttf', 42)
        self.font_60 = pygame.font.Font('assets/liberationserif.ttf', 60)

    @property
    def start_rect(self) -> pygame.Rect:
        return pygame.Rect(self.main.x_center - TITLE_W, 280 - TITLE_H, 2 * TITLE_W, 2 * TITLE_H)

    @property
    def quit_rect(self) -> pygame.Rect:
        return pygame.Rect(self.main.x_center - TITLE_W, 380 - TITLE_H, 2 * TITLE_W, 2 * TITLE_H)

    def display_menu(self):

        if self.playing == Playing.ENDING_WIN:
            text = 'YOU WIN'
            color = 0x00ff00ff
        elif self.playing == Playing.ENDING_LOSE:
            text = 'YOU LOSE'
            color = 0xffffffff
        else:
            text = 'DARKNESS: THE ESCAPE'
            color = 0xffffffff

        self.playing = Playing.MENU
        clear_board(self.canvas)
        draw_centered_text(self.canvas, self.font_60.render(text, True, color), self.main.x_center, 90)
        pygame.draw.rect(self.canvas, 0x00aa00, self.start_rect)
        draw_centered_text(self.canvas, self.font_42.render('PLAY', True, 0xffffffff), self.main.x_center, 280)
        pygame.draw.rect(self.canvas, 0xaa0000, self.quit_rect)
        draw_centered_text(self.canvas, self.font_42.render('QUIT', True, 0xffffffff), self.main.x_center, 380)

    def handle_event(self, event: pygame.event.Event):
        if self.playing == Playing.MENU:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if self.start_rect.collidepoint(mouse_pos):
                    self.run_game()
                if self.quit_rect.collidepoint(mouse_pos):
                    pygame.quit()
                    sys.exit(0)

    def run_game(self) -> None:
        self.playing = Playing.GAME
        self.board = Board(None)
        generator.fill(self.board, BOARD_SIZE)

    def tick_loop(self) -> None:
        """Tick loop."""
        if self.playing == Playing.GAME:
            self.tick_game()

    def tick_game(self) -> None:
        """Game tick loop."""

        # Movement
        a = 0.7
        if pygame.key.get_pressed()[pygame.K_w]:
            self.y_velocity -= a
        if pygame.key.get_pressed()[pygame.K_a]:
            self.x_velocity -= a
        if pygame.key.get_pressed()[pygame.K_s]:
            self.y_velocity += a
        if pygame.key.get_pressed()[pygame.K_d]:
            self.x_velocity += a
        self.x_velocity *= 0.93
        self.y_velocity *= 0.93
        self.player_x += self.x_velocity
        self.player_y += self.y_velocity

        # Rectangular collision physics

        # Rendering
        clear_board(self.canvas)
        # Alignment is the offset of the top-left (0,0) corner of the map.
        alignment_x = self.main.x_center - self.player_x
        alignment_y = self.main.y_center - self.player_y

        for x in range(BOARD_SIZE):
            for y in range(BOARD_SIZE):
                x_c = int(x*CELL_SIZE + alignment_x)
                y_c = int(y*CELL_SIZE + alignment_y)
                pygame.draw.rect(self.canvas, 0xffc0c0c0, pygame.Rect(x_c + 6, y_c + 6, CELL_SIZE-12, CELL_SIZE-12))


        pygame.draw.rect(self.canvas, 0x00ff00ff, pygame.Rect(self.main.x_center-10, self.main.y_center-10, 20, 20))

        #
        # A "cell" will be 160 pixels (a square)
        # You should draw lines (rectangles) to divide the cells
        # The player should always appear in the middle
        # Basically, you should align the **BACKGROUND** such that the player appears in the middle.
        #    When player at x=40, y=40 the player appears in the middle of the 0,0 cell.
        #    When player at x=120, y=120 the player appears in the middle of the 120,120 cell.
        #    And so on.
        #
