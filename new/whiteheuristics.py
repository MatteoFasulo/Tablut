# import boardmanager
# import copy
import numpy as np


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


def is_white_gonna_be_eaten(board, alpha0):
    """
    Board: [[0 0 0 2 2 2 0 0 0]
            [0 0 0 0 2 0 0 0 0]
            [0 0 0 0 1 0 0 0 0]
            [2 0 0 0 1 0 0 0 2]
            [2 2 1 1 3 1 1 2 2]
            [2 0 0 0 1 0 0 0 2]
            [0 0 0 0 1 0 0 0 0]
            [0 0 0 0 2 0 0 0 0]
            [0 0 0 2 2 2 0 0 0]]
    """
    fitness = 0
    for white in board.whites:
        x, y = white
        if x > 0 and board.pieces[x-1, y] == 1 and can_this_tile_be_reached_by_a_black_pawn(board, x+1, y):
            fitness += alpha0

        if x < board.pieces.shape[0]-1 and board.pieces[x+1, y] == 1 and can_this_tile_be_reached_by_a_black_pawn(board, x-1, y):
            fitness += alpha0

        if y > 0 and board.pieces[x, y-1] == 1 and can_this_tile_be_reached_by_a_black_pawn(board, x, y+1):
            fitness += alpha0

        if y < board.pieces.shape[1]-1 and board.pieces[x, y+1] == 1 and can_this_tile_be_reached_by_a_black_pawn(board, x, y-1):
            if white[1] < len(board.pieces)-1 and board.pieces[white[0]][white[1]+1] == 1 and can_this_tile_be_reached_by_a_black_pawn(board, white[0], white[1]-1):
                fitness += alpha0
    return fitness


def king_distance(board, beta0):
    # King Distance:
    # Calculate the fastest path out for the king
    # Calculate the number of black pieces in each quadrant
    # The more black pieces there are in the quadrant, the lower the fitness
    # TODO: fix the fitness number and the beta0 value
    fitness = 0
    if board.king[0] > 4 and board.king[1] > 4:
        # King is in the bottom right quadrant
        bp = board.check_num_pieces_in_quadrant(1, 1)
        fitness += beta0 * 1-(bp*0.2)
    if board.king[0] > 4 and board.king[1] < 4:
        # King is in the bottom left quadrant
        bp = board.check_num_pieces_in_quadrant(3, 1)
        fitness += beta0 * 1-(bp*0.2)
    if board.king[0] < 4 and board.king[1] > 4:
        # King is in the top right quadrant
        bp = board.check_num_pieces_in_quadrant(2, 1)
        fitness += beta0 * 1-(bp*0.2)
    if board.king[0] < 4 and board.king[1] < 4:
        # King is in the top left quadrant
        bp = board.check_num_pieces_in_quadrant(4, 1)
        fitness += beta0 * 1-(bp*0.2)

    if board.king[0] != 4 and board.king[1] != 4:
        if board._is_there_a_clear_view(board.king, [board.king[0], 0]) or \
                board._is_there_a_clear_view(board.king, [board.king[0], len(board.pieces)-1]) or\
                board._is_there_a_clear_view(board.king, [0, board.king[1]]) or \
                board._is_there_a_clear_view(board.king, [len(board.pieces)-1, board.king[1]]):
            fitness += 1000  # Maximum value of heuristic

    return fitness


def external_pawn_more_fitness(board, gamma0):
    # "Pedoni esterna euristica più alta"
    # Since the fitness is computed on a static board, and not on a move, I have to count the number of pieces _far_ from the castle. The further they are as a whole, the higher the fitness
    # Consider concetric circles around the castle, the pieces that are in a circle further increase the fitness
    # There is no need to remove fitness if the pieces are near the castle, we just need to give better fitness to the pieces that are far
    # This heuristic HAS to be balanced with others, because it can lead to a situation where the white pieces are too far from the castle and the black pieces can easily win
    # The castle is at [4,4]
    fitness = 0
    for white in board.whites:
        fitness += gamma0 * ((white[0] - board.king[0])
                             ** 2 + (white[1] - board.king[1])**2)**0.5

    return fitness


def king_defence(board, theta0):
    fitness = 0
    # TODO: implement the special capture rule
    # King defence: If my king can be killed in the next move by the black player, apply a very strong negative fitness (static analysis)
    xking, yking = board.king
    if xking > 0:
        if board.pieces[xking-1][yking] == 1:
            # Check if there's a black piece that can kill the king on his RIGHT side
            for x in range(xking+1, len(board.pieces)):
                if board.pieces[x][yking] == 1 and board._is_there_a_clear_view(board.king, [x, yking]):
                    fitness += theta0
    if xking < len(board.pieces)-1:
        if board.pieces[xking+1][yking] == 1:
            # Check if there's a black piece that can kill the king on his LEFT side
            for x in range(xking-1, -1, -1):
                if board.pieces[x][yking] == 1 and board._is_there_a_clear_view(board.king, [x, yking]):
                    fitness += theta0
    if yking > 0:
        if board.pieces[xking][yking-1] == 1:
            # Check if there's a black piece that can kill the king on his TOP side
            for y in range(yking+1, len(board.pieces)):
                if board.pieces[xking][y] == 1 and board._is_there_a_clear_view(board.king, [xking, y]):
                    fitness += theta0
    if yking < len(board.pieces)-1:
        if board.pieces[xking][yking+1] == 1:
            # Check if there's a black piece that can kill the king on his TOP side
            for y in range(yking-1, -1, -1):
                if board.pieces[xking][y] == 1 and board._is_there_a_clear_view(board.king, [xking, y]):
                    fitness += theta0

    return fitness


# STATIC ANALYSIS (Gives the fitness of a STATIC board position)
def white_fitness(board, alpha0, beta0, gamma0, theta0, epsilon0):
    """
    Returns the float value of the current state of the board for white
    """

    fitness = 0
    fitness += is_white_gonna_be_eaten(board, alpha0)
    fitness += king_distance(board, beta0)
    fitness += external_pawn_more_fitness(board, gamma0)
    fitness += king_defence(board, theta0)
    # Number of pawns
    fitness += len(board.get_white())*epsilon0
    return fitness


# DYNAMIC ANALYSIS (analyze a move given in input)
# def white_fitness_dynamic(board: boardmanager, move: str, piece: int, alpha0, beta0, gamma0):
#    assert piece in [1, 2, 3], "piece should be 1 (black), 2(white) or 3(king)"
#    """
#    move must be written in the notation (x1,y1,x2,y2)
#    the board must be in the state BEFORE the move
#    piece is the piece that has been moved (1 black, 2 white, 3 king)
#    """
#    x1, y1, x2, y2 = move
#    local_pieces = copy.deepcopy(board.pieces)
#    local_pieces[x2][y2] = local_pieces[x1][y1]
#    local_pieces[x1][y1] = 0
#
#    if piece == 1:
#        local_whites = copy.deepcopy(board.whites)
#        # DO NOT CHANGE local_black and local_king SINCE THEY ARE REFERRING TO THE ACTUAL BOARD, THEY ARE READ ONLY
#        local_black = board.blacks
#        local_king = board.king
#        for white in local_whites:
#            if white[0] == x1 and white[1] == y1:
#                del white
#                break
#    elif piece == 2:
#        local_whites = board.whites
#        local_black = copy.deepcopy(board.blacks)
#        local_king = board.king
#        for black in local_black:
#            if black[0] == x1 and black[1] == y1:
#                del black
#                break
#    else:
#        local_whites = board.whites
#        local_black = board.blacks
#        local_king = copy.deepcopy(board.king)
#        local_king = [x2, y2]
#
#    fitness = 0
#    # Use only the local_XXXX variables in a read only way
#    if move in board.white_moves_to_eat:
#        fitness += alpha0
#
#    if piece == 3:
#        # A king bad position is a position if there are blacks around him
#        n_blacks = 0
#        if local_pieces[local_king[0]][local_king[1]+1] == 1:
#            n_blacks += 1
#        if local_pieces[local_king[0]+1][local_king[1]] == 1:
#            n_blacks += 1
#        if local_pieces[local_king[0]][local_king[1]-1] == 1:
#            n_blacks += 1
#        if local_pieces[local_king[0]-1][local_king[1]] == 1:
#            n_blacks += 1
#
#        fitness += n_blacks * beta0
#
#    # If my move get closer to a black piece, do that
#    if piece == 2:
#        n_blacks = 0
#        try:
#            if local_pieces[x2][y2+1] == 1:
#                n_blacks += 1
#        except:
#            pass
#        try:
#            if local_pieces[x2+1][y2] == 1:
#                n_blacks += 1
#        except:
#            pass
#        try:
#            if local_pieces[x2][y2-1] == 1:
#                n_blacks += 1
#        except:
#            pass
#        try:
#            if local_pieces[x2-1][y2] == 1:
#                n_blacks += 1
#        except:
#            pass
#        fitness += n_blacks * gamma0
#
#    return fitness
