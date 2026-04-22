"""
This Implementation of Goats and Tigers game
Author: Sravya Adapa (nadapa2)
"""
from platform import node

import networkx as nx
import matplotlib.pyplot as plt
from enum import Enum
from networkx.classes import is_empty, neighbors
from shapely.predicates import is_valid
from webcolors import names


def original_layout():
    nodes = {
        # row 0
        0: (0, 4),

        # row 1 (6 nodes)
        1: (-2.5, 3), 2: (-1.5, 3), 3: (-0.5, 3),
        4: (0.5, 3), 5: (1.5, 3), 6: (2.5, 3),

        # row 2 (6 nodes)
        7: (-2.5, 2), 8: (-1.5, 2), 9: (-0.5, 2),
        10: (0.5, 2), 11: (1.5, 2), 12: (2.5, 2),

        # row 3 (6 nodes)
        13: (-2.5, 1), 14: (-1.5, 1), 15: (-0.5, 1),
        16: (0.5, 1), 17: (1.5, 1), 18: (2.5, 1),

        # row 4 (4 nodes)
        19: (-1.5, 0), 20: (-0.5, 0),
        21: (0.5, 0), 22: (1.5, 0),
    }

    edges = [
        # top
        (0, 2), (0, 3), (0, 4), (0,5),
        # row1
        (1, 2), (2, 3), (3, 4), (4, 5), (5, 6),

        # row2
        (7, 8), (8, 9), (9, 10), (10, 11), (11, 12),

        # row3
        (13, 14), (14, 15), (15, 16), (16, 17), (17, 18),

        # row4
        (19, 20), (20, 21), (21, 22),

        # verticals
        (1, 7), (7, 13),
        (2, 8), (8, 14),
        (3, 9), (9, 15),
        (4, 10), (10, 16),
        (5, 11), (11, 17),
        (6, 12), (12, 18),

        # bottom links
        (14, 19), (15, 20), (16, 21), (17, 22),

        # diagonals
        (3, 9), (4, 10)
    ]

    return nodes, edges

class Board():
    def __init__(self):
        self.G = nx.Graph()
        self.positions = {}
        self.build()

    def build(self, ):
        nodes, edges = original_layout()
        for id, pos in nodes.items():
            self.G.add_node(id, pos=pos, value= None)
        self.G.add_edges_from(edges)
        self.positions = nx.get_node_attributes(self.G, "pos")


    def set_value(self, node, value):
        if value not in [None, "T", "G"]:
            raise ValueError("Invalid Value")
        self.G.nodes[node]["value"] = value
    def is_empty(self, node):
        return self.G.nodes[node]["value"] == None
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
        nx.draw(
            self.G,
            self.positions,
            with_labels=True,
            node_color=color_map,
            node_size=800
        )
        plt.show()

class PieceType(Enum):
    TIGER = "T"
    GOAT = "G"

class Player():
    """
    Super Class ( Human and AI)
    Piece type( Tiger, Goat)
    """
    def __init__(self,name, piece_type: PieceType):
        self.name = name
        self.piece_type = PieceType
    def get_move(self, board):
        raise NotImplementedError()

class AIPlayer(Player):
    """
    AI Player
    """
    def get_move(self, board):
        pass

class HumanPlayer(Player):
    """Human Player"""
    def get_move(self, board, goats_to_place):
        while True:
            if self.piece_type == PieceType.GOAT and goats_to_place > 0:
                move_type = "place"
                move = input(f"{self.name} place goat on board. Enter node: ")
                node = int(move)
                # if not is_valid(self.piece_type,move_type,node):
                #     raise ValueError("Invalid Value")
                return (move_type, node)
            else:
                move_type = "move"
                move = input(f"move your {self.piece_type} n"
                             f"\nEnter source node and destination node: ")
                source, destination = map(int, move.split(" "))
                # if not is_valid(self.piece_type, move_type, source, destination):
                #     raise ValueError("Invalid Value")
                return (move_type, source, destination)


class Game():
    def __init__(self):
        self.board = Board()
        self.players = [HumanPlayer("Goat Player", PieceType.GOAT),
                        HumanPlayer("Tiger Player", PieceType.TIGER)]
        self.index = 0
        self.goats_to_place = 15
        self.goats_captured = 0
        self.tigers_blocked = 0
        self.initialize_tigers()

    def initialize_tigers(self):
        nodes = [1,3,4]
        for node in nodes:
            self.board.set_value(node, "T")

    def switch_player(self):
        self.index = 1 - self.index

    def get_current_player(self):
        return self.players[self.index]

    def is_game_over(self, board):
        if self.goats_captured == 15:
            print("Tigers Wins")
            return True
        elif self.tigers_blocked == 3:
            print("Goats Win")
            return True
        return False

    # def is_valid(self, move,board):
    #     pass

    def apply_move(self, move):
        player = self.get_current_player()
        if move[0] == "place":
            _, node = move
            self.board.set_value(node, "G")
            self.goats_to_place -= 1
        elif move[0] == "move":
            _, source, destination = move
            piece = player.piece_type
            if piece == "T" and destination not in self.board.get_neighbors(source):
                self.capture(source, destination)
            self.board.set_value(destination, piece)
            self.board.set_value(source, None)
        if self.is_tiger_blocked(board):
            self.tigers_blocked += 1

    def is_tiger_blocked(self, board):
        pass

    def capture(self, source, destination):
        src_pos = self.board.get_position(source)
        dst_pos = self.board.get_position(destination)
        mid = ((src_pos[0] + dst_pos[0]) / 2,
               (src_pos[1] + dst_pos[1]) / 2)
        for node in self.board.G.nodes:
            if self.board.get_position(node) == mid:
                self.board.set_value(node, None)
                self.goats_captured += 1

    def game(self):
        while not self.is_game_over(self.board):
            player = self.get_current_player()
            move = player.get_move(self.board)
            while True:
                move = player.get_move(board, self.goats_to_place)
                if self.board.is_valid(move, player.piece_type, self.goats_to_place):
                    break
                else:
                    print("Invalid move. Try again.")
            self.apply_move(move, self.board)
            # self.board.draw()
            self.switch_player()

if __name__ == '__main__':
    board = Board()
    board.set_value(0, "T")
    board.set_value(1, "G")
    board.draw()


