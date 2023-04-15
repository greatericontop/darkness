"""Generates a board with a maze."""

from __future__ import annotations

import random

import util
from mazegen.game_structures import Board, D, Edge, Node


def edge_set_choice(the_set: set[Edge]) -> Edge:
    currently_selected = None
    if len(the_set) == 0:
        raise RuntimeError('you attempted this with an empty set')
    for i, item in enumerate(the_set):
        if random.random() < 1 / (i+1):
            currently_selected = item
    assert currently_selected is not None
    return currently_selected


def fill(board: Board, size: int):
    """Fill the board."""
    # Initialization
    board.board = [[Node(x, y) for y in range(size)] for x in range(size)]
    board_edges: list[tuple[int, int, int, int]] = []
    visited_nodes: set[tuple[int, int]] = set()  # We are NOT using :Node:s here because they're mutable and unhashable
    available_edges: set[Edge] = set()
    root_node = board.board[0][0]  # TODO: ROOT NODE SHOULD BE A RANDOM NODE (ON THE EDGE)
    visited_nodes.add(root_node.tuple())
    available_edges.add(board.get_edge(0, 0, 0, 1))
    available_edges.add(board.get_edge(0, 0, 1, 0))

    while True:
        # Get edge
        next_edge = edge_set_choice(available_edges)
        available_edges.remove(next_edge)
        # Potentially quit if the edge is connected (redundant)
        if next_edge.node1.tuple() in visited_nodes and next_edge.node2.tuple() in visited_nodes:
            # if it's a redundant edge including the root node, always skip
            if next_edge.node1.tuple() == root_node.tuple() or next_edge.node2.tuple() == root_node.tuple():
                continue
            # normal loop/cycle, percentage to skip
            if random.random() <= 0.72718281828:  # TODO: you put a TOTALLY arbitrary number here
                continue
        if next_edge.node1.tuple() in visited_nodes:
            unvisited_node = next_edge.node2
        elif next_edge.node1.tuple() in visited_nodes:
            unvisited_node = next_edge.node1
        else:
            raise RuntimeError('at least one of the nodes in an edge must be visited')
        # Update
        visited_nodes.add(unvisited_node.tuple())
        board_edges.append(next_edge.tuple())
        for dx, dy in zip(util.D_X, util.D_Y):
            x1 = unvisited_node.x + dx
            y1 = unvisited_node.y + dy
            if x1 < 0 or y1 < 0 or x1 >= size or y1 >= size:  # edge leads to a nonexistent place
                continue
            edge_1_tuple = (unvisited_node.x, unvisited_node.y, x1, y1)
            edge_2_tuple = (x1, y1, unvisited_node.x, unvisited_node.y)
            if edge_1_tuple in board_edges or edge_2_tuple in board_edges:  # must account for both orientations
                continue
            available_edges.add(board.get_edge(*edge_1_tuple))
        if len(visited_nodes) == size**2:  # all visited
            break

    # Set up the nodes with their connections using the edges
    for x1, y1, x2, y2 in board_edges:
        if y1 == y2 and x1+1 == x2:
            board.board[x1][y1].connections[D.RIGHT] = True
            board.board[x2][y2].connections[D.LEFT] = True
        elif y1 == y2 and x1-1 == x2:
            board.board[x1][y1].connections[D.LEFT] = True
            board.board[x2][y2].connections[D.RIGHT] = True
        elif x1 == x2 and y1+1 == y2:
            board.board[x1][y1].connections[D.DOWN] = True
            board.board[x2][y2].connections[D.UP] = True
        elif x1 == x2 and y1-1 == y2:
            board.board[x1][y1].connections[D.UP] = True
            board.board[x2][y2].connections[D.DOWN] = True
