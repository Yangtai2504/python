import pygame
import random
import numpy as np

# ================= CẤU HÌNH TRÒ CHƠI =================
N = int(input("Nhập kích thước bàn cờ (N x N): "))  # Nhập kích thước bảng
MINE_COUNT = int(input("Nhập số lượng mìn: "))  # Nhập số mìn
TILE_SIZE = 40  # Kích thước mỗi ô
WIDTH, HEIGHT = N * TILE_SIZE, N * TILE_SIZE

# Màu sắc
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (192, 192, 192)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)  # Cờ

# Khởi tạo pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Minesweeper")

# ================= KHỞI TẠO BẢNG CHƠI =================
board = np.zeros((N, N), dtype=int)  # 0: ô trống, 9: ô có mìn
revealed = np.full((N, N), False)   # Trạng thái mở ô
flags = np.full((N, N), False)      # Cờ mìn

# Đặt mìn ngẫu nhiên
mine_positions = random.sample(range(N * N), MINE_COUNT)
for pos in mine_positions:
    row, col = divmod(pos, N)
    board[row][col] = 9

# Tính số mìn xung quanh
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

# ================= VẼ BẢNG CHƠI =================
def draw_board():
    screen.fill(WHITE)
    for r in range(N):
        for c in range(N):
            x, y = c * TILE_SIZE, r * TILE_SIZE
            rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)

            if revealed[r][c]:  # Ô đã mở
                if board[r][c] == 9:
                    pygame.draw.rect(screen, RED, rect)  # Mìn
                else:
                    pygame.draw.rect(screen, GRAY, rect)
                    if board[r][c] > 0:
                        font = pygame.font.Font(None, 36)
                        text = font.render(str(board[r][c]), True, BLACK)
                        screen.blit(text, (x + 10, y + 5))
            else:  # Ô chưa mở
                pygame.draw.rect(screen, GREEN, rect)
                if flags[r][c]:  # Nếu đã đặt cờ
                    pygame.draw.rect(screen, YELLOW, rect)

            pygame.draw.rect(screen, BLACK, rect, 2)

# ================== LOGIC MỞ Ô ==================
def reveal_cell(row, col):
    if revealed[row][col] or flags[row][col]:  # Nếu đã mở hoặc có cờ thì bỏ qua
        return
    revealed[row][col] = True

    if board[row][col] == 0:  # Nếu là ô trống, mở rộng BFS
        queue = [(row, col)]
        while queue:
            r, c = queue.pop(0)
            for nr in range(max(0, r - 1), min(N, r + 2)):
                for nc in range(max(0, c - 1), min(N, c + 2)):
                    if not revealed[nr][nc] and board[nr][nc] != 9:
                        revealed[nr][nc] = True
                        if board[nr][nc] == 0:
                            queue.append((nr, nc))

# ================== GẮN CỜ MÌN ==================
def toggle_flag(row, col):
    if not revealed[row][col]:  # Chỉ có thể gắn cờ ở ô chưa mở
        flags[row][col] = not flags[row][col]

# ================== AUTO CHƠI AI ==================
def auto_play():
    for r in range(N):
        for c in range(N):
            if revealed[r][c] and board[r][c] > 0:
                hidden_cells = [
                    (nr, nc)
                    for nr in range(max(0, r - 1), min(N, r + 2))
                    for nc in range(max(0, c - 1), min(N, c + 2))
                    if not revealed[nr][nc] and not flags[nr][nc]
                ]
                flagged_cells = [
                    (nr, nc)
                    for nr in range(max(0, r - 1), min(N, r + 2))
                    for nc in range(max(0, c - 1), min(N, c + 2))
                    if flags[nr][nc]
                ]

                # Nếu số ô ẩn == số mìn cần tìm -> đánh dấu mìn
                if len(hidden_cells) == board[r][c] - len(flagged_cells):
                    for nr, nc in hidden_cells:
                        flags[nr][nc] = True

                # Nếu số ô ẩn == số cờ đặt -> mở tất cả ô còn lại
                if len(flagged_cells) == board[r][c]:
                    for nr, nc in hidden_cells:
                        reveal_cell(nr, nc)

# ================= GAME LOOP =================
running = True
auto_mode = False

while running:
    screen.fill(WHITE)
    draw_board()
    pygame.display.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:  # Nhấn SPACE để bật Auto Play
                auto_mode = not auto_mode

        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            row, col = y // TILE_SIZE, x // TILE_SIZE

            if event.button == 1 and not auto_mode:  # Chuột trái để mở ô
                if board[row][col] == 9:
                    print("💥 Bạn thua rồi! Game Over.")
                    running = False
                else:
                    reveal_cell(row, col)

            if event.button == 3:  # Chuột phải để gắn cờ
                toggle_flag(row, col)

    if auto_mode:
        auto_play()

pygame.quit()
