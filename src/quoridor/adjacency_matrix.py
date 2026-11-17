from quoridor.vec2 import Vec2

class AdjacencyMatrix:
    def __init__(self, dim: Vec2):
        self.__dim: Vec2 = dim
        self.__mat: list[list[bool]] = [[False for _ in range(0, dim.x * dim.y)] for _ in range(0, dim.x * dim.y)]

    def __idx(self, v: Vec2) -> int:
        return self.__dim.x * v.y + v.x

    def __is_valid(self, v: Vec2):
        return v.x >= 0 and v.x < self.__dim.x and v.y >= 0 and v.y < self.__dim.y

    def dim(self) -> Vec2:
        return self.__dim

    def has_edge(self, v1: Vec2, v2: Vec2) -> bool:
        return self.__is_valid(v1) and self.__is_valid(v2) and self.__mat[self.__idx(v1)][self.__idx(v2)]

    def set_edge(self, v1: Vec2, v2: Vec2, state: bool) -> bool:
        if not self.__is_valid(v1) or not self.__is_valid(v2):
            return False

        idx1 = self.__idx(v1)
        idx2 = self.__idx(v2)

        self.__mat[idx1][idx2] = state
        self.__mat[idx2][idx1] = state
        return True
