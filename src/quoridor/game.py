from dataclasses import dataclass

from quoridor.adjacency_matrix import AdjacencyMatrix
from quoridor.astar import astar
from quoridor.vec2 import Vec2

BOARD_DIM = Vec2(9, 9)

@dataclass
class Interactions:
    move: bool
    place_wall: bool
    cell: Vec2

class Quoridor:
    def __init__(self, dim: Vec2 = BOARD_DIM):
        self.dim: Vec2 = dim
        self.turn: int = 0
        self.adj_mat: AdjacencyMatrix = AdjacencyMatrix(self.dim)
        
        self.player_positions: list[Vec2] = [
            Vec2(self.dim.x // 2, 0),
            Vec2(self.dim.x // 2, self.dim.y - 1)
        ]

        self.horizontal_walls: list[Vec2] = []

        self.vertical_walls: list[Vec2] = []

        self.__init_graph()

        self._origin_mouse_right: Vec2 | None = None

    def __init_graph(self):
        neighbors = [(1, 0), (0, 1)]

        for y in range(self.dim.y):
            for x in range(self.dim.x):
                curr = Vec2(x, y)
                for dx, dy in neighbors:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.dim.x and 0 <= ny < self.dim.y:
                        self.adj_mat.set_edge(curr, Vec2(nx, ny), True)

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
        # The wall runs along the drag and spans the two dragged cells.
        # Horizontal drag: horizontal wall on the cells' top edge.
        # Vertical drag: vertical wall on the cells' right edge.
        # Both are clamped at the board border.
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
        goals = [self.dim.y - 1, 0]
        return all(astar(self.adj_mat, pos, goal) is not None for pos, goal in zip(self.player_positions, goals))

    def place_wall(self, anchor: Vec2, horizontal: bool) -> bool:
        if self._wall_conflicts(anchor, horizontal):
            return False

        edges = self._wall_edges(anchor, horizontal)
        for a, b in edges:
            self.adj_mat.set_edge(a, b, False)

        if not self._all_players_have_path():
            for a, b in edges:
                self.adj_mat.set_edge(a, b, True)
            return False

        (self.horizontal_walls if horizontal else self.vertical_walls).append(anchor)
        return True

    def update(self, interactions: Interactions):
        if interactions.move:
            self.player_positions[0] = interactions.cell
        elif interactions.place_wall:
            if self._origin_mouse_right is None and self._in_bounds(interactions.cell):
                self._origin_mouse_right = interactions.cell

        if not interactions.place_wall and self._origin_mouse_right is not None:
            wall = self._wall_from_drag(self._origin_mouse_right, interactions.cell)
            if wall is not None:
                _ = self.place_wall(*wall)
            self._origin_mouse_right = None
