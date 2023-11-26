import os
import sys
import time
import pygetwindow as gw
from configparser import ConfigParser
from Wrapper import timer

base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
logs_dir = os.path.join(base_dir, "AutoSlayerLogs")
settings_file_path = os.path.join(logs_dir, "settings.txt")

@timer
def load_settings():
    settings = ConfigParser()
    settings.read(settings_file_path)
    return settings

@timer
def update_settings(setting):
    settings = load_settings()
    state = settings.getboolean("Settings", str(setting))
    state = not state
    
    settings.set("Settings", str(setting), str(state))
    with open(settings_file_path, "w") as configfile:
        settings.write(configfile)

@timer
def get_idle_slayer_window():
    while True:
        # Find the Idle Slayer window by its title
        idle_slayer_windows = gw.getWindowsWithTitle("Idle Slayer")
        if idle_slayer_windows:
            return idle_slayer_windows[0]
        time.sleep(1)  # Wait for 1 second before checking again