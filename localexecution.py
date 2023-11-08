import matplotlib.pyplot as plt
from boardmanager import Board, BadMoveException

def localrun(player_team : str, player_name : str, timelimit : int):
    """
    Simulate a game of TABLUT without connecting to the server

        Parameters:
            player_team (str): The player's team [white/black]
            player_name (str): The player's name
            timetimit (int): The timelimit to compute a move

        Returns:
            None
    """

    board = Board()

    conv = {
        0 : "A",
        1 : "B",
        2 : "C",
        3 : "D",
        4 : "E",
        5 : "F",
        6 : "G",
        7 : "H",
        8 : "I"
    }

    alpha0 = -5
    beta0 = 15
    gamma0 = 0.5
    theta0 = -1000
    epsilon0 = 2

    L = []
    for move in board.all_possible_moves("WHITE"):
        fit = 0
        fit += board.white_fitness_dynamic(move) + board.white_fitness(move, alpha0, beta0, gamma0, theta0,epsilon0)
        L.append((move, fit))
    L = sorted(L, key= lambda x: x[1], reverse=True)
    mv = L[0][0]
    mvstr = f"{conv[mv[1]]}{mv[0]+1}-{conv[mv[3]]}{mv[2]+1}"
    board.move(mvstr)

    fig, _ = board.print_board()

    while True:
        move = input("Fai una mossa: ")
        try:
            board.move(move)
        except BadMoveException as e:
            print(e)
        

        L = []
        for move in board.all_possible_moves("WHITE"):
            fit = 0
            fit += board.white_fitness_dynamic(move) + board.white_fitness(move, alpha0, beta0, gamma0, theta0,epsilon0)
            L.append((move, fit))
        L = sorted(L, key= lambda x: x[1], reverse=True)
        mv = L[0][0]
        mvstr = f"{conv[mv[0]]}{mv[1]+1}-{conv[mv[2]]}{mv[3]+1}"
        print(mvstr)
        board.move(mvstr)

        #print(mvstr, L[0][1])

        try:
            plt.close(fig) # TODO transform this into a generator (or dynamic update of the window) https://www.geeksforgeeks.org/how-to-update-a-plot-on-same-figure-during-the-loop/
        except:
            pass

        fig, _ = board.print_board()