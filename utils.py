import json
import socket
import struct
import numpy as np
from enum import Enum

from boardmanager import Board, BadMoveException

class Utils:
    def __init__(self, board):
        self.board = board

    def evalutate_utility(self, board, move, player):
        """
        Evaluate the utility of a move
        """

        fit = 0
        if player == "WHITE":
            fit += self.board.white_fitness_dynamic(move) + self.board.white_fitness(move, -5, 0.01, -1000)
        else:
            fit += 0
        return fit

class Pawn(Enum):
    EMPTY = 0
    WHITE = 1
    BLACK = 2
    KING = 3

class Converter:
    # TODO convert matrix to json check if it works and if it's needed
    def json_to_matrix(self, json_state):
        data = list(json_state.items())
        array = np.array(data, dtype = object)

        board = np.array(array[0, 1], dtype = object)
        turn = array[1,1]
        
        blacks = []
        whites = []
        pieces = [[],[],[],[],[],[],[],[],[]]

        state = np.zeros((9,9), dtype = Pawn)
        for i in range(0,9):
            for j in range (0,9):
                if board[i,j] == 'EMPTY':
                    state[i,j] = Pawn.EMPTY.value
                    pieces[i].append(Pawn.EMPTY.value)
                elif board[i,j] == 'WHITE':
                    state[i,j] = Pawn.WHITE.value
                    pieces[i].append(Pawn.WHITE.value)
                    whites.append([i,j])
                elif board[i,j] == 'BLACK':
                    state[i,j] = Pawn.BLACK.value
                    pieces[i].append(Pawn.BLACK.value)
                    blacks.append([i,j])
                elif board[i,j] == 'KING':
                    state[i,j] = Pawn.KING.value
                    pieces[i].append(Pawn.KING.value)
                    king = [i,j]
                    king_position = (i,j)
        board = Board()
        board.whites = whites
        board.blacks = blacks
        board.king = king
        board.pieces = pieces

        for row in board.pieces:
            print(row)
        return board, turn, king_position

class Network:
    def __init__(self, name, player, server_ip = 'localhost', converter = None, sock = None, timeout = 60):
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
        if self.server_ip != 'localhost':
            self.sock.connect(server_address)
        else:
            from localexecution import localrun
            localrun(self.player, self.name, timelimit=self.timeout)
            return state, turn, king_pos

        # Send the player's name to the server
        self.sock.send(struct.pack('>i', len(self.name)))
        self.sock.send(self.name.encode())

        return self.get_state()

    def get_state(self):
        len_bytes = struct.unpack('>i', self.recvall(4))[0]
        current_state_server_bytes = self.sock.recv(len_bytes)

        # Converting byte into json 
        json_current_state_server = json.loads(current_state_server_bytes)
        #print(json_current_state_server)

        state, turn, king_pos = self.converter.json_to_matrix(json_current_state_server)
        return state, turn, king_pos

    def send_move(self, move):
        _form, _to = move
        turn = self.player

        move = json.dumps({"from": _form, "to": _to, "turn": turn})

        self.sock.send(struct.pack('>i', len(move)))
        self.sock.send(move.encode())
        return move