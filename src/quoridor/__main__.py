import pygame
from pygame.typing import Point

from quoridor.game import Interactions, Quoridor, Result
from quoridor.vec2 import Vec2

CELLS_PER_ROW: int = 9
TILE_SIZE: int = 64
BOARD_SIZE: int = TILE_SIZE * CELLS_PER_ROW
PLAYER_SIZE: int = 15

def main():
    _ = pygame.init()
    screen = pygame.display.set_mode((BOARD_SIZE, BOARD_SIZE))
    clock = pygame.time.Clock()
    running = True

    game = Quoridor()

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

        result = game.update(interactions)

        if result == Result.WHITE:
            print("WHITE WON!")
        elif result == Result.BLACK:
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
    

if __name__ == "__main__":
    main()
