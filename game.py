"""Game class."""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass
import enum
import sys
from typing import TYPE_CHECKING

import pygame

from mazegen import generator
from mazegen.game_structures import Board, D
from util import clear_board, draw_centered_text

if TYPE_CHECKING:
    from main import Main

TITLE_W = 240
TITLE_H = 35
BOARD_SIZE = 20
THICKNESS = 8
CELL_SIZE = 360
OPENING_BUFFER_SIZE = THICKNESS + 115
PLAYER_SIZE = 15


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

    player_x: float = dataclasses.field(init=False, default=100.0)
    player_y: float = dataclasses.field(init=False, default=100.0)
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
            text = 'YOU WIN!'
            color = 0x00ff00ff
        elif self.playing == Playing.ENDING_LOSE:
            text = 'YOU LOSE!'
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

    def end_game(self, win: bool) -> None:
        self.playing = Playing.ENDING_WIN if win else Playing.ENDING_LOSE
        self.display_menu()

    def tick_loop(self) -> None:
        """Tick loop."""
        if self.playing == Playing.GAME:
            self.tick_game()

    def tick_game(self) -> None:
        """Game tick loop."""

        # Movement
        a = 0.65
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


        # Rectangular collision physics
        # Find extreme bounding box of movement
        self.do_physics()


        self.player_x += self.x_velocity
        self.player_y += self.y_velocity

        # Rendering
        clear_board(self.canvas)
        # Alignment is the offset of the top-left (0,0) corner of the map.
        alignment_x = self.main.x_center - self.player_x
        alignment_y = self.main.y_center - self.player_y

        for x in range(BOARD_SIZE):
            for y in range(BOARD_SIZE):
                x_c = int(x * CELL_SIZE + alignment_x)
                y_c = int(y * CELL_SIZE + alignment_y)
                pygame.draw.rect(self.canvas, 0xc0c0c0, pygame.Rect(x_c + THICKNESS, y_c + THICKNESS, CELL_SIZE - 2*THICKNESS, CELL_SIZE - 2*THICKNESS))
                # Left sided edge
                if self.board.board[x][y].connections[D.LEFT]:
                    pygame.draw.rect(self.canvas, 0xc0c0c0,
                                     pygame.Rect(x_c-THICKNESS, y_c+OPENING_BUFFER_SIZE, 2*THICKNESS, CELL_SIZE-2*OPENING_BUFFER_SIZE))
                # Top sided edge
                if self.board.board[x][y].connections[D.UP]:
                    pygame.draw.rect(self.canvas, 0xc0c0c0,
                                     pygame.Rect(x_c+OPENING_BUFFER_SIZE, y_c-THICKNESS, CELL_SIZE-2*OPENING_BUFFER_SIZE, 2*THICKNESS))
        # fat player (just like you)
        pygame.draw.rect(self.canvas, 0xff00ff, pygame.Rect(self.main.x_center-PLAYER_SIZE, self.main.y_center-PLAYER_SIZE, 2*PLAYER_SIZE, 2*PLAYER_SIZE))

        #
        # A "cell" will be 160 pixels (a square)
        # You should draw lines (rectangles) to divide the cells
        # The player should always appear in the middle
        # Basically, you should align the **BACKGROUND** such that the player appears in the middle.
        #    When player at x=40, y=40 the player appears in the middle of the 0,0 cell.
        #    When player at x=120, y=120 the player appears in the middle of the 120,120 cell.
        #    And so on.
        #

    def do_physics(self):
        x_before, y_before = self.player_x, self.player_y
        x_after, y_after = x_before + self.x_velocity, y_before + self.y_velocity
        x_min = min(x_before - PLAYER_SIZE, x_after - PLAYER_SIZE)
        x_max = max(x_before + PLAYER_SIZE, x_after + PLAYER_SIZE)
        y_min = min(y_before - PLAYER_SIZE, y_after - PLAYER_SIZE)
        y_max = max(y_before + PLAYER_SIZE, y_after + PLAYER_SIZE)
        # Check all 4 walls of the current cell
        cell_i = int(x_before / CELL_SIZE)
        cell_j = int(y_before / CELL_SIZE)
        cell_x = cell_i * CELL_SIZE
        cell_y = cell_j * CELL_SIZE
        cell = self.board.board[cell_i][cell_j]
        connections = cell.connections

        # walls_to_check[x] = (wall_x_min, wall_x_max, wall_y_min, wall_y_max)
        walls_to_check = []
        if not connections[D.LEFT]:
            walls_to_check.append((cell_x - THICKNESS, cell_x + THICKNESS, cell_y, cell_y + CELL_SIZE))
        walls_to_check.append((cell_x - THICKNESS, cell_x + THICKNESS, cell_y, cell_y + OPENING_BUFFER_SIZE))
        walls_to_check.append((cell_x - THICKNESS, cell_x + THICKNESS, cell_y + CELL_SIZE - OPENING_BUFFER_SIZE, cell_y + CELL_SIZE))
        if not connections[D.RIGHT]:
            walls_to_check.append((cell_x + CELL_SIZE - THICKNESS, cell_x + CELL_SIZE + THICKNESS, cell_y, cell_y + CELL_SIZE))
        walls_to_check.append((cell_x + CELL_SIZE - THICKNESS, cell_x + CELL_SIZE + THICKNESS, cell_y, cell_y + OPENING_BUFFER_SIZE))
        walls_to_check.append((cell_x + CELL_SIZE - THICKNESS, cell_x + CELL_SIZE + THICKNESS, cell_y + CELL_SIZE - OPENING_BUFFER_SIZE, cell_y + CELL_SIZE))
        if not connections[D.UP]:
            walls_to_check.append((cell_x, cell_x + CELL_SIZE, cell_y - THICKNESS, cell_y + THICKNESS))
        walls_to_check.append((cell_x, cell_x + OPENING_BUFFER_SIZE, cell_y - THICKNESS, cell_y + THICKNESS))
        walls_to_check.append((cell_x + CELL_SIZE - OPENING_BUFFER_SIZE, cell_x + CELL_SIZE, cell_y - THICKNESS, cell_y + THICKNESS))
        if not connections[D.DOWN]:
            walls_to_check.append((cell_x, cell_x + CELL_SIZE, cell_y + CELL_SIZE - THICKNESS, cell_y + CELL_SIZE + THICKNESS))
        walls_to_check.append((cell_x, cell_x + OPENING_BUFFER_SIZE, cell_y + CELL_SIZE - THICKNESS, cell_y + CELL_SIZE + THICKNESS))
        walls_to_check.append((cell_x + CELL_SIZE - OPENING_BUFFER_SIZE, cell_x + CELL_SIZE, cell_y + CELL_SIZE - THICKNESS, cell_y + CELL_SIZE + THICKNESS))

        has_intersected = False
        for wall_x_min, wall_x_max, wall_y_min, wall_y_max in walls_to_check:
            intersecting = not (
                    x_max < wall_x_min or x_min > wall_x_max
                    or y_max < wall_y_min or y_min > wall_y_max
            )
            if intersecting:
                has_intersected = True
                break
        if has_intersected:  # We'll apply physics if at least one collision failed its check.
            if self.x_velocity**2 + self.y_velocity**2 >= 0.16:
                # If the Euclidean velocity is >=0.4, reduce by half and try again.
                self.x_velocity *= 0.5
                self.y_velocity *= 0.5
                self.do_physics()  # Do this again, since this function modifies the velocity.
            else:
                # If it's negligible, simply stop.
                self.x_velocity = 0
                self.y_velocity = 0







