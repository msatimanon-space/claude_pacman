#!/usr/bin/env python3
"""Terminal-based Pac-Man game using curses."""
import curses
import time
import random
import math

# Map: # = wall, . = dot, o = power pellet, - = ghost door, G = ghost house, ' ' = empty
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

DIR_OFFSETS = {
    'LEFT':  (0, -1),
    'RIGHT': (0,  1),
    'UP':    (-1, 0),
    'DOWN':  (1,  0),
}

OPPOSITE = {'LEFT': 'RIGHT', 'RIGHT': 'LEFT', 'UP': 'DOWN', 'DOWN': 'UP'}


class PacmanGame:
    def __init__(self):
        self.reset()

    def reset(self):
        self.grid = [list(row) for row in MAP_DATA]
        self.score = 0
        self.lives = 3
        self.dots_remaining = sum(row.count('.') + row.count('o') for row in self.grid)
        self.game_over = False
        self.won = False
        self.fright_timer = 0
        self.frame = 0
        self.mode_timer = 0
        self.init_positions()

    def init_positions(self):
        self.pac_r, self.pac_c = 23, 14
        self.pac_dir = 'LEFT'
        self.pac_next_dir = 'LEFT'
        self.fright_timer = 0

        self.ghosts = [
            {'r': 14, 'c': 12, 'color': 1, 'dir': 'UP', 'name': 'blinky',
             'frightened': False, 'eaten': False, 'release': 0,
             'scatter': (0, COLS - 3)},
            {'r': 14, 'c': 14, 'color': 2, 'dir': 'UP', 'name': 'pinky',
             'frightened': False, 'eaten': False, 'release': 30,
             'scatter': (0, 2)},
            {'r': 14, 'c': 16, 'color': 3, 'dir': 'UP', 'name': 'inky',
             'frightened': False, 'eaten': False, 'release': 60,
             'scatter': (ROWS - 1, COLS - 1)},
            {'r': 14, 'c': 18, 'color': 4, 'dir': 'UP', 'name': 'clyde',
             'frightened': False, 'eaten': False, 'release': 90,
             'scatter': (ROWS - 1, 0)},
        ]

    def is_wall(self, r, c):
        if r < 0 or r >= ROWS or c < 0 or c >= COLS:
            return False  # tunnel
        ch = self.grid[r][c]
        return ch == '#' or ch == 'G' or ch == '-'

    def is_wall_ghost(self, r, c):
        if r < 0 or r >= ROWS or c < 0 or c >= COLS:
            return False
        ch = self.grid[r][c]
        return ch == '#' or ch == 'G'

    def can_move(self, r, c, d, is_ghost=False):
        dr, dc = DIR_OFFSETS[d]
        nr, nc = r + dr, c + dc
        if nc < 0: nc = COLS - 1
        if nc >= COLS: nc = 0
        if is_ghost:
            return not self.is_wall_ghost(nr, nc)
        return not self.is_wall(nr, nc)

    def move_entity(self, r, c, d):
        dr, dc = DIR_OFFSETS[d]
        nr, nc = r + dr, c + dc
        if nc < 0: nc = COLS - 1
        if nc >= COLS: nc = 0
        return nr, nc

    def get_ghost_target(self, ghost):
        if ghost['eaten']:
            return (14, 14)
        if ghost['frightened']:
            return (random.randint(0, ROWS - 1), random.randint(0, COLS - 1))

        in_scatter = (self.mode_timer < 140 or
                      (400 <= self.mode_timer < 540) or
                      (800 <= self.mode_timer < 840))

        if in_scatter:
            return ghost['scatter']

        if ghost['name'] == 'blinky':
            return (self.pac_r, self.pac_c)
        elif ghost['name'] == 'pinky':
            dr, dc = DIR_OFFSETS[self.pac_dir]
            return (self.pac_r + dr * 4, self.pac_c + dc * 4)
        elif ghost['name'] == 'inky':
            dr, dc = DIR_OFFSETS[self.pac_dir]
            ar, ac = self.pac_r + dr * 2, self.pac_c + dc * 2
            blinky = self.ghosts[0]
            return (2 * ar - blinky['r'], 2 * ac - blinky['c'])
        else:  # clyde
            dist = math.sqrt((ghost['r'] - self.pac_r) ** 2 + (ghost['c'] - self.pac_c) ** 2)
            if dist > 8:
                return (self.pac_r, self.pac_c)
            return ghost['scatter']

    def move_ghost(self, ghost):
        if ghost['release'] > 0:
            ghost['release'] -= 1
            return

        target = self.get_ghost_target(ghost)
        dirs = ['UP', 'DOWN', 'LEFT', 'RIGHT']
        best_dir = ghost['dir']
        best_dist = float('inf')

        for d in dirs:
            if d == OPPOSITE[ghost['dir']]:
                continue
            if not self.can_move(ghost['r'], ghost['c'], d, is_ghost=True):
                continue
            nr, nc = self.move_entity(ghost['r'], ghost['c'], d)
            dd = math.sqrt((nr - target[0]) ** 2 + (nc - target[1]) ** 2)
            if dd < best_dist:
                best_dist = dd
                best_dir = d

        ghost['dir'] = best_dir
        if self.can_move(ghost['r'], ghost['c'], ghost['dir'], is_ghost=True):
            ghost['r'], ghost['c'] = self.move_entity(ghost['r'], ghost['c'], ghost['dir'])

        if ghost['eaten'] and ghost['r'] == 14 and ghost['c'] == 14:
            ghost['eaten'] = False
            ghost['frightened'] = False

    def update(self):
        if self.game_over or self.won:
            return

        self.frame += 1
        self.mode_timer += 1

        # Move pacman every other frame
        if self.frame % 2 == 0:
            if self.can_move(self.pac_r, self.pac_c, self.pac_next_dir):
                self.pac_dir = self.pac_next_dir
            if self.can_move(self.pac_r, self.pac_c, self.pac_dir):
                self.pac_r, self.pac_c = self.move_entity(self.pac_r, self.pac_c, self.pac_dir)

            cell = self.grid[self.pac_r][self.pac_c]
            if cell == '.':
                self.grid[self.pac_r][self.pac_c] = ' '
                self.score += 10
                self.dots_remaining -= 1
            elif cell == 'o':
                self.grid[self.pac_r][self.pac_c] = ' '
                self.score += 50
                self.dots_remaining -= 1
                self.fright_timer = 60
                for g in self.ghosts:
                    if not g['eaten']:
                        g['frightened'] = True
                        g['dir'] = OPPOSITE[g['dir']]

            if self.dots_remaining <= 0:
                self.won = True
                return

        # Move ghosts every 3 frames
        if self.frame % 3 == 0:
            for g in self.ghosts:
                self.move_ghost(g)

        # Fright timer
        if self.fright_timer > 0:
            self.fright_timer -= 1
            if self.fright_timer == 0:
                for g in self.ghosts:
                    g['frightened'] = False

        # Collision
        for g in self.ghosts:
            if g['r'] == self.pac_r and g['c'] == self.pac_c:
                if g['frightened'] and not g['eaten']:
                    g['eaten'] = True
                    self.score += 200
                elif not g['eaten']:
                    self.lives -= 1
                    if self.lives <= 0:
                        self.game_over = True
                    else:
                        self.init_positions()
                    return


def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(80)

    # Init colors
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_RED, -1)      # blinky
    curses.init_pair(2, curses.COLOR_MAGENTA, -1)   # pinky
    curses.init_pair(3, curses.COLOR_CYAN, -1)      # inky
    curses.init_pair(4, curses.COLOR_YELLOW, -1)    # clyde (reuse yellow)
    curses.init_pair(5, curses.COLOR_YELLOW, -1)    # pacman
    curses.init_pair(6, curses.COLOR_BLUE, -1)      # walls
    curses.init_pair(7, curses.COLOR_WHITE, -1)     # dots
    curses.init_pair(8, curses.COLOR_BLUE, curses.COLOR_BLUE)  # frightened ghost
    curses.init_pair(9, curses.COLOR_WHITE, curses.COLOR_BLUE) # frightened blinking

    game = PacmanGame()
    paused = True

    while True:
        key = stdscr.getch()

        if key == ord('q') or key == ord('Q'):
            break
        elif key == curses.KEY_LEFT or key == ord('a') or key == ord('A'):
            game.pac_next_dir = 'LEFT'
            paused = False
        elif key == curses.KEY_RIGHT or key == ord('d') or key == ord('D'):
            game.pac_next_dir = 'RIGHT'
            paused = False
        elif key == curses.KEY_UP or key == ord('w') or key == ord('W'):
            game.pac_next_dir = 'UP'
            paused = False
        elif key == curses.KEY_DOWN or key == ord('s') or key == ord('S'):
            game.pac_next_dir = 'DOWN'
            paused = False
        elif key == ord(' '):
            if game.game_over or game.won:
                game.reset()
                paused = True
            else:
                paused = not paused

        if not paused:
            game.update()

        # Draw
        stdscr.clear()
        max_y, max_x = stdscr.getmaxyx()

        # Header
        header = f" Score: {game.score}  Lives: {'C ' * game.lives}  Dots: {game.dots_remaining} "
        if max_x > len(header):
            stdscr.addstr(0, (max_x - len(header)) // 2, header, curses.color_pair(5) | curses.A_BOLD)

        # Ghost positions for overlay
        ghost_positions = {}
        for g in game.ghosts:
            ghost_positions[(g['r'], g['c'])] = g

        # Draw map
        y_offset = 1
        for r in range(ROWS):
            if r + y_offset >= max_y - 1:
                break
            x_offset = max(0, (max_x - COLS * 2) // 2)
            for c in range(COLS):
                if x_offset + c * 2 + 1 >= max_x:
                    break

                # Check if pacman is here
                if r == game.pac_r and c == game.pac_c:
                    mouth = {
                        'LEFT': '< ',  'RIGHT': ' >',
                        'UP':   'V ',   'DOWN':  'A ',
                    }
                    pac_char = mouth.get(game.pac_dir, 'C ')
                    try:
                        stdscr.addstr(r + y_offset, x_offset + c * 2, pac_char,
                                      curses.color_pair(5) | curses.A_BOLD)
                    except curses.error:
                        pass
                    continue

                # Check if ghost is here
                if (r, c) in ghost_positions:
                    g = ghost_positions[(r, c)]
                    if g['eaten']:
                        gchar = '""'
                        gpair = curses.color_pair(7)
                    elif g['frightened']:
                        if game.fright_timer < 15 and game.frame % 6 < 3:
                            gchar = '&&'
                            gpair = curses.color_pair(9) | curses.A_BOLD
                        else:
                            gchar = '&&'
                            gpair = curses.color_pair(8) | curses.A_BOLD
                    else:
                        gchar = 'MM'
                        gpair = curses.color_pair(g['color']) | curses.A_BOLD
                    try:
                        stdscr.addstr(r + y_offset, x_offset + c * 2, gchar, gpair)
                    except curses.error:
                        pass
                    continue

                ch = game.grid[r][c]
                if ch == '#':
                    try:
                        stdscr.addstr(r + y_offset, x_offset + c * 2, '██',
                                      curses.color_pair(6))
                    except curses.error:
                        pass
                elif ch == '.':
                    try:
                        stdscr.addstr(r + y_offset, x_offset + c * 2, '· ',
                                      curses.color_pair(7))
                    except curses.error:
                        pass
                elif ch == 'o':
                    try:
                        stdscr.addstr(r + y_offset, x_offset + c * 2, '● ',
                                      curses.color_pair(7) | curses.A_BOLD)
                    except curses.error:
                        pass
                elif ch == '-':
                    try:
                        stdscr.addstr(r + y_offset, x_offset + c * 2, '--',
                                      curses.color_pair(7))
                    except curses.error:
                        pass
                else:
                    try:
                        stdscr.addstr(r + y_offset, x_offset + c * 2, '  ')
                    except curses.error:
                        pass

        # Status messages
        msg_y = ROWS + y_offset + 1
        if msg_y < max_y:
            if game.game_over:
                msg = "GAME OVER! Press SPACE to restart or Q to quit"
                try:
                    stdscr.addstr(msg_y, max(0, (max_x - len(msg)) // 2), msg,
                                  curses.color_pair(1) | curses.A_BOLD)
                except curses.error:
                    pass
            elif game.won:
                msg = "YOU WIN! Press SPACE to restart or Q to quit"
                try:
                    stdscr.addstr(msg_y, max(0, (max_x - len(msg)) // 2), msg,
                                  curses.color_pair(5) | curses.A_BOLD)
                except curses.error:
                    pass
            elif paused:
                msg = "Arrow Keys/WASD to move | SPACE to pause | Q to quit"
                try:
                    stdscr.addstr(msg_y, max(0, (max_x - len(msg)) // 2), msg,
                                  curses.color_pair(7))
                except curses.error:
                    pass

        stdscr.refresh()


if __name__ == '__main__':
    curses.wrapper(main)
