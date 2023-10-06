#!/usr/bin/python3

import curses
import curses.textpad
from math import floor

def clamp(x, a, b):
    return min(max(x, a), b)

NORMAL, EDIT = range(2)

bl = "└"
br = "┘"
tl = "┌"
tr = "┐"

tm = "┬"
lm = "├"
rm = "┤"
bm = "┴"

h = "─"
v = "│"

c = "┼"

class Table:
    def __init__(self, win):
        super().__init__()
        self.win = win
        self.header_rows = 0
        self.items = []

        # Constraints to solve for each column
        #   Unconstrained columns are allocated equal proportion of the leftover space
        #   Constraints on non-existent columns are ignored
        self.constraints = {}

        # Solution to constraint problem
        #   If there is no solution, the entire table is set to pink
        self.solution = {}

    def set_weight(self, column, weight):
        self.constraints[column] = {"type": "weight", "value": weight}

    def set_width(self, column, width):
        self.constraints[column] = {"type": "width", "value": width}

    def solve(self):
        n = max(len(row) for row in self.items)
        solution = [None for _ in range(n)]
        (_, w) = self.win.getyx()

        # Horizontal space not taken by frames
        leftover = w - n - 1

        # Allocate widths
        for i in range(n):
            w = self.constraints.get(i)
            if w is not None:
                if w["type"] == "width":
                    solution[i] = w["value"]
                    leftover -= solution[i]

        # Allocate weights
        space = leftover
        for i in range(n):
            w = self.constraints.get(i)
            if w is not None and w["type"] == "weight":
                solution[i] = floor(space * w["value"])
                leftover -= solution[i]

        # Allocated unconstrained weights
        unconstrained_col_width = leftover // solution.count(None)
        for i in range(n):
            w = self.constraints.get(i)
            if w is None:
                solution[i] = unconstrained_col_width
                leftover -= solution[i]

        # Donate any leftover to the first weighted column
        for i in range(n):
            w = self.constraints.get(i)
            if w is None or w["type"] == "weight":
                solution[i] += leftover
                break

        # Not enought space for allocation
        if leftover < 0:
            raise ValueError("Solver failed")

        return solution

    def scroll_down(self):
        pass

    def scroll_up(self):
        pass

    def scroll_top(self):
        pass

    def scroll_bottom(self):
        pass

    def draw(self):
        (h, w) = self.win.getyx()

def main(stdscr):
    scr1 = curses.newwin(14, 14)

    stdscr.clear()
    stdscr.border()
    stdscr.refresh()

    scr1.clear()
    scr1.border()
    scr1.refresh()

    stdscr.getch()

curses.wrapper(main)
