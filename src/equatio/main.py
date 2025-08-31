
#hier kommt die py.game Umgebung

import pygame
import numpy as np
import random

pygame.init()
pygame.font.init()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = SCREEN_WIDTH
CELL_NUMBER= 16
white=(255,255,255)
black=(0,0,0)
grey=(128,128,128)
fps =60
timer = pygame.time.Clock()
rows = int(np.sqrt(CELL_NUMBER))
cols = int(np.sqrt(CELL_NUMBER))
new_board = True
options_list = []
spaces = []

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Equation")
title_font = pygame.font.Font("freesansbold.ttf", 50)
small_font = pygame.font.Font("freesansbold.ttf", 26)

def generate_board():
    global options_list
    global spaces
    for item in range(CELL_NUMBER):
        options_list.append(item)

    for item in range(CELL_NUMBER):
        piece = options_list[random.randint(0,len(options_list)-1)]
        spaces.append(piece)
        options_list.remove(piece)

def draw_background():
    top_menu = pygame.draw.rect(screen, black, [0, 0, SCREEN_WIDTH, 1/8*SCREEN_HEIGHT],0)
    title_text = title_font.render("Equatio", True, white)
    screen.blit(title_text, (0.0125*SCREEN_WIDTH,0.025*SCREEN_HEIGHT))
    board_space = pygame.draw.rect(screen, grey, [0, 1/8* SCREEN_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT-2/8*SCREEN_HEIGHT], 0)
    bottom_menu = pygame.draw.rect(screen, black, [0, SCREEN_HEIGHT-1/8*SCREEN_HEIGHT, SCREEN_WIDTH, 1 / 8 * SCREEN_HEIGHT], 0)

def draw_board():
    global rows
    global cols
    board_list =[]
    for i in range(cols):
        for j in range(rows):
            piece = pygame.draw.rect(screen, white, [i*190+10,j*140+110,180,130],0,4)
            board_list.append(piece)
            piece_text = small_font.render(f'{spaces[i * rows + j]}', True, grey)
            screen.blit(piece_text, (i*190+15,j*140+115))

    return board_list

running = True
while running:
    timer.tick(fps)
    screen.fill(white)
    if new_board:
        generate_board()
        print(spaces)
        new_board = False


    draw_background()
    draw_board()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.flip()
pygame.quit()

