#!/usr/bin/env python3
"""Simple terminal Pac-Man using ANSI escape codes and raw input."""
import sys
import os
import time
import random
import math
import tty
import termios
import select

# ANSI colors
YELLOW = '\033[93m'
RED = '\033[91m'
PINK = '\033[95m'
CYAN = '\033[96m'
ORANGE = '\033[33m'
BLUE = '\033[94m'
WHITE = '\033[97m'
DIM = '\033[2m'
BOLD = '\033[1m'
RESET = '\033[0m'
BLINK_BLUE = '\033[44;97m'
CLEAR = '\033[2J\033[H'
HIDE_CURSOR = '\033[?25l'
SHOW_CURSOR = '\033[?25h'

MAP_DATA = [
    "############################",
    "#............##............#",
    "#.####.#####.##.#####.####.#",
    "#o####.#####.##.#####.####o#",
    "#.####.#####.##.#####.####.#",
    "#..........................#",
    "#.####.##.########.##.####.#",
    "#.####.##.########.##.####.#",
    "#......##....##....##......#",
    "######.##### ## #####.######",
    "     #.##### ## #####.#     ",
    "     #.##          ##.#     ",
    "     #.## ###--### ##.#     ",
    "######.## #GGGGGG# ##.######",
    "      .   #GGGGGG#   .      ",
    "######.## #GGGGGG# ##.######",
    "     #.## ######## ##.#     ",
    "     #.##          ##.#     ",
    "     #.## ######## ##.#     ",
    "######.## ######## ##.######",
    "#............##............#",
    "#.####.#####.##.#####.####.#",
    "#.####.#####.##.#####.####.#",
    "#o..##.......  .......##..o#",
    "###.##.##.########.##.##.###",
    "###.##.##.########.##.##.###",
    "#......##....##....##......#",
    "#.##########.##.##########.#",
    "#.##########.##.##########.#",
    "#..........................#",
    "############################",
]

COLS = 28
ROWS = 31
DIR_OFFSETS = {'LEFT': (0, -1), 'RIGHT': (0, 1), 'UP': (-1, 0), 'DOWN': (1, 0)}
OPPOSITE = {'LEFT': 'RIGHT', 'RIGHT': 'LEFT', 'UP': 'DOWN', 'DOWN': 'UP'}


class Game:
    def __init__(self):
        self.reset()

    def reset(self):
        self.grid = [list(row) for row in MAP_DATA]
        self.score = 0
        self.lives = 3
        self.dots = sum(row.count('.') + row.count('o') for row in self.grid)
        self.over = False
        self.won = False
        self.fright = 0
        self.frame = 0
        self.mode_t = 0
        self.init_pos()

    def init_pos(self):
        self.pr, self.pc, self.pdir, self.pnext = 23, 14, 'LEFT', 'LEFT'
        self.fright = 0
        self.ghosts = [
            {'r':14,'c':12,'color':RED,'dir':'UP','name':'blinky','fr':False,'eat':False,'rel':0,'sc':(0,25)},
            {'r':14,'c':14,'color':PINK,'dir':'UP','name':'pinky','fr':False,'eat':False,'rel':30,'sc':(0,2)},
            {'r':14,'c':16,'color':CYAN,'dir':'UP','name':'inky','fr':False,'eat':False,'rel':60,'sc':(30,27)},
            {'r':14,'c':18,'color':ORANGE,'dir':'UP','name':'clyde','fr':False,'eat':False,'rel':90,'sc':(30,0)},
        ]

    def wall(self, r, c, ghost=False):
        if r < 0 or r >= ROWS or c < 0 or c >= COLS:
            return False
        ch = self.grid[r][c]
        if ghost:
            return ch in ('#', 'G')
        return ch in ('#', 'G', '-')

    def can(self, r, c, d, ghost=False):
        dr, dc = DIR_OFFSETS[d]
        nr, nc = r + dr, (c + dc) % COLS
        if nc < 0: nc = COLS - 1
        return not self.wall(nr, nc, ghost)

    def mv(self, r, c, d):
        dr, dc = DIR_OFFSETS[d]
        return r + dr, (c + dc) % COLS

    def ghost_target(self, g):
        if g['eat']: return (14, 14)
        if g['fr']: return (random.randint(0, ROWS-1), random.randint(0, COLS-1))
        scatter = self.mode_t < 140 or 400 <= self.mode_t < 540 or 800 <= self.mode_t < 840
        if scatter: return g['sc']
        if g['name'] == 'blinky': return (self.pr, self.pc)
        if g['name'] == 'pinky':
            dr, dc = DIR_OFFSETS[self.pdir]
            return (self.pr + dr*4, self.pc + dc*4)
        if g['name'] == 'inky':
            dr, dc = DIR_OFFSETS[self.pdir]
            ar, ac = self.pr + dr*2, self.pc + dc*2
            b = self.ghosts[0]
            return (2*ar - b['r'], 2*ac - b['c'])
        d = math.sqrt((g['r']-self.pr)**2 + (g['c']-self.pc)**2)
        return (self.pr, self.pc) if d > 8 else g['sc']

    def move_ghost(self, g):
        if g['rel'] > 0: g['rel'] -= 1; return
        t = self.ghost_target(g)
        best_d, best_dist = g['dir'], float('inf')
        for d in ('UP','DOWN','LEFT','RIGHT'):
            if d == OPPOSITE[g['dir']]: continue
            if not self.can(g['r'], g['c'], d, True): continue
            nr, nc = self.mv(g['r'], g['c'], d)
            dd = math.sqrt((nr-t[0])**2 + (nc-t[1])**2)
            if dd < best_dist: best_dist, best_d = dd, d
        g['dir'] = best_d
        if self.can(g['r'], g['c'], g['dir'], True):
            g['r'], g['c'] = self.mv(g['r'], g['c'], g['dir'])
        if g['eat'] and g['r'] == 14 and g['c'] == 14:
            g['eat'] = g['fr'] = False

    def update(self):
        if self.over or self.won: return
        self.frame += 1
        self.mode_t += 1

        if self.frame % 2 == 0:
            if self.can(self.pr, self.pc, self.pnext): self.pdir = self.pnext
            if self.can(self.pr, self.pc, self.pdir):
                self.pr, self.pc = self.mv(self.pr, self.pc, self.pdir)
            ch = self.grid[self.pr][self.pc]
            if ch == '.':
                self.grid[self.pr][self.pc] = ' '; self.score += 10; self.dots -= 1
            elif ch == 'o':
                self.grid[self.pr][self.pc] = ' '; self.score += 50; self.dots -= 1
                self.fright = 60
                for g in self.ghosts:
                    if not g['eat']: g['fr'] = True; g['dir'] = OPPOSITE[g['dir']]
            if self.dots <= 0: self.won = True; return

        if self.frame % 3 == 0:
            for g in self.ghosts: self.move_ghost(g)

        if self.fright > 0:
            self.fright -= 1
            if self.fright == 0:
                for g in self.ghosts: g['fr'] = False

        for g in self.ghosts:
            if g['r'] == self.pr and g['c'] == self.pc:
                if g['fr'] and not g['eat']:
                    g['eat'] = True; self.score += 200
                elif not g['eat']:
                    self.lives -= 1
                    if self.lives <= 0: self.over = True
                    else: self.init_pos()
                    return

    def render(self):
        gpos = {(g['r'], g['c']): g for g in self.ghosts}
        pac_mouth = {'LEFT': '<', 'RIGHT': '>', 'UP': 'v', 'DOWN': '^'}
        lines = []
        lives_str = 'C ' * self.lives
        lines.append(f"{YELLOW}{BOLD} SCORE: {self.score}   LIVES: {lives_str}  DOTS: {self.dots}{RESET}")
        lines.append("")

        for r in range(ROWS):
            row = ""
            for c in range(COLS):
                if r == self.pr and c == self.pc:
                    row += f"{YELLOW}{BOLD}{pac_mouth.get(self.pdir, 'C')}{RESET} "
                elif (r, c) in gpos:
                    g = gpos[(r, c)]
                    if g['eat']:
                        row += f'{WHITE}""{RESET}'
                    elif g['fr']:
                        if self.fright < 15 and self.frame % 6 < 3:
                            row += f'{WHITE}{BOLD}&&{RESET}'
                        else:
                            row += f'{BLINK_BLUE}&&{RESET}'
                    else:
                        row += f"{g['color']}{BOLD}MM{RESET}"
                else:
                    ch = self.grid[r][c]
                    if ch == '#':
                        row += f"{BLUE}██{RESET}"
                    elif ch == '.':
                        row += f"{DIM}· {RESET}"
                    elif ch == 'o':
                        row += f"{WHITE}{BOLD}● {RESET}"
                    elif ch == '-':
                        row += f"{WHITE}--{RESET}"
                    else:
                        row += "  "
            lines.append(row)

        if self.over:
            lines.append(f"\n{RED}{BOLD}  GAME OVER! Press 'r' to restart or 'q' to quit{RESET}")
        elif self.won:
            lines.append(f"\n{YELLOW}{BOLD}  YOU WIN! Press 'r' to restart or 'q' to quit{RESET}")
        else:
            lines.append(f"\n{DIM}  Arrow Keys/WASD: move | q: quit | r: restart{RESET}")

        return '\n'.join(lines)


def get_key():
    """Non-blocking key read."""
    if select.select([sys.stdin], [], [], 0)[0]:
        ch = sys.stdin.read(1)
        if ch == '\x1b':
            ch2 = sys.stdin.read(2)
            if ch2 == '[A': return 'UP'
            if ch2 == '[B': return 'DOWN'
            if ch2 == '[C': return 'RIGHT'
            if ch2 == '[D': return 'LEFT'
            return None
        return ch
    return None


def main():
    old_settings = termios.tcgetattr(sys.stdin)
    try:
        tty.setraw(sys.stdin.fileno())
        sys.stdout.write(HIDE_CURSOR)
        sys.stdout.flush()

        game = Game()
        started = False

        while True:
            key = get_key()

            if key == 'q' or key == 'Q':
                break
            elif key in ('UP', 'DOWN', 'LEFT', 'RIGHT'):
                game.pnext = key
                started = True
            elif key in ('w', 'W'): game.pnext = 'UP'; started = True
            elif key in ('s', 'S'): game.pnext = 'DOWN'; started = True
            elif key in ('a', 'A'): game.pnext = 'LEFT'; started = True
            elif key in ('d', 'D'): game.pnext = 'RIGHT'; started = True
            elif key in ('r', 'R'):
                game.reset(); started = False

            if started:
                game.update()

            sys.stdout.write(CLEAR + game.render() + '\n')
            sys.stdout.flush()
            time.sleep(0.08)

    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        sys.stdout.write(SHOW_CURSOR)
        sys.stdout.flush()
        print("\nThanks for playing!")


if __name__ == '__main__':
    main()
