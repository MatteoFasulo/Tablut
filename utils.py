import json
import socket
import sys
import struct
from enum import Enum

import numpy as np

from concurrent.futures._base import TimeoutError

######## COSTANTS ########
GRAY = (150, 150, 150)
WHITE = (200, 200, 200)
WHITE2 = (180, 180, 180)
RED = (255, 0, 0)
RED2 = (200, 0, 0)
GREEN = (0, 255, 0)
GREEN2 = (0, 200, 0)
BLUE = (0, 0, 255)
##########################


class Pawn(Enum):
    EMPTY = 0
    WHITE = 1
    BLACK = 2
    KING = 3
    THRONE = 4


class WinException(Exception):
    pass


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


class Network:
    def __init__(self, name, player, server_ip='localhost', converter=None, sock=None, timeout=60):
        if not sock:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock

        if converter:
            self.converter = converter
        else:
            self.converter = Converter()

        self.server_ip = server_ip
        self.name = name
        self.player = player
        self.timeout = timeout

    def recvall(self, n):
        # Helper function to recv n bytes or return None if EOF is hit
        data = b''
        while len(data) < n:
            packet = self.sock.recv(n - len(data))
            if not packet:
                return None
            data += packet
        return data

    def connect(self):
        if self.player == 'WHITE':
            # Connect the socket to the port where the server is listening
            server_address = (self.server_ip, 5800)
        elif self.player == 'BLACK':
            # Connect the socket to the port where the server is listening
            server_address = (self.server_ip, 5801)
        else:
            raise ConnectionError("Player must be WHITE or BLACK!")

        # Establish a connection with the server
        self.sock.connect(server_address)

        # Send the player's name to the server
        self.sock.send(struct.pack('>i', len(self.name)))
        self.sock.send(self.name.encode())

        return self.get_state()

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

    def send_move(self, move):
        _from, _to = move
        turn = self.player

        move = json.dumps({"from": _from, "to": _to, "turn": turn})

        self.sock.send(struct.pack('>i', len(move)))
        self.sock.send(move.encode())
        return move

    def check_turn(self, player):
        return self.turn == player
