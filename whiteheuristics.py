import boardmanager
import copy

#STATIC ANALYSIS (Gives the fitness of a STATIC board position)
def white_fitness(board, alpha0, beta0, gamma0, theta0):
        """
        Returns the float value of the current state of the board for white
        """

        fitness = 0
        for white in board.whites:
            if white[0] > 0 and board.pieces[white[0]-1][white[1]] == 1:
                for i in range(white[0]+2, len(board.pieces)):
                    if i < len(board.pieces) and board.pieces[i][white[1]] == 1:
                        if board._is_there_a_clear_view(white, [i,white[1]]):
                            fitness += alpha0
                            break

            if white[0] < len(board.pieces)-1 and board.pieces[white[0]+1][white[1]] == 1:
                for i in range(white[0]-2, -1, -1):
                    if i >= 0 and board.pieces[i][white[1]] == 1:
                        if board._is_there_a_clear_view(white, [i,white[1]]):
                            fitness += alpha0
                            break

            if white[1] > 0 and board.pieces[white[0]][white[1]-1] == 1:
                for i in range(white[1]+2, len(board.pieces)):
                    if i < len(board.pieces) and board.pieces[white[0]][i] == 1:
                        if board._is_there_a_clear_view(white, [white[0],1]):
                            fitness += alpha0
                            break

            if white[1] < len(board.pieces)-1 and board.pieces[white[0]][white[1]+1] == 1:
                for i in range(white[1]-2, -1, -1):
                    if i >= 0 and board.pieces[white[0]][i] == 1:
                        if board._is_there_a_clear_view(white, [white[0],i]):
                            fitness += alpha0
                            break
        #"Pedoni esterna euristica più alta"
        #Since the fitness is computed on a static board, and not on a move, I have to count the number of pieces _far_ from the castle. The further they are as a whole, the higher the fitness
        #Consider concetric circles around the castle, the pieces that are in a circle further increase the fitness
        #There is no need to remove fitness if the pieces are near the castle, we just need to give better fitness to the pieces that are far
        #This heuristic HAS to be balanced with others, because it can lead to a situation where the white pieces are too far from the castle and the black pieces can easily win
        #The castle is at [4,4]
        for white in board.whites:
            fitness += beta0 * ((white[0] - board.king[0])**2 + (white[1] - board.king[1])**2)**0.5

        #TODO: implement the special capture rule
        #King defence: If my king can be killed in the next move by the black player, apply a very strong negative fitness (static analysis)
        xking, yking = board.king
        if xking > 0:
            if board.pieces[xking-1][yking] == 1:
                #Check if there's a black piece that can kill the king on his RIGHT side
                for x in range(xking+1, len(board.pieces)):
                    if board.pieces[x][yking] == 1 and board._is_there_a_clear_view(board.king, [x, yking]):
                        fitness += gamma0
        if xking < len(board.pieces)-1:
            if board.pieces[xking+1][yking] == 1:
                #Check if there's a black piece that can kill the king on his LEFT side
                for x in range(xking-1, -1, -1):
                    if board.pieces[x][yking] == 1 and board._is_there_a_clear_view(board.king, [x, yking]):
                        fitness += gamma0
        if yking > 0:
            if board.pieces[xking][yking-1] == 1:
                #Check if there's a black piece that can kill the king on his TOP side
                for y in range(yking+1, len(board.pieces)):
                    if board.pieces[xking][y] == 1 and board._is_there_a_clear_view(board.king, [xking, y]):
                        fitness += gamma0
        if yking < len(board.pieces)-1:
            if board.pieces[xking][yking+1] == 1:
                #Check if there's a black piece that can kill the king on his TOP side
                for y in range(yking-1, -1, -1):
                    if board.pieces[xking][y] == 1 and board._is_there_a_clear_view(board.king, [xking, y]):
                        fitness += gamma0

        #Number of pawns
        fitness += len(board.whites)*theta0

        return fitness







#DYNAMIC ANALYSIS (analyze a move given in input)
def white_fitness_dynamic(board : boardmanager, move : str, piece : int, alpha0, beta0, gamma0):
    assert piece in [1,2,3], "piece should be 1 (black), 2(white) or 3(king)"
    """
    move must be written in the notation (x1,y1,x2,y2)
    the board must be in the state BEFORE the move
    piece is the piece that has been moved (1 black, 2 white, 3 king)
    """
    x1,y1,x2,y2 = move
    local_pieces = copy.deepcopy(board.pieces)
    local_pieces[x2][y2] = local_pieces[x1][y1]
    local_pieces[x1][y1] = 0

    if piece == 1:
        local_whites = copy.deepcopy(board.whites)
        #DO NOT CHANGE local_black and local_king SINCE THEY ARE REFERRING TO THE ACTUAL BOARD, THEY ARE READ ONLY
        local_black = board.blacks
        local_king = board.king
        for white in local_whites:
            if white[0] == x1 and white[1] == y1:
                del white
                break
    elif piece == 2:
        local_whites = board.whites
        local_black = copy.deepcopy(board.blacks)
        local_king = board.king
        for black in local_black:
            if black[0] == x1 and black[1] == y1:
                del black
                break
    else:
        local_whites = board.whites
        local_black = board.blacks
        local_king = copy.deepcopy(board.king)
        local_king = [x2,y2]

    fitness = 0
    #Use only the local_XXXX variables in a read only way
    if move in board.white_moves_to_eat:
        fitness += alpha0

    if piece == 3:
        #A king bad position is a position if there are blacks around him
        n_blacks = 0
        if local_pieces[local_king[0]][local_king[1]+1] == 1:
            n_blacks += 1
        if local_pieces[local_king[0]+1][local_king[1]] == 1:
            n_blacks += 1
        if local_pieces[local_king[0]][local_king[1]-1] == 1:
            n_blacks += 1
        if local_pieces[local_king[0]-1][local_king[1]] == 1:
            n_blacks += 1
        
        fitness += n_blacks * beta0


    #If my move get closer to a black piece, do that
    if piece == 2:
        n_blacks = 0
        try:
            if local_pieces[x2][y2+1] == 1:
                n_blacks += 1
        except:
            pass
        try:
            if local_pieces[x2+1][y2] == 1:
                n_blacks += 1
        except:
            pass
        try:
            if local_pieces[x2][y2-1] == 1:
                n_blacks += 1
        except:
            pass
        try:
            if local_pieces[x2-1][y2] == 1:
                n_blacks += 1
        except:
            pass
        fitness += n_blacks * gamma0
            
    return fitness
