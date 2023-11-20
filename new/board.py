import time
from collections import defaultdict

import numpy as np
import matplotlib.pyplot as plt

# utils
from utils import Pawn, WHITE, WHITE2, RED, RED2, GREEN, GREEN2, BLUE, GRAY


class Board(defaultdict):
    empty = Pawn.EMPTY
    off = '#'

    def __init__(self, width, height, to_move, **kwds):
        self.__dict__.update(width=width, height=height,
                             to_move=to_move, **kwds)

        self.board = [
            [GRAY, WHITE, WHITE2, RED2, RED, RED2, WHITE2, WHITE, GRAY],
            [WHITE, WHITE2, WHITE, WHITE2, RED2, WHITE2, WHITE, WHITE2, WHITE],
            [WHITE2, WHITE, WHITE2, WHITE, GREEN, WHITE, WHITE2, WHITE, WHITE2],
            [RED2, WHITE2, WHITE, WHITE2, GREEN2, WHITE2, WHITE, WHITE2, RED2],
            [RED, RED2, GREEN, GREEN2, BLUE, GREEN2, GREEN, RED2, RED],
            [RED2, WHITE2, WHITE, WHITE2, GREEN2, WHITE2, WHITE, WHITE2, RED2],
            [WHITE2, WHITE, WHITE2, WHITE, GREEN, WHITE, WHITE2, WHITE, WHITE2],
            [WHITE, WHITE2, WHITE, WHITE2, RED2, WHITE2, WHITE, WHITE2, WHITE],
            [GRAY, WHITE, WHITE2, RED2, RED, RED2, WHITE2, WHITE, GRAY],
        ]

    # AIMA methods
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

    # Board methods
    def get_white(self):
        # print("SONO DENTRO GETWHITE")
        # print(self.pieces)
        pawns = np.where(self.pieces == Pawn.WHITE.value)
        coordinates = list(zip(pawns[1], pawns[0]))
        self.white = coordinates
        self.whites = self.white
        # print(self.white)
        return coordinates

    def get_black(self):
        pawns = np.where(self.pieces == Pawn.BLACK.value)
        coordinates = list(zip(pawns[1], pawns[0]))
        self.black = coordinates
        return coordinates

    def get_king(self):
        pawns = np.where(self.pieces == Pawn.KING.value)
        coordinates = list(zip(pawns[1], pawns[0]))
        self.king = coordinates[0]
        return coordinates[0]

    def _is_there_a_clear_view(self, piece1, piece2):
        if piece1[0] == piece2[0]:
            offset = 1 if piece1[1] <= piece2[1] else -1
            for i in range(piece1[1] + offset, piece2[1], offset):
                if self.pieces[piece1[0]][i] != 0:
                    return False
            return True
        elif piece1[1] == piece2[1]:
            offset = 1 if piece1[0] <= piece2[0] else -1
            for i in range(piece1[0] + offset, piece2[0], offset):
                if self.pieces[i][piece1[1]] != 0:
                    return False
            return True
        else:
            return False

    # Representation of the board
    def display(self):
        fig, ax = plt.subplots()

        ax.matshow(self.board, cmap="Greys")

        # Changes the size of the pieces
        fontsize = 30

        # Places the pieces on the board
        for row in range(len(self.pieces)):
            for piece in range(len(self.pieces[row])):
                char = '⛀' if self.pieces[row][piece] == 2 else "⛂" if self.pieces[
                    row][piece] == 1 else "⛁" if self.pieces[row][piece] == 3 else ""
                color = "black" if self.pieces[row][piece] == 1 else "white"
                ax.text(row, piece, char, ha='center', va='center',
                        color=color, fontsize=fontsize)

        plt.box(on=None)
        ax.set_xticks([0, 1, 2, 3, 4, 5, 6, 7, 8])
        ax.set_yticks([0, 1, 2, 3, 4, 5, 6, 7, 8])
        ax.set_xticklabels(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I'])
        ax.set_yticklabels(['1', '2', '3', '4', '5', '6', '7', '8', '9'])
        plt.show(block=False)
        plt.pause(5)
