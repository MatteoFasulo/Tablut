import copy
import random

# numpy
import numpy as np

# AIMA
from aima.games import Game

# Board class
from board import Board

# utils
from utils import Pawn

# heuristics
from whiteheuristics import white_fitness  # white_fitness_dynamic
from blackheuristics import black_fitness  # black_fitness_dynamic


class Tablut(Game):
    def __init__(self, height: int = 9, width: int = 9):
        """
        Initializes a Tablut game object.

        Parameters:
        - height (int): The height of the game board. Default is 9.
        - width (int): The width of the game board. Default is 9.
        """
        self.initial = Board(height=height, width=width,
                             to_move='WHITE', utility=0)

        self.width = width
        self.height = height

    def update_state(self, pieces, turn):
        """
        Update the state of the board.

        Args:
            pieces (list): The positions of the pieces on the board.
            turn (str): The current turn ('WHITE' or 'BLACK').

        Returns:
            None
        """
        # Update board state
        self.initial.pieces = pieces
        self.initial.to_move = turn
        self.to_move = turn

        # Update pawns coordinates
        white_pos = self.initial.get_white()
        black_pos = self.initial.get_black()
        king_pos = self.initial.get_king()

        # Shuffle the list of possible moves
        # random.shuffle(white_pos)
        # random.shuffle(black_pos)

        # White has also the king
        white_pos.insert(0, king_pos)

        # Get the current player and compute the list of possible moves
        if turn == 'WHITE':
            self.squares = [[x, (k, l)] for x in white_pos for k in range(
                self.width) for l in range(self.height)]
        elif turn == 'BLACK':
            self.squares = [[x, (k, l)] for x in black_pos for k in range(
                self.width) for l in range(self.height)]

    def move(self, move):
        """
        Moves a pawn on the board according to the given move.

        Args:
            move (tuple): A tuple containing the starting and ending positions of the move.

        Returns:
            Tablut: The updated Tablut object after the move has been made.
        """
        # Extract the starting and ending position from the move
        from_pos, to_pos = move
        x1, y1 = from_pos
        x2, y2 = to_pos

        pawn_type = self.initial.pieces[x1][y1]

        new_board = copy.deepcopy(self.initial.pieces)

        # Get the pawn type
        if pawn_type == Pawn.EMPTY.value or pawn_type == Pawn.THRONE.value:
            self.initial.pieces = new_board
            return self

        if self.initial.pieces[x2][y2] != Pawn.EMPTY.value:
            self.initial.pieces = new_board
            return self

        if x1 == 4 and y1 == 4:
            new_board[x1][y1] = Pawn.THRONE.value
        else:
            new_board[x1][y1] = Pawn.EMPTY.value

        # Remove the pawn from the starting position and add it to the ending position
        new_board[x2][y2] = pawn_type

        # Check if there are any captures (important otherwise heuristics won't work)
        self.initial.check_attacks(x2, y2)

        self.initial.pieces = new_board

        # Change turn
        self.initial.to_move = (
            "BLACK" if self.initial.to_move == "WHITE" else "WHITE")
        return self

    def actions(self, pieces, player, board) -> set:
        """
        Returns a set of allowed moves for the current player.

        Args:
            pieces (numpy.ndarray): The current state of the game board.
            player (str): The current player ('WHITE' or 'BLACK').
            board (numpy.ndarray): The current state of the game board.

        Returns:
            set: A set of allowed moves for the current player.
        """
        pawns = np.where(pieces == Pawn.WHITE.value)
        coordinates = list(zip(pawns[0], pawns[1]))
        white = coordinates

        pawns = np.where(pieces == Pawn.BLACK.value)
        coordinates = list(zip(pawns[0], pawns[1]))
        black = coordinates

        pawns = np.where(pieces == Pawn.KING.value)
        coordinates = list(zip(pawns[0], pawns[1]))
        king = coordinates[0]

        white.insert(0, king)

        throne = [(4, 4)]

        # print("White pieces:", white)

        # Get the list of the opponent pieces
        if player == 'WHITE':
            player_pieces = white
            opponent_pieces = black

        elif player == 'BLACK':
            player_pieces = black
            opponent_pieces = white

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
            from_row, from_col = from_pos

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
                            (board[from_row][from_col] not in (RED, RED2) and board[from_row][from_col - i] in (RED, RED2)):

                        flags[0] = True
                        forbidden_moves.add(
                            (from_pos, (from_row, from_col - i)))

                if from_row - i >= 0:
                    if flags[1] or (from_row - i, from_col) in occupied_squares or \
                            (board[from_row][from_col] not in (RED, RED2) and board[from_row - i][from_col] in (RED, RED2)):

                        flags[1] = True
                        forbidden_moves.add(
                            (from_pos, (from_row - i, from_col)))

                if from_col + i < self.width:
                    if flags[2] or (from_row, from_col+i) in occupied_squares or \
                            (board[from_row][from_col] not in (RED, RED2) and board[from_row][from_col + i] in (RED, RED2)):

                        flags[2] = True
                        forbidden_moves.add(
                            (from_pos, (from_row, from_col+i)))

                if from_row + i < self.width:
                    if flags[3] or (from_row + i, from_col) in occupied_squares or \
                            (board[from_row][from_col] not in (RED, RED2) and board[from_row + i][from_col] in (RED, RED2)):

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

    def result(self, state, move, flag: bool = False):
        """
        Apply the given move to the state and return the resulting state.

        Parameters:
        - state: The current state of the game.
        - move: The move to be applied to the state.
        - alpha0, beta0, gamma0, theta0, epsilon0: Parameters for computing the utility of the board.
        - flag: A flag indicating whether the move should be applied to the state or not. Default is False.

        Returns:
        The resulting state after applying the move.
        """
        # Apply the move locally and check for captures
        game = Tablut()

        if isinstance(state, Tablut):
            game.initial.pieces = copy.deepcopy(state.initial.pieces)
        elif isinstance(state, Board):
            game.initial.pieces = copy.deepcopy(state.pieces)

        game.initial.get_white()
        game.initial.get_black()
        game.initial.get_king()

        if flag is False:
            game = game.move(move)

        game.update_state(game.initial.pieces, game.initial.to_move)

        # Compute the utility of the board

        # Update the utility of the board
        game.initial.utility = self.compute_utility(
            game.initial, player=game.initial.to_move)

        print("UTILITY: ", game.initial.utility)

        # return the new board
        return game.initial

    def utility(self, board, player):
        """Return the value to player; 1 for win, -1 for loss, 0 otherwise.

        Args:
            board (Board): The current game board.
            player (str): The player for whom to calculate the utility.

        Returns:
            int: The utility value for the specified player.
        """
        return board.utility if player == 'WHITE' else board.utility

    def terminal_test(self, board, player):
        """
        Check if the current board state is a terminal state.

        Parameters:
        - board: The current board state.

        Returns:
        - True if the game is in a terminal state (winning move or no more moves), False otherwise.
        """
        return self.check_win(board, player)

    def compute_utility(self, board, player) -> float:

        if self.check_win(board, player):
            return +1e10 if player == 'WHITE' else -1e10
        else:
            if player == 'WHITE':
                fitness = white_fitness(board)

            elif player == 'BLACK':
                fitness = black_fitness(board)

            return fitness

    def check_win(self, state, player):
        """
        End of game:
        - King captured (BLACK wins)
        - King escaped (WHITE wins)
        - A player can’t move any checker in any direction: that player loses
        - The same "state" of the game is reached twice: draw
        """

        if isinstance(state, Board):
            white_pieces = state.get_white()
            black_pieces = state.get_black()
            king_pieces = state.get_king()

        elif isinstance(state, Tablut):
            white_pieces = state.initial.get_white()
            black_pieces = state.initial.get_black()
            king_pieces = state.initial.get_king()

        if player == 'WHITE':
            if len(black_pieces) == 0:
                return True

        elif player == 'BLACK':
            # King captured
            if king_pieces is None:
                return True

            if len(white_pieces) == 0:
                return True

        return False

    def convert_move(self, move):
        """Convert move to (A1, A2) format
        Move: ((x1, y1), (x2, y2))
        Example: ((0,3), (3,3))
        Convert to: (D1, D4)"""

        cols = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']

        from_pos = move[0]
        x1, y1 = from_pos

        to_pos = move[1]
        x2, y2 = to_pos

        from_letter = cols[y1]
        to_letter = cols[y2]

        new_from_row = x1 + 1
        new_to_row = x2 + 1

        return (from_letter+str(new_from_row), to_letter+str(new_to_row))

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
