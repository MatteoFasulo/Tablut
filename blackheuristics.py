# Black heuristics
def black_fitness(board):
    """
    Black heuristics should be based on:
    - Number of black pawns
    - Number of white pawns
    - Number of black pawns next to the king
    - Free path to the king
    - A coefficient of encirclement of the king
    """

    fitness = 0

    alpha0, beta0, gamma0, theta0, epsilon0 = [0.958245251997756, 0.25688393654958275, 0.812052344592159, 0.9193347856045799, 1.7870310915100207]

    king_pos = board.get_king()

    # Number of black pawns
    fitness += alpha0 * len(board.blacks)

    # Number of white pawns
    fitness -= beta0 * len(board.whites)

    # Number of black pawns next to the king
    fitness += gamma0 * pawns_around(board, king_pos, distance=1)

    # Free path to the king
    free_paths = [board._is_there_a_clear_view(black_pawn, king_pos)
                  for black_pawn in board.blacks]
    # theta0 times the n° free ways to king
    fitness += theta0 * sum(free_paths)

    # norm_fitness = (fitness / (alpha0 * len(board.blacks) + gamma0 *
    #                           pawns_around(board, king_pos, distance=2) + theta0 * sum(free_paths)))

    # print("BLACK FITNESS: ", norm_fitness)

    return fitness


def pawns_around(board, pawn, distance: int):
    """
    Returns the number of pawns around a given pawn within a certain distance (usually the king)
    """
    x, y = pawn
    count = 0
    for i in range(-distance, distance+1):
        for j in range(-distance, distance+1):
            if i == 0 and j == 0:
                continue
            if (x+i, y+j) in board.blacks:
                count += 1
    return count
