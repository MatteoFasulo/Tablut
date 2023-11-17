import sys
import random
import math
import time
import functools
import sys
import copy
from collections import namedtuple, Counter, defaultdict
from enum import Enum

from threading import Thread

# numpy
import numpy as np

# matplotlib
import matplotlib.pyplot as plt

# aima
from aima.games import alpha_beta_search, Game, GameState

# utils
from utils import Converter, Pawn, Network


class Board(defaultdict):
    empty = Pawn.EMPTY
    off = '#'

    def __init__(self, width, height, to_move, **kwds):
        self.__dict__.update(width=width, height=height,
                             to_move=to_move, **kwds)

        self.pieces = np.array([
            [Pawn.EMPTY, Pawn.EMPTY, Pawn.EMPTY, Pawn.BLACK, Pawn.BLACK,
                Pawn.BLACK, Pawn.EMPTY, Pawn.EMPTY, Pawn.EMPTY],
            [Pawn.EMPTY, Pawn.EMPTY, Pawn.EMPTY, Pawn.EMPTY, Pawn.BLACK,
                Pawn.EMPTY, Pawn.EMPTY, Pawn.EMPTY, Pawn.EMPTY],
            [Pawn.EMPTY, Pawn.EMPTY, Pawn.EMPTY, Pawn.EMPTY, Pawn.WHITE,
                Pawn.EMPTY, Pawn.EMPTY, Pawn.EMPTY, Pawn.EMPTY],
            [Pawn.BLACK, Pawn.EMPTY, Pawn.EMPTY, Pawn.EMPTY, Pawn.WHITE,
                Pawn.EMPTY, Pawn.EMPTY, Pawn.EMPTY, Pawn.BLACK],
            [Pawn.BLACK, Pawn.BLACK, Pawn.WHITE, Pawn.WHITE, Pawn.KING,
                Pawn.WHITE, Pawn.WHITE, Pawn.BLACK, Pawn.BLACK],
            [Pawn.BLACK, Pawn.EMPTY, Pawn.EMPTY, Pawn.EMPTY, Pawn.WHITE,
                Pawn.EMPTY, Pawn.EMPTY, Pawn.EMPTY, Pawn.BLACK],
            [Pawn.EMPTY, Pawn.EMPTY, Pawn.EMPTY, Pawn.EMPTY, Pawn.WHITE,
                Pawn.EMPTY, Pawn.EMPTY, Pawn.EMPTY, Pawn.EMPTY],
            [Pawn.EMPTY, Pawn.EMPTY, Pawn.EMPTY, Pawn.EMPTY, Pawn.BLACK,
                Pawn.EMPTY, Pawn.EMPTY, Pawn.EMPTY, Pawn.EMPTY],
            [Pawn.EMPTY, Pawn.EMPTY, Pawn.EMPTY, Pawn.BLACK, Pawn.BLACK,
                Pawn.BLACK, Pawn.EMPTY, Pawn.EMPTY, Pawn.EMPTY],
        ])

        # Get the indices of the white, black and king pieces
        white_pawns = np.where(self.pieces == Pawn.WHITE)
        self.white = list(zip(white_pawns[0], white_pawns[1]))

        black_pawns = np.where(self.pieces == Pawn.BLACK)
        self.black = list(zip(black_pawns[0], black_pawns[1]))

        king_pawn = np.where(self.pieces == Pawn.KING)
        self.king = list(zip(king_pawn[0], king_pawn[1]))

    def to_move(self, state):
        return self.__dict__['to_move']

    def new(self, changes: dict, **kwds) -> 'Board':
        "Given a dict of {(x, y): contents} changes, return a new Board with the changes."
        board = Board(width=self.width, height=self.height, **kwds)
        board.update(self)
        board.update(changes)

        return board

    def __missing__(self, loc):
        x, y = loc
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.empty
        else:
            return self.off

    def __hash__(self):
        return hash(tuple(sorted(self.items()))) + hash(self.to_move)

    def __str__(self):
        """
        Given an np.array of pieces, return a string representation of the board
        with rows separated by newlines.
        """
        # Create a new array of integers representing the pieces
        pieces_int = np.vectorize(lambda x: x.value)(self.pieces)

        return str(pieces_int)

    def display(self):
        """
        Representation of the board using matplotlib
        """

        # Create a new array of integers representing the pieces
        pieces_int = np.vectorize(lambda x: x.value)(self.pieces)

        fig, ax = plt.subplots()
        ax.matshow(pieces_int, cmap="Set3")

        # Changes the size of the pieces
        fontsize = 30

        # Dictionary to map Pawn values to their respective characters and colors
        pawn_dict = {Pawn.BLACK: ("⛂", "black"), Pawn.WHITE: (
            "⛀", "white"), Pawn.KING: ("⛁", "white")}

        # Places the pieces on the board
        for pawn_value, (char, color) in pawn_dict.items():
            for x, y in np.argwhere(self.pieces == pawn_value):
                ax.text(x, y, char, ha='center', va='center',
                        color=color, fontsize=fontsize)

        plt.box(on=None)
        ax.set_xticks([0, 1, 2, 3, 4, 5, 6, 7, 8])
        ax.set_yticks([0, 1, 2, 3, 4, 5, 6, 7, 8])
        ax.set_xticklabels(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I'])
        ax.set_yticklabels(['1', '2', '3', '4', '5', '6', '7', '8', '9'])
        plt.show(block=False)
        return fig, ax


class Tablut(Game):
    def __init__(self, player, height=9, width=9):
        self.initial = Board(height=height, width=width,
                             to_move='WHITE', utility=0)
        self.to_move = player

        self.width = width
        self.height = height

        pieces = self.initial.white if self.initial.to_move == 'WHITE' else self.initial.black

        # Get the list of all the possible moves
        self.squares = [[x, (k, l)] for x in pieces for k in range(
            width) for l in range(height)]

    def actions(self, board) -> set:
        """Illegal moves are:
        - moving out of the board (off-board) based on the current board size # handled by self.squares
        - moving on the throne which is the center of the board (4,4) # handled by forbidden_moves
        - moving on another piece (already occupied position)
        - moving on the same position where the piece is currently located (not moving)
        - moving a piece that is not yours (based on the current player)
        - moving diagonally (only orthogonally)
        - moving a step over another piece (jumping or climbing)
        """

        white = board.white
        black = board.black
        king = board.king

        # Get the current player
        player = board.to_move

        # Get the opponent
        opponent = 'BLACK' if player == 'WHITE' else 'WHITE'

        # Get the list of the opponent pieces
        opponent_pieces = black if player == 'WHITE' else white

        # Get the list of the current player pieces
        player_pieces = white if player == 'WHITE' else black

        # Get the list of the king
        king_pieces = king

        # Get the list of the occupied squares in coordinates (x, y)
        occupied_squares = np.argwhere(
            (board.pieces == Pawn.WHITE) | (board.pieces == Pawn.BLACK) | (board.pieces == Pawn.KING))

        # Get the list of the occupied squares in coordinates (x, y)
        occupied_squares = set(map(tuple, occupied_squares))

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

            forbidden_moves.add((from_pos, from_pos))  # starting position

            if from_pos in opponent_pieces:
                forbidden_moves.add((from_pos, to_pos))

            # remove diagonal moves
            if from_row != to_row and from_col != to_col:
                forbidden_moves.add((from_pos, to_pos))

            # remove moves which implies to jumping over a piece
            j = None
            if from_row == to_row:
                if from_col > to_col:
                    for i in range(to_col, from_col):
                        if (from_row, i) in occupied_squares:
                            forbidden_moves.add((from_pos, (from_row, i)))
                            j = i
                            break
                    if j:
                        for i in range(0, j):
                            forbidden_moves.add((from_pos, (from_row, i)))

                else:
                    for i in range(from_col, to_col):
                        if (from_row, i) in occupied_squares:
                            forbidden_moves.add((from_pos, (from_row, i)))
                            j = i
                            break
                    if j:
                        for i in range(j+1, self.width):
                            forbidden_moves.add((from_pos, (from_row, i)))

            else:
                if from_row > to_row:
                    for i in range(to_row, from_row):
                        if (i, from_col) in occupied_squares:
                            forbidden_moves.add((from_pos, (i, from_col)))
                            j = i
                            break
                    if j:
                        for i in range(0, j):
                            forbidden_moves.add((from_pos, (i, from_col)))
                else:
                    for i in range(from_row, to_row):
                        if (i, from_col) in occupied_squares:
                            forbidden_moves.add((from_pos, (i, from_col)))
                            j = i
                            break
                    if j:
                        for i in range(j+1, self.height):
                            forbidden_moves.add((from_pos, (i, from_col)))

        # return difference between all possible moves and forbidden moves (list of tuples)
        total_moves = set(tuple(tuple(k) for k in h)
                          for h in self.squares)
        print("total_moves: ", total_moves)

        allowed_moves = total_moves - forbidden_moves
        print("forbidden_moves: ", forbidden_moves)

        return allowed_moves

    def result(self, board, square):
        """Place a marker for current player on square."""
        player = board.to_move
        board = board.new({square: player}, to_move=(
            'BLACK' if player == 'WHITE' else 'WHITE'))
        win = False  # TODO : add win condition here
        board.utility = (0 if not win else +1 if player == 'WHITE' else -1)
        return board

    def utility(self, board, player):
        """Return the value to player; 1 for win, -1 for loss, 0 otherwise."""
        return board.utility if player == 'WHITE' else -board.utility

    def terminal_test(self, board):
        """A board is a terminal state if it is won or there are no empty squares."""
        return board.utility != 0 or len(self.squares) == len(board)

    def convert_move(self, move):
        """Convert move to (A1, A2) format
        Move: ((x1, y1), (x2, y2))"""
        cols = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']

        # Get the starting position
        from_pos = move[0]
        from_row, from_col = from_pos

        # Get the ending position
        to_pos = move[1]
        to_row, to_col = to_pos

        # Convert the starting position
        from_col = cols[from_col]
        from_row = from_row + 1

        # Convert the ending position
        to_col = cols[to_col]
        to_row = to_row + 1

        return (from_col + str(from_row), to_col + str(to_row))

    def display(self, board):
        print(board)


def play_game(name: str, team: str, server_ip: str, timeout: int):
    # Initialize network
    network = Network(name, team, server_ip, timeout=timeout)
    # Get initial state and turn
    pieces, turn = network.connect()

    # Initialize game
    game = Tablut(team)

    # Assign initial state
    game.initial.pieces = pieces

    # Assign turn
    game.initial.to_move = turn[-1]

    # Play game
    state = game.initial

    while not game.terminal_test(state):
        player = state.to_move
        if player == team:
            start = time.time()
            move = h_alphabeta_search(game, state)[-1]
            end = time.time()

            # Send move to server
            print("Move: ", move)
            converted_move = game.convert_move(move)
            print("Converted move: ", converted_move)
            del game
            network.send_move(converted_move)
            pieces, turn = network.get_state()
            game = Tablut(team)
            game.initial.pieces = pieces
            game.initial.to_move = turn
            state = game.result(state, move)
            print('Player', player, 'move:',
                  move, 'time: ', end-start, 's.')
            print(state, '\n')
            # state.display()
        else:
            print("Waiting for other player's move...")
            pieces, turn = network.get_state()
            game = Tablut(team)
            game.initial.pieces = pieces
            game.initial.to_move = turn
            state = game.result(state, move)


class Pawn(Enum):
    EMPTY = 0
    BLACK = 1
    WHITE = 2
    KING = 3


def random_player(game, state):
    return random.choice(list(game.actions(state)))


def player(search_algorithm):
    """A game player who uses the specified search algorithm"""
    return lambda game, state: search_algorithm(game, state)[1]


infinity = float('inf')


def cache(function):
    "Like lru_cache(None), but only considers the first argument of function."
    cache = {}

    def wrapped(x, *args):
        if x not in cache:
            cache[x] = function(x, *args)
        return cache[x]
    return wrapped


def cutoff_depth(d):
    """A cutoff function that searches to depth d."""
    return lambda game, state, depth: depth > d

# TODO change depth (d)


def h_alphabeta_search(game, state, cutoff=cutoff_depth(1), h=lambda s, p: 0):
    """Search game to determine best action; use alpha-beta pruning.
    As in [Figure 5.7], this version searches all the way to the leaves."""

    player = state.to_move

    @cache
    def max_value(state, alpha, beta, depth):
        if game.terminal_test(state):
            return game.utility(state, player), None
        if cutoff(game, state, depth):
            return h(state, player), None
        v, move = -infinity, None
        for a in game.actions(state):
            v2, _ = min_value(game.result(state, a), alpha, beta, depth+1)
            if v2 > v:
                v, move = v2, a
                alpha = max(alpha, v)
            if v >= beta:
                return v, move
        return v, move

    @cache
    def min_value(state, alpha, beta, depth):
        if game.terminal_test(state):
            return game.utility(state, player), None
        if cutoff(game, state, depth):
            return h(state, player), None
        v, move = +infinity, None
        for a in game.actions(state):
            v2, _ = max_value(game.result(state, a), alpha, beta, depth + 1)
            if v2 < v:
                v, move = v2, a
                beta = min(beta, v)
            if v <= alpha:
                return v, move
        return v, move

    return max_value(state, -infinity, +infinity, 0)


color = sys.argv[1]
name = sys.argv[2]
print(color)
play_game(name=name, team=color, server_ip='57.129.16.112', timeout=60)
