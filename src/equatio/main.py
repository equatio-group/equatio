"""Main game environment using pygame with drag-and-drop between board and equation bar."""

import random
from itertools import product

import numpy as np
import pygame

from equation import  JSON_DIR # add EquationSet import
from term import Term, JSON_DIR
from equation_set import EquationSet, JSON_DIR

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


def build_grid(width, height):
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


def build_equation_bar(width, height, screen):
    """Draw equation bar and return slot rects + button rect."""
    bar_top = height - EQUATION_BAR_HEIGHT
    bar_center_y = bar_top + EQUATION_BAR_HEIGHT // 2

    slot_rects = []
    eq_font = pygame.font.Font(FONT_NAME, EQUAL_SIGN_FONT_SIZE)
    eq_text = eq_font.render("=", True, WHITE)

    total_slots_width = SLOT_WIDTH * (2 * SLOTS_PER_SIDE) + SLOT_MARGIN * (2 * SLOTS_PER_SIDE - 1)
    total_width = total_slots_width + eq_text.get_width() + CHECK_BUTTON_WIDTH + 40
    start_x = (width - total_width) / 2

    # Left-hand slots
    for i in range(SLOTS_PER_SIDE):
        x = start_x + i * (SLOT_WIDTH + SLOT_MARGIN)
        rect = pygame.Rect(x, bar_center_y - SLOT_HEIGHT // 2, SLOT_WIDTH, SLOT_HEIGHT)
        pygame.draw.rect(screen, GREY, rect, border_radius=5)
        slot_rects.append(rect)

    # Equal sign
    eq_x = slot_rects[-1].right + SLOT_MARGIN
    screen.blit(eq_text, (eq_x, bar_center_y - eq_text.get_height() // 2))

    # Right-hand slots
    rhs_start_x = eq_x + eq_text.get_width() + SLOT_MARGIN
    for i in range(SLOTS_PER_SIDE):
        x = rhs_start_x + i * (SLOT_WIDTH + SLOT_MARGIN)
        rect = pygame.Rect(x, bar_center_y - SLOT_HEIGHT // 2, SLOT_WIDTH, SLOT_HEIGHT)
        pygame.draw.rect(screen, GREY, rect, border_radius=5)
        slot_rects.append(rect)

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


class DraggableTerm:
    """Class representing a draggable term bound to a grid cell or equation slot."""

    def __init__(self, term: Term, pos_key, rect, container="grid"):
        self.term = term
        self.image = pygame.image.load(term.get_sprite_path()).convert_alpha()
        self.rect = self.image.get_rect(center=rect.center)

        # position info
        self.pos_key = pos_key  # (row, col) or slot index
        self.container = container  # "grid" or "slot"
        self.origin_key = pos_key
        self.origin_rect = rect
        self.origin_container = container
        self.dragging = False

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)

    def handle_event(self, event, grid, slots, cell_rects, slot_rects):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
                self.mouse_offset = (self.rect.x - event.pos[0], self.rect.y - event.pos[1])
                # clear current container
                if self.container == "grid":
                    r, c = self.pos_key
                    grid[r][c] = None
                elif self.container == "slot":
                    slots[self.pos_key] = None

        elif event.type == pygame.MOUSEBUTTONUP and self.dragging:
            self.dragging = False
            x, y = event.pos

            # check grid cells
            for (r, c), rect in cell_rects.items():
                if rect.collidepoint((x, y)) and grid[r][c] is None:
                    self.container = "grid"
                    self.pos_key = (r, c)
                    self.rect.center = rect.center
                    grid[r][c] = self
                    self.origin_key = self.pos_key
                    self.origin_rect = rect
                    self.origin_container = "grid"
                    return

            # check slot rects
            for idx, rect in enumerate(slot_rects):
                if rect.collidepoint((x, y)) and slots[idx] is None:
                    self.container = "slot"
                    self.pos_key = idx
                    self.rect.center = rect.center
                    slots[idx] = self
                    self.origin_key = self.pos_key
                    self.origin_rect = rect
                    self.origin_container = "slot"
                    return

            # else return to origin
            self.pos_key = self.origin_key
            self.rect.center = self.origin_rect.center
            self.container = self.origin_container
            if self.container == "grid":
                r, c = self.pos_key
                grid[r][c] = self
            else:
                slots[self.pos_key] = self

        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.rect.x = event.pos[0] + self.mouse_offset[0]
            self.rect.y = event.pos[1] + self.mouse_offset[1]


def main() -> None:
    pygame.init()
    pygame.font.init()

    width, height = 800, 800
    screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
    pygame.display.set_caption("Equatio")

    clock = pygame.time.Clock()
    running = True
    
    feedback_message = ""
    feedback_timer = 0
    font = pygame.font.Font(FONT_NAME, 32)

    # containers
    grid = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    slots = [None for _ in range(2 * SLOTS_PER_SIDE)]

    cell_rects = build_grid(width, height)
    slot_rects, check_button_rect = build_equation_bar(width, height, screen)

# === Load equation set and extract terms from JSON ===
    # change file name to the one you actually want to load
    equation_set = EquationSet.from_json(JSON_DIR / "standard_set.json")
    all_terms = equation_set.all_terms

    # Randomly distribute terms into grid cells
    available_positions = list(cell_rects.keys())
    random.shuffle(available_positions)

    draggable_terms = []
    for term, pos in zip(all_terms, available_positions):
        rect = cell_rects[pos]
        dt = DraggableTerm(term, pos, rect, "grid")
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

                # re-center terms in their current positions
                for dt in draggable_terms:
                    if dt.container == "grid":
                        rect = cell_rects[dt.pos_key]
                    else:
                        # slots are rebuilt during draw
                        continue
                    dt.rect.center = rect.center
                    dt.origin_rect = rect

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if check_button_rect.collidepoint(event.pos):
                    # --- Collect terms from slots ---
                    left_terms = [slots[i].term for i in range(SLOTS_PER_SIDE) if slots[i]]
                    right_terms = [slots[i].term for i in range(SLOTS_PER_SIDE, 2 * SLOTS_PER_SIDE) if slots[i]]

                    # --- Check against equations in set ---
                    correct = False
                    
                    left_codes = sorted([t.latex_code for t in left_terms])
                    right_codes = sorted([t.latex_code for t in right_terms])

                    for eq in equation_set.equations:
                        if ((left_codes == [t.latex_code for t in eq.left] and
                            right_codes == [t.latex_code for t in eq.right]) or
                            (left_codes == [t.latex_code for t in eq.right] and
                            right_codes == [t.latex_code for t in eq.left])):
                            correct = True
                            break
                    # --- after checking for correct equation ---
                    if correct:
                        feedback_message = "Correct!"
                        # Remove terms used in the equation
                        used_terms = [dt for dt in slots if dt]
                        for dt in used_terms:
                            if dt in draggable_terms:
                                draggable_terms.remove(dt)
                        slots = [None for _ in range(len(slots))]

                        # If no draggable terms left -> show final message
                        if not draggable_terms:
                            feedback_message = "Great, you know it all!"
                    else:
                        feedback_message = "Incorrect!"
                        # Return terms to their original positions
                        for i, dt in enumerate(slots):
                            if dt:
                                if dt.origin_container == "grid":
                                    # return to original grid cell
                                    r, c = dt.origin_key
                                    dt.pos_key = (r, c)
                                    dt.rect.center = dt.origin_rect.center
                                    dt.container = "grid"
                                    grid[r][c] = dt
                                else:
                                    # fallback: place back into first free grid cell
                                    for (r, c), rect in cell_rects.items():
                                        if grid[r][c] is None:
                                            dt.pos_key = (r, c)
                                            dt.rect.center = rect.center
                                            dt.container = "grid"
                                            grid[r][c] = dt
                                            break
                                slots[i] = None

                    feedback_timer = pygame.time.get_ticks()

            for dt in draggable_terms:
                dt.handle_event(event, grid, slots, cell_rects, slot_rects)

        screen.fill(WHITE)
        draw_background(screen, width, height)

        # draw grid
        for (r, c), rect in cell_rects.items():
            if grid[r][c] is None:
                continue
            else:
                pygame.draw.rect(screen, WHITE, rect, border_radius=4)
            pygame.draw.rect(screen, GREY, rect, 1)
        # equation bar (rebuild each frame)
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
            screen.blit(msg_surf, (width // 2 - msg_surf.get_width() // 2,
                                   height - EQUATION_BAR_HEIGHT - 40))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()