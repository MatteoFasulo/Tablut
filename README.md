# \tLut 🎉🤖

<div style="display: flex; justify-content: center;">
    <img src="https://everyboard.org/assets/images/light/Tablut.png" width="40%">
</div>

## Introduction 🚀

Hey there, code explorers! 🌟 Welcome to the mind-blowing world of Tablut, brought to you by the genius minds of [University of Bologna's AI course](https://corsi.unibo.it/2cycle/artificial-intelligence) for the mind-bending academic year 2023/2024! 🧠🎓

Our mission? Oh, just to create an AI wizard 🧙 capable of dominating the [epic game of Tablut](https://en.wikipedia.org/wiki/Tafl_games) using the jaw-dropping [Minimax algorithm with Alpha-Beta pruning](https://en.wikipedia.org/wiki/Alpha%E2%80%93beta_pruning). Yeah, we're that ambitious! 🚀

And who's behind this magical project? None other than the fantastic foursome:

- [Matteo Fasulo](https://github.com/MatteoFasulo) 🌙
- [Luca Tedeschini](https://github.com/LucaTedeschini) 🐍
- [Antonio Gravina](https://github.com/GravAnt) 🔥
- [Norberto Casarin](https://github.com/BandoleroNext) 🚀

## Project Philosophy 🌐

Hold on to your hats, folks! This project is pure Python 3.9 sorcery! 🐍 The code? It's organized so neatly, even Marie Kondo would be proud! 🧹 Plus, it's comment city, making it a breeze to understand. Oh, and did we mention we've sprinkled some [AIMA Python code](https://github.com/aimacode/aima-python) magic? Yup, we went all out! 🚀✨

## How to Run the Code 🚀

Ready for the magic show? 🎩✨ To dive into the enchanting world of Tablut, simply run the mystical [`play.py`](play.py) file. Just toss in these enchanting arguments:

- `--team`: Choose your team, either `WHITE` or `BLACK`. 🏴‍☠️🏳️
- `--name`: Declare the name of your agent. ✨
- `--ip`: Provide the IP address of the server. Default is `localhost`. 🌐

Behold the spell to run this enchanting code:

```bash
py play.py --team WHITE --name "\tLut" --ip <server_ip>
```

Oh, and if you're in the Windows realm, use `python3` for Linux adventures. 🐧✨

### WHITE Heuristics

In the implementation of the WHITE player's heuristics, several factors are taken into consideration to evaluate the current state of the Tablut board. These factors contribute to the overall fitness of the position for the WHITE player. The key components of the WHITE heuristics include:

1. **Vulnerability to Capture:**
   - A measure of the risk of WHITE pieces being captured by BLACK pawns.
   - Utilizes the concept of clear views to assess potential threats to WHITE pieces.

2. **King's Distance and Safety:**
   - Evaluates the distance of the WHITE king from the corners of the board.
   - Incorporates the number of BLACK pieces in each quadrant to assess the safety of the king.

3. **External Pawn Distribution:**
   - Calculates the fitness based on the distribution of WHITE pawns relative to the king.
   - Promotes a strategic arrangement of WHITE pieces with respect to the center of the board.

4. **King's Defense:**
   - Considers the ability of BLACK pieces to potentially capture the WHITE king in the next move.
   - Applies a strong negative fitness if the king is at risk of capture.

5. **King's Movement:**
   - Evaluates the movement of the WHITE king, promoting a balanced position across the board.

The combination of these factors aims to provide a comprehensive assessment of the Tablut board from the perspective of the WHITE player.

### BLACK Heuristics

The BLACK player's heuristics focus on evaluating the strategic aspects of the Tablut board, taking into account various factors that influence the overall fitness of the position. The primary considerations in the BLACK heuristics are:

1. **Number of BLACK and WHITE Pawns:**
   - Assigns fitness based on the count of BLACK and WHITE pawns on the board.

2. **Proximity of BLACK Pawns to the King:**
   - Evaluates the number of BLACK pawns within a certain distance of the WHITE king.
   - A higher count encourages a more aggressive position.

3. **Path to the King:**
   - Assesses the availability of free paths for BLACK pawns to reach and potentially capture the WHITE king.

4. **Encirclement of the King:**
   - Introduces a coefficient of encirclement, considering the positioning of BLACK pawns around the WHITE king.

The BLACK heuristics aim to capture the strategic advantages, focusing on pawn count, proximity to the king, and the potential to create threats against the WHITE player. These factors collectively contribute to the fitness evaluation for the BLACK player in the Tablut game.

Prepare to be amazed, mortals! 🎩✨
