"""Data structures and stuff for the game."""

import dataclasses
from dataclasses import dataclass


class D:
    LEFT = 0
    RIGHT = 1
    UP = 2
    DOWN = 3


@dataclass
class Node:
    x: int
    y: int
    connections: list[bool, bool, bool, bool] = dataclasses.field(init=False, default_factory=lambda: [False, False, False, False])

    def tuple(self) -> tuple:
        return self.x, self.y

    def __repr__(self):
        return f'Node({self.x}, {self.y})'


@dataclass(frozen=True)
class Edge:
    """Represents an edge. This class is redundant during actual gameplay and only matters during generation."""
    node1: Node
    node2: Node

    def tuple(self) -> tuple:
        return self.node1.x, self.node1.y, self.node2.x, self.node2.y

    def __eq__(self, other):
        return self.node1 == other.node1 and self.node2 == other.node2

    def __hash__(self):
        return hash(self.tuple())

    def __repr__(self):
        return f'Edge({self.node1}, {self.node2})'


@dataclass
class Board:
    board: list[list[Node]] = dataclasses.field(init=False)
    maze_exit_x: int = dataclasses.field(init=False)
    maze_exit_y: int = dataclasses.field(init=False)

    def get_edge(self, x1: int, y1: int, x2: int, y2: int):
        """Convenience method to get an edge."""
        return Edge(self.board[x1][y1], self.board[x2][y2])
