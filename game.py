"""Game class."""

from __future__ import annotations

import dataclasses
import random
from dataclasses import dataclass
import enum
import sys
from typing import TYPE_CHECKING

import pygame

import util
from mazegen import generator
from mazegen.game_structures import Board, D
from entity.monster import Monster
from util import clear_board, draw_centered_text

if TYPE_CHECKING:
    from main import Main

TITLE_W = 240
TITLE_H = 35
BOARD_SIZE = 26
THICKNESS = 10
CELL_SIZE = 440
OPENING_BUFFER_SIZE = THICKNESS + 135
PLAYER_SIZE = 15
PLAYER_ACCEL = 0.65


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
    monsters: list = dataclasses.field(init=False, default=None)

    tick_start: int = dataclasses.field(init=False, default=None)

    board: Board = dataclasses.field(init=False)

    player_x: float = dataclasses.field(init=False, default=0.0)
    player_y: float = dataclasses.field(init=False, default=0.0)
    x_velocity: float = dataclasses.field(init=False, default=0.0)
    y_velocity: float = dataclasses.field(init=False, default=0.0)

    font_42: pygame.font.Font = dataclasses.field(init=False)
    font_60: pygame.font.Font = dataclasses.field(init=False)
    font_16_nerd: pygame.font.Font = dataclasses.field(init=False)

    def __post_init__(self):
        self.font_42 = pygame.font.Font('assets/liberationserif.ttf', 42)
        self.font_60 = pygame.font.Font('assets/liberationserif.ttf', 60)
        self.font_16_nerd = pygame.font.Font('assets/jetbrainsmononerd.ttf', 16)

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
            color = 0xff0000ff
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
        self.tick_start = self.main.number_tick
        self.playing = Playing.GAME
        self.board = Board()
        for _ in range(100):
            generator.fill(self.board, BOARD_SIZE)
            # Make up to 60 attempts to spawn in a dark square
            for i in range(60):
                spawn_x = random.randrange(BOARD_SIZE)
                spawn_y = random.randrange(BOARD_SIZE)
                if self.board.board[spawn_x][spawn_y].is_darkest():
                    break
            number = 0
            for x in range(BOARD_SIZE):
                for y in range(BOARD_SIZE):
                    if self.board.board[x][y].is_darkest(): number += 1
            print(f'Attempts x{i} with {number} darkests')
        self.player_x = spawn_x * CELL_SIZE + CELL_SIZE // 2
        self.player_y = spawn_y * CELL_SIZE + CELL_SIZE // 2
        self.x_velocity = 0.0
        self.y_velocity = 0.0
        self.monsters = [
            Monster(game=self, _x=-1.0, _y=-1.0, speed=2.75+1.25*random.random()),  # 2.75 to 4.0
            Monster(game=self, _x=-1.0, _y=-1.0, speed=2.0+1.0*random.random()),  # 2.0 to 3.0
            Monster(game=self, _x=-1.0, _y=-1.0, speed=1.0+1.5*random.random()),  # 1.0 to 2.5
            Monster(game=self, _x=-1.0, _y=-1.0, speed=1.0+1.5*random.random()),  # 1.0 to 2.5
            Monster(game=self, _x=-1.0, _y=-1.0, speed=1.0+1.5*random.random()),  # 1.0 to 2.5
        ]

    def end_game(self, win: bool) -> None:
        self.playing = Playing.ENDING_WIN if win else Playing.ENDING_LOSE
        self.display_menu()

    def tick_loop(self) -> None:
        """Tick loop."""
        if self.playing == Playing.GAME:
            self.tick_game()

    @property
    def alignment_x(self) -> float:
        return self.main.x_center - self.player_x

    @property
    def alignment_y(self) -> float:
        return self.main.y_center - self.player_y

    def tick_game(self) -> None:
        """Game tick loop."""

        # Movement
        if pygame.key.get_pressed()[pygame.K_w]:
            self.y_velocity -= PLAYER_ACCEL
        if pygame.key.get_pressed()[pygame.K_a]:
            self.x_velocity -= PLAYER_ACCEL
        if pygame.key.get_pressed()[pygame.K_s]:
            self.y_velocity += PLAYER_ACCEL
        if pygame.key.get_pressed()[pygame.K_d]:
            self.x_velocity += PLAYER_ACCEL
        self.x_velocity *= 0.93
        self.y_velocity *= 0.93

        # Rectangular collision physics
        self.do_physics()
        self.player_x += self.x_velocity
        self.player_y += self.y_velocity

        cell_x = int(self.player_x / CELL_SIZE)
        cell_y = int(self.player_y / CELL_SIZE)
        if cell_x == self.board.maze_exit_x and cell_y == self.board.maze_exit_y:
            self.end_game(True)
            return

        # Rendering
        clear_board(self.canvas)
        for x in range(BOARD_SIZE):
            for y in range(BOARD_SIZE):
                x_c = int(x * CELL_SIZE + self.alignment_x)
                y_c = int(y * CELL_SIZE + self.alignment_y)
                node_power_color = self.board.board[x][y].color()
                cell_color = 0xffffff if x == self.board.maze_exit_x and y == self.board.maze_exit_y else node_power_color
                pygame.draw.rect(self.canvas, cell_color,
                                 pygame.Rect(x_c + THICKNESS, y_c + THICKNESS, CELL_SIZE - 2 * THICKNESS,
                                             CELL_SIZE - 2 * THICKNESS))
                # Left sided edge
                if self.board.board[x][y].connections[D.LEFT]:
                    # edge color is the darker of the two node colors
                    edge_color = min(node_power_color, self.board.board[x-1][y].color())
                    pygame.draw.rect(self.canvas, edge_color,
                                     pygame.Rect(x_c - THICKNESS, y_c + OPENING_BUFFER_SIZE, 2 * THICKNESS,
                                                 CELL_SIZE - 2 * OPENING_BUFFER_SIZE))
                # Top sided edge
                if self.board.board[x][y].connections[D.UP]:
                    edge_color = min(node_power_color, self.board.board[x][y-1].color())
                    pygame.draw.rect(self.canvas, edge_color,
                                     pygame.Rect(x_c + OPENING_BUFFER_SIZE, y_c - THICKNESS,
                                                 CELL_SIZE - 2 * OPENING_BUFFER_SIZE, 2 * THICKNESS))
        # Player
        pygame.draw.rect(self.canvas, 0xff00ff,
                         pygame.Rect(self.main.x_center - PLAYER_SIZE, self.main.y_center - PLAYER_SIZE,
                                     2 * PLAYER_SIZE, 2 * PLAYER_SIZE))

        for x in self.monsters:
            x.tick()

        if self.tick_start:
            ticks_passed = self.main.number_tick - self.tick_start
            seconds = ticks_passed // self.main.TPS
            time_text = f'\uf64f {seconds // 60:02d}:{seconds % 60:02d}'
            util.draw_right_align_text(self.canvas, self.font_16_nerd.render(time_text, True, 0x00ffffff),
                                       self.main.x_size - 5, 5)

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
        walls_to_check.append(
            (cell_x - THICKNESS, cell_x + THICKNESS, cell_y + CELL_SIZE - OPENING_BUFFER_SIZE, cell_y + CELL_SIZE))
        if not connections[D.RIGHT]:
            walls_to_check.append(
                (cell_x + CELL_SIZE - THICKNESS, cell_x + CELL_SIZE + THICKNESS, cell_y, cell_y + CELL_SIZE))
        walls_to_check.append(
            (cell_x + CELL_SIZE - THICKNESS, cell_x + CELL_SIZE + THICKNESS, cell_y, cell_y + OPENING_BUFFER_SIZE))
        walls_to_check.append((cell_x + CELL_SIZE - THICKNESS, cell_x + CELL_SIZE + THICKNESS,
                               cell_y + CELL_SIZE - OPENING_BUFFER_SIZE, cell_y + CELL_SIZE))
        if not connections[D.UP]:
            walls_to_check.append((cell_x, cell_x + CELL_SIZE, cell_y - THICKNESS, cell_y + THICKNESS))
        walls_to_check.append((cell_x, cell_x + OPENING_BUFFER_SIZE, cell_y - THICKNESS, cell_y + THICKNESS))
        walls_to_check.append(
            (cell_x + CELL_SIZE - OPENING_BUFFER_SIZE, cell_x + CELL_SIZE, cell_y - THICKNESS, cell_y + THICKNESS))
        if not connections[D.DOWN]:
            walls_to_check.append(
                (cell_x, cell_x + CELL_SIZE, cell_y + CELL_SIZE - THICKNESS, cell_y + CELL_SIZE + THICKNESS))
        walls_to_check.append(
            (cell_x, cell_x + OPENING_BUFFER_SIZE, cell_y + CELL_SIZE - THICKNESS, cell_y + CELL_SIZE + THICKNESS))
        walls_to_check.append((cell_x + CELL_SIZE - OPENING_BUFFER_SIZE, cell_x + CELL_SIZE,
                               cell_y + CELL_SIZE - THICKNESS, cell_y + CELL_SIZE + THICKNESS))

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
            if self.x_velocity ** 2 + self.y_velocity ** 2 >= 0.16:
                # If the Euclidean velocity is >=0.4, reduce by half and try again.
                self.x_velocity *= 0.5
                self.y_velocity *= 0.5
                self.do_physics()  # Do this again, since this function modifies the velocity.
            else:
                # If it's negligible, simply stop.
                self.x_velocity = 0
                self.y_velocity = 0
