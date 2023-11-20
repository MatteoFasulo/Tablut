import time
from collections import defaultdict

import numpy as np
import matplotlib.pyplot as plt

# utils
from utils import Pawn


class Board(defaultdict):
    empty = Pawn.EMPTY
    off = '#'

    def __init__(self, width, height, to_move, **kwds):
        self.__dict__.update(width=width, height=height,
                             to_move=to_move, **kwds)

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
