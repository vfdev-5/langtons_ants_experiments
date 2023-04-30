import pickle

from datetime import datetime
from pathlib import Path
from typing import Optional

import fire
import pygame as pg

from ants import LangtonsAnt, Colony, half_pi


white = 255, 240, 200
black = 20, 20, 40
true_black = 0, 0, 0


class ColonyRenderer(Colony):

    board_color = white
    cell_color = black
    cell_size = 5

    ant_colors = [
        (255, 10, 10),
        (10, 10, 255),
    ]

    def draw(self, screen):
        screen.fill(self.board_color)
        for cell in self.board:
            x, y = cell
            rect = [
                self.cell_size * x,
                self.cell_size * y,
                self.cell_size,
                self.cell_size,
            ]
            pg.draw.rect(screen, self.cell_color, rect)

        for ant in self.ants:
            x, y = ant.position
            rect = [
                self.cell_size * x,
                self.cell_size * y,
                self.cell_size,
                self.cell_size,
            ]
            color = self.ant_colors[int(ant.white_turn_right)]
            pg.draw.rect(screen, color, rect)


def main(
    checkpoint: Optional[str] = None,
    exp_name: Optional[str] = None,
    cells_to_remove_from_init_pkl: Optional[str] = None,
    init_state: Optional[str] = None,
    step_by_step: bool = False,
    debug: bool = False,
):
    pg.init()

    screen = pg.display.set_mode((600, 600))
    screen.fill(white)

    pg.display.set_caption("Langton's ants")
    clock = pg.time.Clock()

    screen_width, screen_height = pg.display.get_window_size()
    print("Screen size:", screen_width, screen_height)

    if checkpoint is not None:
        assert Path(checkpoint).exists(), f"{checkpoint} is not found"
        colony, step = load_colony_state(checkpoint)
        print(
            f"Loaded a colony from checkpoint {checkpoint}: \n\tstep={step},\n\tcolony={colony}\n"
        )
    else:
        colony, step = init_colony_state(init_state)

    ##### Copy init cells to store as non-visited
    import copy

    nonvisited_init_cells = copy.deepcopy(colony.board)

    if cells_to_remove_from_init_pkl is not None:
        with open(cells_to_remove_from_init_pkl, "rb") as f:
            data = pickle.load(f)

        print(f"Remove init cells: {data}")
        count_before = len(colony.board)
        colony.board = colony.board - data
        print(f"- Removed {count_before - len(colony.board)} cells")

    ##### Setup experiment output folder
    output_path = None
    if not debug:
        now = datetime.now().strftime("%Y%m%d-%H%M%S")
        if exp_name is not None:
            now = f"{now}_{exp_name}"
        output_path = Path(__file__).parent / "output" / now
        output_path.mkdir(exist_ok=True, parents=True)

    ##### Loop
    done = False
    pause = False
    acc = 0.0
    max_acc = 25.0

    do_next = not step_by_step

    do_check_on_highway = True
    ant_directions = []

    while not done:

        for e in pg.event.get():
            if e.type == pg.QUIT or (
                e.type == pg.KEYDOWN and (e.key == pg.K_ESCAPE or e.key == pg.K_q)
            ):
                done = True
                break
            elif e.type == pg.KEYDOWN:
                if e.key == pg.K_SPACE:
                    pause = not pause
                elif e.key == pg.K_0:
                    print("Super slow mode: max_acc=2.0")
                    max_acc = 2.0
                elif e.key == pg.K_1:
                    print("Slower mode: max_acc=25.0")
                    max_acc = 25.0
                elif e.key == pg.K_2:
                    print("Faster mode: max_acc=100.0")
                    max_acc = 100.0
                elif e.unicode == "+":
                    colony.cell_size += 2
                elif e.unicode == "-":
                    colony.cell_size -= 2
                elif e.key == pg.K_RETURN:
                    do_next = True
                elif e.key == pg.K_s:
                    print(step, end=" ")
                elif e.key == pg.KMOD_LCTRL | pg.K_s:
                    if debug:
                        continue
                    filepath = output_path / f"checkpoint_{step}.pkl"
                    save_colony_state(filepath, colony, step)
                    print(f"Saved current game state: {filepath}")
                    pg.image.save(screen, output_path / f"screenshot_{step}.png")

        if pause:
            pg.display.update()
            clock.tick(1.0 + acc)
            continue

        colony.draw(screen)

        if (step == 0 or step % 250 == 0) and not debug:
            filepath = output_path / f"checkpoint_{step}.pkl"
            save_colony_state(filepath, colony, step)
            pg.image.save(screen, output_path / f"screenshot_{step}.png")

        if step > 0 and step % 1000 == 0:
            print(step, end=" ")

        if do_next:
            ant_directions.append(colony.ants[0].dir_as_int)
            colony.next()
            step += 1
            do_next = not step_by_step

            if do_check_on_highway and check_on_highway(ant_directions):
                print(f"First detected the ant on the highway pattern, step={step}")
                pause = True
                do_check_on_highway = False

        nonvisited_init_cells = nonvisited_init_cells & colony.board

        pg.display.update()
        clock.tick(1.0 + acc)
        acc = min(max_acc, acc + 1.0)

    pg.quit()

    if len(nonvisited_init_cells) > 0 and not debug:
        print("nonvisited_init_cells:", nonvisited_init_cells)
        with open(output_path / "nonvisited_init_cells.pkl", "wb") as f:
            pickle.dump(nonvisited_init_cells, f, pickle.HIGHEST_PROTOCOL)


def save_colony_state(filepath, colony, step):
    # An arbitrary collection of objects supported by pickle.
    data = {
        "step": step,
        "colony": colony,
    }
    with open(filepath, "wb") as f:
        # Pickle the 'data' dictionary using the highest protocol available.
        pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)


def load_colony_state(filepath):
    with open(filepath, "rb") as f:
        # The protocol version used is detected automatically, so we do not
        # have to specify it.
        data = pickle.load(f)
    return data["colony"], data["step"]


def init_colony_state(init_state):
    if init_state is not None:
        assert init_state in ("smin", "s8", "s14", "s22", "random10", "4pix")

        if init_state == "smin":
            colony = ColonyRenderer(
                ants=[
                    LangtonsAnt(39, 45, orientation=3 * half_pi, white_turn_right=True),
                ],
                init_state={
                    (41, 40),  # required
                    (41, 43),  # required
                    (41, 42),  # required
                    (40, 45),  # required
                    (39, 43),  # required
                    (40, 44),  # not required but faster to get to the highway
                    (39, 42),  # required
                    (40, 41),  # required
                },
            )
        elif init_state == "s8":
            colony = ColonyRenderer(
                ants=[
                    LangtonsAnt(39, 45, orientation=3 * half_pi, white_turn_right=True),
                ],
                init_state={
                    (41, 40),  # required
                    (41, 43),  # required
                    (41, 42),  # required
                    (40, 45),  # required
                    (39, 43),  # required
                    (40, 44),  # not required but faster to get to the highway
                    (39, 42),  # required
                    (40, 41),  # required
                },
            )
        if init_state == "s14":
            colony = ColonyRenderer(
                ants=[
                    LangtonsAnt(39, 45, orientation=3 * half_pi, white_turn_right=True),
                ],
                init_state={
                    (41, 40),
                    (40, 43),
                    (41, 43),
                    (38, 45),
                    (41, 42),
                    (40, 45),
                    (39, 43),
                    (41, 45),
                    (42, 44),
                    (40, 44),
                    (39, 42),
                    (40, 41),
                    (42, 43),
                    (41, 41),
                },
            )
        elif init_state == "s22":
            colony = ColonyRenderer(
                ants=[
                    LangtonsAnt(42, 44, orientation=3 * half_pi, white_turn_right=True),
                ],
                init_state={
                    (42, 48),
                    (43, 43),
                    (44, 48),
                    (45, 49),
                    (47, 46),
                    (45, 46),
                    (42, 47),
                    (41, 45),
                    (42, 44),
                    (42, 50),
                    (43, 51),
                    (43, 48),
                    (46, 50),
                    (41, 44),
                    (42, 43),
                    (42, 49),
                    (42, 46),
                    (43, 47),
                    (46, 49),
                    (46, 46),
                    (45, 44),
                    (47, 47),
                },
            )
        elif init_state == "4pix":
            colony = ColonyRenderer(
                ants=[
                    LangtonsAnt(50, 50),
                ],
                init_state={(47, 47), (53, 53), (47, 53), (53, 47)},
            )
        elif init_state == "random10":
            import random

            random.seed(0)
            colony = ColonyRenderer(
                ants=[
                    LangtonsAnt(
                        x=random.randint(20, 80),
                        y=random.randint(20, 80),
                        white_turn_right=bool(random.randint(0, 1)),
                    )
                    for _ in range(10)
                ]
            )
    else:
        colony = ColonyRenderer(
            ants=[
                LangtonsAnt(50, 50),
            ]
        )
        # colony = ColonyRenderer(ants=[LangtonsAnt(50, 50), ], init_state={(45, 45), })
        # colony = ColonyRenderer(ants=[LangtonsAnt(50, 50), ], init_state={(45, 45), (55, 55)})
        # colony = ColonyRenderer(
        #     ants=[LangtonsAnt(50, 50), ],
        #     init_state={
        #         (47, 47), (47, 50), (47, 53),
        #         (50, 47), (50, 53),
        #         (53, 47), (53, 50), (53, 53)
        #     }
        # )
    return colony, 0


def check_on_highway(ant_directions):
    pattern = "232103032321030123232103032101230303210101210123032303210121010121232323032101212321030103212323210303012321030323210301232321030321012303032101012101230323032101210101212323230321012123210301032123232103030123210303232103012323210303210123030321010121012303230321012101012123232303210121232103010321232321030301"
    ant_dirs_str = "".join(ant_directions)
    return pattern in ant_dirs_str


if __name__ == "__main__":
    fire.Fire(main)
