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

from board import Board


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


def h_alphabeta_search(game, state, cutoff=cutoff_depth(10)):
    """Search game to determine best action; use alpha-beta pruning.
    As in [Figure 5.7], this version searches all the way to the leaves."""

    player = state.to_move

    @cache
    def max_value(state, alpha, beta, depth):
        if game.terminal_test(state):
            return game.utility(state, player), None
        if cutoff(game, state, depth):
            print("CUTOFF")
            return game.compute_utility(state), None
        v, move = -infinity, None
        for a in game.actions(state):
            v2, _ = min_value(game.result(state, a), alpha, beta, depth+1)
            print("MIN VALUE: ", v2)
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
            print("CUTOFF")
            return game.compute_utility(state), None
        v, move = +infinity, None
        for a in game.actions(state):
            print(a)
            v2, _ = max_value(game.result(state, a), alpha, beta, depth + 1)
            print("MAX VALUE: ", v2)
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
    game = Tablut()
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

                # Update the game state for the current player
                game.update_state(pieces, turn)

            # Get move
            start = time.time()
            with ThreadPoolExecutor(max_workers=os.cpu_count() + 4) as executor:
                future = executor.submit(
                    h_alphabeta_search, game, state)
                move = future.result()[-1]

                # Idea (calculate another move in parallel from the result of the first best move)
                # future = executor.submit(
                #    h_alphabeta_search, game, game.result(state, move))
                # move = future.result()[-1]
            end = time.time()

            # Send move to server
            converted_move = game.convert_move(move)
            print(
                f"Move: {move} | Converted to: {converted_move} | time: {end-start} s.")
            network.send_move(converted_move)
            # state.display()
            pieces, turn = network.get_state()

            # Update the game state for the current player
            game.update_state(pieces, turn)

            # Update state
            state = game.result(state, move)

            # state.display()

            # Notify the other thread
            cond.notify_all()

    print('Game over!')


color = sys.argv[1]
name = sys.argv[2]
try:
    ip = sys.argv[3]
except:
    ip = "localhost"

play_game(name=name, team=color, server_ip=ip, timeout=60)
