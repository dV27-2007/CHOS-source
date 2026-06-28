#!/usr/bin/env python3
import shutil
import subprocess
import sys
from pathlib import Path
import tkinter as tk

BG = "#030606"
PANEL = "#071010"
PANEL2 = "#06110f"
SEL = "#0f2f29"
BR2 = "#137a66"
BR = "#1edbb2"
FG = "#2fffd0"

FONT = ("JetBrains Mono", 11)
FONT_SMALL = ("JetBrains Mono", 10)
FONT_TITLE = ("JetBrains Mono", 16, "bold")


def path_is_relative_to(path, parent):
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


class Files(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CHOS Files")
        self.geometry("980x620")
        self.minsize(980, 620)
        self.configure(bg=BG)

        self.home = Path.home()
        self.path = self.home
        self.hist = []
        self.show_hidden = False
        self.directory_items = []
        self.items = []
        self.clipboard_item = None
        self.clipboard_mode = None

        self.path_var = tk.StringVar()
        self.search_var = tk.StringVar()
        self.info_var = tk.StringVar(value="")
        self.notice_var = tk.StringVar(value="READY")

        self.build_ui()
        self.search_var.trace_add("write", self.on_search_change)

        start_path = Path(sys.argv[1]).expanduser() if len(sys.argv) > 1 else self.home
        self.open_start_path(start_path)

    def build_ui(self):
        root = tk.Frame(self, bg=BG, padx=14, pady=14)
        root.pack(fill="both", expand=True)

        header = tk.Frame(root, bg=BG)
        header.pack(fill="x")

        tk.Label(
            header,
            text="CHOS FILES",
            bg=BG,
            fg=FG,
            font=FONT_TITLE,
        ).pack(side="left")

        tk.Label(
            header,
            text="OFFICIAL CHOS FILE MANAGER",
            bg=BG,
            fg=BR,
            font=FONT_SMALL,
        ).pack(side="right", pady=(4, 0))

        toolbar_outer, toolbar = self.panel(root)
        toolbar_outer.pack(fill="x", pady=(10, 0))

        for text, command in [
            ("Back", self.back),
            ("Up", self.up),
            ("Home", lambda: self.open_dir(self.home)),
            ("Refresh", self.refresh),
            ("Hidden", self.toggle_hidden),
        ]:
            self.button(toolbar, text, command).pack(side="left", padx=(0, 6))

        path_outer, path_row = self.panel(root)
        path_outer.pack(fill="x", pady=(10, 0))

        tk.Label(
            path_row,
            text="PATH",
            bg=PANEL,
            fg=BR,
            font=FONT_SMALL,
            width=8,
            anchor="w",
        ).pack(side="left", padx=(0, 8))

        self.path_entry = self.entry(path_row, self.path_var)
        self.path_entry.pack(side="left", fill="x", expand=True)
        self.path_entry.bind("<Return>", self.open_path_entry)
        self.path_entry.bind("<KP_Enter>", self.open_path_entry)

        self.button(path_row, "Go", self.open_path_entry).pack(side="left", padx=(8, 0))

        middle = tk.Frame(root, bg=BG)
        middle.pack(fill="both", expand=True, pady=(10, 0))

        sidebar_outer, sidebar = self.panel(middle, inner_bg=PANEL2, padx=10, pady=10)
        sidebar_outer.pack(side="left", fill="y")

        tk.Label(
            sidebar,
            text="SHORTCUTS",
            bg=PANEL2,
            fg=BR,
            font=FONT_SMALL,
            anchor="w",
        ).pack(fill="x", pady=(0, 8))

        for name, target in [
            ("Home", self.home),
            ("Desktop", self.home / "Desktop"),
            ("Downloads", self.home / "Downloads"),
            ("Documents", self.home / "Documents"),
            ("Pictures", self.home / "Pictures"),
            ("Root", Path("/")),
        ]:
            self.button(sidebar, name, lambda path=target: self.open_dir(path), fill=True).pack(
                fill="x", pady=3
            )

        content_outer, content = self.panel(middle)
        content_outer.pack(side="left", fill="both", expand=True, padx=(10, 0))

        search_row = tk.Frame(content, bg=PANEL)
        search_row.pack(fill="x")

        tk.Label(
            search_row,
            text="SEARCH",
            bg=PANEL,
            fg=BR,
            font=FONT_SMALL,
            width=8,
            anchor="w",
        ).pack(side="left", padx=(0, 8))

        self.search_entry = self.entry(search_row, self.search_var)
        self.search_entry.pack(side="left", fill="x", expand=True)

        self.button(search_row, "Clear", self.clear_search).pack(side="left", padx=(8, 0))

        list_outer = tk.Frame(content, bg=BR2, padx=1, pady=1)
        list_outer.pack(fill="both", expand=True, pady=(10, 0))

        list_frame = tk.Frame(list_outer, bg=PANEL2)
        list_frame.pack(fill="both", expand=True)

        self.listbox = tk.Listbox(
            list_frame,
            bg=PANEL2,
            fg=FG,
            selectbackground=BR,
            selectforeground=BG,
            activestyle="none",
            font=FONT,
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=BR2,
            highlightcolor=BR,
            exportselection=False,
            selectmode=tk.BROWSE,
        )
        self.listbox.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(
            list_frame,
            command=self.listbox.yview,
            bg=PANEL2,
            activebackground=BR2,
            troughcolor=PANEL,
            bd=0,
            highlightthickness=0,
            relief="flat",
            takefocus=0,
        )
        scrollbar.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=scrollbar.set)

        self.listbox.bind("<Double-Button-1>", self.open_sel)
        self.listbox.bind("<Return>", self.open_sel)
        self.listbox.bind("<KP_Enter>", self.open_sel)
        self.listbox.bind("<Button-3>", self.menu)
        self.listbox.bind("<Up>", lambda event: self.move_selection(-1))
        self.listbox.bind("<Down>", lambda event: self.move_selection(1))

        actions_outer, actions = self.panel(root)
        actions_outer.pack(fill="x", pady=(10, 0))

        for text, command in [
            ("Open", self.open_sel),
            ("New Folder", self.new_folder),
            ("New File", self.new_file),
            ("Rename", self.rename),
            ("Copy", self.copy_item),
            ("Cut", self.cut_item),
            ("Paste", self.paste_item),
            ("Trash", self.trash),
            ("Copy Path", self.copy_path),
        ]:
            self.button(actions, text, command).pack(side="left", padx=(0, 6))

        status_outer, status = self.panel(root, inner_bg=PANEL2, padx=12, pady=8)
        status_outer.pack(fill="x", pady=(10, 0))

        self.info_label = tk.Label(
            status,
            textvariable=self.info_var,
            bg=PANEL2,
            fg=FG,
            font=FONT_SMALL,
            anchor="w",
        )
        self.info_label.pack(side="left", fill="x", expand=True)

        self.notice_label = tk.Label(
            status,
            textvariable=self.notice_var,
            bg=PANEL2,
            fg=BR,
            font=FONT_SMALL,
            anchor="e",
        )
        self.notice_label.pack(side="right")

        for sequence, handler in [
            ("<BackSpace>", self.on_backspace),
            ("<Delete>", self.on_delete),
            ("<F5>", self.on_refresh_key),
            ("<Escape>", self.on_escape),
            ("<Control-f>", self.focus_search),
            ("<Control-F>", self.focus_search),
            ("<Control-l>", self.focus_path),
            ("<Control-L>", self.focus_path),
            ("<Control-h>", self.on_toggle_hidden_key),
            ("<Control-H>", self.on_toggle_hidden_key),
            ("<Control-c>", self.on_copy_shortcut),
            ("<Control-C>", self.on_copy_shortcut),
            ("<Control-x>", self.on_cut_shortcut),
            ("<Control-X>", self.on_cut_shortcut),
            ("<Control-v>", self.on_paste_shortcut),
            ("<Control-V>", self.on_paste_shortcut),
        ]:
            self.bind(sequence, handler)

    def panel(self, parent, inner_bg=PANEL, padx=10, pady=10):
        outer = tk.Frame(parent, bg=BR2, padx=1, pady=1)
        inner = tk.Frame(outer, bg=inner_bg, padx=padx, pady=pady)
        inner.pack(fill="both", expand=True)
        return outer, inner

    def button(self, parent, text, command, fill=False):
        width = 14 if fill else 0
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=PANEL2,
            fg=FG,
            activebackground=SEL,
            activeforeground=FG,
            relief="flat",
            bd=0,
            font=FONT,
            padx=10,
            pady=5,
            highlightthickness=1,
            highlightbackground=BR2,
            highlightcolor=BR,
            takefocus=0,
            anchor="w" if fill else "center",
            width=width,
        )

    def entry(self, parent, variable):
        return tk.Entry(
            parent,
            textvariable=variable,
            bg=PANEL2,
            fg=FG,
            insertbackground=FG,
            selectbackground=BR2,
            selectforeground=FG,
            relief="flat",
            bd=0,
            font=FONT,
            highlightthickness=1,
            highlightbackground=BR2,
            highlightcolor=BR,
        )

    def dialog_button(self, parent, text, command):
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=PANEL2,
            fg=FG,
            activebackground=SEL,
            activeforeground=FG,
            relief="flat",
            bd=0,
            font=FONT,
            padx=12,
            pady=5,
            highlightthickness=1,
            highlightbackground=BR2,
            highlightcolor=BR,
        )

    def open_start_path(self, target):
        try:
            target = target.expanduser()
            if target.exists() and target.is_file():
                self.open_dir(target.parent, push=False, selected_name=target.name)
            else:
                self.open_dir(target, push=False)
        except Exception as exc:
            self.show_error("CHOS Files", f"Cannot open:\n{target}\n\n{exc}")
            self.open_dir(self.home, push=False)

    def is_text_input_focus(self, widget=None):
        widget = widget or self.focus_get()
        return isinstance(widget, tk.Entry)

    def selected_name(self):
        selected = self.sel()
        return selected.name if selected else None

    def set_notice(self, message):
        self.notice_var.set(message)

    def update_info(self, dirs_count, files_count, visible_count):
        parts = [f"{dirs_count} dirs", f"{files_count} files", f"{visible_count} shown"]
        parts.append("hidden on" if self.show_hidden else "hidden off")
        query = self.search_var.get().strip()
        if query:
            parts.append(f"filter: {query}")
        self.info_var.set(" | ".join(parts))

    def center_dialog(self, dialog):
        self.update_idletasks()
        dialog.update_idletasks()
        width = dialog.winfo_reqwidth()
        height = dialog.winfo_reqheight()
        x = self.winfo_rootx() + max(0, (self.winfo_width() - width) // 2)
        y = self.winfo_rooty() + max(0, (self.winfo_height() - height) // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")

    def ask_text(self, title, prompt, initialvalue=""):
        result = {"value": None}
        dialog = tk.Toplevel(self)
        dialog.title(title)
        dialog.configure(bg=BG)
        dialog.transient(self)
        dialog.resizable(False, False)

        border = tk.Frame(dialog, bg=BR, padx=1, pady=1)
        border.pack(fill="both", expand=True, padx=14, pady=14)

        body = tk.Frame(border, bg=PANEL, padx=16, pady=16)
        body.pack(fill="both", expand=True)

        tk.Label(body, text=prompt, bg=PANEL, fg=FG, font=FONT, justify="left").pack(
            anchor="w"
        )

        value = tk.StringVar(value=initialvalue)
        entry = self.entry(body, value)
        entry.pack(fill="x", pady=(10, 0))

        buttons = tk.Frame(body, bg=PANEL)
        buttons.pack(fill="x", pady=(14, 0))

        def close():
            dialog.destroy()

        def accept():
            result["value"] = value.get().strip()
            dialog.destroy()

        self.dialog_button(buttons, "Cancel", close).pack(side="right")
        self.dialog_button(buttons, "Save", accept).pack(side="right", padx=(0, 6))

        dialog.bind("<Escape>", lambda event: close())
        dialog.bind("<Return>", lambda event: accept())
        dialog.bind("<KP_Enter>", lambda event: accept())
        dialog.grab_set()
        self.center_dialog(dialog)
        entry.focus_set()
        entry.selection_range(0, tk.END)
        self.wait_window(dialog)
        return result["value"]

    def ask_yes_no(self, title, message, confirm_text="Confirm"):
        result = {"value": False}
        dialog = tk.Toplevel(self)
        dialog.title(title)
        dialog.configure(bg=BG)
        dialog.transient(self)
        dialog.resizable(False, False)

        border = tk.Frame(dialog, bg=BR, padx=1, pady=1)
        border.pack(fill="both", expand=True, padx=14, pady=14)

        body = tk.Frame(border, bg=PANEL, padx=16, pady=16)
        body.pack(fill="both", expand=True)

        tk.Label(
            body,
            text=message,
            bg=PANEL,
            fg=FG,
            font=FONT,
            justify="left",
            wraplength=420,
        ).pack(anchor="w")

        buttons = tk.Frame(body, bg=PANEL)
        buttons.pack(fill="x", pady=(14, 0))

        def close():
            dialog.destroy()

        def confirm():
            result["value"] = True
            dialog.destroy()

        self.dialog_button(buttons, "Cancel", close).pack(side="right")
        self.dialog_button(buttons, confirm_text, confirm).pack(side="right", padx=(0, 6))

        dialog.bind("<Escape>", lambda event: close())
        dialog.bind("<Return>", lambda event: confirm())
        dialog.bind("<KP_Enter>", lambda event: confirm())
        dialog.grab_set()
        self.center_dialog(dialog)
        self.wait_window(dialog)
        return result["value"]

    def show_error(self, title, message):
        dialog = tk.Toplevel(self)
        dialog.title(title)
        dialog.configure(bg=BG)
        dialog.transient(self)
        dialog.resizable(False, False)

        border = tk.Frame(dialog, bg=BR, padx=1, pady=1)
        border.pack(fill="both", expand=True, padx=14, pady=14)

        body = tk.Frame(border, bg=PANEL, padx=16, pady=16)
        body.pack(fill="both", expand=True)

        tk.Label(body, text="ERROR", bg=PANEL, fg=BR, font=FONT_SMALL).pack(anchor="w")
        tk.Label(
            body,
            text=message,
            bg=PANEL,
            fg=FG,
            font=FONT,
            justify="left",
            wraplength=460,
        ).pack(anchor="w", pady=(6, 0))

        buttons = tk.Frame(body, bg=PANEL)
        buttons.pack(fill="x", pady=(14, 0))

        def close():
            dialog.destroy()

        self.dialog_button(buttons, "Close", close).pack(side="right")
        dialog.bind("<Escape>", lambda event: close())
        dialog.bind("<Return>", lambda event: close())
        dialog.bind("<KP_Enter>", lambda event: close())
        dialog.grab_set()
        self.center_dialog(dialog)
        self.wait_window(dialog)

    def clean_name(self, name, label):
        if name is None:
            return None
        cleaned = name.strip()
        if not cleaned:
            return None
        if "/" in cleaned or cleaned in {".", ".."}:
            raise ValueError(f"{label} must be a single file or folder name.")
        return cleaned

    def run_command(self, command, error_prefix):
        result = subprocess.run(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            error_text = result.stderr.strip() or "Command failed."
            raise RuntimeError(f"{error_prefix}\n\n{error_text}")

    def scan_directory(self, target):
        return list(target.iterdir())

    def open_path_entry(self, event=None):
        text = self.path_var.get().strip()
        if not text:
            return "break"

        target = Path(text).expanduser()
        if target.exists() and target.is_file():
            self.open_dir(target.parent, selected_name=target.name, focus_target=self.path_entry)
        else:
            self.open_dir(target, focus_target=self.path_entry)
        return "break"

    def open_dir(self, target, push=True, selected_name=None, focus_target=None):
        try:
            target = Path(target).expanduser().resolve()
            if not target.is_dir():
                raise NotADirectoryError("Not a folder.")

            if focus_target is None:
                current_focus = self.focus_get()
                if current_focus in {self.path_entry, self.search_entry}:
                    focus_target = current_focus

            items = self.scan_directory(target)
            if push and target != self.path:
                self.hist.append(self.path)

            self.path = target
            self.path_var.set(str(target))
            self.directory_items = items
            self.render(selected_name=selected_name, focus_target=focus_target)
        except Exception as exc:
            self.show_error("CHOS Files", f"Cannot open:\n{target}\n\n{exc}")

    def render(self, selected_name=None, focus_target=None):
        if selected_name is None:
            selected_name = self.selected_name()

        query = self.search_var.get().strip().lower()
        items = list(self.directory_items)
        if not self.show_hidden:
            items = [item for item in items if not item.name.startswith(".")]
        if query:
            items = [item for item in items if query in item.name.lower()]

        dirs = sorted((item for item in items if item.is_dir()), key=lambda item: item.name.lower())
        files = sorted(
            (item for item in items if not item.is_dir()), key=lambda item: item.name.lower()
        )
        self.items = dirs + files

        self.listbox.delete(0, tk.END)
        for item in self.items:
            if item.is_dir():
                self.listbox.insert(tk.END, f"[DIR] {item.name}")
            else:
                self.listbox.insert(tk.END, f"      {item.name}")

        self.update_info(len(dirs), len(files), len(self.items))

        if self.items:
            index = 0
            if selected_name:
                for idx, item in enumerate(self.items):
                    if item.name == selected_name:
                        index = idx
                        break
            self.select_index(index)

        if focus_target in {self.path_entry, self.search_entry}:
            focus_target.focus_set()
        else:
            self.focus_list()

    def focus_list(self):
        if self.items and not self.listbox.curselection():
            self.select_index(0)
        self.listbox.focus_set()

    def select_index(self, index):
        if not self.items:
            return
        index = max(0, min(index, len(self.items) - 1))
        self.listbox.selection_clear(0, tk.END)
        self.listbox.selection_set(index)
        self.listbox.activate(index)
        self.listbox.see(index)

    def move_selection(self, delta):
        if not self.items:
            return "break"

        selection = self.listbox.curselection()
        if selection:
            current = selection[0]
        else:
            current = -1 if delta > 0 else len(self.items)
        target = max(0, min(current + delta, len(self.items) - 1))
        self.select_index(target)
        return "break"

    def sel(self):
        selection = self.listbox.curselection()
        if not selection:
            return None
        index = selection[0]
        if index >= len(self.items):
            return None
        return self.items[index]

    def open_sel(self, event=None):
        target = self.sel()
        if not target:
            return "break"

        if target.is_dir():
            self.open_dir(target)
            return "break"

        try:
            self.run_command(["xdg-open", str(target)], "Failed to open file.")
            self.set_notice(f"Opened: {target.name}")
        except Exception as exc:
            self.show_error("CHOS Files", f"Cannot open file:\n{target}\n\n{exc}")
        return "break"

    def back(self):
        if self.hist:
            self.open_dir(self.hist.pop(), push=False)

    def up(self):
        self.open_dir(self.path.parent)

    def refresh(self):
        self.open_dir(self.path, push=False, selected_name=self.selected_name())

    def toggle_hidden(self):
        self.show_hidden = not self.show_hidden
        self.render()
        self.set_notice("Hidden files shown" if self.show_hidden else "Hidden files hidden")

    def clear_search(self):
        if not self.search_var.get():
            return
        current_focus = self.focus_get()
        focus_target = current_focus if current_focus in {self.path_entry, self.search_entry} else None
        selected_name = self.selected_name()
        self.search_var.set("")
        self.render(selected_name=selected_name, focus_target=focus_target)
        self.set_notice("Search cleared")

    def on_search_change(self, *_):
        if not hasattr(self, "listbox"):
            return
        focus_target = self.search_entry if self.focus_get() == self.search_entry else None
        self.render(focus_target=focus_target)

    def create_target(self, prompt, label, action):
        try:
            name = self.clean_name(self.ask_text("CHOS Files", prompt), label)
            if not name:
                return False
            target = self.path / name
            action(target)
            self.open_dir(self.path, push=False, selected_name=name)
            return True
        except Exception as exc:
            self.show_error("CHOS Files", f"{label} failed.\n\n{exc}")
            return False

    def new_folder(self):
        created = self.create_target(
            "Folder name:",
            "Folder name",
            lambda target: target.mkdir(exist_ok=False),
        )
        if created:
            self.set_notice("Folder created")

    def new_file(self):
        created = self.create_target(
            "File name:",
            "File name",
            lambda target: target.touch(exist_ok=False),
        )
        if created:
            self.set_notice("File created")

    def move_path_to_trash(self, target):
        if shutil.which("gio"):
            self.run_command(["gio", "trash", str(target)], "gio trash failed.")
            return
        if shutil.which("trash-put"):
            self.run_command(["trash-put", str(target)], "trash-put failed.")
            return
        raise RuntimeError("No trash backend found. Install gio or trash-put.")

    def maybe_replace_target(self, target):
        if not target.exists():
            return True
        replace = self.ask_yes_no(
            "CHOS Files",
            f"Replace existing item?\n\n{target.name}\n\nThe current item will be moved to trash first.",
            confirm_text="Replace",
        )
        if not replace:
            return False
        self.move_path_to_trash(target)
        return True

    def rename(self):
        source = self.sel()
        if not source:
            return

        try:
            name = self.clean_name(
                self.ask_text("CHOS Files", "New name:", initialvalue=source.name),
                "New name",
            )
            if not name or name == source.name:
                return

            target = source.with_name(name)
            if target.exists() and not self.maybe_replace_target(target):
                return

            source.rename(target)
            self.open_dir(self.path, push=False, selected_name=target.name)
            self.set_notice(f"Renamed: {source.name} -> {target.name}")
        except Exception as exc:
            self.show_error("CHOS Files", f"Rename failed.\n\n{exc}")

    def trash(self):
        target = self.sel()
        if not target:
            return

        confirm = self.ask_yes_no(
            "CHOS Files",
            f"Move to trash?\n\n{target.name}",
            confirm_text="Trash",
        )
        if not confirm:
            return

        try:
            self.move_path_to_trash(target)
            self.open_dir(self.path, push=False)
            self.set_notice(f"Trashed: {target.name}")
        except Exception as exc:
            self.show_error("CHOS Files", f"Trash failed.\n\n{exc}")

    def copy_path(self):
        target = self.sel() or self.path
        self.clipboard_clear()
        self.clipboard_append(str(target))
        self.set_notice(f"Path copied: {target.name if target != self.path else self.path}")

    def copy_item(self, event=None):
        target = self.sel()
        if not target:
            return "break"
        self.clipboard_item = target
        self.clipboard_mode = "copy"
        self.set_notice(f"Copy queued: {target.name}")
        return "break"

    def cut_item(self, event=None):
        target = self.sel()
        if not target:
            return "break"
        self.clipboard_item = target
        self.clipboard_mode = "cut"
        self.set_notice(f"Cut queued: {target.name}")
        return "break"

    def paste_item(self, event=None):
        if not self.clipboard_item or not self.clipboard_mode:
            self.set_notice("Clipboard is empty")
            return "break"

        source = self.clipboard_item
        target = self.path / source.name

        try:
            if not source.exists():
                raise FileNotFoundError(f"Source no longer exists:\n{source}")

            if target == source:
                raise RuntimeError("The selected item is already in this folder.")

            if source.is_dir() and path_is_relative_to(self.path.resolve(), source.resolve()):
                raise RuntimeError("Cannot paste a folder into itself or one of its child folders.")

            if target.exists() and not self.maybe_replace_target(target):
                return "break"

            if self.clipboard_mode == "copy":
                if source.is_dir():
                    shutil.copytree(source, target)
                else:
                    shutil.copy2(source, target)
                self.set_notice(f"Copied: {source.name}")
            else:
                shutil.move(str(source), str(target))
                self.clipboard_item = None
                self.clipboard_mode = None
                self.set_notice(f"Moved: {target.name}")

            self.open_dir(self.path, push=False, selected_name=target.name)
        except Exception as exc:
            self.show_error("CHOS Files", f"Paste failed.\n\n{exc}")
        return "break"

    def menu(self, event):
        if not self.items:
            return

        index = self.listbox.nearest(event.y)
        self.select_index(index)

        selected = self.sel()
        menu = tk.Menu(
            self,
            tearoff=0,
            bg=PANEL2,
            fg=FG,
            activebackground=SEL,
            activeforeground=FG,
            relief="flat",
            bd=0,
        )
        menu.add_command(label="Open", command=self.open_sel, state="normal" if selected else "disabled")
        menu.add_separator()
        menu.add_command(label="Copy", command=self.copy_item, state="normal" if selected else "disabled")
        menu.add_command(label="Cut", command=self.cut_item, state="normal" if selected else "disabled")
        menu.add_command(
            label="Paste",
            command=self.paste_item,
            state="normal" if self.clipboard_item else "disabled",
        )
        menu.add_separator()
        menu.add_command(label="Rename", command=self.rename, state="normal" if selected else "disabled")
        menu.add_command(label="Trash", command=self.trash, state="normal" if selected else "disabled")
        menu.add_command(label="Copy Path", command=self.copy_path)
        menu.add_separator()
        menu.add_command(label="New Folder", command=self.new_folder)
        menu.add_command(label="New File", command=self.new_file)
        menu.tk_popup(event.x_root, event.y_root)

    def on_backspace(self, event):
        if self.is_text_input_focus(event.widget):
            return None
        self.up()
        return "break"

    def on_delete(self, event):
        if self.is_text_input_focus(event.widget):
            return None
        self.trash()
        return "break"

    def on_refresh_key(self, event):
        self.refresh()
        return "break"

    def on_toggle_hidden_key(self, event):
        if self.is_text_input_focus(event.widget):
            return None
        self.toggle_hidden()
        return "break"

    def focus_search(self, event=None):
        self.search_entry.focus_set()
        self.search_entry.selection_range(0, tk.END)
        self.search_entry.icursor(tk.END)
        return "break"

    def focus_path(self, event=None):
        self.path_entry.focus_set()
        self.path_entry.selection_range(0, tk.END)
        self.path_entry.icursor(tk.END)
        return "break"

    def on_escape(self, event):
        if self.search_var.get():
            self.clear_search()
        else:
            self.focus_list()
        return "break"

    def on_copy_shortcut(self, event):
        if self.is_text_input_focus(event.widget):
            return None
        return self.copy_item(event)

    def on_cut_shortcut(self, event):
        if self.is_text_input_focus(event.widget):
            return None
        return self.cut_item(event)

    def on_paste_shortcut(self, event):
        if self.is_text_input_focus(event.widget):
            return None
        return self.paste_item(event)


if __name__ == "__main__":
    Files().mainloop()
