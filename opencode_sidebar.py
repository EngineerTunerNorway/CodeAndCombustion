#!/usr/bin/env python3
"""Flashy terminal sidebar UI for opencode."""

from __future__ import annotations

import curses
import locale
import time

locale.setlocale(locale.LC_ALL, "")

PANELS = [
    ("Workspace", "Ready"),
    ("Agents", "2 Active"),
    ("Tasks", "5 Queued"),
    ("Logs", "Streaming"),
    ("Security", "Clean"),
    ("Wallet", "Connected"),
]

SPINNER = ["◜", "◠", "◝", "◞", "◡", "◟"]


def safe_addstr(screen: curses.window, y: int, x: int, text: str, style: int = 0) -> None:
    """Write text without crashing if dimensions are too small."""
    try:
        screen.addstr(y, x, text, style)
    except curses.error:
        pass


def draw_sidebar(screen: curses.window, selected: int, tick: int) -> None:
    screen.erase()
    height, width = screen.getmaxyx()
    sidebar_w = max(30, min(42, width // 3))
    sidebar_w = min(sidebar_w, width - 1)
    color_count = 7 if curses.has_colors() else 1

    for y in range(height):
        band = ((y // 2) + tick) % color_count
        style = curses.color_pair((band % color_count) + 1) if curses.has_colors() else 0
        safe_addstr(screen, y, 0, " " * sidebar_w, style)

    for y in range(height):
        safe_addstr(screen, y, sidebar_w - 1, "│", curses.A_BOLD)

    header = f" {SPINNER[tick % len(SPINNER)]} OPENCODE SIDEBAR "
    safe_addstr(screen, 1, 2, header, curses.A_BOLD | curses.A_UNDERLINE)
    safe_addstr(screen, 3, 2, "Neon Control Hub", curses.A_DIM)

    start_y = 5
    for idx, (name, status) in enumerate(PANELS):
        y = start_y + idx * 2
        if y >= height - 3:
            break
        marker = "▶" if idx == selected else "•"
        line = f"{marker} {name:<10}  {status}"
        style = curses.A_BOLD if idx == selected else curses.A_NORMAL
        if idx == selected:
            style |= curses.A_REVERSE
        safe_addstr(screen, y, 2, line[: sidebar_w - 4], style)

    if height > 4:
        safe_addstr(screen, height - 3, 2, "↑/↓ move  Enter pulse", curses.A_DIM)
        safe_addstr(screen, height - 2, 2, "q to quit", curses.A_DIM)

    safe_addstr(screen, 0, sidebar_w + 2, "Main Canvas", curses.A_BOLD)
    safe_addstr(
        screen,
        2,
        sidebar_w + 2,
        "Use this sidebar with your opencode workflow for",
        curses.A_DIM,
    )
    safe_addstr(
        screen,
        3,
        sidebar_w + 2,
        "quick context switching and status visibility.",
        curses.A_DIM,
    )

    screen.refresh()


def run(screen: curses.window) -> None:
    curses.curs_set(0)
    screen.nodelay(True)
    screen.keypad(True)

    if curses.has_colors():
        curses.start_color()
        curses.use_default_colors()
        palette = [
            curses.COLOR_MAGENTA,
            curses.COLOR_BLUE,
            curses.COLOR_CYAN,
            curses.COLOR_GREEN,
            curses.COLOR_YELLOW,
            curses.COLOR_RED,
            curses.COLOR_WHITE,
        ]
        for idx, fg in enumerate(palette, start=1):
            curses.init_pair(idx, fg, -1)

    selected = 0
    tick = 0
    pulse_until = 0.0

    while True:
        draw_sidebar(screen, selected, tick)
        key = screen.getch()

        if key in (ord("q"), ord("Q")):
            break
        if key == curses.KEY_UP:
            selected = (selected - 1) % len(PANELS)
        elif key == curses.KEY_DOWN:
            selected = (selected + 1) % len(PANELS)
        elif key in (10, 13, curses.KEY_ENTER):
            pulse_until = time.time() + 0.5

        if pulse_until > time.time():
            safe_addstr(
                screen,
                1,
                24,
                " PULSE ",
                curses.A_BOLD | curses.A_BLINK | curses.A_REVERSE,
            )
            screen.refresh()

        tick += 1
        time.sleep(0.08)


if __name__ == "__main__":
    curses.wrapper(run)
