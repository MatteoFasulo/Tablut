import argparse
import socket
from argList import argList
from localexecution import localrun

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Play a game of TABLUT')
    parser.add_argument("timelimit", help="The max time to compute a move")
    l = argList(["white", "black"])
    parser.add_argument("team", type=str, choices=l, help="The player's team [white/black]")
    parser.add_argument("name", type=str, help="The player's name")
    parser.add_argument("--ip", help="The ip of the server. Leave this blank to run locally")
    args = parser.parse_args()

    if args.ip == None:
        localrun(args.team, args.name, args.timelimit)
    else:
        ip = args.ip
        #Check if the IP is correct
        socket.inet_aton(ip)
        print("Run on the server's ip")