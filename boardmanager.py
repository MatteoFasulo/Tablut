import matplotlib.pyplot as plt
import whiteheuristics
import copy

######## COSTANTS ########
GRAY = (150,150,150)
WHITE = (200,200,200)
WHITE2 = (180,180,180)
RED = (255,0,0)
RED2 = (200,0,0)
GREEN = (0,255,0)
GREEN2 = (0,200,0)
BLUE = (0,0,255)
##########################

class BadMoveException(Exception):
    def __init__(self, msg):
        super().__init__(msg)

class Board():
    def __init__(self):
        """
        Instances a board
        """
        #This list of lists represents the color of the board
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
        #This list of lists is the pieces, 0 is an empty square, 1 is a black piece, 2 is a white piece and 3 is the king
        self.pieces = [
            [0,0,0,1,1,1,0,0,0],
            [0,0,0,0,1,0,0,0,0],
            [0,0,0,0,2,0,0,0,0],
            [1,0,0,0,2,0,0,0,1],
            [1,1,2,2,3,2,2,1,1],
            [1,0,0,0,2,0,0,0,1],
            [0,0,0,0,2,0,0,0,0],
            [0,0,0,0,1,0,0,0,0],
            [0,0,0,1,1,1,0,0,0],
        ]

        self.king = [4,4]

        self.whites = [
            [2,4],
            [3,4],
            [4,2],
            [4,3],
            [4,5],
            [4,6],
            [5,4],
            [6,4]
        ]

        self.blacks = [
            [0,3],
            [0,4],
            [0,5],
            [1,4],
            [3,0],
            [3,8],
            [4,0],
            [4,1],
            [4,7],
            [4,8],
            [5,0],
            [5,8],
            [7,4],
            [8,3],
            [8,4],
            [8,5]
        ]

        self.white_moves_to_eat = []


    def reset_board(self):
        """
        Resets the board to its original state
        """
        self.__init__()

    def print_board(self):
        """
        Prints the board using matplotlib
        """
        fig, ax = plt.subplots()
        ax.matshow(self.board, cmap="Greys")
        #Changes the size of the pieces
        fontsize = 30

        #Places the pieces on the board
        for row in range(len(self.pieces)):
            for piece in range(len(self.pieces[row])):
                char = '⛀' if self.pieces[row][piece] == 2 else "⛂" if self.pieces[row][piece] == 1 else "⛁" if self.pieces[row][piece] == 3 else ""
                color = "black" if self.pieces[row][piece] == 1 else "white"
                ax.text(row, piece, char, ha='center', va='center', color=color, fontsize=fontsize)
        
        plt.box(on=None)
        ax.set_xticks([0,1,2,3,4,5,6,7,8])
        ax.set_yticks([0,1,2,3,4,5,6,7,8])
        ax.set_xticklabels(['A','B','C','D','E','F','G','H','I'])
        ax.set_yticklabels(['1','2','3','4','5','6','7','8','9'])
        plt.show(block=False)
        return fig, ax

    def _convert_move(self, move):
        if not isinstance(move, str):
            return move
            
        chars = ["A", "B", "C", "D", "E", "F", "G", "H", "I"]
        x1 = None
        y1 = None
        x2 = None
        y2 = None
        #Controllo sintattico sulla mossa
        for c in move:
            if c == "-":
                continue
            elif c in chars:
                if x1 == None:
                    x1 = chars.index(c)
                elif x2 == None:
                    x2 = chars.index(c)
                else:
                    raise BadMoveException(f"The move {move} is not written correctly")
            elif c in "123456789":
                if y1 == None:
                    y1 = int(c) - 1
                elif y2 == None:
                    y2 = int(c) - 1
                else:
                    raise BadMoveException(f"The move {move} is not written correctly")
            else:
                raise BadMoveException(f"The move {move} is not written correctly")
        return x1, y1, x2, y2


    def check_legality(self, x1,y1,x2,y2):
        #Check for diagonal movement
        if not (x1 == x2 or y1 == y2):
            return False
        
        #Check for Out of Bound movement
        if y2 >= 9 or x2 >= 9:
            return False

        #Check if you are moving a piece
        if self.pieces[x1][y1] == 0:

            return False

        #Check if the destination square is already occupied
        if self.pieces[x2][y2] != 0:

            return False
        
        #Check if the path is clear
        if x1 == x2:
            if y1 < y2:
                for i in range(y1+1,y2+1):
                    if self.pieces[x1][i] != 0:

                        return False
            else:
                for i in range(y1-1,y2, -1):
                    if self.pieces[x1][i] != 0:

                        return False
        else:
            if x1 < x2:
                for i in range(x1+1,x2+1):
                    if self.pieces[i][y1] != 0:

                        return False
            else:
                for i in range(x1-1, x2, -1):
                    if self.pieces[i][y1] != 0:

                        return False
        
        #Check if moving into a barrack from outside
        if self.board[x1][y1] in [WHITE, WHITE2] and self.board[x2][y2] in [RED, RED2]:
            return False
        #Check if moving into the castle
        if self.board[x1][y1] in [WHITE, WHITE2, RED, RED2, GREEN, GREEN2, GRAY] and self.board[x2][y2] == BLUE:
            return False
        return True
    
    def __check_attacks(self, x, y):
        #TODO: controllo di mangiata (guardare le regole perché non è chiaro) con solamente un pezzo (e quindi quando ci sono tipo i muri di mezzo)
        #Horizontal check
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
        #Vertical check
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
        


    def move(self, move):
        """
        Moves a piece on the board
            Parameters:
                move (str): a string representing the move, for example "A3-B3"
        """
        x1,y1,x2,y2 = self._convert_move(move)
        if self.check_legality(x1,y1,x2,y2):
            self.pieces[x2][y2] = self.pieces[x1][y1]
            self.pieces[x1][y1] = 0 
            for p in self.whites:
                if p[0] == x1 and p[1] == y1:
                    p[0] = x2
                    p[1] = y2
                    break
            for p in self.blacks:
                if p[0] == x1 and p[1] == y1:
                    p[0] = x2
                    p[1] = y2
                    break
            if self.king[0] == x1 and self.king[1] == y1:
                self.king = [x2,y2]
            self.__check_attacks(x2,y2)
        else:
            raise BadMoveException(f"Your move {move} is not legal")
    
        self.eat_black()
        
    def _is_there_a_clear_view(self,piece1,piece2):
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
        
    #FIXME: Controllare che non usi troppa memoria
    def white_fitness(self, move, alpha0, beta0, gamma0):
        tmp_board = Board()
        tmp_board.pieces = copy.deepcopy(self.pieces)
        tmp_board.blacks = copy.deepcopy(self.blacks)
        tmp_board.whites = copy.deepcopy(self.whites)
        tmp_board.king = copy.deepcopy(self.king)

        tmp_board.pieces[move[2]][move[3]] = tmp_board.pieces[move[0]][move[1]]
        tmp_board.pieces[move[0]][move[1]] = 0

        if tmp_board.pieces[move[2]][move[3]] == 1:
            for black in tmp_board.blacks:
                if black[0] == move[0] and black[1] == move[1]:
                    black[0] = move[2]
                    black[0] = move[3]
        elif tmp_board.pieces[move[2]][move[3]] == 2:
            for white in tmp_board.whites:
                if white[0] == move[0] and white[1] == move[1]:
                    white[0] = move[2]
                    white[0] = move[3]
        else:
            tmp_board.king = [move[2], move[3]]


        return whiteheuristics.white_fitness(tmp_board, alpha0, beta0, gamma0)
    
    def white_fitness_dynamic(self, move):
        piece = self.pieces[move[0]][move[1]]
        return whiteheuristics.white_fitness_dynamic(self, move, piece, alpha0=10000)

    def all_possible_moves(self, player):
        moves = []
        if player == "WHITE":
            pawns = self.whites + [self.king]
        elif player == "BLACK":
            pawns = self.blacks
        
        for pawn in pawns:
            #Check right moves
            for i in range(pawn[1]+1, len(self.pieces)):
                if self.check_legality(pawn[0], pawn[1], pawn[0], i):
                    moves.append([pawn[0], pawn[1], pawn[0], i])

            #Check left moves
            for i in range(0, pawn[1]):
                if self.check_legality(pawn[0], pawn[1], pawn[0], i):
                    moves.append([pawn[0], pawn[1], pawn[0], i])

            #Check top moves
            for i in range(pawn[0]+1, len(self.pieces)):
                if self.check_legality(pawn[0], pawn[1], i, pawn[1]):
                    moves.append([pawn[0], pawn[1], i, pawn[1]])

            #Check bottom moves
            for i in range(0, pawn[0]):
                if self.check_legality(pawn[0], pawn[1], i, pawn[1]):
                    moves.append([pawn[0], pawn[1], i, pawn[1]])

        return moves
    

    # TODO: implement the dynamic analysis logic
    # If I can eat a black piece, I have to do it
    # TODO: Does the king eat? If so, remember to put [] when concatenation with whites
    # TODO: Special capture rules
    def eat_black(self):
        '''
        If a black piece can be eaten it returns a list of initial and final position of the white piece that eats
        '''
        #TODO: manage possible exception
        #TODO: If a piece can capture more than one enemy in a move, give more fitness to that move
        moves_to_eat = []
        for white in self.whites:
            # Checking right
            for i in range(white[1]+1, len(self.pieces)-1, 1):
                try:
                    if self.pieces[white[0]+1][i] == 1 and self.pieces[white[0]+2][i] == 2 and self.check_legality(white[0],white[1], white[0], i):
                        moves_to_eat.append([white[0],white[1], white[0], i])
                    if self.pieces[white[0]-1][i] == 1 and self.pieces[white[0]-2][i] == 2 and self.check_legality(white[0],white[1], white[0], i):
                        moves_to_eat.append([white[0],white[1], white[0], i]) 
                except:
                    pass
                if self.pieces[white[0]][i] == 1 and self.pieces[white[0]][i+1] == 2 and self.check_legality(white[0], white[1], white[0], i-1):
                    moves_to_eat.append([white[0], white[1], white[0], i-1])
                    break
            # Checking left
            for i in range(0, white[1]):
                try:
                    if self.pieces[white[0]+1][i] == 1 and self.pieces[white[0]+2][i] == 2 and self.check_legality(white[0],white[1], white[0], i):
                        moves_to_eat.append([white[0],white[1], white[0], i])
                    if self.pieces[white[0]-1][i] == 1 and self.pieces[white[0]-2][i] == 2 and self.check_legality(white[0],white[1], white[0], i):
                        moves_to_eat.append([white[0],white[1], white[0], i]) 
                except:
                    pass
                if self.pieces[white[0]][i] == 1 and self.pieces[white[0]][i-1] == 2 and self.check_legality(white[0], white[1], white[0], i+1):
                    moves_to_eat.append([white[0], white[1], i+1])
                    break
            # Checking up
            for i in range(0, white[0]):
                try:
                    if self.pieces[i][white[1]+1] == 1 and self.pieces[i][white[1]+2] == 2 and self.check_legality(white[0],white[1], i, white[1]):
                        moves_to_eat.append([white[0],white[1], i, white[1]])
                    if self.pieces[i][white[1]-1] == 1 and self.pieces[i][white[1]-2] == 2 and self.check_legality(white[0],white[1], i, white[1]):
                        moves_to_eat.append([white[0],white[1], i, white[1]]) 
                except:
                    pass
                if self.pieces[i][white[1]] == 1 and self.pieces[i-1][white[1]] == 2 and self.check_legality(white[0], white[1], i+1, white[1]):
                    moves_to_eat.append([white[0], white[1], i+1, white[1]])
                    break
            # Checking down
            for i in range(white[0]+1, len(self.pieces)-1, 1):
                try:
                    if self.pieces[i][white[1]+1] == 1 and self.pieces[i][white[1]+2] == 2 and self.check_legality(white[0],white[1], i, white[1]):
                        moves_to_eat.append([white[0],white[1], i, white[1]])
                    if self.pieces[i][white[1]-1] == 1 and self.pieces[i][white[1]-2] == 2 and self.check_legality(white[0],white[1], i, white[1]):
                        moves_to_eat.append([white[0],white[1], i, white[1]]) 
                except:
                    pass
                if self.pieces[i][white[1]] == 1 and self.pieces[i+1][white[1]] == 2 and self.check_legality(white[0], white[1], i-1, white[1]):
                    moves_to_eat.append([white[0], white[1], i-1, white[1]])
                    break



        self.white_moves_to_eat = moves_to_eat


    def moves_to_eat_king(self):
        if self.king == [4,4]:
            self.black_moves_to_eat_king = self.eat_king_in_castle()
        else:
            self.black_moves_to_eat_king = self.eat_king_outside_castle()


    def eat_king_in_castle(self):
        '''
        You should check if the king is in the castle before calling this function
        It returns starting and ending position of the piece that can eat the king, otherwise it returns [-1,-1], [-1,-1]
        '''
        position = self.check_sourrounded_king_castle()
        if position == [-1,-1]:
            return position + position
        for black in self.blacks:
            if self.check_legality(black[0], black[1], position[0], position[1]):
                return black, position
        return [[-1,-1], [-1,-1]]



    def check_sourrounded_king_castle(self):
        '''
        It returns the coordinates of one of the four tiles around the king, if the other three are occupied by three blacks
        It returns [-1,-1] if the king is not sorrounded or he's not in the castle
        '''
        if self.pieces[4][3] == 1 and self.pieces[3][4] == 1 and self.pieces[4][5] == 1:
            return [5,4]
        if self.pieces[4][3] == 1 and self.pieces[5][4] == 1 and self.pieces[4][5] == 1:
            return [3,4]
        if self.pieces[5][4] == 1 and self.pieces[3][4] == 1 and self.pieces[4][5] == 1:
            return [4,3]
        if self.pieces[4][3] == 1 and self.pieces[3][4] == 1 and self.pieces[5][4] == 1:
            return [4,5]
        return [-1,-1]



    def check_sourrounded_king_outside(self):
        '''
        It returns a list of possible moves to eat the king, when he's outside the castle
        If there isn't any feasable move, it returns [-1,-1]
        '''
        r, c = self.king
        tiles = []
        if self.pieces[r][c-1] == 1:
            tiles.append([r, c+1])
        elif self.pieces[r][c+1] == 1:
            tiles.append([r, c-1])
        if self.pieces[r-1][c] == 1:
            tiles.append([r+1][c])
        elif self.pieces[r+1][c] == 1:
            tiles.append([r-1][c])
        return tiles if len(tiles) > 0 else [-1,-1]



    def eat_king_outside_castle(self):
        '''
        You should check if the king is not in the castle before calling this function
        It returns starting and ending position of the piece that can eat the king, otherwise it returns [[-1,-1], [-1,-1]]
        '''
        position = self.check_sourrounded_king_outside()
        if position == [-1,-1]:
            return position + position
        for black in self.blacks:
            if self.check_legality(black[0], black[1], position[0][0], position[0][1]):
                return [black, [position[0][0], position[0][1]]]
            if len(position) == 2 and self.check_legality(black[0], black[1], position[1][0], position[1][1]):
                return [black, [position[1][0], position[1][1]]]
        return [[-1,-1], [-1,-1]]        