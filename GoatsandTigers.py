"""
This Implementation of Goats and Tigers game
Author: Sravya Adapa (nadapa2)
"""
import networkx as nx
import matplotlib.pyplot as plt
from enum import Enum

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
        self.name = names
        self.piece_type = PieceType
    def move(self, board):
        raise NotImplementedError()

class AIPlayer(Player):
    """
    AI Player
    """
    def get_move(self, board):
        pass

class HumanPlayer(Player):
    """Human Player"""
    def get_move(self, board):
        pass

class Game():
    def __init__(self):
        self.board = Board()
        self.player1 = Player()
        self.player2 = Player()
        self.index = 0

    def switch_player(self):
        self.index = 1 - self.index

    def get_current_player(self):
        return self.players[self.index]

    def is_game_over(self, board):
        pass
    def is_valid(self, move,board):
        pass
    def apply_move(self, move, board):
        pass
    def game(self):
        while not self.is_game_over(self.board):
            player = self.get_current_player()
            move = player.get_move(self.board)
            if is_valid(move,board):
                self.apply_move(move, board)
                self.board.draw()
            self.switch_player()





if __name__ == '__main__':
    board = Board()
    board.set_value(0, "T")
    board.set_value(1, "G")
    board.draw()


