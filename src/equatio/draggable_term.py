# Class for a draggable term on the GUI

from __future__ import annotations

import pygame

from term import Term


class DraggableTerm:
    """Class representing a draggable term bound to a grid cell or equation slot."""

    def __init__(
        self,
        term: Term,
        pos_key: tuple[int, int] | int,
        rect: pygame.Rect,
        container: str = "grid",
        s_width: int = 0,
    ) -> None:
        self.term = term
        self.image = pygame.image.load(term.get_sprite_path()).convert_alpha()
        original_width, original_height = self.image.get_size()
        desired_width, desired_height = (s_width / 12, s_width / 30)
        scale_factor = min(
            desired_width / original_width, desired_height / original_height
        )
        new_size = (
            int(original_width * scale_factor),
            int(original_height * scale_factor),
        )
        self.image = pygame.transform.smoothscale(self.image, new_size)
        self.rect = self.image.get_rect(center=rect.center)

        # position info
        self.pos_key = pos_key  # (row, col) or slot index
        self.container = container  # "grid" or "slot"
        self.origin_key = pos_key
        self.origin_rect = rect
        self.origin_container = container
        self.dragging = False

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.image, self.rect.topleft)

    def handle_event(
        self,
        event: pygame.event.Event,
        grid: list[list[DraggableTerm | None]],
        slots: list[DraggableTerm | None],
        cell_rects: dict[tuple[int, int], pygame.Rect],
        slot_rects: list[pygame.Rect],
    ) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
                self.mouse_offset = (
                    self.rect.x - event.pos[0],
                    self.rect.y - event.pos[1],
                )
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
