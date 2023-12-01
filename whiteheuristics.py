import math
from utils import RED, RED2, BLUE, Pawn
import copy


def can_this_tile_be_reached_by_a_black_pawn(board, x, y):
    if x < 0 or x >= len(board.pieces):
        return False
    if y < 0 or y >= len(board.pieces):
        return False
    for i in range(0, x+1):
        if board.pieces[i][y] == 1 and board._is_there_a_clear_view([x, y], [i, y]):
            return True
    for i in range(x, len(board.pieces)):
        if board.pieces[i][y] == 1 and board._is_there_a_clear_view([x, y], [i, y]):
            return True
    for j in range(0, y+1):
        if board.pieces[x][j] == 1 and board._is_there_a_clear_view([x, y], [x, j]):
            return True
    for j in range(y, len(board.pieces)):
        if board.pieces[x][j] == 1 and board._is_there_a_clear_view([x, y], [x, j]):
            return True
    return False


def king_distance_from_center(king):
    return ((king[0] - 4)**2 + (king[1] - 4)**2)**0.5


def king_surrounded(board):
    king = board.king
    c = 0
    blocked_pos = []
    try:
        if board.pieces[king[0]+1][king[1]] == Pawn.BLACK.value:
            c += 1
            blocked_pos.append((king[0]+1, king[1]))
    except:
        pass
    try:
        if board.pieces[king[0]-1][king[1]] == Pawn.BLACK.value:
            c += 1
            blocked_pos.append((king[0]-1, king[1]))
    except:
        pass
    try:
        if board.pieces[king[0]][king[1]+1] == Pawn.BLACK.value:
            c += 1
            blocked_pos.append((king[0], king[1]+1))
    except:
        pass
    try:
        if board.pieces[king[0]][king[1]-1] == Pawn.BLACK.value:
            c += 1
            blocked_pos.append((king[0], king[1]-1))
    except:
        pass
    return c, blocked_pos


weights = [[0, 20, 20, -6, -6, -6, 20, 20, 0],
           [20, 1, 1, -5, -6, -5, 1,  1, 20],
           [20, 1, 4,  1, -2,  1, 4,  1, 20],
           [-6, -5, 1,  1,  1,  1, 1, -5, -6],
           [-6, -6, -2,  1,  2,  1, -2, -6, -6],
           [-6, -5, 1,  1,  1,  1, 1, -5, -6],
           [20, 1, 4,  1, -2,  1, 4,  1, 20],
           [20, 1, 1, -5, -6, -5, 1,  1, 20],
           [0, 20, 20, -6, -6, -6, 20, 20, 0]]


def position_weight(king):
    global weights
    return weights[king[0]][king[1]]


def white_fitness(board):
    """
    Returns the float value of the current state of the board for white
    """

    

    king_pos = board.get_king()

    alpha0, beta0, gamma0, theta0, epsilon0, omega0 = [
        0.21639120828483156, 0.723587137336777, 9, 1.06923818569000507, 2.115749207248323, 10]

    #alpha0, beta0, gamma0, theta0, epsilon0, omega0 = [
    #    12, 22, 9, 1, 2, 20]

    fitness = 0

    # Blackpieces
    num_blacks = len(board.blacks)
    fitness -= alpha0 * num_blacks

    # whitepieces
    num_whites = len(board.whites)
    fitness += beta0 * num_whites

    # king distance
    fitness += king_distance_from_center(board.king) * gamma0

    # free ways
    free_paths = [board._is_there_a_clear_view(black_pawn, king_pos)
                  for black_pawn in board.blacks]
    # theta0 times the n° free ways to king
    fitness -= omega0 * sum(free_paths)

    # king surrounded
    king_vals, _ = king_surrounded(board)
    fitness -= king_vals * theta0

    fitness += position_weight(board.king) * epsilon0

    norm_fitness = (
        fitness / (16 * beta0 + math.sqrt(32) * gamma0 + 20*epsilon0))

    # print("WHITE FITNESS: ", norm_fitness)

    return fitness
