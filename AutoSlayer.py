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
        time.sleep(0.1)
        settings = load_settings()
        if not settings.getboolean("Settings", "paused"):
            window = get_idle_slayer_window()
            
            print("Checking For Chesthunt...")
            if pixel_search_in_window((255, 255, 255), 470, 810, 180, 230,shade=0) is not None:
                if pixel_search_in_window((246, 143, 55), 180, 260, 265, 330,shade=1) is not None:
                    print("second color found")
                    if pixel_search_in_window((173, 78, 26), 170, 260, 265, 330,shade=1) is not None:
                        print("third color found")
                        chest_hunt()
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
            # Used to find different pixel rgb values within a certain area. I use this for finding out what rgb values to search for in the script.
            if color == (0, 0, 0):
                print(f"Pixel at ({x}, {y}) - Color: {pixel_color}")
            
            if color_match(pixel_color, color, shade):
                return x, y
    return None

def color_match(actual_color, target_color, shade):
    for i in range(3):
        if abs(actual_color[i] - target_color[i]) > shade:
            return False
    return True
    
def CyclePortals():
    settings = load_settings()
    if settings.getboolean("Settings", "cycleportalsstate") and not settings.getboolean("Settings", "chesthuntactivestate"):  
        print("Checking For Portal...")
        window = get_idle_slayer_window()
        
        time.sleep(0.3)
        if pixel_search_in_window((255, 255, 255), 1150, 1215, 110, 175, shade=1) or pixel_search_in_window((31,31,31), 1150, 1215, 110, 175, shade=1) or pixel_search_in_window((41,1,48), 1150, 1215, 110, 175, shade=1):
            return
        else:
            # Attempt to fix pyautogui.FAILSAFE error
            # Calculate the target coordinates within screen boundaries
            target_x = min(max(window.left + 1160, 0), pyautogui.size()[0])
            target_y = min(max(window.top + 150, 0), pyautogui.size()[1])
            pyautogui.moveTo(target_x, target_y)
            #pyautogui.moveTo(window.left + 1160, window.top + 150)
            pyautogui.leftClick()
            write_log_entry(f"Portal Activated")
            
def chest_hunt():
    settings = load_settings()
    chesthuntactivestate = settings.getboolean("Settings", "chesthuntactivestate")
    chesthuntactivestate = not chesthuntactivestate
    
    settings_file_path = os.path.join(logs_dir, "settings.txt")
    settings.set("Settings", "chesthuntactivestate", str(chesthuntactivestate))
    with open(settings_file_path, "w") as configfile:
        settings.write(configfile)
            
    write_log_entry(f"Chesthunt")
    
    window = get_idle_slayer_window()
    
    if settings.getboolean("Settings", "nolockpickingstate"):
        time.sleep(4)
    else:
        time.sleep(2)
    
    saver_x = 0
    saver_y = 0
    pixel_x = window.left + 185
    pixel_y = window.top + 325
    
    # Locate saver
    for y in range(3):
        for x in range(10):
            pixel_position = pixel_search_in_window((255, 235, 4), 171, 1114, 240, 520, shade=0)
            if pixel_position is not None:
                saver_x, saver_y = window.left + pixel_position[0], window.top + pixel_position[1]
                break
            pixel_x += 95
        if saver_x > 0:
            break
        pixel_y += 95
        pixel_x = window.left + 185
    
    # Actual chest hunt
    pixel_x = window.left + 185
    pixel_y = window.top + 325
    count = 0
    
    print(f"Saver x: {saver_x}, Saver y: {saver_y}")
    print(f"Saver Chest: {saver_x + 32}, {saver_y + 43}")
    (print((saver_y + 43)) if saver_y != 850 else print((saver_y - 27)))
    
    for y in range(3):
        for x in range(10):
            # After opening 2 chests, open saver
            if count == 2 and saver_x > 0:
                pyautogui.click(saver_x + 32, ((saver_y + 43) if saver_y != 850 else (saver_y - 27)))
                if settings.getboolean("Settings", "nolockpickingstate"):
                    time.sleep(1.5)
                else:
                    time.sleep(0.55)
            
            # Skip saver no matter what
            if (pixel_y - 23) == ((saver_y + 43) if saver_y != 850 else (saver_y - 27)) and (pixel_x + 32) == (saver_x + 43):
                if count < 2:  # Go to the next chest if saver is the first two chests
                    pixel_x += 95
                elif x == 10:
                    break
                else:
                    #pixel_x += 95
                    continue
            
            # Open chest
            pyautogui.click(pixel_x + 33, pixel_y - 23)
            if settings.getboolean("Settings", "nolockpickingstate"):
                time.sleep(1.5)
            else:
                time.sleep(0.55)
            
            print(f"{count} Pixel x: {pixel_x}, Pixel y: {pixel_y}")
            print(f"{count} Chest Opened: {pixel_x + 33}, {pixel_y - 23}")
            
            # Check if chest hunt ended
            if pixel_search_in_window((179, 0, 0), 300, 500, 650, 700, shade=1) or pixel_search_in_window((180, 0, 0), 300, 500, 650, 700, shade=1) is not None:
                print("exit x")
                break
            
            time.sleep(0.5)
            # Wait more based on conditions
            sleep_time = 0
            if pixel_search_in_window((255,0,0), 470, 810, 180, 230, shade=1) is not None:
                sleep_time = 2 if settings.getboolean("Settings", "nolockpickingstate") else 1
                print("mimic")
            elif pixel_search_in_window((106,190,48), 580, 680, 650, 720, shade=1) is not None:
                print("2x")
                sleep_time = 3 if settings.getboolean("Settings", "nolockpickingstate") else 1.5
            
            time.sleep(sleep_time)
            pixel_x += 95
            count += 1     
        
        if pixel_search_in_window((179, 0, 0), 300, 500, 650, 700, shade=1) or pixel_search_in_window((180, 0, 0), 300, 500, 650, 700, shade=1) is not None:
            print("exit y")
            break
        
        pixel_y += 95
        pixel_x = window.left + 185
    
    # Look for close button until found
    while pixel_search_in_window((179, 0, 0), 300, 500, 650, 700, shade=1) or pixel_search_in_window((180, 0, 0), 300, 500, 650, 700, shade=1) is not None:
        print("exit chesthunt")
        pyautogui.click(window.left + 643, window.top + 693)
        break
    
    settings.set("Settings", "chesthuntactivestate", str(False))
    with open(settings_file_path, "w") as configfile:
        settings.write(configfile)
    print(chesthuntactivestate)

def stop_threads():
    #os._exit(0) # Used to close program when coding. Compiled script does not need this
    event.set()  # Set the event to stop the threads 

def main():
    app = GUI.App()  # Create an instance of the App class
    app.mainloop()   # Start the main loop of the GUI
    

if __name__ == "__main__":
    settings = load_settings()
    settings_file_path = os.path.join(logs_dir, "settings.txt")
    settings.set("Settings", "chesthuntactivestate", str(False))
    with open(settings_file_path, "w") as configfile:
        settings.write(configfile)
    
    settings.set("Settings", "paused", str(False))
    with open(settings_file_path, "w") as configfile:
        settings.write(configfile)
    
    main_thread = threading.Thread(target=main)
    main_thread.start()
    
    time.sleep(2)  # Allow some time for the GUI to start
    
    arrow_keys_thread = threading.Thread(target=arrow_keys)
    arrow_keys_thread.daemon = True
    arrow_keys_thread.start()
    
    general_gameplay_thread = threading.Thread(target=general_gameplay)
    general_gameplay_thread.start()