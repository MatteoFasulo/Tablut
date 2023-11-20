import os
import sys
import random
import time

# threading
import threading

# concurrent futures
from concurrent.futures import ThreadPoolExecutor

# Tablut Class
from tablut import Tablut

# utils
from utils import Network


def random_player(game, state):
    return random.choice(list(game.actions(state)))


def player(search_algorithm):
    """A game player who uses the specified search algorithm"""
    return lambda game, state: search_algorithm(game, state)[1]


infinity = float('inf')


def cache(function):
    "Like lru_cache(None), but only considers the first argument of function."
    cache = {}

    def wrapped(x, *args):
        if x not in cache:
            cache[x] = function(x, *args)
        return cache[x]
    return wrapped


def cutoff_depth(d):
    """A cutoff function that searches to depth d."""
    return lambda game, state, depth: depth > d

# TODO change depth (d)


def h_alphabeta_search(game, state, cutoff=cutoff_depth(5), h=lambda s, p: 0):

    player = state.to_move

    @cache
    def max_value(state, alpha, beta, depth):
        if game.terminal_test(state):
            return game.utility(state, player), None
        if cutoff(game, state, depth):
            return h(state, player), None
        v, move = -infinity, None
        for a in game.actions(state):
            v2, _ = min_value(game.result(state, a), alpha, beta, depth + 1)
            if v2 > v:
                v, move = v2, a
                alpha = max(alpha, v)
            if v >= beta:
                return v, move
        return v, move

    @cache
    def min_value(state, alpha, beta, depth):
        if game.terminal_test(state):
            return game.utility(state, player), None
        if cutoff(game, state, depth):
            return h(state, player), None
        v, move = +infinity, None
        for a in game.actions(state):
            v2, _ = max_value(game.result(state, a), alpha, beta, depth + 1)
            if v2 < v:
                v, move = v2, a
                beta = min(beta, v)
            if v <= alpha:
                return v, move
        return v, move

    return max_value(state, -infinity, +infinity, 0)


def play_game(name: str, team: str, server_ip: str, timeout: int):
    # Clear the screen
    os.system('cls' if os.name == 'nt' else 'clear')

    # Initialize network
    network = Network(name, team, server_ip, timeout=timeout)
    # Get initial state and turn
    pieces, turn = network.connect()

    # Initialize game
    game = Tablut(team, pieces)
    game.update_state(pieces, turn)

    # Create a condition variable
    cond = threading.Condition()

    # Play game
    state = game.initial

    while not game.terminal_test(state):
        with cond:
            while not network.check_turn(player=team):
                print('Waiting for opponent move...')
                cond.wait(timeout=1)
                pieces, turn = network.get_state()

                print(f"PIECES:\n{pieces}")
                print(f"TURN:\n{turn}")

                # Update the game state for the current player
                game.update_state(pieces, turn)

            # Get move
            start = time.time()
            with ThreadPoolExecutor(max_workers=os.cpu_count() + 4) as executor:
                future = executor.submit(
                    h_alphabeta_search, game, state)
                move = future.result()[-1]
            end = time.time()

            print('Chosen move:', move)

            # Send move to server
            converted_move = game.convert_move(move)
            print("Converted move:", converted_move)
            network.send_move(converted_move)
            state.display()
            pieces, turn = network.get_state()

            # Update the game state for the current player
            game.update_state(pieces, turn)

            # Update state
            state = game.result(state, pieces)

            print('move:', converted_move, 'time: ', end-start, 's.')
            state.display()

            # Notify the other thread
            cond.notify_all()

    print('Game over!')


color = sys.argv[1]
name = sys.argv[2]
ip = sys.argv[3] if sys.argv[3] else 'localhost'
play_game(name=name, team=color, server_ip=ip, timeout=60)
