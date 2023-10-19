import matplotlib.pyplot as plt

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
        plt.show()

    def __convert_move(self, move):
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


    def __check_legality(self, x1,y1,x2,y2):
        #Check for diagonal movement
        if not (x1 == x2 or y1 == y2):
            print("NOT LEGAL DIAGONAL")
            return False
        
        #Check for Out of Bound movement
        if y2 >= 9 or x2 >= 9:
            print("NOT LEGAL OUTOFBOUND")
            return False

        #Check if you are moving a piece
        if self.pieces[x1][y1] == 0:
            print("NOT LEGAL NOTAPIECE")

            return False

        #Check if the destination square is already occupied
        if self.pieces[x2][y2] != 0:
            print("NOT LEGAL ALREADYOCCUPIED")

            return False
        
        #Check if the path is clear
        if x1 == x2:
            if y1 < y2:
                for i in range(y1+1,y2+1):
                    if self.pieces[x1][i] != 0:
                        print("PATHNOTCLEAR 1")

                        return False
            else:
                for i in range(y1-1,y2, -1):
                    if self.pieces[x1][i] != 0:
                        print("PATHNOTCLEAR 2")

                        return False
        else:
            if x1 < x2:
                for i in range(x1+1,x2+1):
                    if self.pieces[i][y1] != 0:
                        print("PATHNOTCLEAR 3")

                        return False
            else:
                for i in range(x1-1, x2, -1):
                    if self.pieces[i][y1] != 0:
                        print("PATHNOTCLEAR 4")

                        return False
        
        #Check if moving into a barrack from outside
        if self.board[x1][y1] in [WHITE, WHITE2] and self.board[x2][y2] in [RED, RED2]:
            print("NOT LEGAL ENTERINGABARRACK")
            return False
        #Check if moving into the castle
        if self.board[x1][y1] in [WHITE, WHITE2, RED, RED2, GREEN, GREEN2, GRAY] and self.board[x2][y2] == BLUE:
            print("NOT LEAGL ENTERINGCASTLE")
            return False
        return True
    



    def move(self, move):
        #TODO: implementare se la mossa è valida
        """
        Moves a piece on the board
            Parameters:
                move (str): a string representing the move, for example "A3-B3"
        """
        x1,y1,x2,y2 = self.__convert_move(move)
        if self.__check_legality(x1,y1,x2,y2):

            self.pieces[x2][y2] = self.pieces[x1][y1]
            self.pieces[x1][y1] = 0 
        else:
            raise BadMoveException(f"Your move {move} is not legal")

