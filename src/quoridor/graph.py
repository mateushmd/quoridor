import math

from quoridor.vec2 import Vec2

class Graph:
    __DIR_TO_SHIFT: dict[tuple[int, int], int] = {
        (1, 0): 0,
        (1, -1): 1,
        (0, -1): 2,
        (-1, -1): 3,
        (-1, 0): 4,
        (-1, 1): 5,
        (0, 1): 6,
        (1, 1): 7
    }

    def __init__(self, dim: Vec2):
        self.__dim: Vec2 = dim
        self.__bit_map: list[list[int]] = [[ 0 for _ in range(0, dim.x)] for _ in range(0, dim.y)]

    def __check_bit(self, v: Vec2, shift: int) -> bool:
        return self.__bit_map[v.y][v.x] >> shift & 1 == 1

    def __set_bit(self, v: Vec2, shift: int, value: bool) -> None:
        mask = 1 << shift
        if value:
            self.__bit_map[v.y][v.x] |= mask
        else:
            self.__bit_map[v.y][v.x] &= ~mask

    def __is_valid(self, v: Vec2):
        return v.x >= 0 and v.x < self.__dim.x and v.y >= 0 and v.y < self.__dim.y

    def dim(self) -> Vec2:
        return self.__dim

    def has_edge(self, v1: Vec2, v2: Vec2) -> bool:
        diff = v2 - v1
        if (diff.x == 0 and diff.y == 0) or (abs(diff.x) > 1 or abs(diff.y) > 1):
            return False

        return self.__is_valid(v1) and self.__is_valid(v2) and self.__check_bit(v1, self.__DIR_TO_SHIFT[(diff.x, diff.y)])

    def set_edge(self, v1: Vec2, v2: Vec2, state: bool) -> bool:
        if not self.__is_valid(v1) or not self.__is_valid(v2):
            return False

        diff = v2 - v1

        if (diff.x == 0 and diff.y == 0) or (abs(diff.x) > 1 or abs(diff.y) > 1):
            return False

        self.__set_bit(v1, self.__DIR_TO_SHIFT[(diff.x, diff.y)], state)

        return True
