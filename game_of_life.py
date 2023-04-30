import numpy as np


class GameOfLife:
    def __init__(self, init_state=None):

        if init_state is None:
            init_state = {(0, 0), (0, 1), (1, 0), (1, 1)}

        self.live_cells = set()
        self._bounds = None

        for cell in init_state:
            self.live_cells.add(cell)
        self._compute_bounds()

    def _compute_bounds(self):
        array = np.array(list(self.live_cells))
        if len(array) < 1:
            self._bounds = None
        else:
            min_x, min_y = array.min(axis=0)
            max_x, max_y = array.max(axis=0)
            self._bounds = [(min_x, min_y), (max_x, max_y)]

    def next(self):
        # Any live cell with fewer than two live neighbours dies, as if by underpopulation.
        # Any live cell with two or three live neighbours lives on to the next generation.
        # Any live cell with more than three live neighbours dies, as if by overpopulation.
        # Any dead cell with exactly three live neighbours becomes a live cell, as if by reproduction.

        dead_cells = []
        for cell in self.live_cells:
            x, y = cell
            num_neighbours = 0
            for dx, dy in [
                (-1, -1),
                (0, -1),
                (1, -1),
                (-1, 0),
                (1, 0),
                (-1, 1),
                (0, 1),
                (1, 1),
            ]:
                nx, ny = x + dx, y + dy
                if (nx, ny) in self.live_cells:
                    num_neighbours += 1
            if not num_neighbours in (2, 3):
                dead_cells.append((x, y))

        new_live_cells = []
        if self._bounds is not None:
            for x in range(self._bounds[0][0] - 1, self._bounds[1][0] + 2):
                for y in range(self._bounds[0][1] - 1, self._bounds[1][1] + 2):
                    if (x, y) in self.live_cells:
                        continue

                    num_neighbours = 0
                    for dx, dy in [
                        (-1, -1),
                        (0, -1),
                        (1, -1),
                        (-1, 0),
                        (1, 0),
                        (-1, 1),
                        (0, 1),
                        (1, 1),
                    ]:
                        nx, ny = x + dx, y + dy
                        if (nx, ny) in self.live_cells:
                            num_neighbours += 1
                    if num_neighbours == 3:
                        new_live_cells.append((x, y))

        for dead_cell in dead_cells:
            self.live_cells.remove(dead_cell)

        for cell in new_live_cells:
            self.live_cells.add(cell)

        self._compute_bounds()


def create_block(x=1, y=1, size=2):
    output = set()
    for nx in range(x, x + size):
        for ny in range(y, y + size):
            output.add((nx, ny))
    return output


def create_blinker(x=1, y=1):
    return {(x + 0, y + 1), (x + 1, y + 1), (x + 2, y + 1)}


def create_beacon(x=1, y=1):
    b1 = create_block(x, y)
    b2 = create_block(x + 2, y + 2)
    return b1 | b2


def create_toad(x=2, y=2):
    b1 = create_blinker(x, y)
    b2 = create_blinker(x - 1, y + 1)
    return b1 | b2


def create_penta_decathlon(x, y):
    output = set()
    for i in range(3):
        for j in range(8):
            if i == 1 and j in (1, 6):
                continue
            nx, ny = x + i, y + j
            output.add((nx, ny))
    return output


def create_r_pentomino(x, y):
    return {(x - 1, y), (x, y), (x, y + 1), (x, y - 1), (x + 1, y - 1)}


def create_gospel_glider_gun(x, y):
    b1 = create_block(x, y)
    b2 = create_block(x + 34, y - 1)
    b3 = {
        (x + 10, y),
        (x + 10, y + 1),
        (x + 10, y + 2),
        (x + 11, y - 1),
        (x + 11, y + 3),
        (x + 12, y - 2),
        (x + 13, y - 2),
        (x + 12, y + 4),
        (x + 13, y + 4),
        (x + 14, y + 1),
        (x + 15, y - 1),
        (x + 15, y + 3),
        (x + 16, y),
        (x + 16, y + 1),
        (x + 16, y + 2),
        (x + 17, y + 1),
    }
    b4 = {
        (x + 20, y - 2),
        (x + 20, y - 1),
        (x + 20, y),
        (x + 21, y - 2),
        (x + 21, y - 1),
        (x + 21, y),
        (x + 22, y - 3),
        (x + 22, y + 1),
        (x + 24, y - 3),
        (x + 24, y - 4),
        (x + 24, y + 1),
        (x + 24, y + 2),
    }
    return b1 | b2 | b3 | b4
