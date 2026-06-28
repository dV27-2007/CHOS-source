# CHOS Files

Official CHOS file manager for CHOS Linux.

CHOS Files is currently a Tkinter MVP with the CHOS dark cyber-terminal palette and basic daily file-management operations.

## Run

Run the source file directly:

```bash
python3 apps/chos-files/src/chos_files.py
```

Run the repository launcher:

```bash
./bin/chos-files
```

Run the installed command:

```bash
chos-files
```

Run the desktop entry:

```bash
gtk-launch chos-files
```

## Current features

- current path bar with `Go`
- left sidebar shortcuts
- current-directory search filter
- open folders in place
- open files with `xdg-open`
- new folder
- new file
- rename
- copy, cut, paste
- overwrite confirmation before replacement
- move to trash with `gio trash` or `trash-put`
- copy selected path
- hidden files toggle
- right-click context menu

## Keyboard shortcuts

- `Up` / `Down`: move selection in the file list
- `Enter`: open selected file or folder
- `BackSpace`: go to the parent directory when focus is not in a text field
- `Ctrl+F`: focus the search field and select its text
- `Ctrl+L`: focus the path field and select its text
- `Escape`: clear search, or focus the file list when search is already empty
- `F5`: refresh the current directory
- `Delete`: move the selected item to trash
- `Ctrl+C`: copy the selected file or folder
- `Ctrl+X`: cut the selected file or folder
- `Ctrl+V`: paste into the current directory
- `Ctrl+H`: show or hide hidden files

## Notes

- Search only filters the current directory and never changes the current path.
- Replacing an existing file or folder asks for confirmation and trashes the old target first.
- Trash support requires `gio` or `trash-put`.
