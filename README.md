# CS2 Anti-AFK Tool for Linux

A lightweight, user-space anti-AFK tool for Counter-Strike 2 on Linux. Works while the game is **alt-tabbed** using external input simulation via `xdotool`. No game memory is read or written.

---

## Features

- **Alt-Tab Compatible** – Sends input to the CS2 window even when it's not focused
- **No Memory Access** – Uses only `xdotool` for external input simulation
- **Configurable** – YAML configuration or CLI flags for intervals and action types
- **Multiple Input Methods** – Keyboard presses, mouse movement, or both
- **Lightweight** – Minimal CPU/memory usage; pure Python with no heavy dependencies
- **Easy Toggle** – Start/stop with `Ctrl+C`
- **Optional Logging** – Log activity to a file or stdout
- **User-Space Only** – No `sudo`, no systemd, just run it

---

## Requirements

- Python 3.7+
- `xdotool`
- `PyYAML` (only needed for `--config` YAML file support)

---

## Installation

### 1. Install `xdotool`

**Ubuntu / Debian:**
```bash
sudo apt install xdotool
```

**Fedora:**
```bash
sudo dnf install xdotool
```

**Arch Linux:**
```bash
sudo pacman -S xdotool
```

### 2. Install Python dependencies

```bash
pip3 install --user -r requirements.txt
```

Or, if you only want to use CLI flags (no YAML config file):
```bash
# No Python dependencies needed — PyYAML is only required for --config
```

---

## Usage

### Quick start (with defaults)
```bash
python3 cs2_anti_afk.py
```
Defaults: presses `W` + small mouse movement every 30–60 seconds.

### With a configuration file
```bash
python3 cs2_anti_afk.py --config config.yaml
```

### With CLI flags
```bash
python3 cs2_anti_afk.py --interval-min 20 --interval-max 50 --actions key_forward mouse_move
```

### All options
```
usage: cs2_anti_afk.py [-h] [--config FILE] [--interval-min SECONDS]
                        [--interval-max SECONDS] [--actions ACTION [ACTION ...]]
                        [--mouse-move-range PIXELS] [--log-file FILE] [--verbose]

Options:
  --config FILE              Path to YAML configuration file
  --interval-min SECONDS     Minimum interval between actions (default: 30)
  --interval-max SECONDS     Maximum interval between actions (default: 60)
  --actions ACTION ...       Actions: key_forward key_back key_left key_right mouse_move
  --mouse-move-range PIXELS  Max pixel range for mouse movement (default: 10)
  --log-file FILE            Path to write activity log
  --verbose                  Enable verbose/debug output
```

### Stop the tool
Press `Ctrl+C` at any time.

---

## Configuration File

Copy and edit `config.yaml`:

```yaml
window_title: "Counter-Strike 2"
interval_min: 30
interval_max: 60
actions:
  - key_forward
  - mouse_move
mouse_move_range: 10
log_file:       # leave empty for stdout only
verbose: false
```

---

## How It Works

1. Uses `xdotool search --name "Counter-Strike 2"` to find the CS2 window by title
2. Sends key presses or mouse movements directly to that window ID — no focus change required
3. Waits a randomized interval before the next action
4. Repeats until stopped with `Ctrl+C`

Because input is sent to the window by ID (not by focus), the tool works while CS2 is alt-tabbed. No game files, memory, or processes are accessed.

---

## Troubleshooting

**`xdotool not found`**
Install `xdotool` for your distribution (see Installation above).

**`CS2 window not found`**
Make sure CS2 is running before starting the tool. If the window title is different, update `window_title` in `config.yaml` or check the title with:
```bash
xdotool search --name "" | while read id; do xdotool getwindowname "$id" 2>/dev/null; done | grep -i counter
```

**Tool doesn't prevent AFK kick**
Try reducing `interval_min`/`interval_max` or adding more actions (e.g., `key_forward key_back`).

---

## License

MIT
