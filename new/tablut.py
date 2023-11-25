import copy

# numpy
import numpy as np

# AIMA
from aima.games import Game

# Board class
from board import Board

# utils
from utils import Pawn

# heuristics
from whiteheuristics import white_fitness, white_fitness_dynamic
from blackheuristics import black_fitness_dynamic


class Tablut(Game):
    def __init__(self, height: int = 9, width: int = 9):
        self.initial = Board(height=height, width=width,
                             to_move='WHITE', utility=0)

        self.width = width
        self.height = height

    def copy_and_modify(self, to_move, utility):
        copied_tablut = copy.copy(self)

        copied_tablut.initial.to_move = to_move
        copied_tablut.initial.utility = utility

        return copied_tablut

    def update_state(self, pieces, turn):
        # Update board state
        self.initial.pieces = pieces
        self.initial.to_move = turn
        self.to_move = turn

        # Update pawns coordinates
        white_pos = self.initial.get_white()
        black_pos = self.initial.get_black()
        king_pos = self.initial.get_king()

        # White has also the king
        white_pos.append(king_pos)

        # Get the current player and compute the list of possible moves
        if turn == 'WHITE':
            self.squares = [[x, (k, l)] for x in white_pos if x is not None for k in range(
                self.width) for l in range(self.height)]
        elif turn == 'BLACK':
            self.squares = [[x, (k, l)] for x in black_pos if x is not None for k in range(
                self.width) for l in range(self.height)]

        # print("White:", white_pos)
        # print("Black:", black_pos)

        self.initial.moves = self.actions(self.initial)
        self.black_moves_to_eat_king = self.eat_king_in_castle()

    def move(self, state, move):
        """
        Applies the given move to the board and returns the new board state.

        Args:
            board (Board): The current board state.
            move (tuple): The move to be applied, represented as a tuple of two positions.

        Returns:
            Board: The new board state after applying the move.
        """
        # Extract the starting and ending position from the move
        from_pos, to_pos = move
        x1, y1 = from_pos
        x2, y2 = to_pos

        board = state.initial

        # Get the pawn type
        pawn_type = board.pieces[x1][y1]

        # Remove the pawn from the starting position and add it to the ending position
        board.pieces[x1][y1] = Pawn.EMPTY.value
        board.pieces[x2][y2] = pawn_type

        # Check if there are any captures (important otherwise heuristics won't work)
        board.check_attacks(x2, y2)
        board.eat_black()
        # print(board.pieces)

        return board

    def actions(self, board) -> set:
        # TODO "mossa che scavalca una citadel è vietata"

        white = board.get_white()
        black = board.get_black()
        throne = [(4, 4)]

        # Get the current player
        player = board.to_move

        # print("White pieces:", white)

        # Get the list of the opponent pieces
        if player == 'WHITE':
            player_pieces = white
            opponent_pieces = black

        elif player == 'BLACK':
            player_pieces = black
            opponent_pieces = white

        # Get the list of the occupied squares in coordinates (x, y)
        # occupied_squares = np.argwhere(
        #    (board.pieces == Pawn.WHITE.value) | (board.pieces == Pawn.BLACK.value) | (board.pieces == Pawn.KING.value))

        # Occupied squares as the set of tuples of white, black and king pieces
        occupied_squares = player_pieces + opponent_pieces + throne

        # Get the list of the occupied squares in coordinates (x, y)
        occupied_squares = set(map(tuple, occupied_squares))
        # throne is always an occupied square (even if it is empty) | you can't go through it

        # Initialize forbidden moves set
        forbidden_moves = set()

        # Starting position (tuple) and ending position (tuple)
        for move in self.squares:
            from_pos = move[0]
            try:
                from_row, from_col = from_pos
            except TypeError:
                print(f"Something went wrong with the {move = }")
            to_pos = move[1]
            to_row, to_col = to_pos

            for occ_place in occupied_squares:
                forbidden_moves.add(
                    (from_pos, occ_place))  # occupied squares

            forbidden_moves.add((from_pos, from_pos))  # starting position

            # Can't move enemy's pawn
            if from_pos in opponent_pieces:
                forbidden_moves.add((from_pos, to_pos))

            # remove diagonal moves
            if from_row != to_row and from_col != to_col:
                forbidden_moves.add((from_pos, to_pos))

            # remove moves which implies jumping over a piece
            # The idea is to check in a "circular" way the perimeter around the piece
            # So it only needs one for-loop.
            # If flags are not set, the move is legal. If the flag is set (= i'm on a piece or over it)
            # Add the move to the forbiddens one

            flags = [
                False,
                False,
                False,
                False
            ]

            # If i move from outside a barrack inside a barrack, that move is invalid. But i can move freely move inside barracks
            from utils import RED, RED2
            for i in range(1, self.width):
                if from_col - i >= 0:
                    if (flags[0] or (from_row, from_col - i) in occupied_squares) or \
                            (board.board[from_row][from_col] not in (RED, RED2) and board.board[from_row][from_col - i] in (RED, RED2)):

                        flags[0] = True
                        forbidden_moves.add(
                            (from_pos, (from_row, from_col - i)))

                if from_row - i >= 0:
                    if flags[1] or (from_row - i, from_col) in occupied_squares or \
                            (board.board[from_row][from_col] not in (RED, RED2) and board.board[from_row - i][from_col] in (RED, RED2)):

                        flags[1] = True
                        forbidden_moves.add(
                            (from_pos, (from_row - i, from_col)))

                if from_col + i < self.width:
                    if flags[2] or (from_row, from_col+i) in occupied_squares or \
                            (board.board[from_row][from_col] not in (RED, RED2) and board.board[from_row][from_col + i] in (RED, RED2)):

                        flags[2] = True
                        forbidden_moves.add(
                            (from_pos, (from_row, from_col+i)))

                if from_row + i < self.width:
                    if flags[3] or (from_row + i, from_col) in occupied_squares or \
                            (board.board[from_row][from_col] not in (RED, RED2) and board.board[from_row + i][from_col] in (RED, RED2)):

                        flags[3] = True
                        forbidden_moves.add(
                            (from_pos, (from_row + i, from_col)))

            # Barrack's check
            barracks = (
                (
                    (0, 3),
                    (0, 4),
                    (0, 5),
                    (1, 4)
                ),
                (
                    (3, 0),
                    (4, 0),
                    (5, 0),
                    (4, 1)
                ),
                (
                    (self.width-1, 3),
                    (self.width-1, 4),
                    (self.width-1, 5),
                    (self.width-2, 4)
                ),
                (
                    (3, self.width-1),
                    (4, self.width-1),
                    (5, self.width-1),
                    (4, self.width-2),
                )
            )

        # return difference between all possible moves and forbidden moves (list of tuples)
        total_moves = set(tuple(tuple(k) for k in h)
                          for h in self.squares)

        allowed_moves = total_moves - forbidden_moves

        return allowed_moves

    def result(self, state, move):
        # Copy the board
        board = self.copy_and_modify(
            state.to_move, state.utility)

        # Apply the move locally and check for captures
        new_board = self.move(board, move)

        # Modify the to_move attribute
        new_board.to_move = ("BLACK" if state.to_move == "WHITE" else "WHITE")

        board.update_state(new_board.pieces, new_board.to_move)

        win = self.terminal_test(new_board)

        # Compute the utility of the board
        fitness = self.compute_utility(
            new_board, move, player=new_board.to_move)

        # Update the utility of the board
        new_board.utility = (
            0 if not win else fitness if new_board.to_move == 'WHITE' else -fitness)

        # return the new board
        return new_board

    def utility(self, board, player):
        """Return the value to player; 1 for win, -1 for loss, 0 otherwise."""
        return board.utility if player == 'WHITE' else -board.utility

    def terminal_test(self, board):
        # Check if it is a winning move or if there are no more starting positions (no more moves)
        return self.check_win(board)

    def compute_utility(self, board, move, player) -> float:
        """
        Compute the utility of the board for the current state. Some states are more desirable than others. For example, it is better to win in 2 moves than 3 moves. The utility function assigns a score to the board. The higher the score, the more desirable the state. The utility function is a linear combination of the following features... # TODO
        """

        # if player == 'WHITE':
        # Heuristic weights
        alpha0 = 5  # Adjust these weights as needed
        beta0 = 0.04
        gamma0 = -1000

        # Additional heuristics
        fitness = white_fitness(board, alpha0, beta0,
                                gamma0, theta0=0, epsilon0=1)
        print(f"Fitness: {fitness}")
        return fitness

    def check_win(self, board):
        """
        End of game:
        - King captured (BLACK wins)
        - King escaped (WHITE wins)
        - A player can’t move any checker in any direction: that player loses
        - The same "state" of the game is reached twice: draw
        """

        white_pieces = board.whites
        black_pieces = board.blacks
        king_pieces = board.get_king()

        # No more white pawns
        if len(white_pieces) == 0:
            return True

        # No more black pawns
        if len(black_pieces) == 0:
            return True

        # King is dead (captured)
        if king_pieces is None:
            return True  # king is dead

        # King escaped
        if king_pieces[0] == self.width-1 or king_pieces[1] == self.width-1 or king_pieces[0] == 0 or king_pieces[1] == 0:
            # @Teddy XXX: Do i have to return True or False if white wins?
            return True

        return False

    def convert_move(self, move):
        # TODO check if it is consistent with server board representation
        """Convert move to (A1, A2) format
        Move: ((x1, y1), (x2, y2))
        Example: ((3,0), (3,3))
        Convert to: (D1, D4)"""

        cols = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']

        from_pos = move[0]
        from_row, from_col = from_pos

        to_pos = move[1]
        to_row, to_col = to_pos

        from_letter = cols[from_row]
        to_letter = cols[to_row]

        new_from_col = from_col + 1
        new_to_col = to_col + 1

        return (from_letter+str(new_from_col), to_letter+str(new_to_col))

    def display(self, board):
        board.display()

    # Black heuristics
    def moves_to_eat_king(self):
        '''
        If the king can be eaten, self.black_moves_to_eat_king is set to a list of initial and final position of the white piece that eats
        Otherwise, self.black_moves_to_eat_king is set to [[-1,-1], [-1,-1]]
        '''

        if self.initial.get_king() == (4, 4):
            self.black_moves_to_eat_king = self.eat_king_in_castle()
        else:
            self.black_moves_to_eat_king = self.eat_king_outside_castle()

    def eat_king_in_castle(self):
        '''
        It returns starting and ending position of the piece that can eat the king, otherwise it returns [-1,-1], [-1,-1]
        '''
        position = self.check_sourrounded_king_castle()
        if position == [-1, -1]:
            return [[-1, -1], [-1, -1]]
        for black in self.initial.blacks:
            if ((black[0], black[1]), (position[0], position[1])) in self.initial.moves:
                return black, position
        return [[-1, -1], [-1, -1]]

    def check_sourrounded_king_castle(self):
        '''
        It returns the coordinates of one of the four tiles around the king, if the other three are occupied by three blacks
        It returns [-1,-1] if the king is not sorrounded or he's not in the castle
        '''
        if self.initial.pieces[4][3] == 1 and self.initial.pieces[3][4] == 1 and self.initial.pieces[4][5] == 1:
            return [5, 4]
        if self.initial.pieces[4][3] == 1 and self.initial.pieces[5][4] == 1 and self.initial.pieces[4][5] == 1:
            return [3, 4]
        if self.initial.pieces[5][4] == 1 and self.initial.pieces[3][4] == 1 and self.initial.pieces[4][5] == 1:
            return [4, 3]
        if self.initial.pieces[4][3] == 1 and self.initial.pieces[3][4] == 1 and self.initial.pieces[5][4] == 1:
            return [4, 5]
        return [-1, -1]

    def check_sourrounded_king_outside(self):
        '''
        It returns a list of possible moves to eat the king, when he's outside the castle
        If there isn't any feasable move, it returns [-1,-1]
        '''
        r, c = self.initial.get_king()
        tiles = []
        if self.initial.pieces[r][c-1] == 1:
            tiles.append([r, c+1])
        elif self.initial.pieces[r][c+1] == 1:
            tiles.append([r, c-1])
        if self.initial.pieces[r-1][c] == 1:
            tiles.append([r+1][c])
        elif self.initial.pieces[r+1][c] == 1:
            tiles.append([r-1][c])
        return tiles if len(tiles) > 0 else [-1, -1]

    def eat_king_outside_castle(self):
        '''
        It returns starting and ending position of the piece that can eat the king, otherwise it returns [[-1,-1], [-1,-1]]
        '''
        position = self.check_sourrounded_king_outside()
        if position == [-1, -1]:
            return [[-1, -1], [-1, -1]]
        for black in self.initial.blacks:
            if ((black[0], black[1]), (position[0][0], position[0][1])) in self.initial.moves:
                return [black, [position[0][0], position[0][1]]]
            if len(position) == 2 and ((black[0], black[1]), (position[1][0], position[1][1])) in self.initial.moves:
                return [black, [position[1][0], position[1][1]]]
        return [[-1, -1], [-1, -1]]
