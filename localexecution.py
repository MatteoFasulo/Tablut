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
    print(f"White heuristic: {board.white_fitness(-1,1)}")
    board.print_board()

    while True:
        move = input("Fai una mossa: ")
        try:
            board.move(move)
        except BadMoveException as e:
            print(e)
        
        print(f"White heuristic: {board.white_fitness(-2,1)}")

        board.print_board()