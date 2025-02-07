import pygame
import random
import numpy as np
import time
import tkinter as tk
from tkinter import messagebox

pygame.init()

# ================= CẤU HÌNH  =================
N = int(input("Nhập kích thước bàn cờ (N x N): "))
MINE_COUNT = int(input("Nhập số lượng mìn: "))

TILE_SIZE = 30
HEADER_HEIGHT = 60
WIDTH = N * TILE_SIZE
HEIGHT = N * TILE_SIZE + HEADER_HEIGHT

COLORS = {
    'background': (192, 192, 192), 
    'border_light': (255, 255, 255),  
    'border_dark': (128, 128, 128), 
    'border_darker': (64, 64, 64),   
    'numbers': [
        None,
        (0, 0, 255),      
        (0, 128, 0),      
        (255, 0, 0),      
        (0, 0, 128),     
        (128, 0, 0),      
        (0, 128, 128),    
        (0, 0, 0),       
        (128, 128, 128)   
    ],
    'mine': (0, 0, 0),    
    'flag': (255, 0, 0), 
    'digital': (255, 0, 0)  
}

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Minesweeper")

# ================= KHỞI TẠO =================
board = np.zeros((N, N), dtype=int)
revealed = np.full((N, N), False)
flags = np.full((N, N), False)
game_over = False
start_time = None
current_time = 0
remaining_mines = MINE_COUNT
face_status = 'normal'  
auto_mode = False 

def init_board():
    mine_positions = random.sample(range(N * N), MINE_COUNT)
    for pos in mine_positions:
        row, col = divmod(pos, N)
        board[row][col] = 9

    for r in range(N):
        for c in range(N):
            if board[r][c] == 9:
                continue
            mines_around = sum(
                board[nr][nc] == 9
                for nr in range(max(0, r - 1), min(N, r + 2))
                for nc in range(max(0, c - 1), min(N, c + 2))
            )
            board[r][c] = mines_around
init_board()

def get_neighbors(r, c):
    neighbors = []
    for nr in range(max(0, r - 1), min(N, r + 2)):
        for nc in range(max(0, c - 1), min(N, c + 2)):
            if (nr,nc) != (r,c):
                neighbors.append((nr,nc))
    return neighbors

def count_flagged_neighbors(r, c):
    return sum(flags[nr][nc] for nr, nc in get_neighbors(r, c))

def count_unrevealed_neighbors(r, c):
    return sum(not revealed[nr][nc] for nr, nc in get_neighbors(r, c))

def find_definite_mines():
    definite_mines = []
    for r in range(N):
        for c in range(N):
            if revealed[r][c] and board[r][c] > 0:
                if board[r][c] == count_unrevealed_neighbors(r, c) + count_flagged_neighbors(r, c):
                    for nr, nc in get_neighbors(r, c):
                        if not revealed[nr][nc] and not flags[nr][nc]:
                            definite_mines.append((nr, nc))
    return definite_mines

def find_definite_safe_cells():
    safe_moves = []
    for r in range(N):
        for c in range(N):
            if revealed[r][c] and board[r][c] > 0:
                if count_flagged_neighbors(r, c) == board[r][c] and count_unrevealed_neighbors(r, c) > 0:
                    for nr, nc in get_neighbors(r, c):
                        if not revealed[nr][nc] and not flags[nr][nc]:
                            safe_moves.append((nr, nc))
    return safe_moves

def auto_play():
    global face_status, game_over, start_time
    
    if start_time is None:
        safe_moves = [(r, c) for r in range(N) for c in range(N) if board[r][c] == 0]
        if safe_moves:
            r, c = random.choice(safe_moves)
            start_time = time.time()
            reveal_cell(r, c)
        return
    
    mines = find_definite_mines()
    if mines:
        for r, c in mines:
            toggle_flag(r, c)
        return

    safes = find_definite_safe_cells()
    if safes:
        for r, c in safes:
            reveal_cell(r, c)
        return
    
    unrevealed = [(r, c) for r in range(N) for c in range(N) if not revealed[r][c] and not flags[r][c]]
    if unrevealed:
        r, c = random.choice(unrevealed)
        if board[r][c] == 9:
            face_status = 'dead'
            game_over = True
            revealed[r][c] = True
        else:
            reveal_cell(r, c)

    if np.sum(flags == True) == MINE_COUNT and sum((board == 9) & (flags == True)) == MINE_COUNT:
        face_status = 'win'
        game_over = True
        show_win_message()

font = pygame.font.Font(None, 40)

def draw_3d_rect(surface, rect, color, pressed=False):
    pygame.draw.rect(surface, color, rect)
    if not pressed:
        pygame.draw.line(surface, COLORS['border_light'], rect.topleft, rect.topright)
        pygame.draw.line(surface, COLORS['border_light'], rect.topleft, rect.bottomleft)
        pygame.draw.line(surface, COLORS['border_dark'], rect.bottomleft, rect.bottomright)
        pygame.draw.line(surface, COLORS['border_dark'], rect.topright, rect.bottomright)
    else:
        pygame.draw.line(surface, COLORS['border_dark'], rect.topleft, rect.topright)
        pygame.draw.line(surface, COLORS['border_dark'], rect.topleft, rect.bottomleft)
        pygame.draw.line(surface, COLORS['border_light'], rect.bottomleft, rect.bottomright)
        pygame.draw.line(surface, COLORS['border_light'], rect.topright, rect.bottomright)

def draw_digital_number(number, x, y):
    text = font.render(f"{number:03d}", True, COLORS['digital'])
    background = pygame.Rect(x, y, 70, 40)
    pygame.draw.rect(screen, (0, 0, 0), background)
    screen.blit(text, (x + 5, y + 5))

def draw_face():
    face_rect = pygame.Rect(WIDTH//2 - 25, 10, 50, 50)
    draw_3d_rect(screen, face_rect, COLORS['background'], False)
    center_x = WIDTH//2
    center_y = 35
    if face_status == 'normal':
        pygame.draw.circle(screen, (255, 255, 0), (center_x, center_y), 15)
        pygame.draw.circle(screen, (0, 0, 0), (center_x - 5, center_y - 5), 2)
        pygame.draw.circle(screen, (0, 0, 0), (center_x + 5, center_y - 5), 2)
        pygame.draw.arc(screen, (0, 0, 0), (center_x - 8, center_y - 8, 16, 16), 0, 3.14, 2)
    elif face_status == 'dead':
        pygame.draw.circle(screen, (255, 255, 0), (center_x, center_y), 15)
        pygame.draw.line(screen, (0, 0, 0), (center_x - 5, center_y - 5), (center_x - 3, center_y - 3), 2)
        pygame.draw.line(screen, (0, 0, 0), (center_x - 5, center_y - 3), (center_x - 3, center_y - 5), 2)
        pygame.draw.line(screen, (0, 0, 0), (center_x + 5, center_y - 5), (center_x + 3, center_y - 3), 2)
        pygame.draw.line(screen, (0, 0, 0), (center_x + 5, center_y - 3), (center_x + 3, center_y - 5), 2)
        pygame.draw.arc(screen, (0, 0, 0), (center_x - 8, center_y - 3, 16, 16), 3.14, 6.28, 2)
    elif face_status == 'win':
        pygame.draw.circle(screen, (255, 255, 0), (center_x, center_y), 15)
        pygame.draw.circle(screen, (0, 0, 0), (center_x - 7, center_y - 3), 4)
        pygame.draw.circle(screen, (0, 0, 0), (center_x + 7, center_y - 3), 4)

def draw_board():
    global current_time
    header_rect = pygame.Rect(0, 0, WIDTH, HEADER_HEIGHT)
    draw_3d_rect(screen, header_rect, COLORS['background'])
    draw_digital_number(remaining_mines, 20, 10)
    
    if start_time is not None and not game_over and face_status != 'win':
        current_time = min(999, int(time.time() - start_time))
    draw_digital_number(current_time, WIDTH - 90, 10)
    draw_face()
    board_rect = pygame.Rect(0, HEADER_HEIGHT, WIDTH, HEIGHT - HEADER_HEIGHT)
    draw_3d_rect(screen, board_rect, COLORS['background'])
    for r in range(N):
        for c in range(N):
            cell_rect = pygame.Rect(c * TILE_SIZE, r * TILE_SIZE + HEADER_HEIGHT, TILE_SIZE, TILE_SIZE)
            if revealed[r][c]:
                draw_3d_rect(screen, cell_rect, COLORS['background'], True)
                if board[r][c] > 0 and board[r][c] < 9:
                    text = font.render(str(board[r][c]), True, COLORS['numbers'][board[r][c]])
                    text_rect = text.get_rect(center=cell_rect.center)
                    screen.blit(text, text_rect)
                elif board[r][c] == 9:
                    mine_rect = cell_rect.inflate(-10, -10)
                    pygame.draw.circle(screen, COLORS['mine'], mine_rect.center, 8)
            else:
                draw_3d_rect(screen, cell_rect, COLORS['background'])
                if flags[r][c]:
                    flag_points = [
                        (cell_rect.centerx - 5, cell_rect.centery + 8),
                        (cell_rect.centerx - 5, cell_rect.centery - 8),
                        (cell_rect.centerx + 5, cell_rect.centery)
                    ]
                    pygame.draw.polygon(screen, COLORS['flag'], flag_points)

def reveal_cell(row, col):
    if revealed[row][col] or flags[row][col]:
        return
    
    revealed[row][col] = True

    if board[row][col] == 0:
        for r in range(max(0, row - 1), min(N, row + 2)):
            for c in range(max(0, col - 1), min(N, col + 2)):  # Thay thế 'c + 2' thành 'col + 2'
                if not revealed[r][c] and board[r][c] != 9:
                    reveal_cell(r, c)

def toggle_flag(row, col):
    global remaining_mines
    if not revealed[row][col]:
        flags[row][col] = not flags[row][col]
        remaining_mines += -1 if flags[row][col] else 1

def show_win_message():
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo("Game Over", "Congratulations. You have completed with the bomb :)")
    root.destroy()

# ================= GAME LOOP =================
running = True
while running:
    screen.fill(COLORS['background'])
    draw_board()
    pygame.display.update()
   
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                auto_mode = not auto_mode
                if not auto_mode:
                    face_status = 'normal'
                    current_time = 0
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            if WIDTH//2 - 25 <= x <= WIDTH//2 + 25 and 10 <= y <= 60:
                board = np.zeros((N, N), dtype=int)
                revealed = np.full((N, N), False)
                flags = np.full((N, N), False)
                game_over = False
                start_time = None
                current_time = 0
                remaining_mines = MINE_COUNT
                face_status = 'normal'
                auto_mode = False
                init_board()
                continue

            if not auto_mode and y >= HEADER_HEIGHT:
                row = (y - HEADER_HEIGHT) // TILE_SIZE
                col = x // TILE_SIZE
                if 0 <= row < N and 0 <= col < N and not game_over:
                    if start_time is None:
                        start_time = time.time()
                    if event.button == 1:
                        if board[row][col] == 9:
                            game_over = True
                            face_status = 'dead'
                            revealed[row][col] = True
                        else:
                            reveal_cell(row, col)
                    elif event.button == 3:
                        toggle_flag(row, col)

    if auto_mode and not game_over:
        auto_play()
        pygame.time.wait(150)

pygame.quit()