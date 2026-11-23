import copy
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


class Result(Enum):
    PLAYING = 0,
    WHITE = 1,
    BLACK = 2

class Quoridor:
    _WHITE: bool = False
    _BLACK: bool = True

    def __init__(self, dim: Vec2 = BOARD_DIM):
        self._state: Result = Result.PLAYING
        self._dim: Vec2 = dim
        self._goals: list[int] = [self._dim.y - 2, 0]
        self.turn: bool = False
        self.graph: Graph = Graph(self._dim)
        
        self.player_positions: list[Vec2] = [
            Vec2(self._dim.x // 2, 0),
            Vec2(self._dim.x // 2, self._dim.y - 1)
        ]

        self._walls: list[int] = [10, 10]

        self.horizontal_walls: list[Vec2] = []

        self.vertical_walls: list[Vec2] = []

        self._init_graph()

        self._origin_mouse_right: Vec2 | None = None

        self._wait_flag: bool = False

        self._current_legal_moves: list[Vec2] = []

    def _init_graph(self):
        neighbors = [(1, 0), (0, 1)]

        for y in range(self._dim.y):
            for x in range(self._dim.x):
                curr = Vec2(x, y)
                for dx, dy in neighbors:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self._dim.x and 0 <= ny < self._dim.y:
                        _ = self.graph.set_edge(curr, Vec2(nx, ny), True)

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


    def _wall_conflicts(self, anchor: Vec2, horizontal: bool) -> bool:
        if not (1 <= anchor.x < self._dim.x and 1 <= anchor.y < self._dim.y):
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

    def get_state(self) -> Result:
        return self._state

    def get_dim(self) -> Vec2:
        return self._dim

    def get_current_legal_moves(self) -> list[Vec2]:
        return copy.deepcopy(self._current_legal_moves)

    def in_bounds(self, cell: Vec2) -> bool:
        return 0 <= cell.x < self._dim.x and 0 <= cell.y < self._dim.y

    def place_wall(self, anchor: Vec2, horizontal: bool) -> bool:
        player_i = int(self.turn)

        if self._state != Result.PLAYING or self._walls[player_i] <= 0 or self._wall_conflicts(anchor, horizontal):
            return False

        edges = self._wall_edges(anchor, horizontal)
        for a, b in edges:
            _ = self.graph.set_edge(a, b, False)

        if not self._all_players_have_path():
            for a, b in edges:
                _ = self.graph.set_edge(a, b, True)
            return False

        (self.horizontal_walls if horizontal else self.vertical_walls).append(anchor)

        self._walls[player_i] = self._walls[player_i] - 1 

        self.turn = not self.turn

        return True

    def move(self, legal_move_i: int) -> bool:
        player_i = int(self.turn)

        if self._state != Result.PLAYING or legal_move_i < 0 or legal_move_i >= len(self._current_legal_moves):
            return False

        self.player_positions[player_i] = self._current_legal_moves[legal_move_i]

        if self.player_positions[player_i].y == self._goals[player_i]:
            if self.turn == self._WHITE:
                self._state = Result.WHITE
            elif self.turn == self._BLACK:
                self._state = Result.BLACK

        self.turn = not self.turn

        self._current_legal_moves = self._get_legal_moves(self.turn)

        return True


