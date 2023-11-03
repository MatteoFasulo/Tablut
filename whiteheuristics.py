import boardmanager
import copy

def white_fitness(pieces, whites,alpha0, beta0):
        """
        Returns the float value of the current state of the board for white
        """

        fitness = 0
        for white in whites:
            #"Se alla mossa del nero vengo killato, bassa euristica"
            #I have to check if i have any adjacent black pieces, and if so i have to check if there is another one that could trap me
            #If i move between two black pieces, I can't get eaten so the fitness doesn't decrease
            if white[0] > 0:
                if pieces[white[0]-1][white[1]] == 1:
                    #Check the rows for any black piece
                    for i in range(white[0]+2, len(pieces), 1):
                        if pieces[white[0]][i] == 1:
                            if boardmanager._is_there_a_clear_view(white, [white[0],i]):
                                fitness += alpha0
                                break
            if white[0] < len(pieces)-1:
                if pieces[white[0]+1][white[1]] == 1:
                    #Check the rows for any black piece
                    for i in range(white[0]-2, -1, -1):
                        if pieces[white[0]][i] == 1:
                            if boardmanager._is_there_a_clear_view(white, [white[0],i]):
                                fitness += alpha0
                                break
            if white[1] > 0:
                if pieces[white[0]][white[1]-1] == 1:
                    #Check the columns for any black piece
                    for i in range(white[1]+2, len(pieces), 1):
                        if pieces[i][white[1]] == 1:
                            if boardmanager._is_there_a_clear_view(white, [i,white[1]]):
                                fitness += alpha0
                                break
            if white[1] < len(pieces)-1:
                if pieces[white[0]][white[1]+1] == 1:
                    #Check the columns for any black piece
                    for i in range(white[1]-2, -1, -1):
                        if pieces[i][white[1]] == 1:
                            if boardmanager._is_there_a_clear_view(white, [i,white[1]]):
                                fitness += alpha0
                                break

        #"Pedoni esterna euristica più alta"
        #Since the fitness is computed on a static board, and not on a move, I have to count the number of pieces _far_ from the castle. The further they are as a whole, the higher the fitness
        #Consider concetric circles around the castle, the pieces that are in a circle further increase the fitness
        #There is no need to remove fitness if the pieces are near the castle, we just need to give better fitness to the pieces that are far
        #This heuristic HAS to be balanced with others, because it can lead to a situation where the white pieces are too far from the castle and the black pieces can easily win
        #The castle is at [4,4]
        for white in whites:
            fitness += beta0 * ((white[0] - 4)**2 + (white[1] - 4)**2)**0.5

        return fitness


#DYNAMIC ANALYSIS (analyze a move given in input)
def white_fitness_dynamic(board : boardmanager, move : str, piece : int):
    assert piece in [1,2,3], "piece should be 1 (black), 2(white) or 3(king)"
    """
    move must be written in the notation XY-XY, for example A1-A3 and must be a legal move (no check for legality)
    the board must be in the state BEFORE the move
    piece is the piece that has been moved (1 black, 2 white, 3 king)
    """
    x1,y1,x2,y2 = board._convert_move(move)
    local_pieces = copy.deepcopy(board.pieces)
    local_pieces[x2][y2] = local_pieces[x1][y1]
    local_pieces[x1][y1] = 0

    if piece == 1:
        local_whites = copy(board.whites)
        #DO NOT CHANGE local_black and local_king SINCE THEY ARE REFERRING TO THE ACTUAL BOARD, THEY ARE READ ONLY
        local_black = board.blacks
        local_king = board.king
        for white in local_whites:
            if white[0] == x1 and white[1] == y1:
                del white
                break
    elif piece == 2:
        local_whites = board.whites
        local_black = copy(board.blacks)
        local_king = board.king
        for black in local_black:
            if black[0] == x1 and black[1] == y1:
                del black
                break
    else:
        local_whites = board.whites
        local_black = board.blacks
        local_king = copy(board.king)
        local_king = [x2,y2]

    #Use only the local_XXXX variables in a read only way