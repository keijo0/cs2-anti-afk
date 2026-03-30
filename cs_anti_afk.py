#!/usr/bin/env python3
"""
CS2 Anti-AFK Tool - Simple version for focused game window
"""

import argparse
import logging
import random
import time
import os
import subprocess

try:
    import yaml
except ImportError:
    yaml = None

DEFAULT_CONFIG = {
    "interval_min": 30,
    "interval_max": 60,
    "actions": ["key_forward", "mouse_move"],
    "mouse_move_range": 10,
    "log_file": None,
    "verbose": False,
}

SUPPORTED_ACTIONS = {"key_forward", "key_back", "key_left", "key_right", "mouse_move"}

KEY_MAP = {
    "key_forward": "w",
    "key_back": "s",
    "key_left": "a",
    "key_right": "d",
}

def send_key(key):
    """Send a key press."""
    try:
        subprocess.run(
            ["xdotool", "key", key],
            check=False,
            capture_output=True,
            timeout=5
        )
        logging.debug(f"Sent key: {key}")
    except Exception as e:
        logging.error(f"Failed to send key: {e}")

def move_mouse(move_range):
    """Send a small random mouse movement."""
    dx = random.randint(-move_range, move_range)
    dy = random.randint(-move_range, move_range)
    try:
        subprocess.run(
            ["xdotool", "mousemove_relative", str(dx), str(dy)],
            check=False,
            capture_output=True,
            timeout=5
        )
        logging.debug(f"Moved mouse by ({dx}, {dy})")
    except Exception as e:
        logging.error(f"Failed to move mouse: {e}")

def perform_action(action, mouse_move_range):
    """Perform an anti-AFK action."""
    if action in KEY_MAP:
        send_key(KEY_MAP[action])
    elif action == "mouse_move":
        move_mouse(mouse_move_range)

def run_anti_afk(config):
    """Main loop."""
    logging.info("CS2 Anti-AFK started")
    logging.info(f"Interval: {config['interval_min']:.0f}-{config['interval_max']:.0f}s | Actions: {', '.join(config['actions'])}")
    logging.info("Keep CS2 window focused for input to register")
    
    try:
        while True:
            for action in config["actions"]:
                if action in SUPPORTED_ACTIONS:
                    perform_action(action, config.get("mouse_move_range", DEFAULT_CONFIG["mouse_move_range"]))
            
            sleep_time = random.uniform(config["interval_min"], config["interval_max"])
            logging.info(f"Actions performed. Next in {sleep_time:.1f}s")
            time.sleep(sleep_time)
    except KeyboardInterrupt:
        logging.info("CS2 Anti-AFK stopped")
    except Exception as e:
        logging.error(f"Error: {e}")

def load_config(config_path):
    if yaml is None:
        return DEFAULT_CONFIG
    if not os.path.isfile(config_path):
        return DEFAULT_CONFIG
    with open(config_path, "r") as f:
        user_config = yaml.safe_load(f) or {}
    config = dict(DEFAULT_CONFIG)
    config.update(user_config)
    return config

def validate_config(config):
    interval_min = config.get("interval_min", DEFAULT_CONFIG["interval_min"])
    interval_max = config.get("interval_max", DEFAULT_CONFIG["interval_max"])
    if interval_min <= 0 or interval_max <= 0:
        logging.error("Intervals must be positive")
        return False
    if interval_min > interval_max:
        logging.error("interval_min must be <= interval_max")
        return False
    return True

def setup_logging(config):
    handlers = [logging.StreamHandler()]
    log_file = config.get("log_file")
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    level = logging.DEBUG if config.get("verbose") else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=handlers,
        force=True,
    )

def parse_args():
    parser = argparse.ArgumentParser(description="CS2 Anti-AFK Tool")
    parser.add_argument("--config", type=str, default="config.yaml", help="Path to YAML config file")
    parser.add_argument("--interval-min", type=float, help="Min interval in seconds")
    parser.add_argument("--interval-max", type=float, help="Max interval in seconds")
    parser.add_argument("--actions", nargs="+", choices=sorted(SUPPORTED_ACTIONS), help="Actions to perform")
    parser.add_argument("--mouse-move-range", type=int, help="Mouse move range in pixels")
    parser.add_argument("--log-file", help="Path to log file")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    return parser.parse_args()

def main():
    args = parse_args()
    config = dict(DEFAULT_CONFIG)
    if args.config:
        file_config = load_config(args.config)
        config.update(file_config)
    
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
    
    if not validate_config(config):
        return
    
    try:
        run_anti_afk(config)
    except Exception as e:
        logging.error(f"Failed: {e}")

if __name__ == "__main__":
    main()
