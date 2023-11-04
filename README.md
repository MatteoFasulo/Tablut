# Tablut

## Introduction

This is a project for the course of [Artificial Intelligence of the University of Bologna](https://corsi.unibo.it/2cycle/artificial-intelligence), academic year 2023/2024.

The goal of the project is to implement an agent capable of playing the [game of Tablut](https://en.wikipedia.org/wiki/Tafl_games), using the [Minimax algorithm with Alpha-Beta pruning](https://en.wikipedia.org/wiki/Alpha%E2%80%93beta_pruning) and [Iterative Deepening](https://en.wikipedia.org/wiki/Iterative_deepening_depth-first_search).

The project is developed by a group of four students. There will be a tournament between the agents developed by the students, in order to determine the best one.

## Group members

- [Matteo Fasulo](https://github.com/MatteoFasulo)
- [Luca Tedeschini](https://github.com/LucaTedeschini)
- [Antonio Gravina](https://github.com/GravAnt)
- [Norberto Casarin](https://github.com/BandoleroNext)

## Project philosophy

The project is developed entirely in Python 3.9. The code is organized in a modular way, in order to be easily readable and maintainable. The code is also commented in order to make it more understandable. [AIMA Python code](https://github.com/aimacode/aima-python) is used as a base for the implementation of the game.

## How to run the code

The code can be run by executing the `main.py` file. The file accepts the following arguments:

- `-ip`: the IP address of the server. The default value is `localhost`.
- `--timelimit`: the maximum time in seconds that the agent can use to make a move. The default value is 60 seconds.
- `--team`: the team of the agent, which can be `WHITE` or `BLACK`.
- `--name`: the name of the agent.
