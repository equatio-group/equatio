"""#hiier kommt die py.game Umgebung"""  # stay in english, please ;)
from itertools import product

import pygame
import numpy as np
import random

# Every value which doesn't change and has a "domain purpose" should be a constant.
# If you use a setting on a library function, e.g. `infer_datetime=True` in pandas, True must not be a constant
# I'll mark constants with a comment
# You might want to have a config.py module if you want to separate it from your code,
# or it is also relevant for other modules

SCREEN_WIDTH = 800
SCREEN_HEIGHT = SCREEN_WIDTH
CELL_NUMBER= 16
WHITE = (255, 255, 255)  # Constant naming.
BLACK = (0, 0, 0)
GREY = (128, 128, 128)
FPS = 60

# Below (lower cases variables until first function) should be part of main method and necessary variable shall be forwarded to functions, which interacts wth them.

# new_board = True
# options_list = []  # was only used to generate board
# board = []

def generate_board() -> list[int]:
    # global options_list  # Never ever use global! Get values as parameter.
    # global spaces  # Never ever use global! Get values as parameter.
    board = []
    options = list(range(CELL_NUMBER))
    for item in range(CELL_NUMBER):
        piece = random.choice(options)  # There is a function in random for it ;)
        board.append(piece)
        options.remove(piece)

    return board


def draw_background(screen):  # typing!
    title_font = pygame.font.Font("freesansbold.ttf", 50)  # Move to usage, it is not used anywhere else, or make constant, if it is one.
    top_menu = pygame.draw.rect(screen, BLACK, [0, 0, SCREEN_WIDTH, 1 / 8 * SCREEN_HEIGHT], 0)  # not used
    title_text = title_font.render("Equatio", True, WHITE)
    screen.blit(title_text, (0.0125*SCREEN_WIDTH,0.025*SCREEN_HEIGHT))
    board_space = pygame.draw.rect(screen, GREY, [0, 1 / 8 * SCREEN_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT - 2 / 8 * SCREEN_HEIGHT], 0)  # not used
    bottom_menu = pygame.draw.rect(screen, BLACK, [0, SCREEN_HEIGHT - 1 / 8 * SCREEN_HEIGHT, SCREEN_WIDTH, 1 / 8 * SCREEN_HEIGHT], 0)  # not used


def draw_board(board: list[int], screen) -> list[int]:  # typing for `screen`
    small_font = pygame.font.Font("freesansbold.ttf", 26)  # Move to usage, it is not used anywhere else, or make constant, if it is one.

    number_of_rows = int(np.sqrt(CELL_NUMBER))
    number_of_columns = int(np.sqrt(CELL_NUMBER))  # Use full naming.
    board_list =[]
    for column, row in product(range(number_of_columns), range(number_of_rows)):  # Reduces indentations
        piece = pygame.draw.rect(screen, WHITE, [column*190 + 10, row*140 + 110, 180, 130], 0, 4)  # what do these numbers mean? please make them to named constants
        board_list.append(piece)
        piece_text = small_font.render(f'{board[column * number_of_rows + row]}', True, GREY)
        screen.blit(piece_text, (column*190 + 15,row*140 + 115))  # stay consistent in spacing,   # what do these numbers mean? please make them to named constants

    return board_list  # Why do you return something, when you draw? it is also not used.


def main():
    pygame.init()
    pygame.font.init()
    timer = pygame.time.Clock()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Equation")

    board = generate_board()
    running = True
    while running:
        timer.tick(FPS)
        screen.fill(WHITE)
        # if new_board:  # not needed if board is generated outside of the loop
        #     generate_board()
        #     print(spaces)  # shouldn't be part of the final product, you could try logging instead
        #     new_board = False


        draw_background(screen)
        draw_board(board, screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        pygame.display.flip()
    pygame.quit()

if __name__ == '__main__':
    main()

