import math


half_pi = math.pi * 0.5


class LangtonsAnt:
    def __init__(self, x=0, y=0, white_turn_right=True):
        self.position = [x, y]
        self.orientation = half_pi
        self.white_turn_right = white_turn_right

    def next(self, color):
        if color == "white":
            self.orientation += -half_pi if self.white_turn_right else half_pi
        else:
            self.orientation += half_pi if self.white_turn_right else -half_pi
        self.orientation %= 2 * math.pi
        dx, dy = int(math.cos(self.orientation)), int(math.sin(self.orientation))
        # DEBUG:
        # print(self.position[0], self.position[1], self.orientation, dx, dy)
        self.position[0] += dx
        self.position[1] += dy

    def __repr__(self):
        return f"LangtonsAnt({self.position}, {self.orientation}, white_turn_right={self.white_turn_right})"


class Colony:
    def __init__(self, init_state=None, ants=None):

        if ants is None:
            ants = [
                LangtonsAnt(),
            ]

        if init_state is None:
            init_state = set()

        self.ants = ants
        self.board = init_state

    def next(self):
        for ant in self.ants:
            p = tuple(ant.position)
            color = "black" if p in self.board else "white"
            ant.next(color)
            if color == "white":
                self.board.add(p)
            else:
                self.board.remove(p)

    def __getstate__(self):
        state = self.__dict__.copy()
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)

    def __repr__(self):
        return f"Colony:\nants={self.ants},\nboard={self.board}\n"
