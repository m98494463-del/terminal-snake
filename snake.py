"""Terminal Snake — a colorful snake game for your terminal.

Controls: arrows / WASD to move, P to pause, Q to quit.
"""
import argparse
import curses
import json
import time
from pathlib import Path

from snake_engine import DOWN, LEFT, RIGHT, UP, Game

SCORES = Path.home() / ".terminal_snake.json"
KEYS = {
    curses.KEY_UP: UP, ord("w"): UP, ord("W"): UP,
    curses.KEY_DOWN: DOWN, ord("s"): DOWN, ord("S"): DOWN,
    curses.KEY_LEFT: LEFT, ord("a"): LEFT, ord("A"): LEFT,
    curses.KEY_RIGHT: RIGHT, ord("d"): RIGHT, ord("D"): RIGHT,
}


def load_best() -> int:
    try:
        return json.loads(SCORES.read_text()).get("best", 0)
    except (OSError, ValueError):
        return 0


def save_best(score: int) -> None:
    try:
        SCORES.write_text(json.dumps({"best": score}))
    except OSError:
        pass


def center(win, y, text, attr=0):
    h, w = win.getmaxyx()
    win.addstr(y, max(0, (w - len(text)) // 2), text[: w - 1], attr)


def play(stdscr, wrap: bool) -> None:
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.keypad(True)
    curses.start_color()
    curses.use_default_colors()
    for i, col in enumerate([curses.COLOR_GREEN, curses.COLOR_RED, curses.COLOR_YELLOW,
                             curses.COLOR_CYAN, curses.COLOR_MAGENTA], start=1):
        curses.init_pair(i, col, -1)

    best = load_best()
    while True:
        h, w = stdscr.getmaxyx()
        if h < 12 or w < 30:
            stdscr.erase(); center(stdscr, 0, "Terminal too small (min 30x12)"); stdscr.refresh()
            if stdscr.getch() in (ord("q"), ord("Q")):
                return
            time.sleep(0.2); continue
        game = Game(height=h - 3, width=(w - 3) // 2, wrap=wrap)
        paused = False
        while not game.over:
            key = stdscr.getch()
            while key != -1:
                if key in KEYS:
                    game.turn(KEYS[key])
                elif key in (ord("p"), ord("P"), ord(" ")):
                    paused = not paused
                elif key in (ord("q"), ord("Q")):
                    return
                key = stdscr.getch()
            if not paused:
                game.step()
            draw(stdscr, game, best, paused)
            time.sleep(game.tick_seconds)

        if game.score > best:
            best = game.score
            save_best(best)
        stdscr.nodelay(False)
        center(stdscr, h // 2 - 1, "  GAME OVER  ", curses.color_pair(2) | curses.A_BOLD | curses.A_REVERSE)
        center(stdscr, h // 2 + 1, f"Score {game.score}   Best {best}", curses.A_BOLD)
        center(stdscr, h // 2 + 3, "R = play again   Q = quit")
        stdscr.refresh()
        while (k := stdscr.getch()) not in (ord("r"), ord("R"), ord("q"), ord("Q")):
            pass
        if k in (ord("q"), ord("Q")):
            return
        stdscr.nodelay(True)


def draw(stdscr, game: Game, best: int, paused: bool) -> None:
    stdscr.erase()
    bar = f" SCORE {game.score}   BEST {max(best, game.score)}   LEVEL {game.level} "
    stdscr.addstr(0, 0, bar, curses.color_pair(4) | curses.A_BOLD)
    stdscr.addstr(0, len(bar) + 1, "arrows/WASD  P pause  Q quit", curses.A_DIM)
    top, W = 1, game.width * 2
    border = curses.color_pair(4)
    stdscr.addstr(top, 0, "+" + "-" * W + "+", border)
    for r in range(game.height):
        stdscr.addstr(top + 1 + r, 0, "|", border)
        stdscr.addstr(top + 1 + r, W + 1, "|", border)
    stdscr.addstr(top + 1 + game.height, 0, "+" + "-" * W + "+", border)

    def cell(pos, text, attr):
        stdscr.addstr(top + 1 + pos[0], 1 + pos[1] * 2, text, attr)

    if game.food:
        cell(game.food, "@@", curses.color_pair(2) | curses.A_BOLD)
    if game.bonus:
        blink = curses.A_BLINK if game.bonus_ttl < 12 else 0
        cell(game.bonus, "$$", curses.color_pair(3) | curses.A_BOLD | blink)
    for i, seg in enumerate(game.snake):
        if i == 0:
            cell(seg, "██", curses.color_pair(5) | curses.A_BOLD)
        else:
            cell(seg, "██" if i % 2 else "▓▓", curses.color_pair(1))
    if paused:
        center(stdscr, top + game.height // 2, "  PAUSED  ", curses.A_REVERSE | curses.A_BOLD)
    stdscr.refresh()


def main():
    parser = argparse.ArgumentParser(description="Colorful snake game for the terminal")
    parser.add_argument("--wrap", action="store_true", help="walls wrap around instead of killing you")
    args = parser.parse_args()
    curses.wrapper(play, args.wrap)


if __name__ == "__main__":
    main()
