# Tablut Documentation

Welcome to the official documentation for \tLut, the AI wizard developed by the brilliant minds from the University of Bologna's AI course for the academic year 2023/2024! In this documentation, we'll provide you with a comprehensive understanding of the game of Tablut and how to interact with our enchanting AI creation.

## Table of Contents

1. [Introduction](#introduction)
2. [Project Philosophy](#project-philosophy)
3. [How to Run the Code](#how-to-run-the-code)
    - [Running on Linux](#running-on-linux)
    - [Running on Windows](#running-on-windows)
4. [WHITE Heuristics](#white-heuristics)
5. [BLACK Heuristics](#black-heuristics)

## 1. Introduction <a name="introduction"></a>

Tablut is an epic board game with a rich history, and it's the focal point of our AI project. Originating from the tafl family of games, Tablut involves two players - WHITE and BLACK. The WHITE player's objective is to help their king escape to one of the corners of the board, while the BLACK player aims to capture the king. The game unfolds on a square board, and victory depends on strategic moves and careful planning.

For a detailed overview of the game, you can refer to the [Tablut Wikipedia page](https://en.wikipedia.org/wiki/Tafl_games).

## 2. Project Philosophy <a name="project-philosophy"></a>

Our is written in Python 3.9, since the most recent AIMA library is not compatible with further versions. We've incorporated the [AIMA Python code](https://github.com/aimacode/aima-python) magic to enhance the enchanting experience. Dive into the source code to explore the intricacies of our implementation and witness the fusion of AI and game strategy.

## 3. How to Run the Code <a name="how-to-run-the-code"></a>

To embark on the magical journey of Tablut with \tLut, follow these simple steps.

### Running on Linux <a name="running-on-linux"></a>

```bash
python3 play.py --team WHITE --name "\tLut" --ip <server_ip>
```

### Running on Windows <a name="running-on-windows"></a>


```powershell
py play.py --team WHITE --name "\tLut" --ip <server_ip>
```

Adjust the arguments accordingly to choose your team, declare the agent's name, and provide the server's IP address.
