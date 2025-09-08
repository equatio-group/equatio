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
GREEN = (0, 200, 0)

# Fonts and FPS
TITLE_FONT_SIZE = 50
CELL_FONT_SIZE = 26
FONT_NAME = "freesansbold.ttf"
FPS = 60

# Padding between cells
CELL_PADDING = 10

# Equation Bar Constants
EQUATION_BAR_HEIGHT = 100
SLOT_WIDTH = 80
SLOT_HEIGHT = 80
SLOT_MARGIN = 10
SLOTS_PER_SIDE = 4
EQUAL_SIGN_FONT_SIZE = 40
BUTTON_FONT_SIZE = 30
CHECK_BUTTON_WIDTH = 120
CHECK_BUTTON_HEIGHT = 50


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


def draw_equation_bar(screen, width, height, lhs_terms=None, rhs_terms=None):
    if lhs_terms is None:
        lhs_terms = []
    if rhs_terms is None:
        rhs_terms = []

    bar_top = height - EQUATION_BAR_HEIGHT
    bar_center_y = bar_top + EQUATION_BAR_HEIGHT // 2

    # Dynamic width calculation for slots and margins
    max_total_width = width * 0.9  # Max 90% of window width
    # We have 8 slots + 7 margins + "=" + button + spacing to button
    # Button has fixed width
    fixed_width = CHECK_BUTTON_WIDTH + 40  # Button + extra margin

    available_width = max_total_width - fixed_width
    slot_margin = SLOT_MARGIN  # Initial value

    # Calculate max slot width
    # 8 slots + 7 margins
    slot_width = (available_width - slot_margin * (2 * SLOTS_PER_SIDE - 1)) / (2 * SLOTS_PER_SIDE)

    # Clamp slot width between 40 and 80
    slot_width = max(40, min(slot_width, 80))

    # If slot width is small, reduce margin if needed
    if slot_width <= 40:
        slot_margin = max(5, (available_width - slot_width * (2 * SLOTS_PER_SIDE)) / (2 * SLOTS_PER_SIDE - 1))

    # Total width of equation bar (slots + margins + "=")
    eq_font = pygame.font.Font(FONT_NAME, EQUAL_SIGN_FONT_SIZE)
    eq_text = eq_font.render("=", True, WHITE)
    total_slots_width = slot_width * (2 * SLOTS_PER_SIDE) + slot_margin * (2 * SLOTS_PER_SIDE - 1)
    total_width = total_slots_width + eq_text.get_width() + fixed_width

    start_x = (width - total_width) / 2

    slot_rects = []

    # LHS slots
    for i in range(SLOTS_PER_SIDE):
        x = start_x + i * (slot_width + slot_margin)
        rect = pygame.Rect(x, bar_center_y - SLOT_HEIGHT // 2, slot_width, SLOT_HEIGHT)
        pygame.draw.rect(screen, GREY, rect, border_radius=5)
        slot_rects.append(rect)
        term_text = lhs_terms[i] if i < len(lhs_terms) else "—"
        font = pygame.font.Font(FONT_NAME, 24)
        text_surf = font.render(term_text, True, BLACK)
        text_rect = text_surf.get_rect(center=rect.center)
        screen.blit(text_surf, text_rect)

    # Equal sign
    eq_x = slot_rects[-1].right + slot_margin
    screen.blit(eq_text, (eq_x, bar_center_y - eq_text.get_height() // 2))

    # RHS slots
    rhs_start_x = eq_x + eq_text.get_width() + slot_margin
    for i in range(SLOTS_PER_SIDE):
        x = rhs_start_x + i * (slot_width + slot_margin)
        rect = pygame.Rect(x, bar_center_y - SLOT_HEIGHT // 2, slot_width, SLOT_HEIGHT)
        pygame.draw.rect(screen, GREY, rect, border_radius=5)
        slot_rects.append(rect)
        term_text = rhs_terms[i] if i < len(rhs_terms) else "—"
        font = pygame.font.Font(FONT_NAME, 24)
        text_surf = font.render(term_text, True, BLACK)
        text_rect = text_surf.get_rect(center=rect.center)
        screen.blit(text_surf, text_rect)

    # Check button
    button_x = slot_rects[-1].right + 30
    button_y = bar_center_y - CHECK_BUTTON_HEIGHT // 2
    check_button_rect = pygame.Rect(button_x, button_y, CHECK_BUTTON_WIDTH, CHECK_BUTTON_HEIGHT)
    pygame.draw.rect(screen, GREEN, check_button_rect, border_radius=8)
    button_font = pygame.font.Font(FONT_NAME, BUTTON_FONT_SIZE)
    button_text = button_font.render("Check", True, WHITE)
    screen.blit(button_text, (check_button_rect.centerx - button_text.get_width() // 2,
                              check_button_rect.centery - button_text.get_height() // 2))

    return slot_rects, check_button_rect


def main() -> None:
    pygame.init()
    pygame.font.init()

    width, height = 800, 800  # Initial window size
    screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
    pygame.display.set_caption("Equatio")

    clock = pygame.time.Clock()
    board = generate_board()
    running = True

    # Example terms as placeholders for slots (can be replaced later by real terms)
    lhs_terms = ["a+b", "x+y", "dp/dz", "baum"]
    rhs_terms = ["q", "r", "s", "t"]

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
        draw_equation_bar(screen, width, height, lhs_terms, rhs_terms)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()

