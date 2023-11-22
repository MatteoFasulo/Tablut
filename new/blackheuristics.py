
# DYNAMIC ANALYSIS (analyze a move given in input)
def black_fitness_dynamic(board, move: str, piece: int, func, alpha0, beta0, gamma0):
    assert piece in [1, 2, 3], "piece should be 1 (black), 2(white) or 3(king)"
    """
    move must be written in the notation (x1,y1,x2,y2)
    the board must be in the state BEFORE the move
    piece is the piece that has been moved (1 black, 2 white, 3 king)
    """
    fitness = 0
    from_pos, to_pos = move
    x1, y1 = from_pos
    x2, y2 = to_pos
    [[x1_eat_king, x2_eat_king], [y1_eat_king, y2_eat_king]] = func

    if x1 == x1_eat_king and x2 == x2_eat_king and y1 == y1_eat_king and y2 == y2_eat_king:
        fitness += alpha0  # alpha0 should be high because this move makes black win

    return fitness
