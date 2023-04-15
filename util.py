"""Utilities for game rendering."""

import pygame

D_X = [-1, 1, 0, 0]
D_Y = [0, 0, -1, 1]


def clear_board(canvas: pygame.Surface):
    canvas.fill(0x252525)


def draw_centered_text(canvas: pygame.Surface, text: pygame.Surface, x: float, y: float) -> None:
    text_rect = text.get_rect()
    canvas.blit(text, (x - text_rect.width / 2, y - text_rect.height / 2))


def draw_right_align_text(canvas: pygame.Surface, text: pygame.Surface, x: float, y: float) -> None:
    text_rect = text.get_rect()
    canvas.blit(text, (x - text_rect.width, y))
