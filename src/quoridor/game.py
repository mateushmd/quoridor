from dataclasses import dataclass
from enum import Enum

from quoridor.graph import Graph
from quoridor.astar import astar
from quoridor.vec2 import Vec2

BOARD_DIM = Vec2(9, 9)

# Dumb and lazy function
# Returns a list with vectors for lateral movement in the perspective of the original offset
def lateral_movements(vec: Vec2) -> list[Vec2]:
    if vec.x != 0:
        return [Vec2(0, 1), Vec2(0, -1)]
    else:
        return [Vec2(1, 0), Vec2(-1, 0)]

@dataclass
class Interactions:
    move: bool
    place_wall: bool
    cell: Vec2

class Result(Enum):
    PLAYING = 0,
    WHITE = 1,
    BLACK = 2

class Quoridor:
    def __init__(self, dim: Vec2 = BOARD_DIM):
        self.dim: Vec2 = dim
        self._goals = [self.dim.y - 1, 0]
        self.turn: bool = False
        self.graph: Graph = Graph(self.dim)
        
        self.player_positions: list[Vec2] = [
            Vec2(self.dim.x // 2, 0),
            Vec2(self.dim.x // 2, self.dim.y - 1)
        ]

        self.horizontal_walls: list[Vec2] = []

        self.vertical_walls: list[Vec2] = []

        self._init_graph()

        self._origin_mouse_right: Vec2 | None = None

        self._wait_flag = False

    def _init_graph(self):
        neighbors = [(1, 0), (0, 1)]

        for y in range(self.dim.y):
            for x in range(self.dim.x):
                curr = Vec2(x, y)
                for dx, dy in neighbors:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.dim.x and 0 <= ny < self.dim.y:
                        self.graph.set_edge(curr, Vec2(nx, ny), True)

    def _wall_edges(self, anchor: Vec2, horizontal: bool) -> list[tuple[Vec2, Vec2]]:
        i, j = anchor.x, anchor.y
        if horizontal:
            return [
                (Vec2(i - 1, j - 1), Vec2(i - 1, j)),
                (Vec2(i, j - 1), Vec2(i, j)),
            ]

        return [
            (Vec2(i - 1, j - 1), Vec2(i, j - 1)),
            (Vec2(i - 1, j), Vec2(i, j)),
        ]

    def _wall_from_drag(self, a: Vec2, b: Vec2) -> tuple[Vec2, bool] | None:
        d = b - a
        if abs(d.x) + abs(d.y) != 1:
            return None

        if d.x != 0:
            return Vec2(max(a.x, b.x), min(a.y + 1, self.dim.y - 1)), True

        return Vec2(min(a.x + 1, self.dim.x - 1), max(a.y, b.y)), False

    def _in_bounds(self, cell: Vec2) -> bool:
        return 0 <= cell.x < self.dim.x and 0 <= cell.y < self.dim.y

    def _wall_conflicts(self, anchor: Vec2, horizontal: bool) -> bool:
        if not (1 <= anchor.x < self.dim.x and 1 <= anchor.y < self.dim.y):
            return True

        if anchor in self.horizontal_walls or anchor in self.vertical_walls:
            return True

        if horizontal:
            return Vec2(anchor.x - 1, anchor.y) in self.horizontal_walls or Vec2(anchor.x + 1, anchor.y) in self.horizontal_walls

        return Vec2(anchor.x, anchor.y - 1) in self.vertical_walls or Vec2(anchor.x, anchor.y + 1) in self.vertical_walls

    def _all_players_have_path(self) -> bool:
        return all(astar(self.graph, pos, goal) is not None for pos, goal in zip(self.player_positions, self._goals))


    def _get_legal_moves(self, player: bool) -> list[Vec2]:
        position = self.player_positions[int(player)]
        opponent = self.player_positions[int(not player)]
        legal_moves: list[Vec2] = []
        initial_offsets = [Vec2(1, 0), Vec2(0, 1), Vec2(-1, 0), Vec2(0, -1)]

        for offset in initial_offsets:
            next_pos = position + offset
            if self.graph.has_edge(position, next_pos):
                if opponent == next_pos:
                    straight_jump = next_pos + offset
                    if self.graph.has_edge(next_pos, straight_jump):
                        legal_moves.append(straight_jump)
                    else:
                        for move in lateral_movements(offset):
                            diag_pos = next_pos + move
                            side_pos = position + move
                            via_opponent = self.graph.has_edge(next_pos, diag_pos)
                            via_side = (
                                self.graph.has_edge(position, side_pos)
                                and self.graph.has_edge(side_pos, diag_pos)
                            )
                            if via_opponent or via_side:
                                legal_moves.append(diag_pos)
                else:
                    legal_moves.append(next_pos)

        return legal_moves


    def place_wall(self, anchor: Vec2, horizontal: bool) -> bool:
        if self._wall_conflicts(anchor, horizontal):
            return False

        edges = self._wall_edges(anchor, horizontal)
        for a, b in edges:
            _ = self.graph.set_edge(a, b, False)

        if not self._all_players_have_path():
            for a, b in edges:
                _ = self.graph.set_edge(a, b, True)
            return False

        (self.horizontal_walls if horizontal else self.vertical_walls).append(anchor)
        return True

    def update(self, interactions: Interactions) -> Result:
        if (not self._wait_flag and interactions.move and 
            interactions.cell not in self.player_positions and
            interactions.cell in self._get_legal_moves(self.turn)):
            self.player_positions[int(self.turn)] = interactions.cell
            
            if self.player_positions[int(self.turn)].y == self._goals[int(self.turn)]:
                if not self.turn:
                    return Result.WHITE
                else:
                    return Result.BLACK

            self.turn = not self.turn
        elif interactions.place_wall:
            if self._origin_mouse_right is None and self._in_bounds(interactions.cell):
                self._origin_mouse_right = interactions.cell

        self._wait_flag = interactions.move

        if not interactions.place_wall and self._origin_mouse_right is not None:
            wall = self._wall_from_drag(self._origin_mouse_right, interactions.cell)
            if wall is not None:
                _ = self.place_wall(*wall)
            self._origin_mouse_right = None

        return Result.PLAYING
