#!/usr/bin/env python3
import curses
import os
import subprocess
import getpass
import random
import time
import math
from datetime import datetime

REAL_USER = getpass.getuser()

MENU_ITEMS = [
    "Development / Start i3",
    "Terminal only",
    "Minecraft",
    "VS Code",
    "Firefox",
    "Reboot",
    "Shutdown",
]

LOGO = [
    " ██████╗██╗  ██╗  ██████╗ ███████╗",
    "██╔════╝██║  ██║ ██╔═══██╗██╔════╝",
    "██║     ███████║ ██║   ██║███████╗",
    "██║     ██╔══██║ ██║   ██║╚════██║",
    "╚██████╗██║  ██║ ╚██████╔╝███████║",
    " ╚═════╝╚═╝  ╚═╝  ╚═════╝ ╚══════╝",
]

STARS = []


def run(cmd):
    os.system("clear")
    os.system(cmd)


def check_password(password):
    result = subprocess.run(
        ["sudo", "-S", "-v"],
        input=password + "\n",
        text=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return result.returncode == 0


def safe_add(stdscr, y, x, text, attr=0):
    h, w = stdscr.getmaxyx()
    if 0 <= y < h and 0 <= x < w:
        try:
            stdscr.addstr(y, x, text[:max(0, w - x - 1)], attr)
        except curses.error:
            pass


def center(stdscr, y, text, color=1, bold=False):
    _, w = stdscr.getmaxyx()
    attr = curses.color_pair(color)
    if bold:
        attr |= curses.A_BOLD
    safe_add(stdscr, y, max(0, (w - len(text)) // 2), text, attr)


def init_stars(stdscr):
    global STARS
    h, w = stdscr.getmaxyx()
    count = max(140, (h * w) // 60)

    cx = w / 2
    cy = h / 2

    STARS = []
    for _ in range(count):
        STARS.append({
            "r": random.uniform(4, min(w, h) * 0.75),
            "angle": random.uniform(0, math.tau),
            "speed": random.uniform(0.08, 0.28),
            "depth": random.uniform(0.3, 2.5),
            "char": random.choice([".", "·", "*", "+"]),
            "tone": random.choice([1, 5, 6, 7, 8]),
        })


def draw_background(stdscr, t):
    h, w = stdscr.getmaxyx()

    if not STARS:
        init_stars(stdscr)

    cx = w / 2
    cy = h / 2

    for s in STARS:
        angle = s["angle"] + t * s["speed"]

        camera_wave = math.sin(t * 0.22) * 3.0
        r = s["r"] + camera_wave

        x = int(cx + math.cos(angle) * r * s["depth"])
        y = int(cy + math.sin(angle) * r * 0.45 * s["depth"])


        if 1 <= x < w - 1 and 2 <= y < h - 2:
            glow = (math.sin(t * 1.5 + s["angle"]) + 1) / 2

            attr = curses.color_pair(s["tone"])
            if glow > 0.65:
                attr |= curses.A_BOLD

            safe_add(stdscr, y, x, s["char"], attr)

    title = " CHOS TERMINAL SYSTEM "
    safe_add(
        stdscr,
        1,
        max(0, (w - len(title)) // 2),
        title,
        curses.color_pair(9) | curses.A_BOLD,
    )


def neon_box(stdscr, y, x, w, h, title="", active=True):
    t = time.time()
    breathe = (math.sin(t * 0.75) + 1) / 2

    border_attr = curses.color_pair(6 if active else 1)
    if breathe > 0.35:
        border_attr |= curses.A_BOLD

    glow_attr = curses.color_pair(10)
    if breathe > 0.68:
        glow_attr |= curses.A_BOLD

    glow_char = "░" if breathe < 0.65 else "▒"

    safe_add(stdscr, y - 1, x + 3, glow_char * max(0, w - 6), glow_attr)
    safe_add(stdscr, y + h, x + 3, glow_char * max(0, w - 6), glow_attr)

    safe_add(stdscr, y, x, "╔" + "═" * (w - 2) + "╗", border_attr)
    for i in range(1, h - 1):
        safe_add(stdscr, y + i, x, "║" + " " * (w - 2) + "║", border_attr)
    safe_add(stdscr, y + h - 1, x, "╚" + "═" * (w - 2) + "╝", border_attr)

    if title:
        safe_add(
            stdscr,
            y + 1,
            x + (w - len(title)) // 2,
            f" {title} ",
            curses.color_pair(3) | curses.A_BOLD,
        )


def draw_clock(stdscr, y, x, width):
    now = datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
    text = f" {now} "
    safe_add(
        stdscr,
        y,
        x + max(0, (width - len(text)) // 2),
        text,
        curses.color_pair(5) | curses.A_BOLD,
    )


def draw_input_frame(stdscr, y, x):
    attr = curses.color_pair(6)
    safe_add(stdscr, y, x, "╭" + "─" * 60 + "╮", attr)
    safe_add(stdscr, y + 1, x, "│", attr)
    safe_add(stdscr, y + 1, x + 61, "│", attr)
    safe_add(stdscr, y + 2, x, "│", attr)
    safe_add(stdscr, y + 2, x + 61, "│", attr)
    safe_add(stdscr, y + 3, x, "╰" + "─" * 60 + "╯", attr)


def draw_login_ui(stdscr, login_value="", password_value="", message=""):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    t = time.time()

    draw_background(stdscr, t)

    bw, bh = 82, 27
    y, x = max(1, (h - bh) // 2), max(1, (w - bw) // 2)

    neon_box(stdscr, y, x, bw, bh, "WELCOME")
    draw_clock(stdscr, y + 3, x, bw)

    for i, line in enumerate(LOGO):
        center(stdscr, y + 5 + i, line, 6, True)

    center(stdscr, y + 12, "TERMINAL ACCESS", 3, True)
    draw_input_frame(stdscr, y + 14, x + 10)

    safe_add(stdscr, y + 15, x + 14, "Login    :", curses.color_pair(3) | curses.A_BOLD)
    safe_add(stdscr, y + 16, x + 14, "Password :", curses.color_pair(3) | curses.A_BOLD)

    safe_add(stdscr, y + 15, x + 27, login_value, curses.color_pair(2) | curses.A_BOLD)
    safe_add(stdscr, y + 16, x + 27, "*" * len(password_value), curses.color_pair(2) | curses.A_BOLD)

    if message:
        safe_add(stdscr, y + 21, x + 12, message, curses.color_pair(4) | curses.A_BOLD)

    return y, x


def read_input(stdscr, field, login_value="", password_value=""):
    value = login_value if field == "login" else password_value
    curses.curs_set(1)
    stdscr.timeout(250)

    while True:
        y, x = draw_login_ui(
            stdscr,
            login_value=value if field == "login" else login_value,
            password_value=value if field == "password" else password_value,
        )

        input_y = y + 15 if field == "login" else y + 16
        input_x = x + 27

        stdscr.move(input_y, input_x + len(value))
        stdscr.refresh()

        ch = stdscr.getch()

        if ch == -1:
            continue

        if ch in (10, 13):
            break

        if ch in (127, 8, curses.KEY_BACKSPACE):
            if value:
                value = value[:-1]
            continue

        if 32 <= ch <= 126:
            value += chr(ch)

    stdscr.timeout(250)
    return value


def login_screen(stdscr):
    curses.curs_set(1)

    while True:
        login = ""
        password = ""

        draw_login_ui(stdscr, login, password)
        login = read_input(stdscr, "login", login, password)

        draw_login_ui(stdscr, login, password)
        password = read_input(stdscr, "password", login, password)

        if login == REAL_USER and check_password(password):
            curses.curs_set(0)
            return

        draw_login_ui(stdscr, login, password, "ACCESS DENIED. Press any key.")
        stdscr.refresh()
        stdscr.getch()


def draw_selected_item(stdscr, y, x, text, t):
    glow = (math.sin(t * 1.4) + 1) / 2

    if glow > 0.55:
        attr = curses.color_pair(11) | curses.A_BOLD
    else:
        attr = curses.color_pair(3) | curses.A_BOLD

    line = f"  ❯ {text} ❮  "
    safe_add(stdscr, y, x, line, attr)


def menu_screen(stdscr):
    curses.curs_set(0)
    selected = 0
    stdscr.timeout(250)

    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        t = time.time()

        draw_background(stdscr, t)

        bw, bh = 82, 28
        y, x = max(1, (h - bh) // 2), max(1, (w - bw) // 2)

        neon_box(stdscr, y, x, bw, bh, "CHOS")
        draw_clock(stdscr, y + 3, x, bw)
        center(stdscr, y + 5, "Choose what you want to do", 3)

        for i, item in enumerate(MENU_ITEMS):
            yy = y + 8 + i * 2

            if i == selected:
                draw_selected_item(stdscr, yy, x + 20, item, t)
            else:
                safe_add(stdscr, yy, x + 22, item, curses.color_pair(1))

        center(stdscr, y + bh - 5, "↑ ↓  select        Enter  run", 3)
        center(stdscr, y + bh - 3, "System ready", 5, True)

        stdscr.refresh()
        key = stdscr.getch()

        if key == -1:
            continue

        if key == curses.KEY_UP:
            selected = (selected - 1) % len(MENU_ITEMS)
        elif key == curses.KEY_DOWN:
            selected = (selected + 1) % len(MENU_ITEMS)
        elif key in (10, 13):
            choice = MENU_ITEMS[selected]

            if choice == "Development / Start i3":
                run("startx")
            elif choice == "Terminal only":
                os.system("clear")
                return
            elif choice == "Minecraft":
                run("cd /usr/games/tlauncher && /usr/games/tlauncher/lib/jvm/jre/bin/java -Dfile.encoding=UTF8 -jar /usr/games/tlauncher/starter-core.jar")
            elif choice == "VS Code":
                run("code --password-store=basic")
            elif choice == "Firefox":
                run("firefox")
            elif choice == "Reboot":
                run("systemctl reboot")
            elif choice == "Shutdown":
                run("systemctl poweroff")


def main(stdscr):
    curses.start_color()
    curses.use_default_colors()

    if curses.COLORS >= 256:
        curses.init_pair(1, 159, -1)  # crystal aqua - normal text
        curses.init_pair(2, 120, -1)  # fresh mint - input / success
        curses.init_pair(3, 228, -1)  # soft gold - warning / highlight
        curses.init_pair(4, 203, -1)  # coral red - error
        curses.init_pair(5, 255, -1)  # pure white - main bright text
        curses.init_pair(6, 45, -1)   # electric cyan - border
        curses.init_pair(7, 117, -1)  # ice blue - stars / secondary
        curses.init_pair(8, 22, -1)   # dark terminal green - logo shadow
        curses.init_pair(9, 46, -1)   # matrix green - CHOS logo / title
        curses.init_pair(10, 82, -1)  # bright green glow - logo glow
        curses.init_pair(11, 219, -1) # rose pink - selected item
    else:
        curses.init_pair(1, curses.COLOR_CYAN, -1)
        curses.init_pair(2, curses.COLOR_GREEN, -1)
        curses.init_pair(3, curses.COLOR_YELLOW, -1)
        curses.init_pair(4, curses.COLOR_RED, -1)
        curses.init_pair(5, curses.COLOR_WHITE, -1)
        curses.init_pair(6, curses.COLOR_CYAN, -1)
        curses.init_pair(7, curses.COLOR_YELLOW, -1)
        curses.init_pair(8, curses.COLOR_GREEN, -1)
        curses.init_pair(9, curses.COLOR_GREEN, -1)
        curses.init_pair(10, curses.COLOR_GREEN, -1)
        curses.init_pair(11, curses.COLOR_MAGENTA, -1)

    stdscr.bkgd(" ", curses.color_pair(1))
    stdscr.keypad(True)
    curses.cbreak()
    curses.noecho()

    init_stars(stdscr)

    login_screen(stdscr)
    menu_screen(stdscr)


if __name__ == "__main__":
    curses.wrapper(main)
