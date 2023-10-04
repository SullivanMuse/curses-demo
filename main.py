#!/usr/bin/python3

import curses
import curses.textpad
import argparse
import fnmatch

def clamp(x, a, b):
    return min(max(x, a), b)

NORMAL, EDIT = range(2)

def main(stdscr):
    global key
    stdscr.clear()
    stdscr.refresh()

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input")
    args = parser.parse_args()
    with open(args.input, "r") as file:
        lines = list(line.strip() for line in file)

    # Prevent curses from blocking on stdscr.getch()
    stdscr.nodelay(True)

    def newline():
        (y, _) = stdscr.getyx()
        stdscr.move(y + 1, 0)

    debug = False
    pattern = ""
    r = 0
    s = 0
    mode = "normal"
    while True:
        (h, w) = stdscr.getmaxyx()
        key = stdscr.getch()

        # Handle events

        # Normal mode
        if mode == "normal":
            if key == ord("q"):
                break
            elif key == ord("d"):
                debug = not debug
            elif key == ord("/"):
                mode = "edit"
                continue

        # Edit filter mode
        elif mode == "edit":
            if key == ord("\n"):
                mode = "normal"
                continue

            # Insert character
            elif ord("a") <= key <= ord("z") or ord("A") <= key <= ord("Z") or key == ord(" ") or key == ord("\t"):
                pattern = pattern[:r] + chr(key) + pattern[r:]
                r += 1
            elif key == curses.KEY_LEFT:
                r -= 1
            elif key == curses.KEY_RIGHT:
                r += 1
            elif key == curses.KEY_BACKSPACE:
                # Delete character at r-1
                pattern = pattern[:r-1] + pattern[r:]
                r -= 1
            elif key == curses.KEY_HOME:
                r = 0
            elif key == curses.KEY_END:
                r = len(pattern)
            elif key == curses.KEY_DC:
                # Delete character at r
                pattern = pattern[:r] + pattern[r+1:]

            # Clamp position
            r = clamp(r, 0, len(pattern))

            # Adjust scroll position
            window_max = s + w - 1
            if r > window_max:
                s += r - window_max
            if r < s:
                s = r

        # Draw
        current = fnmatch.filter(lines, f"*{pattern}*")
        stdscr.clear()
        stdscr.move(0, 0)
        for line in current:
            i = line.index(pattern)
            stdscr.addstr(line[:i])
            stdscr.addstr(line[i:i+len(pattern)], curses.A_BOLD)
            stdscr.addstr(line[i+len(pattern):])
            newline()
        if debug:
            stdscr.move(0, 0)
            stdscr.addnstr(f"(h, w) = {(h, w)}", w - 1); newline()
            stdscr.addnstr(f"(r, s) = {(r, s)}", w - 1); newline()
            stdscr.addnstr(f"mode = {mode}", w - 1); newline()
            stdscr.addnstr(f"buffer = {repr(pattern)}", w - 1); newline()
        if mode == "edit":
            stdscr.move(h - 1, 0)
            stdscr.addnstr(pattern[s : s + w - 1], w - 1)
            stdscr.move(h-1, r - s)
        stdscr.refresh()

        # Limit the FPS
        curses.napms(16)

curses.wrapper(main)
