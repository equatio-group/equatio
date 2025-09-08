"""Main game environment using pygame."""

import random
from itertools import product

import numpy as np
import pygame

# === Constants ===

CELL_COUNT = 16
GRID_SIZE = int(np.sqrt(CELL_COUNT))

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (128, 128, 128)

# Fonts and FPS
TITLE_FONT_SIZE = 50
CELL_FONT_SIZE = 26
FONT_NAME = "freesansbold.ttf"
FPS = 60

# Padding between cells
CELL_PADDING = 10


def generate_board() -> list[int]:
    """Generates a shuffled list of unique integers for the game board."""
    return random.sample(range(CELL_COUNT), CELL_COUNT)


def draw_background(screen, width, height) -> None:
    """Draws the top, middle, and bottom UI sections."""
    title_font = pygame.font.Font(FONT_NAME, TITLE_FONT_SIZE)

    # Top menu height (1/8 of height)
    top_height = height / 8
    bottom_height = height / 8
    board_height = height - top_height - bottom_height

    pygame.draw.rect(screen, BLACK, [0, 0, width, top_height])
    title_text = title_font.render("Equatio", True, WHITE)
    screen.blit(title_text, (0.0125 * width, 0.025 * height))

    pygame.draw.rect(screen, GREY, [0, top_height, width, board_height])

    pygame.draw.rect(screen, BLACK, [0, height - bottom_height, width, bottom_height])


def draw_board(board: list[int], screen: pygame.Surface, width: int, height: int) -> None:
    """Draws the grid of numbers on the screen with properly sized cells."""

    cell_font = pygame.font.Font(FONT_NAME, CELL_FONT_SIZE)

    top_height = height / 8
    bottom_height = height / 8
    board_height = height - top_height - bottom_height
    board_width = width

    # Calculate cell size
    cell_width = (board_width - (GRID_SIZE + 1) * CELL_PADDING) / GRID_SIZE
    cell_height = (board_height - (GRID_SIZE + 1) * CELL_PADDING) / GRID_SIZE

    for col, row in product(range(GRID_SIZE), range(GRID_SIZE)):
        x = CELL_PADDING + col * (cell_width + CELL_PADDING)
        y = top_height + CELL_PADDING + row * (cell_height + CELL_PADDING)

        pygame.draw.rect(
            screen,
            WHITE,
            [x, y, cell_width, cell_height],
            0,
            border_radius=4
        )

        number = board[col * GRID_SIZE + row]
        text_surface = cell_font.render(str(number), True, GREY)
        text_rect = text_surface.get_rect(center=(x + cell_width / 2, y + cell_height / 2))
        screen.blit(text_surface, text_rect)


def main() -> None:
    pygame.init()
    pygame.font.init()

    width, height = 800, 800  # initial window size
    screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
    pygame.display.set_caption("Equatio")

    clock = pygame.time.Clock()
    board = generate_board()
    running = True

    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                # Update window size and reset screen surface
                width, height = event.w, event.h
                screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)

        screen.fill(WHITE)

        draw_background(screen, width, height)
        draw_board(board, screen, width, height)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()

