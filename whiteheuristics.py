import boardmanager

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


# TODO: implement the dynamic analysis logic
# If I can eat a black piece, I have to do it
# TODO: Does the king eat?
# What should I do with these moves?
def eat_black(pieces, whites):
    '''
    If a black piece can be eaten it returns a list of initial and final position of the white piece that eats
    '''
    moves_to_eat = []
    for white in whites:
        # Checking right
        for i in range(white[1]+2, len(pieces)-1, 1):
            if pieces[white[0]][i] == 1 and pieces[white[0]][i+1] == 2:
                moves_to_eat.append(white, [white[0], i-1])
        # Checking left
        for i in range(1, white[1]-1, 1):
            if pieces[white[0]][i] == 1 and pieces[white[0]][i-1] == 2:
                moves_to_eat.append(white, [white[0], i+1])
        # Checking up
        for i in range(1, white[0]-1, 1):
            if pieces[i][white[1]] == 1 and pieces[i-1][white[1]] == 2:
                moves_to_eat.append(white, [i+1, white[1]])
        # Checking down
        for i in range(white[0]+2, len(pieces)-1, 1):
            if pieces[i][white[1]] == 1 and pieces[i+1][white[1]] == 2:
                moves_to_eat.append(white, [i-1, white[1]])
    return moves_to_eat