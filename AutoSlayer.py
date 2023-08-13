import GUI  # Import the GUI module
import keyboard
import time
from configparser import ConfigParser
import os
import sys
import threading
import win32gui
import pynput

base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
logs_dir = os.path.join(base_dir, "AutoSlayerLogs")

def load_settings():
    settings = ConfigParser()
    settings_file_path = os.path.join(logs_dir, "settings.txt")
    settings.read(settings_file_path)
    return settings

def arrow_keys():
    # Check if the focused window's title matches the target window title
    target_window_title = "Idle Slayer"
    while True:
        settings = load_settings()
        if not settings.getboolean("Settings", "paused"):
            # Updates jump rate from settings file
            jumpratevalue = int(settings.get("Settings", "jumpratevalue", fallback="150"))
            # Get the focused window's title
            focused_window_title = win32gui.GetWindowText(win32gui.GetForegroundWindow())
            if focused_window_title == target_window_title:  
                keyboard.press_and_release('w')
                keyboard.press_and_release('d')
                time.sleep(jumpratevalue / 1000)  # Convert to seconds
            else:
                time.sleep(1) # Sleep to avoid busy-waiting 
                # P.S. Without this, program was using half my cpu, i would reccomend not removing this
        else:
            time.sleep(1) # Sleep to avoid busy-waiting 
                # P.S. Without this, program was using half my cpu, i would reccomend not removing this

def main():
    app = GUI.App()  # Create an instance of the App class
    app.mainloop()   # Start the main loop of the GUI

if __name__ == "__main__":
    main_thread = threading.Thread(target=main)
    main_thread.start()
    
    time.sleep(2)  # Allow some time for the GUI to start
    
    arrow_keys_thread = threading.Thread(target=arrow_keys)
    arrow_keys_thread.daemon = True
    arrow_keys_thread.start()
    