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
        (_, w) = self.win.getmaxyx()

        # Horizontal space not taken by frames
        leftover = w - n - 1
        self.win.addstr(f"w = {w} ")
        self.win.addstr(f"leftover = {leftover} ")

        # Allocate widths
        for i in range(n):
            w = self.constraints.get(i)
            if w is not None:
                if w["type"] == "width":
                    solution[i] = w["value"]
                    leftover -= solution[i]

        # Allocate weights
        space = leftover
        self.win.addstr(f"space = {space}\n")
        for i in range(n):
            w = self.constraints.get(i)
            if w is not None and w["type"] == "weight":
                solution[i] = floor(space * w["value"])
                leftover -= solution[i]

        # Allocated unconstrained weights
        self.win.addstr(f"leftover = {leftover}\n")
        num_unconstrained_cols = solution.count(None)
        if num_unconstrained_cols != 0:
            unconstrained_col_width = floor(leftover / num_unconstrained_cols)
            for i in range(n):
                w = self.constraints.get(i)
                if w is None:
                    solution[i] = unconstrained_col_width
                    leftover -= solution[i]

        # Donate any leftover to the first weighted column
        for i in range(n):
            w = self.constraints.get(i)
            if w is None or w["type"] == "weight":
                self.win.addstr(f"donatee = {i}\n")
                solution[i] += leftover
                break

        # Not enought space for allocation
        if leftover < 0:
            raise ValueError("Solver failed")

        return solution

    def draw(self):
        # self.win.clear()
        solution = self.solve()
        self.win.addstr("\n")
        self.win.addstr(f"{solution}\n")
        self.win.addstr("*")
        for w in solution:
            self.win.addstr(" " * w)
            self.win.addstr("*")
        self.win.refresh()

def main(stdscr):
    table = Table(stdscr)
    table.items = [
        [1, 2, 3],
        [4, 5, 6],
    ]
    table.set_width(0, 10)
    table.set_weight(1, 0.3)
    table.set_weight(2, 0.7)
    table.draw()

    stdscr.getch()

curses.wrapper(main)
