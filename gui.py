import pygame

# --- Colors ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_SQUARE = (238, 238, 210)
DARK_SQUARE = (118, 150, 86)
ORANGE_RED = (255, 69, 0)
RED = (255, 0, 0)

# --- Size Presets ---
SIZE_PRESETS = {
    "small": {
        "LEFT_PANEL_WIDTH": 150, "RIGHT_PANEL_WIDTH": 150, "BOARD_WIDTH": 400, "HEIGHT": 400,
        "CAPTURED_PIECE_SCALE": 0.4, "font_size": 14, "button_font_size": 16,
        "tooltip_font_size": 12, "notification_font_size": 30,
    },
    "medium": {
        "LEFT_PANEL_WIDTH": 200, "RIGHT_PANEL_WIDTH": 200, "BOARD_WIDTH": 600, "HEIGHT": 600,
        "CAPTURED_PIECE_SCALE": 0.5, "font_size": 18, "button_font_size": 20,
        "tooltip_font_size": 14, "notification_font_size": 40,
    },
    "large": {
        "LEFT_PANEL_WIDTH": 250, "RIGHT_PANEL_WIDTH": 250, "BOARD_WIDTH": 800, "HEIGHT": 800,
        "CAPTURED_PIECE_SCALE": 0.6, "font_size": 22, "button_font_size": 24,
        "tooltip_font_size": 16, "notification_font_size": 50,
    },
}

class GUI:
    def __init__(self, screen, size="medium"):
        self.screen = screen
        self.piece_images = {}
        self.captured_piece_images = {}
        pygame.font.init()
        self.setup_dimensions(size)

    def setup_dimensions(self, size):
        self.size = size
        self.size_preset = SIZE_PRESETS[size]

        self.LEFT_PANEL_WIDTH = self.size_preset['LEFT_PANEL_WIDTH']
        self.RIGHT_PANEL_WIDTH = self.size_preset['RIGHT_PANEL_WIDTH']
        self.BOARD_WIDTH = self.size_preset['BOARD_WIDTH']
        self.HEIGHT = self.size_preset['HEIGHT']
        self.WIDTH = self.LEFT_PANEL_WIDTH + self.BOARD_WIDTH + self.RIGHT_PANEL_WIDTH
        self.ROWS, self.COLS = 8, 8
        self.SQUARE_SIZE = self.BOARD_WIDTH // self.COLS
        self.CAPTURED_PIECE_SCALE = self.size_preset['CAPTURED_PIECE_SCALE']

        self.font = pygame.font.SysFont('Arial', self.size_preset['font_size'])
        self.button_font = pygame.font.SysFont('Arial', self.size_preset['button_font_size'], bold=True)
        self.tooltip_font = pygame.font.SysFont('Arial', self.size_preset['tooltip_font_size'])
        self.notification_font = pygame.font.SysFont('Arial', self.size_preset['notification_font_size'], bold=True)
        
        self.undo_button_rect = pygame.Rect(self.LEFT_PANEL_WIDTH / 2 - 50, self.HEIGHT / 2 - 20, 100, 40)
        
        button_y = 10
        button_size = 30
        self.small_button_rect = pygame.Rect(self.LEFT_PANEL_WIDTH + self.BOARD_WIDTH + 10, button_y, button_size, button_size)
        self.medium_button_rect = pygame.Rect(self.LEFT_PANEL_WIDTH + self.BOARD_WIDTH + 50, button_y, button_size, button_size)
        self.large_button_rect = pygame.Rect(self.LEFT_PANEL_WIDTH + self.BOARD_WIDTH + 90, button_y, button_size, button_size)
        
        self._load_piece_images()

    def resize(self, size):
        self.setup_dimensions(size)
        return pygame.display.set_mode((self.WIDTH, self.HEIGHT))

    def _load_piece_images(self):
        pieces = [ 'w_pawn', 'w_rook', 'w_knight', 'w_bishop', 'w_queen', 'w_king', 'b_pawn', 'b_rook', 'b_knight', 'b_bishop', 'b_queen', 'b_king' ]
        for key in pieces:
            try:
                image = pygame.image.load(f'assets/images/{key}.png')
                self.piece_images[key] = pygame.transform.scale(image, (self.SQUARE_SIZE, self.SQUARE_SIZE))
                captured_size = int(self.SQUARE_SIZE * self.CAPTURED_PIECE_SCALE)
                self.captured_piece_images[key] = pygame.transform.scale(image, (captured_size, captured_size))
            except pygame.error:
                print(f"Warning: Could not load image for {key}.")

    def draw_left_panel(self, white_captured, black_captured):
        panel_rect = pygame.Rect(0, 0, self.LEFT_PANEL_WIDTH, self.HEIGHT)
        pygame.draw.rect(self.screen, (40, 40, 40), panel_rect)
        self.draw_captured_pieces(black_captured, 10) # Black captured pieces at the top
        # Calculate y_start for white captured pieces at the bottom
        # Assuming captured pieces are roughly CAPTURED_PIECE_SCALE * SQUARE_SIZE tall
        captured_piece_height = int(self.SQUARE_SIZE * self.CAPTURED_PIECE_SCALE)
        # Assuming maximum of 4 rows of captured pieces
        y_start_white = self.HEIGHT - 10 - (4 * (captured_piece_height + 5))
        if y_start_white < self.HEIGHT / 2 + 50: # Ensure it doesn't overlap with undo button
            y_start_white = self.HEIGHT / 2 + 50
        self.draw_captured_pieces(white_captured, y_start_white) # White captured pieces at the bottom

    def draw_right_panel(self, move_history):
        panel_rect = pygame.Rect(self.LEFT_PANEL_WIDTH + self.BOARD_WIDTH, 0, self.RIGHT_PANEL_WIDTH, self.HEIGHT)
        pygame.draw.rect(self.screen, (40, 40, 40), panel_rect)

        self.draw_size_buttons() # Draw size buttons

        title_surface = self.font.render("Move History", True, WHITE)
        self.screen.blit(title_surface, (self.LEFT_PANEL_WIDTH + self.BOARD_WIDTH + 10, 70)) # Adjusted y_offset

        white_header_surface = self.font.render("White", True, WHITE)
        self.screen.blit(white_header_surface, (self.LEFT_PANEL_WIDTH + self.BOARD_WIDTH + 10, 100)) # Adjusted y_offset
        black_header_surface = self.font.render("Black", True, WHITE)
        self.screen.blit(black_header_surface, (self.LEFT_PANEL_WIDTH + self.BOARD_WIDTH + 100, 100)) # Adjusted y_offset

        y_offset = 130 # Adjusted starting y_offset
        move_number = 1
        for move_pair in move_history:
            if y_offset > self.HEIGHT - 30: break
            if len(move_pair) > 0:
                white_move = f"{move_number}. {move_pair[0]}"
                white_move_surface = self.font.render(white_move, True, WHITE)
                self.screen.blit(white_move_surface, (self.LEFT_PANEL_WIDTH + self.BOARD_WIDTH + 10, y_offset))
            
            if len(move_pair) > 1:
                black_move = f"{move_pair[1]}"
                black_move_surface = self.font.render(black_move, True, WHITE)
                self.screen.blit(black_move_surface, (self.LEFT_PANEL_WIDTH + self.BOARD_WIDTH + 110, y_offset))
            y_offset += 25
            move_number += 1

    def draw_captured_pieces(self, captured_list, y_start):
        x_offset = 10
        y_offset = y_start
        for piece in captured_list:
            key = f"{'w' if piece.color == 'white' else 'b'}_{piece.__class__.__name__.lower()}"
            if key in self.captured_piece_images:
                self.screen.blit(self.captured_piece_images[key], (x_offset, y_offset))
                x_offset += self.captured_piece_images[key].get_width() + 5
                if x_offset > self.LEFT_PANEL_WIDTH - self.captured_piece_images[key].get_width():
                    x_offset = 10
                    y_offset += self.captured_piece_images[key].get_height() + 5
    
    def draw_board(self):
        for row in range(self.ROWS):
            for col in range(self.COLS):
                color = LIGHT_SQUARE if (row + col) % 2 == 0 else DARK_SQUARE
                pygame.draw.rect(self.screen, color, (self.LEFT_PANEL_WIDTH + col * self.SQUARE_SIZE, row * self.SQUARE_SIZE, self.SQUARE_SIZE, self.SQUARE_SIZE))

    def draw_pieces(self, board):
        for row in range(self.ROWS):
            for col in range(self.COLS):
                piece = board.get_piece(row, col)
                if piece:
                    key = f"{'w' if piece.color == 'white' else 'b'}_{piece.__class__.__name__.lower()}"
                    if key in self.piece_images:
                         self.screen.blit(self.piece_images[key], (self.LEFT_PANEL_WIDTH + col * self.SQUARE_SIZE, row * self.SQUARE_SIZE))

    def highlight_square(self, row, col, color=(255, 255, 0)):
        pygame.draw.rect(self.screen, color, (self.LEFT_PANEL_WIDTH + col * self.SQUARE_SIZE, row * self.SQUARE_SIZE, self.SQUARE_SIZE, self.SQUARE_SIZE), 5)

    def highlight_king(self, board, color):
        king_pos = board.find_king(board.turn)
        if king_pos:
            self.highlight_square(king_pos[0], king_pos[1], color)

    def highlight_keyboard_selection(self, row, col):
        pygame.draw.rect(self.screen, (0, 0, 255), (self.LEFT_PANEL_WIDTH + col * self.SQUARE_SIZE, row * self.SQUARE_SIZE, self.SQUARE_SIZE, self.SQUARE_SIZE), 3)

    def draw_possible_moves(self, moves):
        for move in moves:
            end_row, end_col = move
            pygame.draw.circle(self.screen, (0, 255, 0), (self.LEFT_PANEL_WIDTH + end_col * self.SQUARE_SIZE + self.SQUARE_SIZE // 2, end_row * self.SQUARE_SIZE + self.SQUARE_SIZE // 2), 15)

    def draw_undo_button(self):
        pygame.draw.rect(self.screen, (100, 100, 100), self.undo_button_rect)
        pygame.draw.rect(self.screen, WHITE, self.undo_button_rect, 2)
        text_surface = self.button_font.render("Undo", True, WHITE)
        text_rect = text_surface.get_rect(center=self.undo_button_rect.center)
        self.screen.blit(text_surface, text_rect)

    def draw_size_buttons(self):
        s_text = self.button_font.render("S", True, WHITE)
        m_text = self.button_font.render("M", True, WHITE)
        l_text = self.button_font.render("L", True, WHITE)

        # Draw individual buttons
        pygame.draw.rect(self.screen, (100, 100, 100) if self.size == 'small' else (50,50,50), self.small_button_rect)
        pygame.draw.rect(self.screen, (100, 100, 100) if self.size == 'medium' else (50,50,50), self.medium_button_rect)
        pygame.draw.rect(self.screen, (100, 100, 100) if self.size == 'large' else (50,50,50), self.large_button_rect)

        self.screen.blit(s_text, s_text.get_rect(center=self.small_button_rect.center))
        self.screen.blit(m_text, m_text.get_rect(center=self.medium_button_rect.center))
        self.screen.blit(l_text, l_text.get_rect(center=self.large_button_rect.center))

        # Draw border around the group of buttons
        group_rect_x = self.small_button_rect.left - 5
        group_rect_y = self.small_button_rect.top - 5
        group_rect_width = (self.large_button_rect.right - self.small_button_rect.left) + 10
        group_rect_height = self.small_button_rect.height + 10
        group_rect = pygame.Rect(group_rect_x, group_rect_y, group_rect_width, group_rect_height)
        pygame.draw.rect(self.screen, WHITE, group_rect, 2)

    def draw_tooltip(self, mouse_pos):
        if mouse_pos and self.undo_button_rect.collidepoint(mouse_pos):
            tooltip_text = "Press 'u' or Backspace"
            text_surface = self.tooltip_font.render(tooltip_text, True, BLACK)
            tooltip_rect = text_surface.get_rect(midbottom=self.undo_button_rect.midtop)
            background_rect = tooltip_rect.inflate(10, 5)
            pygame.draw.rect(self.screen, WHITE, background_rect)
            pygame.draw.rect(self.screen, BLACK, background_rect, 1)
            self.screen.blit(text_surface, tooltip_rect)

    def draw_check_notification(self):
        text_surface = self.notification_font.render("Check!", True, ORANGE_RED)
        text_rect = text_surface.get_rect(center=(self.LEFT_PANEL_WIDTH + self.BOARD_WIDTH / 2, self.HEIGHT / 2))
        self.screen.blit(text_surface, text_rect)

    def draw_checkmate_notification(self, winner):
        overlay = pygame.Surface((self.BOARD_WIDTH, self.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (self.LEFT_PANEL_WIDTH, 0))

        game_over_text = self.notification_font.render("Game Over", True, RED)
        game_over_rect = game_over_text.get_rect(center=(self.LEFT_PANEL_WIDTH + self.BOARD_WIDTH / 2, self.HEIGHT / 2 - 30))
        self.screen.blit(game_over_text, game_over_rect)

        if winner != "draw":
            winner_text_str = f"{winner.capitalize()} wins!"
        else:
            winner_text_str = "It's a draw!"
        winner_text = self.font.render(winner_text_str, True, WHITE)
        winner_rect = winner_text.get_rect(center=(self.LEFT_PANEL_WIDTH + self.BOARD_WIDTH / 2, self.HEIGHT / 2 + 30))
        self.screen.blit(winner_text, winner_rect)

    def update_display(self, board, selected_piece=None, possible_moves=[], mouse_pos=None, is_check=False, game_over_winner=None, keyboard_cursor_pos=None):
        self.screen.fill(BLACK)
        self.draw_left_panel(board.white_captured, board.black_captured)
        self.draw_right_panel(board.move_log)
        self.draw_board()
        self.draw_pieces(board)
        
        if keyboard_cursor_pos:
            self.highlight_keyboard_selection(keyboard_cursor_pos[0], keyboard_cursor_pos[1])

        if selected_piece:
            r, c = selected_piece
            self.highlight_square(r, c)
            self.draw_possible_moves(possible_moves)
        
        self.draw_undo_button()
        self.draw_tooltip(mouse_pos)

        if is_check:
            self.draw_check_notification()
            self.highlight_king(board, ORANGE_RED)

        if game_over_winner:
            self.draw_checkmate_notification(game_over_winner)
            self.highlight_king(board, RED)

        pygame.display.update()