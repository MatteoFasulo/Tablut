from aima.games import Game, GameState

import copy
from utils import Utils
from boardmanager import Board

class TablutPlayer(Game):
    """
    Tablut player
    """
    def __init__(self, player, timeout, initial_board, king_position = [4,4]):
        self.utils = Utils(initial_board)
        self.initial = GameState(to_move=player, utility=self.utils.evalutate_utility(initial_board, initial_board), board=initial_board, moves=board.all_possible_moves(player))
        self.timeout = timeout

    # AIMA Methods
    def actions(self, state):
        """
        Return a list of all moves in this state
        """
        player = state.to_move
        board = copy.deepcopy(state.board)
        return self.utils.white_logic(board) if player == "WHITE" else self.utils.black_logic(board)
    
    def result(self, state, move):
        """
        Return the state that results from making a move from a state
        """
        board = copy.deepcopy(state.board)
        old_board = copy.deepcopy(state.board)
        player = state.to_move

        # make move
        board.move(move)

        # swap player
        player = ("BLACK" if player == "WHITE" else player)

        return GameState(to_move=player, utility=self.utils.evalutate_utility(old_board, board), board=board, moves=board.all_possible_moves(player))

    
    def utility(self, state, player):
        """
        Return the value of this final state to player
        1, -1, 0
        """
        return state.utility if player == "WHITE" else -state.utility
    
    def terminal_test(self, state):
        """
        Return True if this is a final state for the game
        """
        return state.utility != 0
