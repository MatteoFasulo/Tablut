# Networking and Game State Handling

The provided code establishes a network connection and handles the conversion of game states between JSON and matrix representations.

This includes classes for network communication (`Network`) and a converter (`Converter`) to facilitate the transformation between JSON and matrix formats.
In order to map each pawn type to a specific value, a set of constants has been defined.
The `Pawn` enumeration defines different pawn types, including `EMPTY`, `WHITE`, `BLACK`, `KING`, and `THRONE` allowing to easily identify the type of each pawn while fetching the game state.
Key components of the implementation are as follows:

#### Networking Functionality

The `Network` class manages the network communication between the game client and server.
It supports connection setup, sending moves, and receiving the current game state.
It utilizes socket programming and JSON encoding/decoding for data exchange.
The `connect` method establishes a connection with the server, and the `get_state` method retrieves the current game state.

#### Game State Conversion

The `Converter` class handles the conversion between JSON representations received from the server and the matrix format used in the code.
It provides the `json_to_matrix` method, converting the JSON state into a 9x9 matrix representing the game board.
This method uses the `Pawn` enumeration to map each pawn type to a specific value by using a numpy method called `vectorize` which applies a lambda function to each element of the board.
The lambda function maps each pawn type to a specific value, as shown below:

```python title="utils.py" linenums="1"
class Converter:
    def json_to_matrix(self, json_state):
        data = list(json_state.items())
        board, turn = data[0], data[1]

        if isinstance(board, tuple):
            board = board[1]

        if isinstance(turn, tuple):
            turn = turn[1]

        board = np.vectorize(lambda x: Pawn[x].value)(board)
        board = board.reshape(9, 9)

        return board, turn
```

### Game State Fetching

The `get_state` method of the `Network` class is responsible for fetching the current game state from the server and checks the returned state for validity. If the turn is not neither `WHITE` nor `BLACK`, the method returns `WHITEWIN`, `BLACKWIN`, or `DRAW` depending on the outcome of the game which is calculated by the Java server.

```python title="utils.py" linenums="1"
def get_state(self):
        len_bytes = struct.unpack('>i', self.recvall(4))[0]
        current_state_server_bytes = self.sock.recv(len_bytes)

        # Converting byte into json
        json_current_state_server = json.loads(current_state_server_bytes)

        state, turn = self.converter.json_to_matrix(json_current_state_server)

        if not turn in ['WHITEWIN', 'BLACKWIN', 'DRAW']:

            self.turn = turn
            self.state = state

            return state, turn

        else:
            if turn == 'WHITEWIN':
                return 0, "WHITE WINS!"
                sys.exit(0)

            elif turn == 'BLACKWIN':
                return 1, "BLACK WINS!"
                sys.exit(0)

            elif turn == 'DRAW':
                return 2, "DRAW!"
                sys.exit(0)
```
