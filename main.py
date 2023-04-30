import pickle

from datetime import datetime
from pathlib import Path

import fire
import pygame as pg

from ants import LangtonsAnt, Colony


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


def main(checkpoint=None, exp_name=None):
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
        # colony = ColonyRenderer(ants=[LangtonsAnt(50, 50), ])
        # colony = ColonyRenderer(ants=[LangtonsAnt(50, 50), ], init_state={(45, 45), })
        # colony = ColonyRenderer(ants=[LangtonsAnt(50, 50), ], init_state={(45, 45), (55, 55)})

        colony = ColonyRenderer(
            ants=[
                LangtonsAnt(50, 50),
            ],
            init_state={(47, 47), (53, 53), (47, 53), (53, 47)},
        )

        # colony = ColonyRenderer(
        #     ants=[LangtonsAnt(50, 50), ],
        #     init_state={
        #         (47, 47), (47, 50), (47, 53),
        #         (50, 47), (50, 53),
        #         (53, 47), (53, 50), (53, 53)
        #     }
        # )

        # import random
        #
        # random.seed(0)
        # colony = ColonyRenderer(
        #     ants=[
        #         LangtonsAnt(
        #             x=random.randint(20, 80), y=random.randint(20, 80), white_turn_right=bool(random.randint(0, 1))
        #         )
        #         for _ in range(10)
        #     ]
        # )
        step = 0

    now = datetime.now().strftime("%Y%m%d-%H%M%S")
    if exp_name is not None:
        now = f"{now}_{exp_name}"
    output_path = Path(__file__).parent / "output" / now
    output_path.mkdir(exist_ok=True, parents=True)

    done = False
    pause = False
    acc = 0.0
    max_acc = 25.0
    while not done:

        for e in pg.event.get():
            if e.type == pg.QUIT or (
                e.type == pg.KEYUP and (e.key == pg.K_ESCAPE or e.key == pg.K_q)
            ):
                done = True
                break
            elif e.type == pg.KEYUP and e.key == pg.K_SPACE:
                pause = not pause
            elif e.type == pg.KEYUP and e.key == pg.K_0:
                print("Super slow mode: max_acc=2.0")
                max_acc = 2.0
            elif e.type == pg.KEYUP and e.key == pg.K_1:
                print("Slower mode: max_acc=25.0")
                max_acc = 25.0
            elif e.type == pg.KEYUP and e.key == pg.K_2:
                print("Faster mode: max_acc=100.0")
                max_acc = 100.0
            elif e.type == pg.KEYUP and e.key == pg.KMOD_LCTRL | pg.K_s:
                filepath = output_path / f"checkpoint_{step}.pkl"
                save_colony_state(filepath, colony, step)
                print(f"Saved current game state: {filepath}")
                pg.image.save(screen, output_path / f"screenshot_{step}.png")

        if pause:
            pg.display.update()
            clock.tick(1.0 + acc)
            continue

        colony.draw(screen)

        if step == 0 or step % 250 == 0:
            filepath = output_path / f"checkpoint_{step}.pkl"
            save_colony_state(filepath, colony, step)
            pg.image.save(screen, output_path / f"screenshot_{step}.png")

        if step % 1000 == 0:
            print(step, end=" ")

        colony.next()
        step += 1

        pg.display.update()
        clock.tick(1.0 + acc)
        acc = min(max_acc, acc + 1.0)

    pg.quit()


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


if __name__ == "__main__":
    fire.Fire(main)
