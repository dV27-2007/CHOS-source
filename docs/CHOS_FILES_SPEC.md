# CHOS Files

CHOS Files is the official file manager of CHOS.

It replaces ranger as the default file manager. Ranger may be installed manually, but it is not part of the official CHOS desktop experience.

## Goal

Create a fast, minimal, dark cyber-terminal file manager with the same visual language as the rest of CHOS:

- CHOS Launcher
- CHOS Power Menu
- CHOS Status Bar
- CHOS Control Center
- CHOS Login Screen

## Visual style

Main palette:

```text
#030606
#071010
#06110f
#0f2f29
#137a66
#1edbb2
#2fffd0
```

No white/yellow default UI.

## First version

MVP features:

- left sidebar
- current path bar
- file/folder list
- current-directory search filter
- open folders
- open files with xdg-open
- back
- up
- refresh
- copy
- cut
- paste
- rename
- new folder
- new file
- move to trash
- safe overwrite confirmation before replace
- show hidden files
- keyboard shortcuts
- right click context menu

## Safety

Delete must use trash, not permanent rm.

Replacing an existing file or folder must ask for confirmation and move the previous target to trash before the replacement happens.

## Current keyboard shortcuts

- `Up` / `Down`: move selection in the file list
- `Enter`: open selected file or folder
- `BackSpace`: go to the parent directory when focus is not inside a text field
- `Ctrl+F`: focus the search field and select its text
- `Ctrl+L`: focus the path field and select its text
- `Escape`: clear search, otherwise focus the file list
- `F5`: refresh the current directory
- `Delete`: move the selected item to trash
- `Ctrl+C`: copy the selected file or folder
- `Ctrl+X`: cut the selected file or folder
- `Ctrl+V`: paste into the current directory
- `Ctrl+H`: show or hide hidden files

## Default command

```bash
chos-files
```

Desktop launch also needs to work through:

```bash
gtk-launch chos-files
```

## Config path

```text
~/.config/chos/files.conf
```

## Source path

```text
apps/chos-files/
```

## Packaging target

CHOS Files must later be packaged as:

```text
chos-files.deb
```

and included in the CHOS ISO.
