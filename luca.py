import random, math, time, functools, sys
import copy
from collections import namedtuple, Counter, defaultdict
from enum import Enum

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
        self.__dict__.update(width=width, height=height, to_move=to_move, **kwds)
        
        self.pieces = np.array([
        [Pawn.EMPTY, Pawn.EMPTY, Pawn.EMPTY, Pawn.BLACK, Pawn.BLACK, Pawn.BLACK, Pawn.EMPTY, Pawn.EMPTY, Pawn.EMPTY],
        [Pawn.EMPTY, Pawn.EMPTY, Pawn.EMPTY, Pawn.EMPTY, Pawn.BLACK, Pawn.EMPTY, Pawn.EMPTY, Pawn.EMPTY, Pawn.EMPTY],
        [Pawn.EMPTY, Pawn.EMPTY, Pawn.EMPTY, Pawn.EMPTY, Pawn.WHITE, Pawn.EMPTY, Pawn.EMPTY, Pawn.EMPTY, Pawn.EMPTY],
        [Pawn.BLACK, Pawn.EMPTY, Pawn.EMPTY, Pawn.EMPTY, Pawn.WHITE, Pawn.EMPTY, Pawn.EMPTY, Pawn.EMPTY, Pawn.BLACK],
        [Pawn.BLACK, Pawn.BLACK, Pawn.WHITE, Pawn.WHITE, Pawn.KING, Pawn.WHITE, Pawn.WHITE, Pawn.BLACK, Pawn.BLACK],
        [Pawn.BLACK, Pawn.EMPTY, Pawn.EMPTY, Pawn.EMPTY, Pawn.WHITE, Pawn.EMPTY, Pawn.EMPTY, Pawn.EMPTY, Pawn.BLACK],
        [Pawn.EMPTY, Pawn.EMPTY, Pawn.EMPTY, Pawn.EMPTY, Pawn.WHITE, Pawn.EMPTY, Pawn.EMPTY, Pawn.EMPTY, Pawn.EMPTY],
        [Pawn.EMPTY, Pawn.EMPTY, Pawn.EMPTY, Pawn.EMPTY, Pawn.BLACK, Pawn.EMPTY, Pawn.EMPTY, Pawn.EMPTY, Pawn.EMPTY],
        [Pawn.EMPTY, Pawn.EMPTY, Pawn.EMPTY, Pawn.BLACK, Pawn.BLACK, Pawn.BLACK, Pawn.EMPTY, Pawn.EMPTY, Pawn.EMPTY],
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
        pawn_dict = {Pawn.BLACK: ("⛂", "black"), Pawn.WHITE: ("⛀", "white"), Pawn.KING: ("⛁", "white")}

        # Places the pieces on the board
        for pawn_value, (char, color) in pawn_dict.items():
            for x, y in np.argwhere(self.pieces == pawn_value):
                ax.text(x, y, char, ha='center', va='center', color=color, fontsize=fontsize)

        plt.box(on=None)
        ax.set_xticks([0,1,2,3,4,5,6,7,8])
        ax.set_yticks([0,1,2,3,4,5,6,7,8])
        ax.set_xticklabels(['A','B','C','D','E','F','G','H','I'])
        ax.set_yticklabels(['1','2','3','4','5','6','7','8','9'])
        plt.show(block=False)
        return fig, ax

class Tablut(Game):
    def __init__(self, player, height=9, width=9):
        self.squares = {(x, y) for x in range(width) for y in range(height)}
        self.initial = Board(height=height, width=width, to_move='WHITE', utility=0)
        self.to_move = player

    def actions(self, board):
        """Legal moves are any square not yet taken."""
        # remove moves on occupied squares
        print(self.to_move)
        print(board.pieces)
        return self.squares - set(board)

    def result(self, board, square):
        """Place a marker for current player on square."""
        player = board.to_move
        board = board.new({square: player}, to_move=('BLACK' if player == 'WHITE' else 'WHITE'))
        win = False # TODO : add win condition here
        board.utility = (0 if not win else +1 if player == 'WHITE' else -1)
        return board

    def utility(self, board, player):
        """Return the value to player; 1 for win, -1 for loss, 0 otherwise."""
        return board.utility if player == 'WHITE' else -board.utility

    def terminal_test(self, board):
        """A board is a terminal state if it is won or there are no empty squares."""
        return board.utility != 0 or len(self.squares) == len(board)

    def display(self, board): 
        print(board)


def play_game(team: str, server_ip: str, timeout: int):
    # Initialize network
    network = Network('Sasso', team, server_ip, timeout=timeout)
    # Get initial state and turn
    pieces, turn = network.connect()
    print("PIECES: ", pieces)
    print("TURN: ", turn)

    print("1")

    # Initialize game
    game = Tablut(team)
    print("2")

    # Assign initial state
    game.initial.pieces = pieces
    print("3")

    # Assign turn
    game.initial.to_move = turn[-1]
    print("4")

    # Play game
    state = game.initial
    print("5")

    while not game.terminal_test(state):
        print("6")

        player = state.to_move
        start = time.time()
        move = h_alphabeta_search(game, state)[-1]
        end = time.time()
        
        # Send move to server
        network.send_move(move)
        pieces, turn = network.get_state()
        game.initial.pieces = pieces
        game.initial.to_move = turn
        state = game.result(state, move)
        print('Player', player, 'move:', move, 'time: ', end-start, 's.')
        print(state,'\n')
        #state.display()
    return state



class Pawn(Enum):
    EMPTY = 0
    BLACK = 1
    WHITE = 2
    KING = 3

test = np.array([
        [Pawn.EMPTY, Pawn.EMPTY, Pawn.EMPTY, Pawn.BLACK, Pawn.BLACK, Pawn.BLACK, Pawn.EMPTY, Pawn.EMPTY, Pawn.EMPTY],
        [Pawn.EMPTY, Pawn.EMPTY, Pawn.EMPTY, Pawn.EMPTY, Pawn.BLACK, Pawn.EMPTY, Pawn.EMPTY, Pawn.EMPTY, Pawn.EMPTY],
        [Pawn.EMPTY, Pawn.EMPTY, Pawn.EMPTY, Pawn.EMPTY, Pawn.WHITE, Pawn.EMPTY, Pawn.EMPTY, Pawn.EMPTY, Pawn.EMPTY],
        [Pawn.BLACK, Pawn.EMPTY, Pawn.EMPTY, Pawn.EMPTY, Pawn.WHITE, Pawn.EMPTY, Pawn.EMPTY, Pawn.EMPTY, Pawn.BLACK],
        [Pawn.BLACK, Pawn.BLACK, Pawn.WHITE, Pawn.WHITE, Pawn.KING, Pawn.WHITE, Pawn.WHITE, Pawn.BLACK, Pawn.BLACK],
        [Pawn.BLACK, Pawn.EMPTY, Pawn.EMPTY, Pawn.EMPTY, Pawn.WHITE, Pawn.EMPTY, Pawn.EMPTY, Pawn.EMPTY, Pawn.BLACK],
        [Pawn.EMPTY, Pawn.EMPTY, Pawn.EMPTY, Pawn.EMPTY, Pawn.WHITE, Pawn.EMPTY, Pawn.EMPTY, Pawn.EMPTY, Pawn.EMPTY],
        [Pawn.EMPTY, Pawn.EMPTY, Pawn.EMPTY, Pawn.EMPTY, Pawn.BLACK, Pawn.EMPTY, Pawn.EMPTY, Pawn.EMPTY, Pawn.EMPTY],
        [Pawn.EMPTY, Pawn.EMPTY, Pawn.EMPTY, Pawn.BLACK, Pawn.BLACK, Pawn.BLACK, Pawn.EMPTY, Pawn.EMPTY, Pawn.EMPTY],
        ])


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

import sys

color = sys.argv[1]
print(color)
play_game(team=color, server_ip='127.0.0.1', timeout=60)