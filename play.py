import argparse
import time
import copy

# numpy
import numpy as np

# threading
import threading

# Tablut Class
from tablut import Tablut
from board import Board

# utils
from utils import Network, WinException

from whiteheuristics import king_surrounded


def cache(function):
    """
    A decorator that caches the result of a function based on its arguments.

    Args:
        function: The function to be cached.

    Returns:
        The wrapped function that caches the result.
    """
    cache = {}

    def wrapped(x, *args, **kwargs):
        pieces = x.pieces.data.tobytes()
        if pieces not in cache:
            cache[pieces] = function(x, *args, **kwargs)
        return cache[pieces]
    return wrapped


def cutoff_depth(d):
    """
    Returns a function that determines if the search should be cut off at a certain depth.

    Parameters:
    d (int): The maximum depth at which the search should be cut off.

    Returns:
    function: A function that takes the current game, state, and depth as parameters and returns True if the search should be cut off, False otherwise.
    """
    return lambda game, state, depth: depth > d


def h_alphabeta_search(state, game, cutoff, time_limit=55):
    """
    Performs a heuristic alpha-beta search to find the best move for a given game state.

    Args:
        state: The current game state.
        game: The game object representing the rules of the game.
        cutoff: The cutoff function that determines when to stop the search.
        time_limit: The maximum time limit for the search.

    Returns:
        The best move to be played from the current state.
    """
    player = state.to_move
    backtrack_dict = dict()

    @cache
    def max_value(state, alpha, beta, depth, action_backtrack=None):
        nonlocal backtrack_dict
        if game.terminal_test(state, player):
            return game.utility(state, player), None
        if cutoff(game, state, depth):
            return game.compute_utility(
                state, player), None
        if time.time() - start_time > time_limit:
            best_action = max(backtrack_dict, key=backtrack_dict.get)
            print("TIMEOUT: ", best_action)
            raise TimeoutError(best_action)
        v, move = -np.inf, None
        if isinstance(state, Tablut):
            pieces = copy.deepcopy(state.initial.pieces)
            board = state.initial.board
        elif isinstance(state, Board):
            pieces = copy.deepcopy(state.pieces)
            board = state.board
        for a in game.actions(pieces, player, board):
            if depth == 0:
                from_pos, to_pos = a
                if from_pos == state.get_king() and to_pos in state.winning_positions:
                    print("WINNING POSITION 1")
                    raise WinException(a)
                if from_pos in state.blacks:
                    king_pos = state.get_king()
                    coef, blocked_pos = king_surrounded(state)
                    if king_pos == (4, 4) and coef == 3 and to_pos in [(3, 4), (5, 4), (4, 3), (4, 5)]:
                        print("WINNING POSITION 2")
                        raise WinException(a)
                    elif king_pos != (4, 4) and coef > 0:
                        new_state = game.result(state, a)
                        _, new_blocked_pos = king_surrounded(new_state)
                        # Check if there are two pawns in new_blocked_pos which have same row or same column
                        if any(p1[0] == p2[0] or p1[1] == p2[1] and p1 != p2 for p1 in new_blocked_pos for p2 in new_blocked_pos):
                            print("WINNING POSITION 3")
                        raise WinException(a)

                action_backtrack = a
                backtrack_dict[a] = 0
            v2, _ = min_value(game.result(state, a), alpha,
                              beta, depth+1, action_backtrack)
            if v2 > v:
                v, move = v2, a
                alpha = max(alpha, v)
                backtrack_dict[action_backtrack] = v
            if v >= beta:
                return v, move
        return v, move

    @cache
    def min_value(state, alpha, beta, depth, action_backtrack):
        nonlocal backtrack_dict
        if game.terminal_test(state, player):
            return game.utility(state, player), None
        if cutoff(game, state, depth):
            return game.compute_utility(
                state, player), None
        if time.time() - start_time > time_limit:
            best_action = max(backtrack_dict, key=backtrack_dict.get)
            print("TIMEOUT: ", best_action)
            raise TimeoutError(best_action)
        v, move = +np.inf, None
        if isinstance(state, Tablut):
            pieces = copy.deepcopy(state.initial.pieces)
            board = state.initial.board  # red2...
        elif isinstance(state, Board):
            pieces = copy.deepcopy(state.pieces)
            board = state.board
        for a in game.actions(pieces, player, board):
            v2, _ = max_value(game.result(state, a),
                              alpha, beta, depth+1, action_backtrack)
            if v2 < v:
                v, move = v2, a
                beta = min(beta, v)
            if v <= alpha:
                return v, move
        return v, move

    start_time = time.time()
    try:
        result = max_value(state, -np.inf, +np.inf, 0)[-1]
    except TimeoutError as e:
        result = e.args[0]
    except WinException as e:
        result = e.args[0]
    return result


def play_game(name: str, team: str, server_ip: str, timeout: int):
    # Clear the screen
    # os.system('cls' if os.name == 'nt' else 'clear')

    # Initialize game
    game = Tablut()

    cond = threading.Condition()

    # Initialize network
    network = Network(name, team, server_ip, timeout=timeout)

    # Get initial state and turn
    pieces, turn = network.connect()

    game.update_state(pieces, turn)

    # Play game
    state = game.initial
    while True:
        with cond:
            while not network.check_turn(player=team):
                cond.wait(timeout=1)
                pieces, turn = network.get_state()
                if type(pieces) != int:
                    game.update_state(pieces, turn)
                else:
                    return pieces, turns

            # Get move
            move = h_alphabeta_search(
                state, game, cutoff_depth(2), time_limit=timeout-5)  # 5 seconds of tolerance for sending the move

            # Send move to server
            converted_move = game.convert_move(move)
            network.send_move(converted_move)
            try:
                pieces, turn = network.get_state()
            except:
                return 3, turns
            if type(pieces) != int:
                # Update the game state for the current player
                game.update_state(pieces, turn)
            else:
                return pieces, turns

            # Update the game state for the current player
            game.update_state(pieces, turn)

            # Update state
            state = copy.copy(game)
            state = state.initial

            # Notify the other thread
            cond.notify_all()


if __name__ == "__main__":
    argparse = argparse.ArgumentParser()

    argparse.add_argument(
        "--team", help="The color of the player: WHITE or BLACK", type=str.upper, choices=["WHITE", "BLACK"], required=True),
    argparse.add_argument(
        "--name", help="The name of the player", type=str, default='\tLut')
    argparse.add_argument(
        "--ip", help="The IP address of the server", type=str, default="localhost")
    argparse.add_argument(
        "--timeout", help="The timeout for the server", type=int, default=60)
    args = argparse.parse_args()

    result, turns = play_game(
        name=args.name, team=args.team, server_ip=args.ip, timeout=args.timeout)
