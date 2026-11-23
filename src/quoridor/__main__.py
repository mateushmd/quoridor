from dataclasses import dataclass

import pygame
from pygame.typing import Point

from quoridor.game import Quoridor, Result
from quoridor.vec2 import Vec2

CELLS_PER_ROW: int = 9
TILE_SIZE: int = 64
BOARD_SIZE: int = TILE_SIZE * CELLS_PER_ROW
PLAYER_SIZE: int = 15

@dataclass
class Interactions:
    move: bool
    place_wall: bool
    cell: Vec2

def main():
    _ = pygame.init()
    screen = pygame.display.set_mode((BOARD_SIZE, BOARD_SIZE))
    clock = pygame.time.Clock()
    running = True

    game = Quoridor()

    wait_flag: bool = False
    origin_mouse_right: None | Vec2 = None

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False


        mouse_buttons = pygame.mouse.get_pressed()
        mouse_position = pygame.mouse.get_pos()

        interactions = Interactions(
            mouse_buttons[0],
            mouse_buttons[2],
            Vec2(mouse_position[0] // TILE_SIZE, CELLS_PER_ROW - mouse_position[1] // TILE_SIZE - 1) 
        )

        legal_moves = game.get_current_legal_moves()

        if (not wait_flag and interactions.move and interactions.cell in legal_moves):
            game.move(legal_moves.index(interactions.cell))
        elif interactions.place_wall:
            if origin_mouse_right is None and game.in_bounds(interactions.cell):
                origin_mouse_right = interactions.cell

        wait_flag = interactions.move

        if not interactions.place_wall and origin_mouse_right is not None:
            wall = wall_from_drag(game, origin_mouse_right, interactions.cell)
            if wall is not None:
                _ = game.place_wall(*wall)
            origin_mouse_right = None

        if game.get_state() == Result.WHITE:
            print("WHITE WON!")
        elif game.get_state() == Result.BLACK:
            print("BLACK WON!")

        _ = screen.fill("green")

        for i in range(0, 9):
            _ = pygame.draw.line(screen, "black", [TILE_SIZE * i, 0], [TILE_SIZE * i, BOARD_SIZE], 3)
            _ = pygame.draw.line(screen, "black", [0, TILE_SIZE * i], [BOARD_SIZE, TILE_SIZE * i], 3)

        for position in game.player_positions:
            _ = pygame.draw.circle(screen, "red", cell_center_to_pixel(position), PLAYER_SIZE / 2)

        for wall in game.horizontal_walls:
            _ = pygame.draw.line(screen, "yellow", grid_to_pixel(wall - Vec2(1, 0)), grid_to_pixel(wall + Vec2(1, 0)), 5)

        for wall in game.vertical_walls:
            _ = pygame.draw.line(screen, "yellow", grid_to_pixel(wall - Vec2(0, 1)), grid_to_pixel(wall + Vec2(0, 1)), 5)

        pygame.display.flip()

        _dt = clock.tick(60) / 1000

    pygame.quit()

def cell_center_to_pixel(pos: Vec2) -> Point:
    return [pos.x * TILE_SIZE + TILE_SIZE / 2, BOARD_SIZE - (pos.y * TILE_SIZE + TILE_SIZE / 2)]

def grid_to_pixel(pos: Vec2) -> Point:
    """Pixel position of a grid intersection (the bottom-left corner of cell `pos`)."""
    return [pos.x * TILE_SIZE, BOARD_SIZE - pos.y * TILE_SIZE]

def wall_from_drag(game: Quoridor, a: Vec2, b: Vec2) -> tuple[Vec2, bool] | None:
    d = b - a
    if abs(d.x) + abs(d.y) != 1:
        return None

    if d.x != 0:
        return Vec2(max(a.x, b.x), min(a.y + 1, game.get_dim().y - 1)), True

    return Vec2(min(a.x + 1, game.get_dim().x - 1), max(a.y, b.y)), False
    

if __name__ == "__main__":
    main()
