# numpy
import numpy as np

# AIMA
from aima.games import Game

# Board class
from board import Board

# utils
from utils import Pawn

# heuristics
from whiteheuristics import white_fitness


class Tablut(Game):
    def __init__(self, player, pieces, height=9, width=9):
        self.initial = Board(height=height, width=width,
                             to_move='WHITE', utility=0)
        self.to_move = player

        self.width = width
        self.height = height

    def update_state(self, pieces, turn):
        # Update board state
        self.initial.pieces = pieces
        self.initial.to_move = turn
        self.to_move = turn

        # Update pawns coordinates
        self.initial.get_white()
        self.initial.get_black()
        self.initial.get_king()

        # Get the current player and compute the list of possible moves
        if turn == 'WHITE':
            self.squares = [[x, (k, l)] for x in self.initial.white for k in range(
                self.width) for l in range(self.height)]
        elif turn == 'BLACK':
            self.squares = [[x, (k, l)] for x in self.initial.black for k in range(
                self.width) for l in range(self.height)]

    def is_capture(self, from_pos, to_pos, player_pieces):
        from_row, from_col = from_pos
        to_row, to_col = to_pos

        # Check if the move captures a piece
        if from_col == to_col:  # Vertical capture
            captured_pos = ((from_row + to_row) // 2, from_col)
        elif from_row == to_row:  # Horizontal capture
            captured_pos = (from_row, (from_col + to_col) // 2)
        else:
            return False

        return captured_pos in player_pieces

    def actions(self, board) -> set:

        white = board.white
        black = board.black
        king = board.king

        # Get the current player
        player = board.to_move

        # print("White pieces:", white)

        # Get the list of the opponent pieces
        opponent_pieces = black if player == 'WHITE' else white
        # print("Opponent pieces:", opponent_pieces)

        # Get the list of the current player pieces
        player_pieces = white if player == 'WHITE' else black

        # Get the list of the king
        king_pieces = king

        # Get the list of the occupied squares in coordinates (x, y)
        occupied_squares = np.argwhere(
            (board.pieces == Pawn.WHITE.value) | (board.pieces == Pawn.BLACK.value) | (board.pieces == Pawn.KING.value))

        # Get the list of the occupied squares in coordinates (x, y)
        occupied_squares = set(map(tuple, occupied_squares))
        # throne is always an occupied square (even if it is empty) | you can't go through it
        occupied_squares.add((4, 4))

        # Initialize forbidden moves set
        forbidden_moves = set()

        # Starting position (tuple) and ending position (tuple)
        for move in self.squares:
            from_pos = move[0]
            from_row, from_col = from_pos
            to_pos = move[1]
            to_row, to_col = to_pos

            # Forbidden moves
            forbidden_moves.add((from_pos, (4, 4)))  # throne

            for occ_place in occupied_squares:
                forbidden_moves.add(
                    (from_pos, occ_place))  # occupied squares
                forbidden_moves.add((occ_place, occ_place))

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

            for i in range(1, self.width):
                if from_col - i >= 0:
                    if flags[0] or (from_row, from_col - i) in occupied_squares:
                        flags[0] = True
                        forbidden_moves.add((from_pos, (from_row, from_col-i)))
                if from_row - i >= 0:
                    if flags[1] or (from_row - i, from_col) in occupied_squares:
                        flags[1] = True
                        forbidden_moves.add((from_pos, (from_row-1, from_col)))
                if from_col + i < self.width:
                    if flags[2] or (from_row, from_col + i) in occupied_squares:
                        flags[2] = True
                        forbidden_moves.add(
                            (from_pos, (from_row, from_col + i)))
                if from_row + i < self.width:
                    if flags[3] or (from_row + i, from_col) in occupied_squares:
                        flags[3] = True
                        forbidden_moves.add(
                            (from_pos, (from_row + i, from_col)))

            # Barrack's check
            # TODO: check if this notation (the coords) is correct
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
            # If i move from outside a barrack inside a barrack, that move is invalid. But i can move freely move inside barracks
            for barrack in barracks:
                if from_pos not in barrack and to_pos in barrack:
                    forbidden_moves.add((from_pos, to_pos))

        # test
        # banned_move = ((4, 8), (0, 8))
        # forbidden_moves.add(banned_move)
        # print(self.convert_move(banned_move))

        # return difference between all possible moves and forbidden moves (list of tuples)
        total_moves = set(tuple(tuple(k) for k in h)
                          for h in self.squares)

        allowed_moves = total_moves - forbidden_moves

        return allowed_moves

    def result(self, board, move):
        """Place a marker for current player on square."""
        player = board.to_move
        board.to_move = 'BLACK' if player == 'WHITE' else 'WHITE'
        win = self.check_win(board)
        board.utility = self.compute_utility(board, win)
        return board

    def utility(self, board, player):
        """Return the value to player; 1 for win, -1 for loss, 0 otherwise."""
        return board.utility if player == 'WHITE' else -board.utility

    def terminal_test(self, board):
        """A board is a terminal state if it is won or there are no empty squares."""
        return board.utility != 0

    def compute_utility(self, board, win: bool) -> float:
        """
        Compute the utility of the board for the current state. Some states are more desirable than others. For example, it is better to win in 2 moves than 3 moves. The utility function assigns a score to the board. The higher the score, the more desirable the state. The utility function is a linear combination of the following features... # TODO
        """
        if win:
            return 99999  # Winning state

        # Heuristic weights
        alpha0 = 1  # Adjust these weights as needed
        beta0 = 1
        gamma0 = 1

        # Additional heuristics
        fitness = white_fitness(board, alpha0, beta0,
                                gamma0, theta0=0, epsilon0=0)

        return fitness

    def check_win(self, board):
        """
        End of game:
        - King captured (BLACK wins)
        - King escaped (WHITE wins)
        - A player can’t move any checker in any direction: that player loses
        - The same "state" of the game is reached twice: draw
        """

        white_pieces = board.white
        black_pieces = board.black
        king_pieces = board.king[0]

        # TODO Check if the king is captured
        if len(king_pieces) == 0:
            return True

        # @Teddy XXX: I'm assuming that king_pieces is in the form (x, y)
        if king_pieces[0] == self.width-1 or king_pieces[1] == self.width-1 or king_pieces[0] == 0 or king_pieces[1] == 0:
            # @Teddy XXX: Do i have to return True or False if white wins?
            return True

        # TODO Check if the king is surrounded
        # @Teddy: Isn't this redundant? We already check if the king is alive or dead

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
