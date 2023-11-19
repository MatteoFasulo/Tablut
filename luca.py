import sys
import random
import math
import time
import functools
import sys
import copy
from collections import namedtuple, Counter, defaultdict
from enum import Enum

import threading

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

    def get_white(self):
        pawns = np.where(self.pieces == Pawn.WHITE.value)
        coordinates = list(zip(pawns[0], pawns[1]))
        self.white = coordinates
        return coordinates

    def get_black(self):
        pawns = np.where(self.pieces == Pawn.BLACK.value)
        coordinates = list(zip(pawns[0], pawns[1]))
        self.black = coordinates
        return coordinates

    def get_king(self):
        pawns = np.where(self.pieces == Pawn.KING.value)
        coordinates = list(zip(pawns[0], pawns[1]))
        self.king = coordinates
        return coordinates

    def to_move(self, state):
        return self.__dict__['to_move']

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
        return str(self.pieces)

    def display(self, fig=None, ax=None):
        """
        Representation of the board using matplotlib
        """

        # Create a new array of integers representing the pieces
        pieces_int = self.pieces

        # If fig and ax are not provided, create a new figure and axis
        if fig is None or ax is None:
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

        # Draw the canvas and flush events
        fig.canvas.draw()
        fig.canvas.flush_events()
        time.sleep(0.1)

        # Display the plot without blocking
        plt.show(block=False)

        return fig, ax


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

    def actions(self, board) -> set:

        white = board.white
        black = board.black
        king = board.king

        # Get the current player
        player = board.to_move

        # Get the opponent
        opponent = 'BLACK' if player == 'WHITE' else 'WHITE'

        # Get the list of the opponent pieces
        opponent_pieces = black if player == 'WHITE' else white
        print("Opponent pieces:", opponent_pieces)

        # Get the list of the current player pieces
        player_pieces = white if player == 'WHITE' else black

        # Get the list of the king
        king_pieces = king

        # Get the list of the occupied squares in coordinates (x, y)
        occupied_squares = np.argwhere(
            (board.pieces == Pawn.WHITE.value) | (board.pieces == Pawn.BLACK.value) | (board.pieces == Pawn.KING.value))

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
                forbidden_moves.add((occ_place, occ_place))

            forbidden_moves.add((from_pos, from_pos))  # starting position

            if from_pos in opponent_pieces:
                forbidden_moves.add((from_pos, to_pos))

            # remove diagonal moves
            if from_row != to_row and from_col != to_col:
                forbidden_moves.add((from_pos, to_pos))

            # remove moves which implies to jumping over a piece
            # TODO rewrite this part of the code
            j = None
            if from_row == to_row:
                if from_col > to_col:
                    for i in range(to_col, from_col):
                        if (from_row, i) in occupied_squares:
                            forbidden_moves.add((from_pos, (from_row, i)))
                            j = i
                    if j:
                        for i in range(0, j):
                            forbidden_moves.add((from_pos, (from_row, i)))

                else:
                    for i in range(from_col, to_col):
                        if (from_row, i) in occupied_squares:
                            forbidden_moves.add((from_pos, (from_row, i)))
                            j = i
                    if j:
                        for i in range(j+1, self.width):
                            forbidden_moves.add((from_pos, (from_row, i)))

            else:
                if from_row > to_row:
                    for i in range(to_row, from_row):
                        if (i, from_col) in occupied_squares:
                            forbidden_moves.add((from_pos, (i, from_col)))
                            j = i
                    if j:
                        for i in range(0, j):
                            forbidden_moves.add((from_pos, (i, from_col)))
                else:
                    for i in range(from_row, to_row):
                        if (i, from_col) in occupied_squares:
                            forbidden_moves.add((from_pos, (i, from_col)))
                            j = i
                    if j:
                        for i in range(j+1, self.height):
                            forbidden_moves.add((from_pos, (i, from_col)))

        # test
        # banned_move = ((4, 8), (0, 8))
        # forbidden_moves.add(banned_move)
        # print(self.convert_move(banned_move))

        # return difference between all possible moves and forbidden moves (list of tuples)
        total_moves = set(tuple(tuple(k) for k in h)
                          for h in self.squares)
        allowed_moves = total_moves - forbidden_moves

        return allowed_moves

    def result(self, board, pieces):
        """Place a marker for current player on square."""
        player = board.to_move
        board.pieces = pieces
        board.to_move = 'BLACK' if player == 'WHITE' else 'WHITE'
        win = self.check_win(board)
        board.utility = (0 if not win else +1 if player == 'WHITE' else -1)
        return board

    def utility(self, board, player):
        """Return the value to player; 1 for win, -1 for loss, 0 otherwise."""
        return board.utility if player == 'WHITE' else -board.utility

    def terminal_test(self, board):
        """A board is a terminal state if it is won or there are no empty squares."""
        return board.utility != 0

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
        king_pieces = board.king

        # TODO Check if the king is captured
        if len(king_pieces) == 0:
            return True

        # TODO Check if the king escaped (16 escape squares, all cells on the edge of the board except for the corners)

        # TODO Check if the king is surrounded

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


def play_game(name: str, team: str, server_ip: str, timeout: int):
    # Initialize network
    network = Network(name, team, server_ip, timeout=timeout)
    # Get initial state and turn
    pieces, turn = network.connect()

    # Initialize game
    game = Tablut(team, pieces)
    game.update_state(pieces, turn)

    # Create a condition variable
    cond = threading.Condition()

    # Play game
    state = game.initial

    while not game.terminal_test(state):
        with cond:
            while not network.check_turn(player=team):
                print('Waiting for opponent move...')
                cond.wait(timeout=1)
                pieces, turn = network.get_state()

                # Update the game state for the current player
                game.update_state(pieces, turn)

            # Get move
            start = time.time()
            move = h_alphabeta_search(game, state)[-1]
            end = time.time()

            print('Chosen move:', move)

            # Send move to server
            converted_move = game.convert_move(move)
            print("Converted move:", converted_move)
            network.send_move(converted_move)
            print(state)
            pieces, turn = network.get_state()

            # Update the game state for the current player
            game.update_state(pieces, turn)

            # Update state
            state = game.result(state, pieces)

            print('move:', converted_move, 'time: ', end-start, 's.')
            print(state)

            # Notify the other thread
            cond.notify_all()

    print('Game over!')


class Pawn(Enum):
    EMPTY = 0
    WHITE = 1
    BLACK = 2
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


def h_alphabeta_search(game, state, cutoff=cutoff_depth(5), h=lambda s, p: 0):

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
