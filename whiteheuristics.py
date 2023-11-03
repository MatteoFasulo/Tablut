#STATIC ANALYSIS (Gives the fitness of a STATIC board position)
def white_fitness(board, alpha0, beta0, gamma0):
        """
        Returns the float value of the current state of the board for white
        """

        fitness = 0
        for white in board.whites:
            #"Se alla mossa del nero vengo killato, bassa euristica"
            #I have to check if i have any adjacent black pieces, and if so i have to check if there is another one that could trap me
            #If i move between two black pieces, I can't get eaten so the fitness doesn't decrease
            if white[0] > 0:
                if board.pieces[white[0]-1][white[1]] == 1:
                    #Check the rows for any black piece
                    for i in range(white[0]+2, len(board.pieces), 1):
                        if board.pieces[white[0]][i] == 1:
                            if board._is_there_a_clear_view(white, [white[0],i]):
                                fitness += alpha0
                                break
            if white[0] < len(board.pieces)-1:
                if board.pieces[white[0]+1][white[1]] == 1:
                    #Check the rows for any black piece
                    for i in range(white[0]-2, -1, -1):
                        if board.pieces[white[0]][i] == 1:
                            if board._is_there_a_clear_view(white, [white[0],i]):
                                fitness += alpha0
                                break
            if white[1] > 0:
                if board.pieces[white[0]][white[1]-1] == 1:
                    #Check the columns for any black piece
                    for i in range(white[1]+2, len(board.pieces), 1):
                        if board.pieces[i][white[1]] == 1:
                            if board._is_there_a_clear_view(white, [i,white[1]]):
                                fitness += alpha0
                                break
            if white[1] < len(board.pieces)-1:
                if board.pieces[white[0]][white[1]+1] == 1:
                    #Check the columns for any black piece
                    for i in range(white[1]-2, -1, -1):
                        if board.pieces[i][white[1]] == 1:
                            if board._is_there_a_clear_view(white, [i,white[1]]):
                                fitness += alpha0
                                break

        #"Pedoni esterna euristica più alta"
        #Since the fitness is computed on a static board, and not on a move, I have to count the number of pieces _far_ from the castle. The further they are as a whole, the higher the fitness
        #Consider concetric circles around the castle, the pieces that are in a circle further increase the fitness
        #There is no need to remove fitness if the pieces are near the castle, we just need to give better fitness to the pieces that are far
        #This heuristic HAS to be balanced with others, because it can lead to a situation where the white pieces are too far from the castle and the black pieces can easily win
        #The castle is at [4,4]
        for white in board.whites:
            fitness += beta0 * ((white[0] - 4)**2 + (white[1] - 4)**2)**0.5

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


        return fitness