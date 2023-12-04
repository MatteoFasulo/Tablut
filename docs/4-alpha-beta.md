# Alpha-Beta

This section will talk about the implementation of the `Alpha-Beta` search algorithm.

## Pruning

In this project it has been used a particular implementation of Alpha-beta `pruning` in a `minmax` context. <br>
Alpha-beta pruning is a search algorithm that aims to reduce the number of nodes evaluated by the minmax algorithm in its search tree. This algorithm stops evaluating a move as soon as it finds at least one possibility that proves the move to be worse than a previously examined move. Such moves do not need to be evaluated further. When applied to a standard minimax tree, alpha-beta pruning returns the same move as minmax would, but it prunes away branches that cannot possibly influence the final decision.

### Cutoff

The cutoff_depth function is a cutoff function that stops the search if it reaches a certain `depth` d. This is used to limit the search space and make the algorithm more efficient.<br>
A depth of 2 is the perfect compromise when it comes to saving computational time and creating a competent agent.

```python title="cutoff_depth"
def cutoff_depth(d):
    """A cutoff function that searches to depth d."""
    return lambda game, state, depth: depth > d
```

## MinMax

The `max_value` and `min_value` functions are the core of the Alpha-Beta search algorithm. They represent the two players (`black` and `white`) in the game, with `max_value` being the active turn player, trying to maximize the score, and `min_value` being the other player, trying to minimize the score.

This simulates a position where every single player will make the perfect move to maximize their future score, considering that the other player will try to do the same.<br>

### Max

Here we see the code of maxvalue:

```python title="maxvalue"
def max_value(state, alpha, beta, depth):
        nonlocal best_move
        if game.terminal_test(state):
            return game.utility(state, player), None
        if cutoff(game, state, depth):
            v = game.compute_utility(state, None, player)
            return v, None
        if time.time() - start_time > time_limit:
            print(f"TIMEOUT at {depth = }, player: {player}")
            raise TimeoutError(best_move)
        v, move = -np.inf, None
        for a in game.actions(state):
            v2, _ = min_value(game.result(state, a), alpha, beta, depth+1)
            if v2 > v:
                v, move = v2, a
                alpha = max(alpha, v)
            if v >= beta:
                return v, move
        return v, move
```

The function takes four parameters: `state`, `alpha`, `beta`, and `depth`.<br>`state` represents the current state of the game. `alpha` and `beta` are the best values that the players can, respectively, guarantee at that level or above. `depth` is the current depth of the search.

The function first checks if the current state is a terminal state or if the cutoff depth has been reached. If either of these conditions are true, it computes the utility of the state and returns it. If not, it iterates over all possible actions, calls `min_value` for the result of each action, and updates the maximum value `v` and the corresponding move if the returned value is greater than the current maximum value. It also updates the `alpha` value.

If the maximum value `v` is greater than or equal to the beta value, the function prunes the remaining branches and returns the maximum value and the corresponding move. This is because the minimizing player will never choose this branch as it already has a better option.

### Min

The `min_value` function works similarly, but it represents the minimizing player and tries to minimize the value. It updates the beta value and prunes the remaining branches if the minimum value is less than or equal to the alpha value.

```python title="minvalue"
def min_value(state, alpha, beta, depth):
        nonlocal best_move
        if game.terminal_test(state):
            return game.utility(state, player), None
        if cutoff(game, state, depth):
            v = game.compute_utility(state, None, player)
            return v, None
        if time.time() - start_time > time_limit:
            print(f"TIMEOUT at {depth = }, player: {player}")
            raise TimeoutError(best_move)
        v, move = +np.inf, None
        for a in game.actions(state):
            v2, _ = max_value(game.result(state, a), alpha, beta, depth + 1)
            if v2 < v:
                v, move = v2, a
                beta = min(beta, v)
            if v <= alpha:
                return v, move
        return v, move
```

These functions are recursive, calling each other until the tree at the chosen depth as been explored or time runs out.

## Timeout

If the time spent exceeds the time limit, both functions raise a `TimeoutError` with the best move found so far.

```python title="timeoutError"
if time.time() - start_time > time_limit:
            print(f"TIMEOUT at {depth = }, player: {player}")
            raise TimeoutError(best_move)
```

This code snippet initiates the Alpha-Beta search algorithm by calling the `max_value` function. It tracks the start time for handling timeouts. If a `TimeoutError` occurs, it retrieves the best move found so far from the exception and returns it. Otherwise, it returns the best move found by the algorithm.

```python title="start-timer"
    start_time = time.time()
    try:
        result = max_value(state, -np.inf, +np.inf, 0)[-1]
    except TimeoutError as e:
        result = e.args[0]
    return result
```
