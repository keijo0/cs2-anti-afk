#!/usr/bin/env python3
"""
CS2 Anti-AFK Tool using evdev
Injects keyboard and mouse input at the system level.
"""

import argparse
import logging
import random
import time
import os
from evdev import InputDevice, ecodes, UInput, list_devices
from select import select

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
    "key_forward": ecodes.KEY_W,
    "key_back": ecodes.KEY_S,
    "key_left": ecodes.KEY_A,
    "key_right": ecodes.KEY_D,
}

def find_keyboard():
    """Auto-detect keyboard device."""
    keyboard_candidates = []
    
    for path in list_devices():
        try:
            device = InputDevice(path)
            caps = device.capabilities()
            name_lower = device.name.lower()
            
            if ecodes.EV_KEY in caps:
                keys = caps[ecodes.EV_KEY]
                has_rel_movement = (ecodes.EV_REL in caps and 
                                   ecodes.REL_X in caps[ecodes.EV_REL] and
                                   ecodes.REL_Y in caps[ecodes.EV_REL])
                
                if (ecodes.KEY_SPACE in keys and ecodes.KEY_A in keys and 
                    not has_rel_movement and "mouse" not in name_lower):
                    priority = 0 if "kbd" in name_lower else 1000
                    keyboard_candidates.append((priority, device, path))
        except:
            continue
    
    if not keyboard_candidates:
        raise RuntimeError("Could not auto-detect keyboard")
    
    keyboard_candidates.sort(key=lambda x: x[0])
    keyboard = keyboard_candidates[0][1]
    logging.info(f"Auto-detected keyboard: {keyboard_candidates[0][2]} ({keyboard.name})")
    return keyboard

class AntiAFK:
    def __init__(self, config):
        self.config = config
        self.keyboard = find_keyboard()
        self.ui = UInput()
        logging.info("AntiAFK initialized")
        self.enabled = True

    def send_key(self, key):
        """Send a key press using evdev."""
        self.ui.write(ecodes.EV_KEY, key, 1)  # Press
        self.ui.syn()
        time.sleep(0.05)
        self.ui.write(ecodes.EV_KEY, key, 0)  # Release
        self.ui.syn()
        logging.debug(f"Sent key press")

    def move_mouse(self, move_range):
        """Send a small random mouse movement."""
        dx = random.randint(-move_range, move_range)
        dy = random.randint(-move_range, move_range)
        self.ui.write(ecodes.EV_REL, ecodes.REL_X, dx)
        self.ui.write(ecodes.EV_REL, ecodes.REL_Y, dy)
        self.ui.syn()
        logging.debug(f"Moved mouse by ({dx}, {dy})")

    def perform_action(self, action):
        """Perform an anti-AFK action."""
        if action in KEY_MAP:
            self.send_key(KEY_MAP[action])
        elif action == "mouse_move":
            self.move_mouse(self.config.get("mouse_move_range", DEFAULT_CONFIG["mouse_move_range"]))

    def run(self):
        """Main loop."""
        logging.info("CS2 Anti-AFK started")
        logging.info(f"Interval: {self.config['interval_min']:.0f}-{self.config['interval_max']:.0f}s | Actions: {', '.join(self.config['actions'])}")
        
        try:
            while True:
                for action in self.config["actions"]:
                    if action in SUPPORTED_ACTIONS:
                        self.perform_action(action)
                
                sleep_time = random.uniform(self.config["interval_min"], self.config["interval_max"])
                logging.info(f"Actions performed. Next in {sleep_time:.1f}s")
                time.sleep(sleep_time)
        except KeyboardInterrupt:
            logging.info("CS2 Anti-AFK stopped")
        except Exception as e:
            logging.error(f"Error: {e}")
        finally:
            try:
                self.ui.close()
                self.keyboard.close()
            except:
                pass

def load_config(config_path):
    """Load configuration from YAML file."""
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
    """Validate configuration."""
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
    """Setup logging."""
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
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="CS2 Anti-AFK Tool (evdev-based)")
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
        anti_afk = AntiAFK(config)
        anti_afk.run()
    except Exception as e:
        logging.error(f"Failed to initialize: {e}")

if __name__ == "__main__":
    main()
