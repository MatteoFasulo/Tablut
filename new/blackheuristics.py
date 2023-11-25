# Black heuristics
def black_fitness(board, alpha0, beta0, gamma0, theta0, epsilon0):
    """
    Black heuristics should be based on:
    - Number of black pawns
    - Number of white pawns
    - Number of black pawns next to the king
    - Free path to the king
    - A coefficient of encirclement of the king
    """

    fitness = 0

    king_pos = board.king

    # Number of black pawns
    fitness += alpha0 * len(board.blacks)

    # Number of white pawns
    fitness += beta0 * len(board.whites)

    # Number of black pawns next to the king
    fitness += gamma0 * 1

    # Free path to the king
    free_paths = [board._is_there_a_clear_view(black_pawn, king_pos)
                  for black_pawn in board.blacks]
    # theta0 times the n° free ways to king
    fitness += theta0 * sum(free_paths)

    # A coefficient of encirclement of the king
    fitness += epsilon0 * 1

    return fitness
