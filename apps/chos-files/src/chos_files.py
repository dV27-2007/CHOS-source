#!/usr/bin/env python3
import sys, subprocess, shutil
from pathlib import Path
import tkinter as tk
from tkinter import simpledialog, messagebox

BG="#030606"; PANEL="#071010"; PANEL2="#06110f"; SEL="#0f2f29"
FG="#2fffd0"; BR="#1edbb2"; BR2="#137a66"
FONT=("JetBrains Mono", 11)

class Files(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CHOS Files")
        self.geometry("980x620")
        self.configure(bg=BG)
        self.path = Path(sys.argv[1]).expanduser() if len(sys.argv) > 1 else Path.home()
        self.path = self.path.resolve()
        self.hist = []
        self.show_hidden = False
        self.items = []
        self.q = tk.StringVar()
        self.ui()
        self.open_dir(self.path, False)

    def btn(self, parent, text, cmd):
        return tk.Button(
            parent, text=text, command=cmd,
            bg=PANEL2, fg=FG,
            activebackground=SEL, activeforeground=FG,
            relief="flat", font=FONT,
            padx=10, pady=5,
            highlightthickness=1,
            highlightbackground=BR2
        )

    def ui(self):
        root = tk.Frame(self, bg=BG, padx=14, pady=14)
        root.pack(fill="both", expand=True)

        tk.Label(
            root, text="CHOS FILES",
            bg=BG, fg=FG,
            font=("JetBrains Mono", 15, "bold")
        ).pack(anchor="w")

        box = tk.Frame(root, bg=BR, padx=1, pady=1)
        box.pack(fill="both", expand=True, pady=(10, 0))

        body = tk.Frame(box, bg=PANEL, padx=10, pady=10)
        body.pack(fill="both", expand=True)

        top = tk.Frame(body, bg=PANEL)
        top.pack(fill="x")

        for text, cmd in [
            ("Back", self.back),
            ("Up", self.up),
            ("Home", lambda: self.open_dir(Path.home())),
            ("Refresh", self.refresh),
            ("Hidden", self.toggle_hidden),
        ]:
            self.btn(top, text, cmd).pack(side="left", padx=(0, 6))

        self.path_var = tk.StringVar()
        entry = tk.Entry(
            top, textvariable=self.path_var,
            bg=PANEL2, fg=FG,
            insertbackground=FG,
            font=FONT, relief="flat",
            highlightthickness=1,
            highlightbackground=BR2,
            highlightcolor=BR
        )
        entry.pack(side="left", fill="x", expand=True)
        entry.bind("<Return>", lambda e: self.open_dir(Path(self.path_var.get()).expanduser()))

        self.btn(top, "Go", lambda: self.open_dir(Path(self.path_var.get()).expanduser())).pack(side="left", padx=(6, 0))

        mid = tk.Frame(body, bg=PANEL)
        mid.pack(fill="both", expand=True, pady=(10, 0))

        side = tk.Frame(mid, bg=PANEL2, padx=8, pady=8)
        side.pack(side="left", fill="y")

        for name, path in [
            ("Home", Path.home()),
            ("Desktop", Path.home() / "Desktop"),
            ("Downloads", Path.home() / "Downloads"),
            ("Documents", Path.home() / "Documents"),
            ("Pictures", Path.home() / "Pictures"),
            ("Root", Path("/")),
        ]:
            self.btn(side, name, lambda p=path: self.open_dir(p)).pack(fill="x", pady=3)

        right = tk.Frame(mid, bg=PANEL)
        right.pack(side="left", fill="both", expand=True, padx=(10, 0))

        search = tk.Entry(
            right, textvariable=self.q,
            bg=PANEL2, fg=FG,
            insertbackground=FG,
            font=FONT, relief="flat",
            highlightthickness=1,
            highlightbackground=BR2,
            highlightcolor=BR
        )
        search.pack(fill="x")
        search.bind("<KeyRelease>", lambda e: self.render())

        lf = tk.Frame(right, bg=BR2, padx=1, pady=1)
        lf.pack(fill="both", expand=True, pady=(8, 0))

        self.list = tk.Listbox(
            lf, bg=PANEL2, fg=FG,
            selectbackground=SEL,
            selectforeground=FG,
            font=FONT,
            relief="flat",
            activestyle="none"
        )
        self.list.pack(side="left", fill="both", expand=True)

        sb = tk.Scrollbar(lf, command=self.list.yview)
        sb.pack(side="right", fill="y")
        self.list.config(yscrollcommand=sb.set)

        self.list.bind("<Double-Button-1>", lambda e: self.open_sel())
        self.list.bind("<Return>", lambda e: self.open_sel())
        self.list.bind("<Button-3>", self.menu)

        bot = tk.Frame(body, bg=PANEL)
        bot.pack(fill="x", pady=(10, 0))

        for text, cmd in [
            ("Open", self.open_sel),
            ("New Folder", self.new_folder),
            ("New File", self.new_file),
            ("Rename", self.rename),
            ("Trash", self.trash),
            ("Copy Path", self.copy_path),
        ]:
            self.btn(bot, text, cmd).pack(side="left", padx=(0, 6))

        self.status = tk.Label(bot, text="", bg=PANEL, fg=FG, font=FONT)
        self.status.pack(side="right")

        self.bind("<BackSpace>", lambda e: self.up())
        self.bind("<Delete>", lambda e: self.trash())
        self.bind("<F5>", lambda e: self.refresh())
        self.bind("<Control-h>", lambda e: self.toggle_hidden())

    def open_dir(self, p, push=True):
        try:
            p = Path(p).expanduser().resolve()
            if not p.is_dir():
                raise Exception("not a folder")
            if push and p != self.path:
                self.hist.append(self.path)
            self.path = p
            self.path_var.set(str(p))
            self.render()
        except Exception as e:
            messagebox.showerror("CHOS Files", f"Cannot open:\n{p}\n\n{e}")

    def render(self):
        query = self.q.get().lower()
        self.list.delete(0, tk.END)

        items = list(self.path.iterdir())
        if not self.show_hidden:
            items = [x for x in items if not x.name.startswith(".")]
        if query:
            items = [x for x in items if query in x.name.lower()]

        dirs = sorted([x for x in items if x.is_dir()], key=lambda x: x.name.lower())
        files = sorted([x for x in items if not x.is_dir()], key=lambda x: x.name.lower())
        self.items = dirs + files

        for x in self.items:
            prefix = "[D] " if x.is_dir() else "    "
            self.list.insert(tk.END, prefix + x.name)

        self.status.config(text=f"{len(dirs)} dirs | {len(files)} files")

    def sel(self):
        s = self.list.curselection()
        return self.items[s[0]] if s else None

    def open_sel(self):
        p = self.sel()
        if not p:
            return
        if p.is_dir():
            self.open_dir(p)
        else:
            subprocess.Popen(["xdg-open", str(p)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def back(self):
        if self.hist:
            self.open_dir(self.hist.pop(), False)

    def up(self):
        self.open_dir(self.path.parent)

    def refresh(self):
        self.open_dir(self.path, False)

    def toggle_hidden(self):
        self.show_hidden = not self.show_hidden
        self.render()

    def new_folder(self):
        name = simpledialog.askstring("CHOS Files", "Folder name:")
        if name:
            (self.path / name).mkdir(exist_ok=False)
            self.render()

    def new_file(self):
        name = simpledialog.askstring("CHOS Files", "File name:")
        if name:
            (self.path / name).touch(exist_ok=False)
            self.render()

    def rename(self):
        p = self.sel()
        if not p:
            return
        name = simpledialog.askstring("CHOS Files", "New name:", initialvalue=p.name)
        if name:
            p.rename(p.parent / name)
            self.render()

    def trash(self):
        p = self.sel()
        if not p:
            return
        if not messagebox.askyesno("CHOS Files", f"Move to trash?\n{p.name}"):
            return

        if shutil.which("gio"):
            subprocess.check_call(["gio", "trash", str(p)])
        elif shutil.which("trash-put"):
            subprocess.check_call(["trash-put", str(p)])
        else:
            messagebox.showerror("CHOS Files", "No trash backend found")
            return

        self.render()

    def copy_path(self):
        p = self.sel() or self.path
        self.clipboard_clear()
        self.clipboard_append(str(p))
        self.status.config(text="path copied")

    def menu(self, e):
        i = self.list.nearest(e.y)
        self.list.selection_clear(0, tk.END)
        self.list.selection_set(i)

        m = tk.Menu(
            self, tearoff=0,
            bg=PANEL2, fg=FG,
            activebackground=SEL,
            activeforeground=FG
        )
        m.add_command(label="Open", command=self.open_sel)
        m.add_command(label="Rename", command=self.rename)
        m.add_command(label="Trash", command=self.trash)
        m.add_command(label="Copy Path", command=self.copy_path)
        m.tk_popup(e.x_root, e.y_root)

Files().mainloop()
