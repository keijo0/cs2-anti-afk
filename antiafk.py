#!/usr/bin/env python3
"""
CS2 Anti-AFK Tool for Linux
Works while CS2 is alt-tabbed using xdotool for external input simulation.
No game memory is read or written.
"""

import argparse
import logging
import os
import random
import subprocess
import sys
import time

try:
    import yaml
except ImportError:
    yaml = None  # Optional; config file won't be available without it

DEFAULT_CONFIG = {
    "window_title": "cs2",
    "interval_min": 10,
    "interval_max": 40,
    "actions": ["key_forward", "key_back", "key_left", "key_right", "mouse_move"],
    "mouse_move_range": 10,
    "log_file": None,
    "verbose": False,
}

SUPPORTED_ACTIONS = {"key_forward", "key_back", "key_left", "key_right", "mouse_move"}


def find_cs2_window(window_title=None):
    """Return the window ID of the CS2 window, or None if not found."""
    if window_title is None:
        window_title = DEFAULT_CONFIG["window_title"]
    try:
        result = subprocess.run(
            ["xdotool", "search", "--name", window_title],
            capture_output=True,
            text=True,
        )
        lines = result.stdout.strip().splitlines()
        if lines:
            return lines[0].strip()
    except FileNotFoundError:
        logging.error("xdotool not found. Please install it (see README).")
        sys.exit(1)
    return None


def send_key(window_id, key):
    """Send a key press to the given window ID."""
    subprocess.run(
        ["xdotool", "key", "--window", window_id, key],
        capture_output=True,
    )
    logging.debug("Sent key '%s' to window %s", key, window_id)


def move_mouse(window_id, move_range):
    """Send a small random mouse movement to the given window ID."""
    dx = random.randint(-move_range, move_range)
    dy = random.randint(-move_range, move_range)
    subprocess.run(
        ["xdotool", "mousemove_relative", "--window", window_id, "--", str(dx), str(dy)],
        capture_output=True,
    )
    logging.debug("Moved mouse by (%d, %d) on window %s", dx, dy, window_id)


def perform_action(window_id, action, config):
    """Perform a single anti-AFK action."""
    key_map = {
        "key_forward": "w",
        "key_back": "s",
        "key_left": "a",
        "key_right": "d",
    }
    if action in key_map:
        key = key_map[action]
        send_key(window_id, key)
    elif action == "mouse_move":
        move_mouse(window_id, config.get("mouse_move_range", DEFAULT_CONFIG["mouse_move_range"]))
    else:
        logging.warning("Unknown action: %s", action)


def load_config(config_path):
    """Load configuration from a YAML file, merging with defaults."""
    if yaml is None:
        logging.error("PyYAML is not installed. Install it with: pip3 install pyyaml")
        sys.exit(1)
    if not os.path.isfile(config_path):
        logging.error("Config file not found: %s", config_path)
        sys.exit(1)
    with open(config_path, "r") as f:
        user_config = yaml.safe_load(f) or {}
    config = dict(DEFAULT_CONFIG)
    config.update(user_config)
    return config


def validate_config(config):
    """Validate configuration values and warn about unknown actions."""
    interval_min = config.get("interval_min", DEFAULT_CONFIG["interval_min"])
    interval_max = config.get("interval_max", DEFAULT_CONFIG["interval_max"])
    if interval_min <= 0 or interval_max <= 0:
        logging.error("Intervals must be positive numbers.")
        sys.exit(1)
    if interval_min > interval_max:
        logging.error("interval_min must be <= interval_max.")
        sys.exit(1)
    for action in config.get("actions", []):
        if action not in SUPPORTED_ACTIONS:
            logging.warning("Unknown action '%s' will be ignored.", action)


def setup_logging(config):
    """Configure logging based on config settings."""
    handlers = [logging.StreamHandler(sys.stdout)]
    log_file = config.get("log_file")
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    level = logging.DEBUG if config.get("verbose") else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=handlers,
    )


def parse_args():
    parser = argparse.ArgumentParser(
        description="CS2 Anti-AFK Tool for Linux (alt-tab compatible, no memory access)"
    )
    parser.add_argument(
        "--config",
        metavar="FILE",
        help="Path to YAML configuration file",
    )
    parser.add_argument(
        "--interval-min",
        type=float,
        help="Minimum interval between actions in seconds (default: 30)",
    )
    parser.add_argument(
        "--interval-max",
        type=float,
        help="Maximum interval between actions in seconds (default: 60)",
    )
    parser.add_argument(
        "--actions",
        nargs="+",
        choices=sorted(SUPPORTED_ACTIONS),
        metavar="ACTION",
        help=(
            "Actions to perform. Choices: "
            + ", ".join(sorted(SUPPORTED_ACTIONS))
            + " (default: key_forward mouse_move)"
        ),
    )
    parser.add_argument(
        "--mouse-move-range",
        type=int,
        help="Maximum pixel range for mouse movement (default: 10)",
    )
    parser.add_argument(
        "--log-file",
        metavar="FILE",
        help="Optional path to write activity log",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose/debug output",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    # Start with defaults, optionally override with config file, then CLI args
    config = dict(DEFAULT_CONFIG)
    if args.config:
        file_config = load_config(args.config)
        config.update(file_config)

    # CLI arguments override config file values
    if args.interval_min is not None:
        config["interval_min"] = args.interval_min
    if args.interval_max is not None:
        config["interval_max"] = args.interval_max
    if args.actions:
        config["actions"] = args.actions
    if args.mouse_move_range is not None:
        config["mouse_move_range"] = args.mouse_move_range
    if args.log_file:
        config["log_file"] = args.log_file
    if args.verbose:
        config["verbose"] = True

    setup_logging(config)
    validate_config(config)

    logging.info("CS2 Anti-AFK started. Press Ctrl+C to stop.")
    logging.info(
        "Interval: %.0f-%.0f seconds | Actions: %s",
        config["interval_min"],
        config["interval_max"],
        ", ".join(config["actions"]),
    )

    while True:
        window_id = find_cs2_window(config.get("window_title"))
        if window_id is None:
            logging.warning(
                "CS2 window not found (title: '%s'). Retrying in 10 seconds...",
                config.get("window_title", DEFAULT_CONFIG["window_title"]),
            )
            time.sleep(10)
            continue

        for action in config["actions"]:
            if action in SUPPORTED_ACTIONS:
                perform_action(window_id, action, config)

        sleep_time = random.uniform(config["interval_min"], config["interval_max"])
        logging.info("Actions performed. Next action in %.1f seconds.", sleep_time)
        time.sleep(sleep_time)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("CS2 Anti-AFK stopped.")
        sys.exit(0)
