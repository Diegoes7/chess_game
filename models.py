import copy

class Board:
    def __init__(self):
        self.board = self._create_board()
        self.turn = "white"
        self.history = [] # Added for undo functionality
        self.move_log = [] # Added for move history
        self.white_captured = []
        self.black_captured = []
        self._populate_board()

    def _create_board(self):
        board = []
        for _ in range(8):
            board.append([None] * 8)
        return board

    def _populate_board(self):
        # White pieces
        self.board[7][0] = Rook("white")
        self.board[7][1] = Knight("white")
        self.board[7][2] = Bishop("white")
        self.board[7][3] = Queen("white")
        self.board[7][4] = King("white")
        self.board[7][5] = Bishop("white")
        self.board[7][6] = Knight("white")
        self.board[7][7] = Rook("white")
        for i in range(8):
            self.board[6][i] = Pawn("white")

        # Black pieces
        self.board[0][0] = Rook("black")
        self.board[0][1] = Knight("black")
        self.board[0][2] = Bishop("black")
        self.board[0][3] = Queen("black")
        self.board[0][4] = King("black")
        self.board[0][5] = Bishop("black")
        self.board[0][6] = Knight("black")
        self.board[0][7] = Rook("black")
        for i in range(8):
            self.board[1][i] = Pawn("black")

    def display(self):
        print("  a b c d e f g h")
        for i, row in enumerate(self.board):
            row_str = f"{8 - i} "
            for piece in row:
                if piece:
                    row_str += piece.symbol + " "
                else:
                    row_str += ". "
            print(row_str)
        print(f"Turn: {self.turn.capitalize()}")

    def get_piece(self, row, col):
        return self.board[row][col]

    def _algebraic_to_coords(self, algebraic_notation):
        col = ord(algebraic_notation[0]) - ord('a')
        row = 8 - int(algebraic_notation[1])
        return row, col
    
    def _coords_to_algebraic(self, row, col):
        return f"{chr(ord('a') + col)}{8 - row}"

    def switch_turn(self):
        self.turn = "black" if self.turn == "white" else "white"

    def undo_move(self):
        if self.history:
            previous_state = self.history.pop()
            self.board = previous_state['board_layout']
            self.turn = previous_state['current_turn']
            self.white_captured = previous_state['white_captured']
            self.black_captured = previous_state['black_captured']
            
            # Also undo the move log
            if self.move_log:
                if len(self.move_log[-1]) == 2:
                    self.move_log[-1].pop()
                else:
                    self.move_log.pop()
            return True
        return False

    def find_king(self, color):
        for r, row in enumerate(self.board):
            for c, piece in enumerate(row):
                if isinstance(piece, King) and piece.color == color:
                    return r, c
        return None

    def is_in_check(self, color):
        king_pos = self.find_king(color)
        if not king_pos:
            return False
        
        king_row, king_col = king_pos
        opponent_color = "black" if color == "white" else "white"

        for r, row in enumerate(self.board):
            for c, piece in enumerate(row):
                if piece and piece.color == opponent_color:
                    if piece.is_valid_move(self, r, c, king_row, king_col):
                        return True
        return False

    def get_all_possible_moves(self, color):
        moves = []
        for r_start, row in enumerate(self.board):
            for c_start, piece in enumerate(row):
                if piece and piece.color == color:
                    for r_end in range(8):
                        for c_end in range(8):
                            board_copy = copy.deepcopy(self)
                            start_pos_alg = board_copy._coords_to_algebraic(r_start, c_start)
                            end_pos_alg = board_copy._coords_to_algebraic(r_end, c_end)
                            if board_copy.move_piece(start_pos_alg, end_pos_alg):
                                moves.append((start_pos_alg, end_pos_alg))
        return moves
    
    def is_checkmate(self, color):
        return self.is_in_check(color) and not self.get_all_possible_moves(color)

    def is_stalemate(self, color):
        return not self.is_in_check(color) and not self.get_all_possible_moves(color)

    def move_piece(self, start_pos, end_pos):
        start_row, start_col = self._algebraic_to_coords(start_pos)
        end_row, end_col = self._algebraic_to_coords(end_pos)

        piece = self.get_piece(start_row, start_col)
        if piece and piece.color == self.turn and piece.is_valid_move(self, start_row, start_col, end_row, end_col):
            # Save the current state for the undo feature
            current_state = {
                'board_layout': copy.deepcopy(self.board),
                'current_turn': self.turn,
                'white_captured': list(self.white_captured),
                'black_captured': list(self.black_captured),
            }
            self.history.append(current_state)

            # Check if move puts own king in check
            board_copy = copy.deepcopy(self)
            board_copy.board[end_row][end_col] = board_copy.board[start_row][start_col]
            board_copy.board[start_row][start_col] = None
            if board_copy.is_in_check(self.turn):
                # If the move is invalid, remove the saved state
                self.history.pop()
                return False

            # Check for capture
            captured_piece = self.get_piece(end_row, end_col)
            if captured_piece:
                if captured_piece.color == 'white':
                    self.black_captured.append(captured_piece)
                else:
                    self.white_captured.append(captured_piece)

            self.board[end_row][end_col] = piece
            self.board[start_row][start_col] = None
            piece.has_moved = True
            
            # Log the move
            move_string = f"{start_pos}{end_pos}"
            if self.turn == "white":
                self.move_log.append([move_string])
            else: # Black's move
                if self.move_log and len(self.move_log[-1]) == 1:
                    self.move_log[-1].append(move_string)
                else: # Should not happen, but as a fallback
                    self.move_log.append(['...', move_string])

            piece.has_moved = True
            return True
        return False
        
class Piece:
    def __init__(self, color):
        self.color = color
        self.has_moved = False

    def __repr__(self):
        return f"{self.color} {self.__class__.__name__}"

    def is_valid_move(self, board, start_row, start_col, end_row, end_col):
        # Base implementation: pieces don't move by default
        return False

class Pawn(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.symbol = "♙" if color == "white" else "♟"

    def is_valid_move(self, board, start_row, start_col, end_row, end_col):
        direction = -1 if self.color == "white" else 1
        
        # Standard one-square move
        if start_col == end_col and start_row + direction == end_row and board.get_piece(end_row, end_col) is None:
            return True

        # Initial two-square move
        if not self.has_moved and start_col == end_col and start_row + 2 * direction == end_row and board.get_piece(end_row, end_col) is None:
            if board.get_piece(start_row + direction, start_col) is None:
                return True

        # Capture move
        if abs(start_col - end_col) == 1 and start_row + direction == end_row:
            target_piece = board.get_piece(end_row, end_col)
            if target_piece and target_piece.color != self.color:
                return True

        return False


class Rook(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.symbol = "♖" if color == "white" else "♜"

    def is_valid_move(self, board, start_row, start_col, end_row, end_col):
        if start_row != end_row and start_col != end_col:
            return False

        target_piece = board.get_piece(end_row, end_col)
        if target_piece and target_piece.color == self.color:
            return False

        if start_row == end_row:
            step = 1 if end_col > start_col else -1
            for col in range(start_col + step, end_col, step):
                if board.get_piece(start_row, col) is not None:
                    return False
        else:
            step = 1 if end_row > start_row else -1
            for row in range(start_row + step, end_row, step):
                if board.get_piece(row, start_col) is not None:
                    return False
        
        return True

class Knight(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.symbol = "♘" if color == "white" else "♞"

    def is_valid_move(self, board, start_row, start_col, end_row, end_col):
        row_diff = abs(start_row - end_row)
        col_diff = abs(start_col - end_col)

        if not ((row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2)):
            return False

        target_piece = board.get_piece(end_row, end_col)
        if target_piece and target_piece.color == self.color:
            return False

        return True

class Bishop(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.symbol = "♗" if color == "white" else "♝"

    def is_valid_move(self, board, start_row, start_col, end_row, end_col):
        if abs(start_row - end_row) != abs(start_col - end_col):
            return False

        target_piece = board.get_piece(end_row, end_col)
        if target_piece and target_piece.color == self.color:
            return False

        row_step = 1 if end_row > start_row else -1
        col_step = 1 if end_col > start_col else -1
        current_row, current_col = start_row + row_step, start_col + col_step
        while current_row != end_row:
            if board.get_piece(current_row, current_col) is not None:
                return False
            current_row += row_step
            current_col += col_step
            
        return True

class Queen(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.symbol = "♕" if color == "white" else "♛"

    def is_valid_move(self, board, start_row, start_col, end_row, end_col):
        is_diagonal = abs(start_row - end_row) == abs(start_col - end_col)
        is_straight = start_row == end_row or start_col == end_col
        if not (is_diagonal or is_straight):
            return False

        target_piece = board.get_piece(end_row, end_col)
        if target_piece and target_piece.color == self.color:
            return False

        if is_straight:
            if start_row == end_row:
                step = 1 if end_col > start_col else -1
                for col in range(start_col + step, end_col, step):
                    if board.get_piece(start_row, col) is not None:
                        return False
            else:
                step = 1 if end_row > start_row else -1
                for row in range(start_row + step, end_row, step):
                    if board.get_piece(row, start_col) is not None:
                        return False
        else:
            row_step = 1 if end_row > start_row else -1
            col_step = 1 if end_col > start_col else -1
            current_row, current_col = start_row + row_step, start_col + col_step
            while current_row != end_row:
                if board.get_piece(current_row, current_col) is not None:
                    return False
                current_row += row_step
                current_col += col_step
        
        return True

class King(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.symbol = "♔" if color == "white" else "♚"

    def is_valid_move(self, board, start_row, start_col, end_row, end_col):
        row_diff = abs(start_row - end_row)
        col_diff = abs(start_col - end_col)

        if row_diff > 1 or col_diff > 1:
            return False

        target_piece = board.get_piece(end_row, end_col)
        if target_piece and target_piece.color == self.color:
            return False
            
        # Check if the move puts the king in check
        board_copy = copy.deepcopy(board)
        board_copy.board[end_row][end_col] = board_copy.board[start_row][start_col]
        board_copy.board[start_row][start_col] = None
        if board_copy.is_in_check(self.color):
            return False
        
        return True
