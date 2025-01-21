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
    root_node = board.board[random.randrange(size)][random.randrange(size)]
    board.maze_exit_x = root_node.x
    board.maze_exit_y = root_node.y
    visited_nodes.add(root_node.tuple())
    for dx, dy in zip(util.D_X, util.D_Y):
        x1 = root_node.x + dx
        y1 = root_node.y + dy
        if x1 < 0 or y1 < 0 or x1 >= size or y1 >= size:  # edge leads to a nonexistent place
            continue
        available_edges.add(board.get_edge(root_node.x, root_node.y, x1, y1))

    while True:
        # Get edge
        next_edge = edge_set_choice(available_edges)
        available_edges.remove(next_edge)
        # Potentially quit if the edge is connected (redundant)
        if next_edge.node1.tuple() in visited_nodes and next_edge.node2.tuple() in visited_nodes:
            # if it's a redundant edge including the root node, always skip
            # note that this doesn't mean there's only one path to the exit, because a non-redundant edge
            #   could have been added naturally
            if next_edge.node1.tuple() == root_node.tuple() or next_edge.node2.tuple() == root_node.tuple():
                continue
            # normal loop/cycle, percentage to skip
            if random.random() <= 0.885:  # (higher makes the game harder by reducing the number of open edges)
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

    # Next, we will set the power (color) of each node
    # This is a weird iterative deepening search.
    # Algorithm:
    #   Goal node power is 6; mark as visited
    #   Add the neighbors to the CURRENT queue
    #   Loop while CURRENT queue is not empty:
    #       Shuffle CURRENT queue
    #       Loop every node in the CURRENT queue:
    #           Power := max adjacent power - ( 20% chance to subtract 1 ); mark as visited
    #           If power <= 0: power = 0
    #           Add neighbors to NEXT queue (if not visited - eventually we will get to all of them)
    #           Mark as visited
    #       NEXT queue becomes CURRENT queue
    visited_nodes = set()
    exit_node = board.board[board.maze_exit_x][board.maze_exit_y]
    exit_node.power = 6
    visited_nodes.add(exit_node.tuple())
    # Add neighbors
    current_queue: list[Node] = []
    for dx, dy in zip(util.D_X, util.D_Y):
        x1 = board.maze_exit_x + dx
        y1 = board.maze_exit_y + dy
        if x1 < 0 or y1 < 0 or x1 >= size or y1 >= size:  # edge leads to a nonexistent place
            continue
        current_queue.append(board.board[x1][y1])
    # Loop
    while current_queue:
        random.shuffle(current_queue)
        next_queue: list[Node] = []
        for node in current_queue:
            # Power
            max_neighbor_power = 0
            for dx, dy in zip(util.D_X, util.D_Y):
                x1 = node.x + dx
                y1 = node.y + dy
                if x1 < 0 or y1 < 0 or x1 >= size or y1 >= size:
                    continue
                neighbor = board.board[x1][y1]
                if neighbor.tuple() in visited_nodes:
                    max_neighbor_power = max(max_neighbor_power, neighbor.power)
            node.power = max(0, max_neighbor_power - (1 if random.random() < 0.515 else 0))
            # Add neighbors
            for dx, dy in zip(util.D_X, util.D_Y):
                x1 = node.x + dx
                y1 = node.y + dy
                if x1 < 0 or y1 < 0 or x1 >= size or y1 >= size:
                    continue
                neighbor = board.board[x1][y1]
                if neighbor.tuple() in visited_nodes or neighbor in next_queue:
                    continue
                next_queue.append(neighbor)
            visited_nodes.add(node.tuple())
        current_queue = next_queue.copy()
