import heapq

from quoridor.graph import Graph
from quoridor.vec2 import Vec2

class _Cell:
    def __init__(self):
        self.parent: Vec2 | None = None
        self.g: float = float('inf')
        self.h: float = float('inf')
        self._is_in_init_state = False

    def f(self) -> float:
        return self.g + self.h

    def is_in_init_state(self) -> bool:
        return self._is_in_init_state

    def mark_as_initialized(self):
        self._is_in_init_state = True

def _h(start: Vec2, target_y: int) -> float:
    return float(abs(start.y - target_y))

def _is_valid(bounds: Vec2, position: Vec2) -> bool:
    return position.x >= 0 and position.x < bounds.x and position.y >= 0 and position.y < bounds.y

def _trace_path(cells: list[list[_Cell]], end_pos: Vec2) -> list[Vec2]:
    path: list[Vec2] = []
    cur_pos: Vec2 | None = end_pos

    while cur_pos is not None:
        path.append(cur_pos)
        cur_cell = cells[cur_pos.y][cur_pos.x]
        cur_pos = cur_cell.parent

    path.reverse()
    return path


def astar(graph: Graph, start: Vec2, target_y: int) -> list[Vec2] | None:
    open: list[tuple[float, int, Vec2]] = []

    heapq.heappush(open, (0.0, id(start), start))

    closed: list[list[bool]] = [[False for _ in range(0, graph.dim().x)] for _ in range(0, graph.dim().y)]
    cells: list[list[_Cell]] = [[_Cell() for _ in range(0, graph.dim().x)] for _ in range(0, graph.dim().y)]

    cells[start.y][start.x].g = 0.0
    cells[start.y][start.x].h = 0.0
    cells[start.y][start.x].parent = None
    cells[start.y][start.x].mark_as_initialized()

    directions = [(0, -1), (-1, 0), (0, 1), (1, 0)]

    while len(open) > 0:
        _, _, current = heapq.heappop(open)

        if current.y == target_y:
            return _trace_path(cells, current)

        closed[current.y][current.x] = True

        for dx, dy in directions:
            next = Vec2(current.x + dx, current.y + dy)
            if next != current and _is_valid(graph.dim(), next) and graph.has_edge(current, next) and not closed[next.y][next.x]:
                gn = cells[current.y][current.x].g + 1.0
                hn = _h(next, target_y)

                if not cells[next.y][next.x].is_in_init_state() or cells[next.y][next.x].f() > gn + hn:
                    heapq.heappush(open, (gn + hn, id(next), next))
                    cells[next.y][next.x].g = gn
                    cells[next.y][next.x].h = hn
                    cells[next.y][next.x].parent = current
                    cells[next.y][next.x].mark_as_initialized()

    return None
