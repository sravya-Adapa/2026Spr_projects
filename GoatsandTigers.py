"""
Goats and Tigers
Author: Sravya Adapa (nadapa2)
This is Goats and Tigers game engine.
"""

import networkx as nx
import matplotlib.pyplot as plt
from enum import Enum
import copy
from collections import deque
import random

from sympy import capture

# These are helpful to detect any repeated moves in the game
MAX_CYCLE_LEN  = 4
HISTORY_MAXLEN = MAX_CYCLE_LEN * 2



def original_layout():
    """
    The original board shape for this game defines by nodes and edges.
    """
    nodes = {
        0: (0, 4),
        1: (-2.5, 3), 2: (-1.5, 3), 3: (-0.5, 3),
        4: (0.5, 3),  5: (1.5, 3),  6: (2.5, 3),
        7: (-2.5, 2), 8: (-1.5, 2), 9: (-0.5, 2),
        10: (0.5, 2), 11: (1.5, 2), 12: (2.5, 2),
        13: (-2.5, 1), 14: (-1.5, 1), 15: (-0.5, 1),
        16: (0.5, 1),  17: (1.5, 1),  18: (2.5, 1),
        19: (-1.5, 0), 20: (-0.5, 0),
        21: (0.5, 0),  22: (1.5, 0),
    }
    edges = [
        (0, 2), (0, 3), (0, 4), (0, 5),
        (1, 2), (2, 3), (3, 4), (4, 5), (5, 6),
        (7, 8), (8, 9), (9, 10), (10, 11), (11, 12),
        (13, 14), (14, 15), (15, 16), (16, 17), (17, 18),
        (19, 20), (20, 21), (21, 22),
        (1, 7), (7, 13),
        (2, 8), (8, 14),
        (3, 9), (9, 15),
        (4, 10), (10, 16),
        (5, 11), (11, 17),
        (6, 12), (12, 18),
        (14, 19), (15, 20), (16, 21), (17, 22),
    ]
    return nodes, edges

# These are define rotation grids.
ROTATION_ZONES = {
    # 3*3 grids
    "T1": {"name": "▲ 0-2-3", "perimeter": [0, 3, 2]},
    "T2": {"name": "▲ 0-3-4", "perimeter": [0, 4, 3]},
    "T3": {"name": "▲ 0-4-5", "perimeter": [0, 5, 4]},
    # 4*4 grids
    "S1":  {"name": "□ 1-2-8-7",    "perimeter": [1,  2,  8,  7]},
    "S2":  {"name": "□ 2-3-9-8",    "perimeter": [2,  3,  9,  8]},
    "S3":  {"name": "□ 3-4-10-9",   "perimeter": [3,  4,  10, 9]},
    "S4":  {"name": "□ 4-5-11-10",  "perimeter": [4,  5,  11, 10]},
    "S5":  {"name": "□ 5-6-12-11",  "perimeter": [5,  6,  12, 11]},
    "S6":  {"name": "□ 7-8-14-13",   "perimeter": [7,  8,  14, 13]},
    "S7":  {"name": "□ 8-9-15-14",   "perimeter": [8,  9,  15, 14]},
    "S8":  {"name": "□ 9-10-16-15",  "perimeter": [9,  10, 16, 15]},
    "S9":  {"name": "□ 10-11-17-16", "perimeter": [10, 11, 17, 16]},
    "S10": {"name": "□ 11-12-18-17", "perimeter": [11, 12, 18, 17]},
    "S11": {"name": "□ 14-15-20-19", "perimeter": [14, 15, 20, 19]},
    "S12": {"name": "□ 15-16-21-20", "perimeter": [15, 16, 21, 20]},
    "S13": {"name": "□ 16-17-22-21", "perimeter": [16, 17, 22, 21]},
}

def build_jump_table():
    """
    This function helps to build a look up table for valid tiger jumps.
    why is this necessary-
    1. Tried implementing graph connectivity to check valid jumps but even angular jumps are valid with this logic
    2. Tried if the source and destination have a midpoint that has goat but some valid jumps are not covered.
    Hence used hardcoded the valid straight lines where jumps are possible and built a lookup table.
    This function is not useful if the shape of the board changes so have to make dynamic.
    :return: Look up table for valid jumps.
    """
    _lines = [
        [1, 2, 3, 4, 5, 6],
        [7, 8, 9, 10, 11, 12],
        [13, 14, 15, 16, 17, 18],
        [19, 20, 21, 22],
        [1, 7, 13],
        [2, 8, 14, 19],
        [3, 9, 15, 20],
        [4, 10, 16, 21],
        [5, 11, 17, 22],
        [6, 12, 18],
        [1, 2, 0],
        [0, 2, 8, 14, 19],
        [0, 3, 9, 15, 20],
        [0, 4, 10, 16, 21],
        [0, 5, 11, 17, 22],
        [6, 5, 0],
    ]
    _, edges = original_layout()
    adj = {}
    for a, b in edges:
        adj.setdefault(a, set()).add(b)
        adj.setdefault(b, set()).add(a)
    table = {}
    seen = set()
    for line in _lines:
        for i in range(len(line) - 2):
            a, b, c = line[i], line[i+1], line[i+2]
            if b not in adj.get(a, set()) or c not in adj.get(b, set()):
                continue
            for src, mid, dst in [(a, b, c), (c, b, a)]:
                if (src, dst) not in seen:
                    table.setdefault(src, {})[dst] = mid
                    seen.add((src, dst))
    return table

VALID_JUMP_LANDINGS = build_jump_table()

class Board():
    """
    This class defines the game board and its methods are used to make any changes on the game board
    like
    1. To set a value to node
    2. To remove a value to node
    3. To check if a node is empty or not
    4. To check the neighbors of a node
    5. To get the position of node
    6. To get the value of a node (Tiger, Goat, NONE)
    7. To draw the current board state.
    """
    def __init__(self):
        self.G = nx.Graph()
        self.positions = {}
        self.build()

    def build(self):
        nodes, edges = original_layout()
        for id, pos in nodes.items():
            self.G.add_node(id, pos=pos, value=None)
        self.G.add_edges_from(edges)
        self.positions = nx.get_node_attributes(self.G, "pos")

    def set_value(self, node, value):
        if value not in [None, "T", "G"]:
            raise ValueError("Invalid value")
        self.G.nodes[node]["value"] = value

    def is_empty(self, node):
        return self.G.nodes[node]["value"] is None

    def get_value(self, node):
        return self.G.nodes[node]["value"]

    def get_position(self, node):
        return self.G.nodes[node]["pos"]

    def get_neighbors(self, node):
        return list(self.G.neighbors(node))

    def draw(self):
        color_map = []
        for node in self.G.nodes:
            val = self.G.nodes[node]["value"]
            if val == "T":
                color_map.append("red")
            elif val == "G":
                color_map.append("green")
            else:
                color_map.append("lightgray")
        nx.draw(self.G, self.positions, with_labels=True,
                node_color=color_map, node_size=800)
        plt.show()


class PieceType(Enum):
    """
    This Class is to define the types of pieces in this game.
    This game has 2 pieces - Tiger and Goat.
    """
    TIGER = "T"
    GOAT  = "G"


class Player():
    """
    This is base class for Players. Each player will be assigned a unique piece type.
    """
    def __init__(self, name, piece_type: PieceType):
        self.name = name
        self.piece_type = piece_type

    def get_move(self, game, goats_to_place):
        """
        Method that has be implemented by each player(AI/HUMAN).
        """
        raise NotImplementedError()


class HumanPlayer(Player):
    """
    This Human Player class.
    """
    def get_move(self, game, goats_to_place):
        """
        This method is used to get move input from human player.
        1. For goats there are 2 phases placement phase and move phase ( move/ rotate). All 15 goats have to placed before moving any piece
        2. The game state will keep track of no. of. gaots placed. If all 15 are placed then Goats are allowed to move/rotate
        3. For tigers, they are pre placed on board in fixed positions, so they only have move phase but allowed to rotate after goats are placed.
        4. If rotation allowed,
        :param game: the current game state
        :param goats_to_place: number of goats yet to place
        :return: (move type, source node, destination node(optional))
        """
        # Goat placement
        if self.piece_type == PieceType.GOAT and game.goats_to_place > 0:
            raw = input(f"{self.name}: Place GOAT — enter node: ")
            return ("place", int(raw))

        # Movement phase for gaots and tigers
        if game.game_type == 'rotation' and game.goats_to_place == 0:
            print("  Options:  m) move piece     r) rotate a zone")
            choice = input("  Choice: ").strip().lower()
            if choice == "r":
                print("  Available zones:")
                for key, z in ROTATION_ZONES.items():
                    blocked = (key == game.last_rotated_zone)
                    status = "  [BLOCKED — just rotated]" if blocked else ""
                    print(f"    {key:4s}  {z['name']}  nodes: {z['perimeter']}{status}")
                zone = input("  Zone key: ").strip().upper()
                direction = input("  Direction (cw / ccw): ").strip().lower()
                return ("rotate", zone, direction == "cw")
        raw = input(f"{self.name}: Move {self.piece_type.value} — 'src dst': ")
        src, dst = map(int, raw.split())
        return ("move", src, dst)


class Game():
    """
    This is game class.
    1. It initialize the board object
    2. Initiaze the Players ojects
    3. Keeps track of essential metrics like no. of goats yet be placed, no. of goats captured, no. of tigers blocked,
       players history.
    """
    def __init__(self, game_type = 'original'):
        self.board = Board()
        self.game_type = game_type
        self.players = [
            HumanPlayer("Tiger Player", PieceType.TIGER),
            HumanPlayer("Goat Player",  PieceType.GOAT),
        ]
        self.index           = 0 # goats turn is first as tigers are already placed on the
        self.goats_to_place  = 15
        self.goats_captured  = 0
        self.tigers_blocked  = 0
        self._player_history = [
            deque(maxlen=HISTORY_MAXLEN),
            deque(maxlen=HISTORY_MAXLEN),
        ]
        self.initialize_tigers()
        self.last_rotated_zone = None

    def initialize_tigers(self):
        """
        To initialize the tigers in fixed positions nodes(0,3,4)
        """
        for node in [0, 3, 4]:
            self.board.set_value(node, "T")

    def switch_player(self):
        """
        Switch Players turn
        """
        self.index = 1 - self.index

    def get_current_player(self):
        """
        To get the current player in the game.
        """
        return self.players[self.index]

    def record_move(self, move):
        """
        To store the move in players history.
        :param move:
        :return:
        """
        self._player_history[self.index].append(move)

    def reset_draw_history(self):
        for h in self._player_history:
            h.clear()

    def is_draw(self):
        """
        To check draw conditions - If players do not have best moves left they will stuck in a cycle making same moves back and forth.
        :return: bool
        """
        return (is_cycle(self._player_history[0]) and
                is_cycle(self._player_history[1]))

    def is_game_over(self):
        """
        To Check if the game is over or not.
        """

        # if tigers capture 5 goats the tigers win
        if self.goats_captured >= 5:
            print("Tigers win!")
            return True

        # if both players stuck in cycle neither of them can win so its a draw.
        if self.is_draw():
            print("It's a draw! Both players are stuck in a repeating cycle.")
            return True

        # If all 3 tigers are blocked the goats win.
        if self.is_tiger_blocked():
            print("Goats win!")
            return True
        return False

    def clone(self) -> "Game":
        """
        Clone the game state for mini max function.
        """
        return copy.deepcopy(self)

    def is_valid(self, move, piece_type):
        """
        This method is to check if the move is valid.
        1. if move is place (Goats) there should be more than 0 goats to place
        2. If the move is place
           a. destination node should be empty
           b. source node should be the players pice type
           c. destination should be in neighbors if the move is not jump.
           d. if the move is jump check if the jump is valid
        3. Check if the rotation is valid
           a. rotation zone should exist
           b. All goats should be placed
           c. If the grid is rotated in last move the in valid.
           d. Players piece should exist in the rotation grid.
        :param move:
        :param piece_type:
        :return:
        """
        if move is None:
            return False
        if move[0] == "place":
            _, node = move
            if piece_type == PieceType.GOAT:
                return self.goats_to_place > 0 and self.board.is_empty(node)
        elif move[0] == "move":
            _, source, destination = move
            if not self.board.is_empty(destination):
                return False
            if self.board.get_value(source) != piece_type.value:
                return False
            neighbours = self.board.get_neighbors(source) #O(k)
            if piece_type == PieceType.GOAT:
                return self.goats_to_place == 0 and destination in neighbours
            elif piece_type == PieceType.TIGER:
                if destination in neighbours:
                    return True
                return self.is_valid_tiger_jump(source, destination)
        elif move[0] == "rotate":
            if self.game_type != "rotation":  # blocked in original mode
                return False
            if self.goats_to_place > 0:  # Phase 1 locked
                return False
            _, zone_key, _cw = move
            if zone_key not in ROTATION_ZONES:
                return False
            if zone_key == self.last_rotated_zone:
                return False
            grid = ROTATION_ZONES[zone_key]["perimeter"]
            return any(self.board.get_value(n) == piece_type.value for n in grid) #O(k)
        return False

    def is_valid_tiger_jump(self, source, destination):
        """
        to check the tiger jump is valid or not
        1. It will look into the jump look up table and if the source and destination exist in the table then
        2. It will check if the middle node has Goat in it if yes then it is a valid jump.
        :return: bool
        """
        mid = VALID_JUMP_LANDINGS.get(source, {}).get(destination)
        if mid is None:
            return False
        return (self.board.get_value(mid) == "G"
                and self.board.is_empty(destination))

    def apply_move(self, move, piece_type: PieceType):
        """
        This method is to apply the decided move and update the board.
        It used board methods to achive the move
        1. Placing Goats ( set the node value)
        2. Moving Goats ( set the destination value and remove the source value)
        3. Moving Tigers ( set the node value and remove the destination value)
        4. Jumping Tigers ( set the destination value, remove source value,
                            capture the goat - remove middle node value and keep track of number of nodes captures)
        """
        if move[0] == "place":
            _, node = move
            if piece_type == PieceType.GOAT:
                self.board.set_value(node, "G")
                self.goats_to_place -= 1
            elif piece_type == PieceType.TIGER:
                self.board.set_value(node, "T")
            self.reset_draw_history()
        elif move[0] == "move":
            _, source, destination = move
            is_jump = (piece_type == PieceType.TIGER and
                       destination not in self.board.get_neighbors(source))
            if is_jump:
                self.capture(source, destination)
            else:
                self.record_move(move)
            self.board.set_value(destination, piece_type.value)
            self.board.set_value(source, None)
        elif move[0] == "rotate":
            _, zone_key, clockwise = move
            self.apply_rotation(zone_key, clockwise)
            self.last_rotated_zone = zone_key
            return
        self.last_rotated_zone = None

    def apply_rotation(self, zone_key, clockwise):
        """
        Rotates the given grid in the given direction.
        """
        ring = ROTATION_ZONES[zone_key]["perimeter"]
        values = [self.board.get_value(n) for n in ring]
        if clockwise:
            values = [values[-1]] + values[:-1]
        else:
            values = values[1:] + [values[0]]
        for node, val in zip(ring, values):
            self.board.set_value(node, val)

    def is_tiger_blocked(self):
        """
        To check if the tigers are blocked or not.
        It will scans the board, if Tiger node is found then checks the neighbors
        If none of the neighbors are empty
        It also checks if any jumps are possible
        the considers as blocked
        Updates the blocked tiger count.
        """
        blocked_count = 0
        for node in self.board.G.nodes:
            if self.board.get_value(node) == "T":
                tiger_can_move = False
                for nb in self.board.get_neighbors(node):
                    if self.board.is_empty(nb):
                        tiger_can_move = True
                        break
                    if self.board.get_value(nb) == "G":
                        for landing, mid_node in VALID_JUMP_LANDINGS.get(node, {}).items():
                            if mid_node == nb and self.board.is_empty(landing):
                                tiger_can_move = True
                                break
                    if tiger_can_move:
                        break
                if not tiger_can_move:
                    blocked_count += 1

        self.tigers_blocked = blocked_count
        return blocked_count == 3

    def capture(self, source, destination):
        """
        To capture the goats.
        """
        mid = VALID_JUMP_LANDINGS[source][destination]
        self.board.set_value(mid, None)
        self.goats_captured += 1
        self.reset_draw_history()

    def game(self):
        """
        This the main game loop that alternated chances for both players.
        """
        while not self.is_game_over():
            player = self.get_current_player()
            while True:
                move = player.get_move(self, self.goats_to_place)
                if move is None:
                    print(f"{player.name} has no valid moves — skipping turn.")
                    break
                if self.is_valid(move, player.piece_type):
                    break
                print("Invalid move. Try again.")
            if move is not None:
                self.apply_move(move, player.piece_type)
                self.board.draw()
            self.switch_player()


class AIPlayer(Player):
    """
    This is AI Player class
    """
    def __init__(self, name, piece_type: PieceType, depth: int = 3):
        super().__init__(name, piece_type)
        self.depth = depth

    def get_move(self, game: "Game", goats_to_place):
        """
        This used Minimax for select the next move of the Player.
        """
        _, move = minimax(
            game, depth=self.depth,
            alpha=float("-inf"), beta=float("inf"),
            perspective=self.piece_type)
        if move is not None:
            print(f"[AI {self.name}] chose: {move}")
        else:
            print(f"[AI {self.name}] has no moves.")
        return move


def is_cycle(history: deque, min_repeats: int = 2, max_cycle: int = MAX_CYCLE_LEN):
    """
    To idenify if the players stuck in a loop.
    1. It takes each player moves history and checks if they are making same moves again and again
    2. If there are 2 cycles of same move for both players then considers they are stuck.
    """
    h = list(history)
    n = len(h)
    for cycle_len in range(1, max_cycle + 1):
        needed = cycle_len * min_repeats
        if n < needed:
            continue
        tail    = h[-needed:]
        pattern = tail[:cycle_len]
        if all(tail[i] == pattern[i % cycle_len] for i in range(needed)):
            return True
    return False


def get_all_moves(game: "Game", piece_type: PieceType):
    """
    This helper function for MiniMax. It will generate all possible moves that a player can make in current game state.
    return: List of all possible moves
    """
    moves = []
    capture_moves = []
    if piece_type == PieceType.GOAT and game.goats_to_place > 0:
        for node in game.board.G.nodes: # O(N)
            if game.board.is_empty(node): # O(1)
                moves.append(("place", node))
        return moves

    for node in game.board.G.nodes: # O(N)
        if game.board.get_value(node) == piece_type.value:
            for nb in game.board.get_neighbors(node): #O(k) k =2-4
                move = ("move", node, nb)
                if game.is_valid(move, piece_type): # # O(k) k can be considered constant
                    moves.append(move)
            if piece_type == PieceType.TIGER:
                for landing, mid_node in VALID_JUMP_LANDINGS.get(node, {}).items(): #O(k) valid jumps is constant
                    if (game.board.get_value(mid_node) == "G" and game.board.is_empty(landing)):
                        move = ("move", node, landing)
                        if game.is_valid(move, piece_type): # O(k) k can be considered constant
                            #moves.append(move)
                            capture_moves.append(move)
    if piece_type == PieceType.TIGER and capture_moves:
        return capture_moves
    if game.game_type == "rotation" and game.goats_to_place == 0:
        for zone_key in ROTATION_ZONES: #O(k) rotation zones are constant
            if zone_key == game.last_rotated_zone:
                continue
            moves.append(("rotate", zone_key, True))
            moves.append(("rotate", zone_key, False))
    return moves


def evaluate(game: "Game", perspective: PieceType):
    """
    This is helper function for MiniMax.
    It evaluates each move from all possible moves based on the given heuristics and piece type.
    """
    # Game over scenario for goats ( when min of 5 goats captured)
    if game.goats_captured >= 5:
        return 10000 if perspective == PieceType.TIGER else -10000
    # a draw scenario
    if game.is_draw():
        return -500
    # game over scenario for tigers ( when all the tigers are blocked)
    if game.is_tiger_blocked():
        return 10000 if perspective == PieceType.GOAT else -10000

    # a positive incentive when goats are captured
    score = game.goats_captured * 2000
    score += len(get_all_moves(game, PieceType.TIGER)) * 10
    score -= len(get_all_moves(game, PieceType.GOAT))  * 5

    if game.tigers_blocked == 1:
        score -= 100
    elif game.tigers_blocked == 2:
        score -= 200

    for node in game.board.G.nodes:
        if game.board.get_value(node) == "T":
            for landing, mid_node in VALID_JUMP_LANDINGS.get(node, {}).items():
                if game.board.is_empty(landing):
                    score += 30
                if (game.board.get_value(mid_node) == "G"
                        and game.board.is_empty(landing)):
                    score += 300
    if perspective == PieceType.GOAT:
        score = -score
    return score


def minimax(game: "Game", depth: int, alpha: int, beta: int,
            perspective: PieceType):
    """
    Minimax algorithm.
    """
    if depth == 0 or game.is_game_over():
        return evaluate(game, perspective), None
    moves = get_all_moves(game, perspective)
    if not moves:
        return evaluate(game, perspective), None
    opponent = PieceType.GOAT if perspective == PieceType.TIGER else PieceType.TIGER
    best_score = float("-inf")
    best_moves =  []
    for move in moves:
        sim = game.clone()
        sim.apply_move(move, perspective)
        score, _ = minimax(sim, depth - 1, -beta, -alpha, opponent)
        score = -score
        if score > best_score:
            best_score = score
            best_moves = [move]
        elif score == best_score:
            best_moves.append(move)

        alpha = max(alpha, best_score)
        if alpha >= beta:
            break
    return best_score, random.choice(best_moves)

def simulate_games(num_games=50):
    tiger_wins = 0
    goat_wins = 0
    draws = 0

    for i in range(num_games):
        game = Game(game_type="original")
        game.players = [
            AIPlayer("Tiger AI", PieceType.TIGER, depth=3),
            AIPlayer("Goat AI", PieceType.GOAT, depth=3),
        ]
        turns = 0
        while not game.is_game_over():
            player = game.get_current_player()
            move = player.get_move(game, game.goats_to_place)
            if move is None or not game.is_valid(move, player.piece_type):
                break
            game.apply_move(move, player.piece_type)
            game.switch_player()
            turns += 1

        if game.goats_captured >= 5:
            tiger_wins += 1
        elif game.is_tiger_blocked():
            goat_wins += 1
        else:
            draws += 1

    print("\n===== Simulation Results =====")
    print(f"Total games : {num_games}")
    print(f"Tiger wins  : {tiger_wins}  ({100 * tiger_wins / num_games:.0f}%)")
    print(f"Goat wins   : {goat_wins}   ({100 * goat_wins / num_games:.0f}%)")
    print(f"Draws       : {draws}        ({100 * draws / num_games:.0f}%)")


if __name__ == '__main__':
    #game = Game(game_type="original")
    # game = Game(game_type="rotation")
    # game.game()
    simulate_games(1)