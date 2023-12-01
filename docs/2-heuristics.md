# Heuristics

The heuristics for both the WHITE and BLACK players are implemented in separate modules (`whiteheuristics.py` and `blackheuristics.py`). These heuristics assess the current state of the board and contribute to the overall fitness of the position for each player: the higher the fitness, the more favorable the move is for the player. 

In order to determine the fitness of a position, the heuristics are weighted and summed together. The weights are the result of the execution of `genetic.py`. The weights are not optimal, but they are good enough to provide a decent performance of the AI.
A more in detail description of how the genetic algorithm works can be found in [Genetic Algorithm for Weight Fine-Tuning](3-genetic_algorithms.md).

<h2>WHITE Heuristics</h2>

The WHITE player's heuristics include factors such as:
<ol>

<li>Number of white pieces
    <ul>
    <li>The more the white pieces are, the more the heuristic value increases</li>
    </ul>
</li>

<li>Number of black pieces
    <ul>
    <li>The more the black pieces are, the more the heuristic value decreases</li>
    </ul>

<li>Distance of the king from the centre
    <ul>
    <li>The more the king is distant from the centre, the more the heuristic value increases</li>
    <li>The euclidean distance is used for this heuristic</li>
    </ul>
</li>

<li>King sorrounded by black pieces
    <ul>
    <li>If the king is sorrounded by black pieces, the heuristic value decreases</li>
    </ul>
</li>

<li>Weights of each position of the board
    <ul>
    <li>Each position of the board has a weight, which is used to calculate the heuristic value</li>
    <li>The winning positions are very heavy</li>
    <li>The positions in which the white pawns cannot go to have negative weight</li>
    </ul>
</li>

</ol>

<h2>BLACK Heuristics</h2>

The BLACK player's heuristics include factors such as:
<ol>

<li>Number of black pieces
    <ul>
    <li>The more the black pieces are, the more the heuristic value increases</li>
    </ul>
</li>

<li>Number of white pieces
    <ul>
    <li>The less the white pieces are, the more the heuristic value decreases</li>
    </ul>

<li>Number of black pawns close to the king
    <ul>
    <li>The closer are the black pawns to the king, the more the fitness value is increased </li>
    </ul>
</li>

<li>Free paths to the king
    <ul>
    <li>It counts how many direct path from any black pawn to the king exists. The fitness increases linearly to the number of paths</li>
    </ul>
</li>

<li>Encirclement coefficient to the king
    <ul>
    <li>A coefficient that measures how much the king is encricled. Clearly the fitness is higher when the king is a lot encircled</li>
    </ul>
</li>

</ol>