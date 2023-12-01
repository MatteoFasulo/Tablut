# Alpha-Beta

This section will talk about the implementation of the `Alpha-Beta` search algorithm.

## MinMax Pruning

In this project it has been used a particular implementation of Alpha-beta `pruning` in a `minmax` context. <br>
Alpha-beta pruning is a search algorithm that aims to reduce the number of nodes evaluated by the minmax algorithm in its search tree. This algorithm stops evaluating a move as soon as it finds at least one possibility that proves the move to be worse than a previously examined move. Such moves do not need to be evaluated further. When applied to a standard minimax tree, alpha-beta pruning returns the same move as minmax would, but it prunes away branches that cannot possibly influence the final decision.

### Cutoff

The cutoff_depth function is a cutoff function that stops the search if it reaches a certain `depth` d. This is used to limit the search space and make the algorithm more efficient.<br>
A depth of 2 is the perfect compromise when it comes to save time while giving a good move

```python title="cutoff_depth"
def cutoff_depth(d):
    """A cutoff function that searches to depth d."""
    return lambda game, state, depth: depth > d
```

