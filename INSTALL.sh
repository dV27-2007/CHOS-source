#!/usr/bin/env bash
set -e
SRC="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$HOME/.local/bin" "$HOME/.config/i3" "$HOME/.config/rofi" "$HOME/.config/chos" "$HOME/.local/share/applications"
cp -a "$SRC/bin/." "$HOME/.local/bin/" 2>/dev/null || true
chmod +x "$HOME/.local/bin/"* 2>/dev/null || true
[ -f "$SRC/config/i3/config" ] && cp -a "$SRC/config/i3/config" "$HOME/.config/i3/config"
cp -a "$SRC/config/rofi/." "$HOME/.config/rofi/" 2>/dev/null || true
cp -a "$SRC/config/chos/." "$HOME/.config/chos/" 2>/dev/null || true
cp -a "$SRC/desktop/." "$HOME/.local/share/applications/" 2>/dev/null || true
update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true
i3 -C -c "$HOME/.config/i3/config"
i3-msg reload 2>/dev/null || true
echo "CH OS installed"
