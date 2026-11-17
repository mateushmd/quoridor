from quoridor.adjacency_matrix import AdjacencyMatrix
from quoridor.vec2 import Vec2

BOARD_DIM = Vec2(9, 9)

class Quoridor:
    def __init__(self, dim: Vec2 = BOARD_DIM):
        self.dim = dim
        self.turn = 0
        self.adj_mat = AdjacencyMatrix(self.dim)
        
        self.player_positions = [
            Vec2(self.dim.x // 2, 0),
            Vec2(self.dim.x // 2, self.dim.y - 1)
        ]

        self.__init_graph()

    def __init_graph(self):
        neighbors = [(1, 0), (0, 1)]

        for y in range(self.dim.y):
            for x in range(self.dim.x):
                curr = Vec2(x, y)
                for dx, dy in neighbors:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.dim.x and 0 <= ny < self.dim.y:
                        self.adj_mat.set_edge(curr, Vec2(nx, ny), True)

    def update(self):
        self.turn += 1
