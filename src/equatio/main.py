# Main game environment using pygame with drag-and-drop between board and equation bar.

from __future__ import annotations
import random

import pygame

from draggable_term import DraggableTerm
from equation_set import EquationSet, JSON_DIR
from gui import (
    EQUATION_BAR_HEIGHT,
    FONT_NAME,
    FPS,
    GRID_SIZE,
    SLOTS_PER_SIDE,
    WHITE,
    draw_background,
    draw_quit_button,
    build_grid,
    build_equation_bar,
)
from term import Term


def main() -> None:
    # Initialising variables
    running: bool = True
    feedback_message: str = ""
    feedback_timer: int = 0
    correct: bool = False

    # Initialising pygame
    pygame.init()
    pygame.font.init()
    font: pygame.font.Font = pygame.font.Font(FONT_NAME, 32)
    clock: pygame.time.Clock = pygame.time.Clock()
    display_info = pygame.display.Info()
    # Set up the display
    width: int = display_info.current_w
    height: int = display_info.current_h
    screen: pygame.Surface = pygame.display.set_mode((width, height), pygame.RESIZABLE)
    pygame.display.set_caption("equatio")

    # Initialise containers
    grid: list[list[DraggableTerm | None]] = [
        [None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)
    ]
    slots: list[DraggableTerm | None] = [None for _ in range(2 * SLOTS_PER_SIDE)]

    cell_rects: dict[tuple[int, int], pygame.Rect] = build_grid(width, height)
    slot_rects: list[pygame.Rect]
    check_button_rect: pygame.Rect
    slot_rects, check_button_rect = build_equation_bar(width, height, screen)

    draggable_terms: list[DraggableTerm] = []

    # Load equation set and extract terms from JSON
    # Change file name to the one you actually want to load
    equation_set: EquationSet = EquationSet.from_json(JSON_DIR / "standard_set.json")
    all_terms: list[Term] = equation_set.all_terms

    # Randomly distribute terms into grid cells
    available_positions: list[tuple[int, int]] = list(cell_rects.keys())
    random.shuffle(available_positions)

    for term, pos in zip(all_terms, available_positions):
        rect = cell_rects[pos]
        dt = DraggableTerm(term, pos, rect, "grid", width)
        grid[pos[0]][pos[1]] = dt
        draggable_terms.append(dt)
    # Note: If there are more terms than cells, some terms will not be placed.

    # Main loop
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

                    if correct:
                        feedback_message = "Correct!"
                        # Remove terms used in the equation
                        used_terms = [dt for dt in slots if dt]
                        for dt in used_terms:
                            if dt in draggable_terms:
                                draggable_terms.remove(dt)
                        # Clear slots
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
