import argparse

from aima.games import random_player, alpha_beta_search, GameState

from player import TablutPlayer
from utils import Network
from argList import argList

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Play a game of TABLUT')
    parser.add_argument("timelimit", help="The max time to compute a move")
    l = argList(["white", "black"])
    parser.add_argument("team", type=str, choices=l, help="The player's team [white/black]")
    parser.add_argument("name", type=str, help="The player's name")
    parser.add_argument("--ip", help="The ip of the server. Leave this blank to run locally")
    args = parser.parse_args()

    if not args.ip:
        args.ip = "localhost"

    network = Network(args.name, args.team, args.ip, timeout=args.timelimit) # TODO fix for localhost or just bind a socket to localhost and use it
    board, _, _  = network.connect()
    tp = TablutPlayer(args.team, args.timelimit, board)

    print("\nInitial State:")
    print(board)

    # Game Loop
    old_board = copy.deepcopy(board)
    goal = False
    i = 0

    while not goal:
        state = GameState(to_move=args.team, utility=tp.utility.evalutate_utility(old_board, board), board=board, moves=board.all_possible_moves(args.team))

        move = alpha_beta_search(state, tp, d=4) # TODO change d (depth)
        print(move)

        move = network.send_move(move)
        old_board = copy.deepcopy(board)

        # get new state
        board, turn, goal = network.get_state()
        i+=1

        # Summary
        print(f"\nMy {i}° move: {move}")
        print(board) # TODO print board with board.print_board
        print("\nWaiting for the opponent...")
        board, turn, goal = network.get_state()
        print(f"\nOpponent's {i}° move: {move}")
        print(board) # TODO print board with board.print_board