# Main game environment using pygame with drag-and-drop between board and equation bar.

from __future__ import annotations
from itertools import product
import random

import numpy as np
import pygame

from draggable_term import DraggableTerm
from equation_set import EquationSet, JSON_DIR


# CONSTANTS
# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (128, 128, 128)
GREEN = (0, 200, 0)
RED = (255, 0, 0)
# Fonts and FPS
TITLE_FONT_SIZE = 50
CELL_FONT_SIZE = 26
FONT_NAME = "freesansbold.ttf"
FPS = 60
# Grid
CELL_COUNT = 16
GRID_SIZE = int(np.sqrt(CELL_COUNT))
# Padding between cells
CELL_PADDING = 10
# Equation Bar
SLOTS_PER_SIDE = 4
BUTTON_FONT_SIZE = 30
EQUATION_BAR_HEIGHT = 100
# Quit Button
QUICK_BUTTON_WIDTH = 100
QUICK_BUTTON_HEIGHT = 40


# GUI FUNCTIONS
def draw_background(screen: pygame.Surface, width: int, height: int) -> None:
    """Draws the top, middle, and bottom UI sections."""
    title_font = pygame.font.Font(FONT_NAME, TITLE_FONT_SIZE)

    top_height = height / 8
    bottom_height = height / 8
    board_height = height - top_height - bottom_height

    pygame.draw.rect(screen, BLACK, [0, 0, width, top_height])
    title_text = title_font.render("Equatio", True, WHITE)
    screen.blit(title_text, (0.0125 * width, 0.025 * height))

    pygame.draw.rect(screen, GREY, [0, top_height, width, board_height])
    pygame.draw.rect(screen, BLACK, [0, height - bottom_height, width, bottom_height])


def build_grid(width: int, height: int) -> dict[tuple[int, int], pygame.Rect]:
    """Compute grid cell rects based on window size."""
    top_height = height / 8
    bottom_height = height / 8
    board_height = height - top_height - bottom_height
    board_width = width

    cell_width = (board_width - (GRID_SIZE + 1) * CELL_PADDING) / GRID_SIZE
    cell_height = (board_height - (GRID_SIZE + 1) * CELL_PADDING) / GRID_SIZE

    cell_rects = {}
    for row, col in product(range(GRID_SIZE), range(GRID_SIZE)):
        x = CELL_PADDING + col * (cell_width + CELL_PADDING)
        y = top_height + CELL_PADDING + row * (cell_height + CELL_PADDING)
        rect = pygame.Rect(x, y, cell_width, cell_height)
        cell_rects[(row, col)] = rect
    return cell_rects


def build_equation_bar(
    width: int, height: int, screen: pygame.Surface
) -> tuple[list[pygame.Rect], pygame.Rect]:
    """Draw equation bar and return slot rects + button rect."""

    # equation bar sizes
    equation_bar_height = height / 11
    slot_width = width / 10
    slot_height = height / 13
    equal_sign_font_size = int(width / 45)
    slot_margin = width / 180
    check_button_width = width / 15
    check_button_height = height / 22
    button_font_size = int(width / 60)

    bar_top = height - equation_bar_height
    bar_center_y = bar_top + equation_bar_height // 2

    slot_rects = []
    eq_font = pygame.font.Font(FONT_NAME, equal_sign_font_size)
    eq_text = eq_font.render("=", True, WHITE)

    total_slots_width = slot_width * (2 * SLOTS_PER_SIDE) + slot_margin * (
        2 * SLOTS_PER_SIDE - 1
    )
    total_width = total_slots_width + eq_text.get_width() + check_button_width + 40
    start_x = (width - total_width) / 2

    # Left-hand slots
    for i in range(SLOTS_PER_SIDE):
        x = start_x + i * (slot_width + slot_margin)
        rect = pygame.Rect(x, bar_center_y - slot_height // 2, slot_width, slot_height)
        pygame.draw.rect(screen, GREY, rect, border_radius=5)
        slot_rects.append(rect)

    # Equal sign
    eq_x = slot_rects[-1].right + slot_margin
    screen.blit(eq_text, (eq_x, bar_center_y - eq_text.get_height() // 2))

    # Right-hand slots
    rhs_start_x = eq_x + eq_text.get_width() + slot_margin
    for i in range(SLOTS_PER_SIDE):
        x = rhs_start_x + i * (slot_width + slot_margin)
        rect = pygame.Rect(x, bar_center_y - slot_height // 2, slot_width, slot_height)
        pygame.draw.rect(screen, GREY, rect, border_radius=5)
        slot_rects.append(rect)

    # Check button
    button_x = slot_rects[-1].right + 30
    button_y = bar_center_y - check_button_height // 2
    check_button_rect = pygame.Rect(
        button_x, button_y, check_button_width, check_button_height
    )
    pygame.draw.rect(screen, GREEN, check_button_rect, border_radius=8)
    button_font = pygame.font.Font(FONT_NAME, button_font_size)
    button_text = button_font.render("Check", True, WHITE)
    screen.blit(
        button_text,
        (
            check_button_rect.centerx - button_text.get_width() // 2,
            check_button_rect.centery - button_text.get_height() // 2,
        ),
    )

    return slot_rects, check_button_rect


def draw_quit_button(screen: pygame.Surface, width: int) -> pygame.Rect:
    """Draws the quit button in the upper right corner."""
    button_x = width - QUICK_BUTTON_WIDTH - 20  # 20 px spacing from right edge
    button_y = 20  # 20 px spacing from top edge
    quit_button_rect = pygame.Rect(
        button_x, button_y, QUICK_BUTTON_WIDTH, QUICK_BUTTON_HEIGHT
    )
    pygame.draw.rect(screen, RED, quit_button_rect, border_radius=8)
    font = pygame.font.Font(FONT_NAME, BUTTON_FONT_SIZE)
    text = font.render("Quit", True, WHITE)
    screen.blit(
        text,
        (
            quit_button_rect.centerx - text.get_width() // 2,
            quit_button_rect.centery - text.get_height() // 2,
        ),
    )
    return quit_button_rect


# MAIN FUNCTION
def main() -> None:
    pygame.init()
    pygame.font.init()

    display_info = pygame.display.Info()
    width, height = display_info.current_w, display_info.current_h
    screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
    pygame.display.set_caption("Equatio")

    clock = pygame.time.Clock()
    running = True

    feedback_message = ""
    feedback_timer = 0
    font = pygame.font.Font(FONT_NAME, 32)

    # Containers
    grid = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    slots = [None for _ in range(2 * SLOTS_PER_SIDE)]

    cell_rects = build_grid(width, height)
    slot_rects, check_button_rect = build_equation_bar(width, height, screen)

    # Load equation set and extract terms from JSON
    # Change file name to the one you actually want to load
    equation_set = EquationSet.from_json(JSON_DIR / "standard_set.json")
    all_terms = equation_set.all_terms

    # Randomly distribute terms into grid cells
    available_positions = list(cell_rects.keys())
    random.shuffle(available_positions)

    draggable_terms = []
    for term, pos in zip(all_terms, available_positions):
        rect = cell_rects[pos]
        dt = DraggableTerm(term, pos, rect, "grid", width)
        grid[pos[0]][pos[1]] = dt
        draggable_terms.append(dt)
    # Note: If there are more terms than cells, some terms will not be placed.
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                width, height = event.w, event.h
                screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
                cell_rects = build_grid(width, height)

                # Re-center terms in their current positions
                for dt in draggable_terms:
                    if dt.container == "grid":
                        rect = cell_rects[dt.pos_key]
                    else:
                        # Slots are rebuilt during draw
                        continue
                    dt.rect.center = rect.center
                    dt.origin_rect = rect

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if check_button_rect.collidepoint(event.pos):
                    # Collect terms from slots
                    left_terms = [
                        slots[i].term for i in range(SLOTS_PER_SIDE) if slots[i]
                    ]
                    right_terms = [
                        slots[i].term
                        for i in range(SLOTS_PER_SIDE, 2 * SLOTS_PER_SIDE)
                        if slots[i]
                    ]

                    # Check against equations in set
                    correct = False

                    left_codes = sorted([t.latex_code for t in left_terms])
                    right_codes = sorted([t.latex_code for t in right_terms])

                    for eq in equation_set.equations:
                        if (
                            left_codes == [t.latex_code for t in eq.left]
                            and right_codes == [t.latex_code for t in eq.right]
                        ) or (
                            left_codes == [t.latex_code for t in eq.right]
                            and right_codes == [t.latex_code for t in eq.left]
                        ):
                            correct = True
                            break
                    # After checking for correct equation
                    if correct:
                        feedback_message = "Correct!"
                        # Remove terms used in the equation
                        used_terms = [dt for dt in slots if dt]
                        for dt in used_terms:
                            if dt in draggable_terms:
                                draggable_terms.remove(dt)
                        slots = [None for _ in range(len(slots))]

                        if not draggable_terms:
                            feedback_message = "Great, you know it all!"
                    else:
                        feedback_message = "Incorrect!"
                        # Return terms to their original positions
                        for i, dt in enumerate(slots):
                            if dt:
                                if dt.origin_container == "grid":
                                    # Return to original grid cell
                                    r, c = dt.origin_key
                                    dt.pos_key = (r, c)
                                    dt.rect.center = dt.origin_rect.center
                                    dt.container = "grid"
                                    grid[r][c] = dt
                                else:
                                    # Fallback: place back into first free grid cell
                                    for (r, c), rect in cell_rects.items():
                                        if grid[r][c] is None:
                                            dt.pos_key = (r, c)
                                            dt.rect.center = rect.center
                                            dt.container = "grid"
                                            grid[r][c] = dt
                                            break
                                slots[i] = None

                    feedback_timer = pygame.time.get_ticks()
                if draw_quit_button(screen, width).collidepoint(event.pos):
                    running = False

            for dt in draggable_terms:
                dt.handle_event(event, grid, slots, cell_rects, slot_rects)

        screen.fill(WHITE)
        draw_background(screen, width, height)
        draw_quit_button(screen, width)
        # Draw grid
        for (r, c), rect in cell_rects.items():
            if grid[r][c]:  # Term on grid position, draw white background rectangle
                pygame.draw.rect(screen, WHITE, rect, border_radius=4)
        # Equation bar (rebuild each frame)
        slot_rects, check_button_rect = build_equation_bar(width, height, screen)

        # re-center slot terms on resize
        for idx, dt in enumerate(slots):
            if dt:
                dt.rect.center = slot_rects[idx].center
                dt.origin_rect = slot_rects[idx]

        for dt in draggable_terms:
            dt.draw(screen)

        # Draw feedback message for 2 seconds
        if feedback_message and pygame.time.get_ticks() - feedback_timer < 2000:
            color = (0, 200, 0) if correct else (200, 0, 0)
            msg_surf = font.render(feedback_message, True, color)
            screen.blit(
                msg_surf,
                (
                    width // 2 - msg_surf.get_width() // 2,
                    height - EQUATION_BAR_HEIGHT - 40,
                ),
            )

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
