import os
import sys
import random
import time

# numpy
import numpy as np

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


def h_alphabeta_search(state, game, cutoff=cutoff_depth(25)):
    """Search game to determine best action; use alpha-beta pruning.
    As in [Figure 5.7], this version searches all the way to the leaves."""

    player = state.to_move

    @cache
    def max_value(state, alpha, beta, depth):
        if game.terminal_test(state):
            print("TERMINAL STATE REACHED")
            return game.compute_utility(state, None, player), None
        if cutoff(game, state, depth):
            print(f"CUTOFF at {depth = }")
            return game.compute_utility(state, None, player), None
        v, move = -np.inf, None
        for a in game.actions(state):
            v2, _ = min_value(game.result(state, a), alpha, beta, depth+1)
            print(f"Move: {a} | Score: {v2}")
            if v2 > v:
                v, move = v2, a
                alpha = max(alpha, v)
            if v >= beta:
                return v, move
        return v, move

    @cache
    def min_value(state, alpha, beta, depth):
        if game.terminal_test(state):
            print("TERMINAL STATE REACHED")
            return game.compute_utility(state, None, player), None
        if cutoff(game, state, depth):
            print(f"CUTOFF at {depth = }")
            return game.compute_utility(state, None, player), None
        v, move = +np.inf, None
        for a in game.actions(state):
            v2, _ = max_value(game.result(state, a), alpha, beta, depth + 1)
            print(f"Move: {a} | Score: {v2}")
            if v2 < v:
                v, move = v2, a
                beta = min(beta, v)
            if v <= alpha:
                return v, move
        return v, move

    return max_value(state, -np.inf, +np.inf, 0)


def alpha_beta_cutoff_search(state, game, d=2, cutoff_test=None, eval_fn=None):
    """Search game to determine best action; use alpha-beta pruning.
    This version cuts off search and uses an evaluation function."""

    player = state.to_move

    # Functions used by alpha_beta
    @cache
    def max_value(state, alpha, beta, depth):
        if cutoff_test(state, depth):
            return eval_fn(state)
        v = -np.inf
        for a in game.actions(state):
            v = max(v, min_value(game.result(state, a), alpha, beta, depth + 1))
            if v >= beta:
                return v
            alpha = max(alpha, v)
        return v

    @cache
    def min_value(state, alpha, beta, depth):
        if cutoff_test(state, depth):
            return eval_fn(state)
        v = np.inf
        for a in game.actions(state):
            v = min(v, max_value(game.result(state, a), alpha, beta, depth + 1))
            if v <= alpha:
                return v
            beta = min(beta, v)
        return v

    # Body of alpha_beta_cutoff_search starts here:
    # The default test cuts off at depth d or at a terminal state
    cutoff_test = (cutoff_test or (lambda state, depth: depth >
                   d or game.terminal_test(state)))
    eval_fn = eval_fn or (lambda state: game.utility(state, player))
    best_score = -np.inf
    beta = np.inf
    best_action = None
    for a in game.actions(state):
        v = min_value(game.result(state, a), best_score, beta, 1)
        if v > best_score:
            best_score = v
            best_action = a
    return best_action


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

    while True:
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
                future = executor.submit(h_alphabeta_search, state, game)
                # future = executor.submit(alpha_beta_cutoff_search, state, game)
                result = future.result(timeout=55)  # Timeout 55 seconds
            end = time.time()

            score, move = result
            # score, move = np.nan, result

            # Send move to server
            converted_move = game.convert_move(move)
            print(
                f"Move: {converted_move} | Score: {score} | time: {end-start:.4f} s.")
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


color = sys.argv[1]
name = sys.argv[2]
try:
    ip = sys.argv[3]
except:
    ip = "localhost"

play_game(name=name, team=color, server_ip=ip, timeout=60)
