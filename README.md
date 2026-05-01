# Goats and Tigers (Bagh-Chal) AI Game

## Overview
This project implements the traditional **Goats and Tigers (Bagh-Chal)** board game with support for:
- Human vs Human
- Human vs AI
- AI vs AI
- Rotation-based variant of the game
The game is modeled using a graph-based board representation and uses the **Minimax algorithm with Alpha-Beta pruning (Negamax style)** for AI decision-making.

## Game Rules
1. Two type of players - Goats(15 pieces), Tigers(3 pieces)
2. At the begining Tigers are placed in fixed positions
3. Then on alterante turns pleyer either place their piece(if goat) or move their piece
4. Goats cannot move until all pieces are placed
5. Each piece can move one step along the connected edge
6. Tigers can capture goats by jumping over the goats
7. Goats can block the tigers by surrounding
8. Tigers aim is to capture atleast 5 goats to win the game
9. Goats aim is to block the 3 tigers to win the game.

    
## Rotation Variation Rules
1. All original game rules apply
2. Once all pieces are placed on the board, a player either move or rotate a grid
3. Any 3*3 or 4*4 grids can be rotated
4. A player cannot rotate the same grid if that grid is rotated in previous turn by other player.
5. To rotate a grid at least one of piece the player should exist in that grid



## Algorithms Analysis

### 1. Game Representation
- The board is represented as a **graph (NetworkX)**:
  - Nodes → positions on the board
  - Edges → valid moves between positions

### 2. Move Generation (`get_all_moves`)
This function generates all valid moves for a player given the current game state.
#### Complexity:

**Time Complexity:**


### 3. Evaluation Function (`evaluate`)

The heuristic function evaluates how good a game state is.

#### Factors:
- Number of goats captured
- Mobility (available moves)
- Tiger blocking
- Capture opportunities

#### Complexity:

### 4. Negamax with Alpha-Beta Pruning

The AI uses a recursive negamax-style algorithm.

#### Complexity:


## Performance Characteristics


## Performance Measurement

### Method

We simulate multiple AI vs AI games and measure:

- Execution time
- Average game length
- Win distribution

### Sample Results


## Profiling
