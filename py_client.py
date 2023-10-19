import socket
import struct
import json

player_name = 'Matteo'
color = 'black'
ip_address = '82.49.144.86'


def recvall(sock, n):
    # Helper function to recv n bytes or return None if EOF is hit
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        if color == 'white':
            # Connect the socket to the port where the server is listening
            server_address = (ip_address, 5800)
        elif color == 'black':
            # Connect the socket to the port where the server is listening
            server_address = (ip_address, 5801)
        else:
            raise Exception("Se giochi o sei bianco oppure sei nero")

        sock.connect(server_address)
        sock.send(struct.pack('>i', len(player_name)))
        sock.send(player_name.encode())
        len_bytes = struct.unpack('>i', recvall(sock, 4))[0]
        current_state_server_bytes = sock.recv(len_bytes)
        json_current_state_server = json.loads(current_state_server_bytes)
        print(json_current_state_server)
        move_for_server = convert_move_for_server(move, color)
        sock.send(struct.pack('>i', len(move_for_server)))
        sock.send(move_for_server.encode())


if __name__ == "__main__":
    main()
