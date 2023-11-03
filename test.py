from aima.games import Game, GameState, GameNode, GameTree, Minimax, AlphaBetaPruning, MonteCarloTreeSearch, Expectimax, \
    MinimaxDecision, AlphaBetaDecision, MonteCarloTreeSearchDecision, ExpectimaxDecision 

import copy

class TablutPlayer(Game):
    """
    Tablut player
    """
    def __init__(self, player, timeout, initial_board, king_position = [4,4]):
        self.initial = GameState(to_move=player, utility=, board=, moves=get_moves(board, player))
        self.timeout = timeout

    # AIMA Methods
    def actions(self, state):
        """
        Return a list of all moves in this state
        """
        player = state.to_move
        board = copy.deepcopy(state.board)
        return self.white_logic(board) if player == "WHITE" else self.black_logic(board)
    
    def result(self, state, move):
        """
        Return the state that results from making a move from a state
        """
        board = copy.deepcopy(state.board)
        old_board = copy.deepcopy(state.board)
        player = state.to_move
        # fare la mossa
        player = ("BLACK" if player == "WHITE" else "WHITE")

        return GameState(to_move=player, utility=, board=board, moves=get_moves(board, player))

    
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

    # Custom Methods
    def get_moves(self, board, player):
        """
        Get all moves for a specific player
        """
        return self.white_logic(board) if player == "WHITE" else self.black_logic(board)
