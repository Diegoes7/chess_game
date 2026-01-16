import pygame
from models import Board
from gui import GUI

def get_row_col_from_mouse(pos, gui):
    x, y = pos
    row = y // gui.SQUARE_SIZE
    col = (x - gui.LEFT_PANEL_WIDTH) // gui.SQUARE_SIZE
    return row, col

def main():
    pygame.init()
    gui = GUI(None, "medium") # Initialize GUI with default medium size
    screen = pygame.display.set_mode((gui.WIDTH, gui.HEIGHT))
    gui.screen = screen # Set the screen for the gui object
    pygame.display.set_caption("Chess")

    board = Board()
    gui = GUI(screen)

    selected_piece = None # Tuple (row, col)
    possible_moves = []
    is_check = False
    game_over_winner = None
    game_over = False
    keyboard_cursor_pos = (0, 0)

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if not game_over:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    
                    # Check if the undo button was clicked
                    if gui.undo_button_rect.collidepoint(pos):
                        if board.undo_move():
                            selected_piece = None
                            possible_moves = []
                            is_check = board.is_in_check(board.turn)
                            print("Last move undone.")
                        else:
                            print("No moves to undo.")
                        continue

                    # Check if a size button was clicked
                    if gui.small_button_rect.collidepoint(pos):
                        screen = gui.resize("small")
                        gui.screen = screen
                        selected_piece = None
                        possible_moves = []
                        continue
                    elif gui.medium_button_rect.collidepoint(pos):
                        screen = gui.resize("medium")
                        gui.screen = screen
                        selected_piece = None
                        possible_moves = []
                        continue
                    elif gui.large_button_rect.collidepoint(pos):
                        screen = gui.resize("large")
                        gui.screen = screen
                        selected_piece = None
                        possible_moves = []
                        continue

                    row, col = get_row_col_from_mouse(pos, gui)

                    # Add boundary check here
                    if not (0 <= row < gui.ROWS and 0 <= col < gui.COLS):
                        selected_piece = None # Clear any selection if clicked outside
                        possible_moves = []
                        continue # Ignore clicks outside the board

                    if selected_piece:
                        end_pos_alg = board._coords_to_algebraic(row, col)
                        start_pos_alg = board._coords_to_algebraic(selected_piece[0], selected_piece[1])
                        
                        if board.move_piece(start_pos_alg, end_pos_alg):
                            previous_turn = board.turn
                            board.switch_turn() # Switch turn only if a valid move is made
                            
                            is_check = board.is_in_check(board.turn)

                            # Check for checkmate/stalemate for the *new* current player
                            if board.is_checkmate(board.turn):
                                game_over = True
                                game_over_winner = previous_turn
                                print(f"Checkmate! {board.turn.capitalize()} loses.")
                            elif board.is_stalemate(board.turn):
                                game_over = True
                                game_over_winner = "draw"
                                print("Stalemate! It's a draw.")
                        
                        selected_piece = None
                        possible_moves = []
                    else:
                        piece = board.get_piece(row, col)
                        if piece and piece.color == board.turn:
                            selected_piece = (row, col)
                            # Generate and store possible moves by filtering all possible moves
                            all_moves = board.get_all_possible_moves(piece.color)
                            possible_moves = []
                            start_pos_alg_selected = board._coords_to_algebraic(row, col)
                            for start_pos_alg, end_pos_alg in all_moves:
                                if start_pos_alg == start_pos_alg_selected:
                                    r_end, c_end = board._algebraic_to_coords(end_pos_alg)
                                    possible_moves.append((r_end, c_end))
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_u or event.key == pygame.K_BACKSPACE:
                        if board.undo_move():
                            selected_piece = None
                            possible_moves = []
                            is_check = board.is_in_check(board.turn)
                            print("Last move undone.")
                        else:
                            print("No moves to undo.")
                    elif event.key == pygame.K_UP:
                        keyboard_cursor_pos = (max(0, keyboard_cursor_pos[0] - 1), keyboard_cursor_pos[1])
                    elif event.key == pygame.K_DOWN:
                        keyboard_cursor_pos = (min(7, keyboard_cursor_pos[0] + 1), keyboard_cursor_pos[1])
                    elif event.key == pygame.K_LEFT:
                        keyboard_cursor_pos = (keyboard_cursor_pos[0], max(0, keyboard_cursor_pos[1] - 1))
                    elif event.key == pygame.K_RIGHT:
                        keyboard_cursor_pos = (keyboard_cursor_pos[0], min(7, keyboard_cursor_pos[1] + 1))
                    elif event.key == pygame.K_RETURN:
                        row, col = keyboard_cursor_pos
                        if selected_piece:
                            end_pos_alg = board._coords_to_algebraic(row, col)
                            start_pos_alg = board._coords_to_algebraic(selected_piece[0], selected_piece[1])
                            
                            if board.move_piece(start_pos_alg, end_pos_alg):
                                previous_turn = board.turn
                                board.switch_turn()
                                
                                is_check = board.is_in_check(board.turn)

                                if board.is_checkmate(board.turn):
                                    game_over = True
                                    game_over_winner = previous_turn
                                elif board.is_stalemate(board.turn):
                                    game_over = True
                                    game_over_winner = "draw"
                            
                            selected_piece = None
                            possible_moves = []
                        else:
                            piece = board.get_piece(row, col)
                            if piece and piece.color == board.turn:
                                selected_piece = (row, col)
                                all_moves = board.get_all_possible_moves(piece.color)
                                possible_moves = []
                                start_pos_alg_selected = board._coords_to_algebraic(row, col)
                                for start_pos_alg, end_pos_alg in all_moves:
                                    if start_pos_alg == start_pos_alg_selected:
                                        r_end, c_end = board._algebraic_to_coords(end_pos_alg)
                                        possible_moves.append((r_end, c_end))

        gui.update_display(board, selected_piece, possible_moves, mouse_pos, is_check, game_over_winner, keyboard_cursor_pos)

    pygame.quit()

if __name__ == "__main__":
    main()
