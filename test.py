from player import TablutPlayer
from boardmanager   import Board
from aima.games import alpha_beta_search
import random

def play_game(game, strategies: dict, verbose=False):
    """Play a turn-taking game. `strategies` is a {player_name: function} dict,
    where function(state, game) is used to get the player's move."""
    state = game.initial
    while not game.is_terminal(state):
        player = state.to_move
        print("a", strategies[player](state, game))
        move = strategies[player](state, game)
        state = game.result(state, move)
        if verbose: 
            print('Player', player, 'move:', move)
            game.display(state)
    return state

board = Board()
tp = TablutPlayer("WHITE", 60, board)
def random_player(game, state): return random.choice(list(game.actions(state)))


def player(search_algorithm):
    """A game player who uses the specified search algorithm"""
    return lambda game, state: search_algorithm(game, state)[1]


play_game(tp, dict(WHITE=player(alpha_beta_search), BLACK=random_player), verbose=True).utility