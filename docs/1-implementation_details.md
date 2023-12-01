# Implementation Details

In this section, we delve into the implementation details of the Tablut AI, known as \tLut. The AI is built upon the Tablut game, a strategic board game with a rich history, and aims to dominate the game using the Minimax algorithm with Alpha-Beta pruning.

## Game Representation

The game is represented by the `Tablut` class, which inherits from the AIMA (`aima.games.Game`) framework. The board itself is represented by the `Board` class, and various utilities and heuristics are provided by additional classes.

### Board Initialization

The `Tablut` class initializes the game board (`Board` object) with a default size of 9x9. The initial state includes the board configuration, the current player to move, and the utility value.

```python title="tablut.py"
self.initial = Board(height=height, width=width, to_move='WHITE', utility=0)
self.width = width
self.height = height
```

## Game Mechanics

### Updating Game State

The `update_state` method is responsible for updating the state of the board based on the current positions of the pieces and the current turn. In order to reduce the search space, the list of possible moves is computed based on the current player. For example, if it's WHITE's turn, the list of possible moves is computed based on the positions of the WHITE pieces. This approach significantly reduces the number of possible moves, as the BLACK pieces are not considered. Also the list comprehension is used to generate the list of possible moves, which is a more elegant approach than using nested loops.

```python title="tablut.py" linenums="1"
def update_state(self, pieces, turn):
    # Update board state
    self.initial.pieces = pieces
    self.initial.to_move = turn
    self.to_move = turn

    # Update pawns coordinates
    white_pos = self.initial.get_white()
    black_pos = self.initial.get_black()
    king_pos = self.initial.get_king()

    # White has also the king
    white_pos.insert(0, king_pos)

    # Get the current player and compute the list of possible moves
    if turn == 'WHITE':
        self.squares = [[x, (k, l)] for x in white_pos for k in range(
            self.width) for l in range(self.height)]
    elif turn == 'BLACK':
        self.squares = [[x, (k, l)] for x in black_pos for k in range(
            self.width) for l in range(self.height)]
```

### Making Moves

The `move` method is responsible for making a move on the board, given a specific move tuple. It handles the updating of the board state, checks for captures, and changes the turn. In our code, moves are represented as tuples of the form `(from_pos, to_pos)`, where `from_pos` and `to_pos` are tuples of the form `(x, y)` representing the coordinates of the piece. The `move` method extracts the starting and ending positions from the move tuple and updates the board accordingly. The `check_attacks` method is then called to check for captures. Finally, the turn is changed to the opposite player.

```python title="tablut.py" linenums="1"
def move(self, move):
    # Extract the starting and ending position from the move
    from_pos, to_pos = move
    x1, y1 = from_pos
    x2, y2 = to_pos

    pawn_type = self.initial.pieces[x1][y1]

    new_board = copy.deepcopy(self.initial.pieces)

    if pawn_type == Pawn.EMPTY.value or pawn_type == Pawn.THRONE.value:
        self.initial.pieces = new_board
        return self

    if self.initial.pieces[x2][y2] != Pawn.EMPTY.value:
        self.initial.pieces = new_board
        return self

    # Code to handle movement and captures

    # Check if there are any captures (important for heuristics)
    self.initial.check_attacks(x2, y2)

    self.initial.pieces = new_board

    # Change turn
    self.initial.to_move = (
        "BLACK" if self.initial.to_move == "WHITE" else "WHITE")
    return self
```

## Terminal State and Victory Conditions

The `check_win` method checks whether the game has reached a terminal state. This includes conditions such as capturing the king (BLACK wins), the king escaping (WHITE wins), a player being unable to move any checker (that player loses), or reaching the same state twice (draw, which is handled by the Java server).

### Caching for Improved Performance

In order to enhance the efficiency of certain functions within this implementation, a caching mechanism has been implemented using the `cache` decorator. This decorator is designed to store and retrieve the results of a function based on its arguments. When a function is decorated with `cache`, the decorator creates an internal cache dictionary. Before executing the original function, the decorator calculates a unique key derived from the function's arguments, specifically focusing on the `pieces` data (which are represented as a NumPy array). The key is calculated by converting the `pieces` data to a byte string and storing it in the cache dictionary. The key is then used to check whether the function has been previously executed with the same arguments. This caching strategy significantly optimizes performance by avoiding redundant calculations, especially in scenarios where the function is called with identical input multiple times.

```python linenums="1"
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
```

For example, the `max_value` and `min_value` functions are decorated with `@cache` to avoid redundant calculations of the utility of the board.

```python title="play.py" linenums="1" hl_lines="1 5"
@cache
def max_value(state, alpha, beta, depth, alpha0, beta0, gamma0, theta0, epsilon0, action_backtrack=None):
    ...

@cache
def min_value(state, alpha, beta, depth, alpha0, beta0, gamma0, theta0, epsilon0, action_backtrack=None):
    ...
```
