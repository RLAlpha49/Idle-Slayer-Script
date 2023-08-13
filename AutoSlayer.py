import GUI  # Import the GUI module
import keyboard
import time
from configparser import ConfigParser
import os
import sys
import threading
import win32gui
import pyautogui
import pygetwindow as gw
from PIL import ImageGrab
from Log import write_log_entry

running_threads = True
event = threading.Event()

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
    while not event.is_set():  # Check the event status
        settings = load_settings()
        if not settings.getboolean("Settings", "paused"):
            # Updates jump rate from settings file
            jumpratevalue = int(settings.get("Settings", "jumpratevalue", fallback="150"))
            # Get the focused window's title
            focused_window_title = win32gui.GetWindowText(win32gui.GetForegroundWindow())
            if focused_window_title == target_window_title:  
                # Plan to change this to arrow keys to somewhat allow the script to work even when the window is not focused
                keyboard.press_and_release('w')
                keyboard.press_and_release('d')
                time.sleep(jumpratevalue / 1000)  # Convert to seconds
            else:
                time.sleep(1) # Sleep to avoid busy-waiting 
                # P.S. Without this, program was using half my cpu, I would reccomend not removing this
        else:
            time.sleep(1) # Sleep to avoid busy-waiting 
            # P.S. Without this, program was using half my cpu, I would reccomend not removing this
                
def general_gameplay():
    while not event.is_set():  # Check the event status
        settings = load_settings()
        if not settings.getboolean("Settings", "paused"):
            window = get_idle_slayer_window()
            CyclePortals()
            
            # Collect Silver boxes
            pixel_position = pixel_search_in_window((255, 192, 0), 560, 730, 30, 55,shade=10)
            if pixel_position:
                pyautogui.moveTo(window.left + pixel_position[0], window.top + pixel_position[1])
                pyautogui.leftClick()
                write_log_entry(f"Silver Box Collected")
            time.sleep(5) # Currently to reduce cpu usage. Will reduce when this function has more code and pixel searches to run
           
        
    
def get_idle_slayer_window():
    # Find the Idle Slayer window by its title
    window = gw.getWindowsWithTitle("Idle Slayer")[0]
    return window

def pixel_search_in_window(color, left, right, top, bottom, shade=None):
    window = get_idle_slayer_window()
    screenshot = ImageGrab.grab(bbox=(window.left, window.top, window.left + 1280, window.top + 720))

    for x in range(left, right):
        for y in range(top, bottom):
            pixel_color = screenshot.getpixel((x, y))
            if color_match(pixel_color, color, shade):
                return x, y
    return None

def color_match(actual_color, target_color, shade):
    for i in range(3):
        if abs(actual_color[i] - target_color[i]) > shade:
            return False
    return True
    
def CyclePortals():
    target_color = (255, 255, 255)  # White color in RGB
    shade_tolerance = 5

    window = get_idle_slayer_window()

    pixel_position = pixel_search_in_window(target_color, 1150, 1215, 110, 175, shade=shade_tolerance)
    if pixel_position:
        return
    else:
        pyautogui.moveTo(window.left + 1160, window.top + 150)
        pyautogui.leftClick()
        write_log_entry(f"Portal Activated")

def stop_threads():
    #os._exit(0) # Used to close program when coding. Compiled script does not need this
    event.set()  # Set the event to stop the threads

    

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
    
    general_gameplay_thread = threading.Thread(target=general_gameplay)
    general_gameplay_thread.start()
    