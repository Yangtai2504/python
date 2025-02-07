import pygame
import numpy as np
import tkinter as tk
from tkinter import messagebox

pygame.init()

WIDTH, HEIGHT = 600, 600
LINE_WIDTH = 8
BOARD_ROWS, BOARD_COLS = 3, 3  
SQUARE_SIZE = WIDTH // BOARD_COLS
PADDING = 20  

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 0, 0)
BLUE = (0, 0, 200)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tic Tac Toe")


board = np.zeros((BOARD_ROWS, BOARD_COLS), dtype=int)

def draw_board():
    """Vẽ lưới của bảng Tic-Tac-Toe"""
    screen.fill(WHITE)
    for row in range(1, BOARD_ROWS):
        pygame.draw.line(screen, BLACK, (0, row * SQUARE_SIZE), (WIDTH, row * SQUARE_SIZE), LINE_WIDTH)
    for col in range(1, BOARD_COLS):
        pygame.draw.line(screen, BLACK, (col * SQUARE_SIZE, 0), (col * SQUARE_SIZE, HEIGHT), LINE_WIDTH)


def draw_figures():
    """Vẽ các hình (O, X) lên bảng"""
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            center_x = col * SQUARE_SIZE + SQUARE_SIZE // 2
            center_y = row * SQUARE_SIZE + SQUARE_SIZE // 2
            if board[row][col] == 2:  
                pygame.draw.line(screen, RED, (center_x - SQUARE_SIZE // 2 + PADDING, center_y - SQUARE_SIZE // 2 + PADDING),
                                 (center_x + SQUARE_SIZE // 2 - PADDING, center_y + SQUARE_SIZE // 2 - PADDING), LINE_WIDTH * 2)
                pygame.draw.line(screen, RED, (center_x + SQUARE_SIZE // 2 - PADDING, center_y - SQUARE_SIZE // 2 + PADDING),
                                 (center_x - SQUARE_SIZE // 2 + PADDING, center_y + SQUARE_SIZE // 2 - PADDING), LINE_WIDTH * 2)

            elif board[row][col] == 1:  
                pygame.draw.circle(screen, BLUE, (center_x, center_y), SQUARE_SIZE // 2 - PADDING, LINE_WIDTH * 2)

def mark_square(row, col, player):
    board[row][col] = player

def available_square(row, col):
    return board[row][col] == 0

def check_winner():
    for i in range(BOARD_ROWS):
        if all(board[i][j] == board[i][0] and board[i][0] != 0 for j in range(BOARD_COLS)):
            return board[i][0]
        if all(board[j][i] == board[0][i] and board[0][i] != 0 for j in range(BOARD_ROWS)):
            return board[0][i]

    if BOARD_ROWS == BOARD_COLS:  
        if all(board[i][i] == board[0][0] and board[0][0] != 0 for i in range(BOARD_ROWS)):
            return board[0][0]
        if all(board[i][BOARD_COLS - i - 1] == board[0][BOARD_COLS - 1] and board[0][BOARD_COLS - 1] != 0 for i in range(BOARD_ROWS)):
            return board[0][BOARD_COLS - 1]
    return None

def minimax(board, depth, is_maximizing):
    """Thuật toán Minimax để AI chơi"""
    winner = check_winner()
    if winner == 1: return 1  
    if winner == 2: return -1  
    if np.all(board != 0): return 0  
    if is_maximizing:
        best_score = -float("inf")
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                if board[row][col] == 0:
                    board[row][col] = 1
                    score = minimax(board, depth + 1, False)
                    board[row][col] = 0
                    best_score = max(score, best_score)
        return best_score
    else:
        best_score = float("inf")
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                if board[row][col] == 0:
                    board[row][col] = 2
                    score = minimax(board, depth + 1, True)
                    board[row][col] = 0
                    best_score = min(score, best_score)
        return best_score

def best_move():
    """Tìm nước đi tốt nhất cho AI"""
    best_score = -float("inf")
    move = None
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            if board[row][col] == 0:
                board[row][col] = 1
                score = minimax(board, 0, False)
                board[row][col] = 0
                if score > best_score:
                    best_score = score
                    move = (row, col)
    return move


def show_game_over_message(winner):
    """Hiển thị thông báo kết quả và nút chơi lại"""
    root = tk.Tk()
    root.withdraw()  

    if winner == 1:
        message = "AI Wins!"
    elif winner == 2:
        message = "You Win!"
    else:
        message = "It's a Draw!"
    response = messagebox.askyesno("Game Over", message + "\nPlay again?")

    root.destroy()
    return response 


def reset_game():
    global board, player
    board = np.zeros((BOARD_ROWS, BOARD_COLS), dtype=int)
    player = 2 # Player starts first
    draw_board()
    pygame.display.update()


draw_board()
pygame.display.update()

player = 2  
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN and player == 2:
            x, y = event.pos
            row, col = y // SQUARE_SIZE, x // SQUARE_SIZE
            if 0 <= row < BOARD_ROWS and 0 <= col < BOARD_COLS and available_square(row, col):  # Check valid move
                mark_square(row, col, player)
                winner = check_winner()
                if winner or np.all(board != 0):
                   play_again = show_game_over_message(winner)
                   if play_again:
                       reset_game()
                   else:
                        running = False
                else:
                  player = 1  


    if player == 1 and running:
        move = best_move()
        if move:
            mark_square(move[0], move[1], 1)
            winner = check_winner()
            if winner or np.all(board != 0):
                play_again = show_game_over_message(winner)
                if play_again:
                    reset_game()
                else:
                    running = False
            else:
                player = 2 


    draw_board() 
    draw_figures()
    pygame.display.update()

pygame.quit()