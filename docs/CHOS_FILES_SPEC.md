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
- open folders
- open files with xdg-open
- back
- forward
- up
- refresh
- copy
- cut
- paste
- rename
- new folder
- new file
- move to trash
- show hidden files
- keyboard shortcuts
- right click context menu

## Safety

Delete must use trash, not permanent rm.

## Default command

```bash
chos-files
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
