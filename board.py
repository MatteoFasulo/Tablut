import time
from collections import defaultdict

import numpy as np

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

        self.winning_positions = set([(0, 1), (0, 2), (0, 7), (0, 8), (1, 0), (2, 0), (2, 8), (
            1, 8), (6, 0), (6, 8), (7, 0), (7, 8), (8, 1), (8, 2), (8, 6), (8, 7)])

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
        pawns = np.where(self.pieces == Pawn.WHITE.value)
        coordinates = list(zip(pawns[0], pawns[1]))
        self.white = coordinates

        king = self.get_king()
        if king is not None:
            self.white.insert(0, king)

        self.whites = self.white
        return coordinates

    def get_black(self):
        pawns = np.where(self.pieces == Pawn.BLACK.value)
        coordinates = list(zip(pawns[0], pawns[1]))
        self.black = coordinates
        self.blacks = self.black
        return coordinates

    def get_king(self):
        pawns = np.where(self.pieces == Pawn.KING.value)
        coordinates = list(zip(pawns[0], pawns[1]))
        try:
            self.king = coordinates[0]
            return coordinates[0]
        except IndexError:  # king has been captured
            return None

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

    def check_attacks(self, x, y):
        # Horizontal check
        if x > 1:
            if self.pieces[x-2][y] == self.pieces[x][y] and self.pieces[x-1][y] != self.pieces[x][y]:
                self.pieces[x-1][y] = 0
                has_deleted = False
                for black in self.blacks:
                    if black[0] == x-1 and black[1] == y:
                        del black
                        has_deleted = True
                        break
                if not has_deleted:
                    for white in self.whites:
                        if white[0] == x-1 and white[1] == y:
                            del white
                            break
        if x < len(self.pieces)-2:
            if self.pieces[x+2][y] == self.pieces[x][y] and self.pieces[x+1][y] != self.pieces[x][y]:
                self.pieces[x+1][y] = 0
                has_deleted = False
                for black in self.blacks:
                    if black[0] == x-1 and black[1] == y:
                        del black
                        has_deleted = True
                        break
                if not has_deleted:
                    for white in self.whites:
                        if white[0] == x-1 and white[1] == y:
                            del white
                            break
        # Vertical check
        if y > 1:
            if self.pieces[x][y-2] == self.pieces[x][y] and self.pieces[x][y-1] != self.pieces[x][y]:
                self.pieces[x][y-1] = 0
                has_deleted = False
                for black in self.blacks:
                    if black[0] == x-1 and black[1] == y:
                        del black
                        has_deleted = True
                        break
                if not has_deleted:
                    for white in self.whites:
                        if white[0] == x-1 and white[1] == y:
                            del white
                            break
        if y < len(self.pieces)-2:
            if self.pieces[x][y+2] == self.pieces[x][y] and self.pieces[x][y+1] != self.pieces[x][y]:
                self.pieces[x][y+1] = 0
                has_deleted = False
                for black in self.blacks:
                    if black[0] == x-1 and black[1] == y:
                        del black
                        has_deleted = True
                        break
                if not has_deleted:
                    for white in self.whites:
                        if white[0] == x-1 and white[1] == y:
                            del white
                            break

        return self

    def eat_black(self):
        '''
        If a black piece can be eaten it returns a list of initial and final position of the white piece that eats
        '''
        moves_to_eat = []
        for white in self.whites:
            for i in range(white[1]+1, len(self.pieces)-1, 1):
                try:
                    if self.pieces[white[0]+1][i] == 1 and self.pieces[white[0]+2][i] == 2:
                        moves_to_eat.append([white[0], white[1], white[0], i])
                    if self.pieces[white[0]-1][i] == 1 and self.pieces[white[0]-2][i] == 2:
                        moves_to_eat.append([white[0], white[1], white[0], i])
                except:
                    pass
                if self.pieces[white[0]][i] == 1 and self.pieces[white[0]][i+1] == 2:
                    moves_to_eat.append([white[0], white[1], white[0], i-1])
                    break
            for i in range(0, white[1]):
                try:
                    if self.pieces[white[0]+1][i] == 1 and self.pieces[white[0]+2][i] == 2:
                        moves_to_eat.append([white[0], white[1], white[0], i])
                    if self.pieces[white[0]-1][i] == 1 and self.pieces[white[0]-2][i] == 2:
                        moves_to_eat.append([white[0], white[1], white[0], i])
                except:
                    pass
                if self.pieces[white[0]][i] == 1 and self.pieces[white[0]][i-1] == 2:
                    moves_to_eat.append([white[0], white[1], i+1])
                    break
            for i in range(0, white[0]):
                try:
                    if self.pieces[i][white[1]+1] == 1 and self.pieces[i][white[1]+2] == 2:
                        moves_to_eat.append([white[0], white[1], i, white[1]])
                    if self.pieces[i][white[1]-1] == 1 and self.pieces[i][white[1]-2] == 2:
                        moves_to_eat.append([white[0], white[1], i, white[1]])
                except:
                    pass
                if self.pieces[i][white[1]] == 1 and self.pieces[i-1][white[1]] == 2:
                    moves_to_eat.append([white[0], white[1], i+1, white[1]])
                    break
            for i in range(white[0]+1, len(self.pieces)-1, 1):
                try:
                    if self.pieces[i][white[1]+1] == 1 and self.pieces[i][white[1]+2] == 2:
                        moves_to_eat.append([white[0], white[1], i, white[1]])
                    if self.pieces[i][white[1]-1] == 1 and self.pieces[i][white[1]-2] == 2:
                        moves_to_eat.append([white[0], white[1], i, white[1]])
                except:
                    pass
                if self.pieces[i][white[1]] == 1 and self.pieces[i+1][white[1]] == 2:
                    moves_to_eat.append([white[0], white[1], i-1, white[1]])
                    break

        self.white_moves_to_eat = moves_to_eat

    def check_num_pieces_in_quadrant(self, n_quadrant, black_or_white):
        """
        Returns the number of pieces in the quadrant of selected color
        (1 = left up, 2 = right up, 3 = left down, 4 = right down)
        """
        if black_or_white not in (1, 2):
            raise Exception("The color must be 1 (black) or 2 (white)")

        num_pieces = 0
        if n_quadrant == 1:
            quadrant = [row[:4] for row in self.board[:4]]
            for i in range(4):
                for j in range(4):
                    if quadrant[i][j] == black_or_white:
                        num_pieces += 1
        elif n_quadrant == 2:
            quadrant = [row[5:] for row in self.board[:4]]
            for i in range(4):
                for j in range(4):
                    if quadrant[i][j] == black_or_white:
                        num_pieces += 1
        elif n_quadrant == 3:
            quadrant = [row[:4] for row in self.board[5:]]
            for i in range(4):
                for j in range(4):
                    if quadrant[i][j] == black_or_white:
                        num_pieces += 1
        elif n_quadrant == 4:
            quadrant = [row[5:] for row in self.board[5:]]
            for i in range(4):
                for j in range(4):
                    if quadrant[i][j] == black_or_white:
                        num_pieces += 1
        else:
            raise Exception("The quadrant number must be between 1 and 4")

        return num_pieces
