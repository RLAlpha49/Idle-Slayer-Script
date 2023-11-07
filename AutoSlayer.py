import GUI
import keyboard
import time
import os
import sys
import threading
import win32gui
import pyautogui
import pytesseract
import cv2
import numpy as np
import re
import pygetwindow as gw
from PIL import ImageGrab, Image
from Log import write_log_entry, increment_stat
from BonusStage import bonus_stage
from PixelSearch import PixelSearchWindow
from Wrapper import timer
from SettingsAndWindow import load_settings, update_settings, get_idle_slayer_window

version = "v1.7"

running_threads = True
event = threading.Event()

base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
logs_dir = os.path.join(base_dir, "AutoSlayerLogs")
settings_file_path = os.path.join(logs_dir, "settings.txt")

# Config's for Tesseract-OCR to extract text more accurately
custom_config = r'--oem 3 --psm 10 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz. --user-patterns "^[1-9]{1,3}[A-Za-z]$"'
custom_config2 = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz%,:.'

# Define a regular expression pattern for matching text with 1-3 numbers, 1 letter, and no leading 0's
pattern = r'(?<![0-9])\d{1,3}[A-Za-z](?![0-9])'

# Track the occurrences of matching text
occurrences = {}

slayer_points = None
total_slayer_points = None

# Initialize the timer and last_check_time
timer_start_time = None
last_check_time = None

# Define the conversion table
notation_table = {
    'K': 10 ** 3,
    'M': 10 ** 6,
    'B': 10 ** 9,
    'T': 10 ** 12,
    'Qa': 10 ** 15,
    'Qi': 10 ** 18,
    'Sx': 10 ** 21,
    'Sp': 10 ** 24,
    'Oc': 10 ** 27,
    'No': 10 ** 30,
    'Dc': 10 ** 33,
    'Ud': 10 ** 36,
    'Dd': 10 ** 39,
    'Td': 10 ** 42,
    'Qt': 10 ** 45,
    'Qd': 10 ** 48,
    'Sd': 10 ** 51,
    'St': 10 ** 54,
    'Od': 10 ** 57,
    'Nd': 10 ** 60,
    'Vg': 10 ** 63,
    'Uv': 10 ** 66,
    'Dv': 10 ** 69,
    'Tv': 10 ** 72,
    'Qav': 10 ** 75,
    'Qiv': 10 ** 78,
    'Sxv': 10 ** 81,
    'Spv': 10 ** 84,
    'Ocv': 10 ** 87
}


@timer
def get_image_text(left, top, right, bottom):
    window = get_idle_slayer_window()
    image = ImageGrab.grab(bbox=(window.left + left, window.top + top, window.left + right, window.top + bottom))
    # Convert the PIL image to a NumPy array
    image_np = np.array(image)
    
    # Convert to grayscale
    gray_image = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)
    
    # Apply thresholding
    _, thresholded_image = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Scaling down the image
    scale_percent = 80
    width = int(thresholded_image.shape[1] * scale_percent / 100)
    height = int(thresholded_image.shape[0] * scale_percent / 100)
    scaled_image = cv2.resize(thresholded_image, (width, height), interpolation=cv2.INTER_AREA)
    
    # Convert the NumPy array back to a PIL image
    image = Image.fromarray(scaled_image)
    
    if left == 1100:
        text = pytesseract.image_to_string(image, config=custom_config, lang='eng')
        screenshot_path = 'screenshot.png'
        # Remove the period and 1-2 numbers following it
        text = (re.sub(r'\.\d{1,2}', '', text)).upper()
    else:
        text = pytesseract.image_to_string(image, config=custom_config2, lang='eng')
        screenshot_path = 'screenshot2.png'
            
    print(text)
    #image.save(screenshot_path) # Saves the image to see what the function is screenshotting
    
    return text
    
def arrow_keys():
    # Check if the focused window's title matches the target window title
    target_window_title = "Idle Slayer"
    while not event.is_set():  # Check the event status
        settings = load_settings()
        if not settings.getboolean("Settings", "paused") and not settings.getboolean("Settings", "chesthuntactivestate"):
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
                time.sleep(2) # Sleep to avoid busy-waiting 
                # P.S. Without this, program was using half my cpu, I would reccomend not removing this
        else:
            time.sleep(2) # Sleep to avoid busy-waiting 
            # P.S. Without this, program was using half my cpu, I would reccomend not removing this

def general_gameplay():
    settings = load_settings()
    if settings.getboolean("Settings", "slayerpoints"):
        update_settings("slayerpoints")
    if settings.getboolean("Settings", "autobuyupgradestate"):
        cooldown_activated = True
        print("Cooldown activated: True")
        auto_upgrades_cooldown = settings.getint("Settings", "autobuyvalue")
        timer = time.time()
    else:
        cooldown_activated = False
        print("Cooldown activated: False")
        
    target_window_title = "Idle Slayer"
    while not event.is_set():  # Check the event status
        focused_window_title = win32gui.GetWindowText(win32gui.GetForegroundWindow())
        if focused_window_title == target_window_title:
            time.sleep(0.1)
            settings = load_settings()
            if not settings.getboolean("Settings", "paused"):
                window = get_idle_slayer_window()
                
                # Claim Quests
                print("Checking For Quests...")
                if pyautogui.pixelMatchesColor(window.left + 1130, window.top + 610, (203, 203, 76), tolerance=1):
                    claim_quests()
                    increment_stat("Claimed Quests")
                    
                # Collect Minions
                print("Checking For Minions...")
                if pyautogui.pixelMatchesColor(window.left + 99, window.top + 113, (255, 255, 122)):
                    collect_minion()
                    increment_stat("Claimed Minions")
                
                # Chesthunt
                print("Checking For Chesthunt...")
                if PixelSearchWindow((255, 255, 255), 470, 810, 180, 230,shade=0) is not None:
                    if PixelSearchWindow((246, 143, 55), 180, 260, 265, 330,shade=1) is not None:
                        if PixelSearchWindow((173, 78, 26), 170, 260, 265, 330,shade=1) is not None:
                            print("Start Chest Hunt...")
                            chest_hunt()
                            increment_stat("ChestHunts")
                
                # Rage When Megahorde
                print("Checking For Megahorde...")
                if pyautogui.pixelMatchesColor(window.left + 419, window.top + 323, (223, 222, 224)):
                    Rage_When_Horde()
                
                # Rage When Soul Bonus
                if settings.getint("Settings", "ragestate") == 3:  
                    print("Checking For Soul Bonus...")
                    if PixelSearchWindow((168, 109, 10), 625, 629, 143, 214, shade=0) is not None:
                        keyboard.press_and_release('e')
                        write_log_entry(f"Rage With Soul Bonus")
                        increment_stat("Rage with Soul Bonus")
                    
                # Portals
                CyclePortals()
                
                # Auto Buy Equipment/Upgrades
                if cooldown_activated is True:
                    if settings.getboolean("Settings", "autobuyupgradestate") is False:
                        cooldown_activated = False
                        print("Cooldown activated: False")
                
                if settings.getboolean("Settings", "autobuyupgradestate"):
                    print("Checking For Auto Buy Upgrade")
                    if not cooldown_activated:
                        cooldown_activated = True
                        auto_upgrades_cooldown = 10 # Activates Auto Buy Upgrade 10 seconds after changing the setting
                        timer = time.time()
                        print("Cooldown activated: True")
                        
                    if auto_upgrades_cooldown < (time.time() - timer):
                        print("Buy Equipment")
                        auto_upgrades_cooldown = settings.getint("Settings", "autobuyvalue") # Keeps Auto Buy Upgrade time the same as value given by user if setting is not changed
                        timer = time.time()
                        # Check if the Idle Slayer window is focused
                        active_window_title = win32gui.GetWindowText(win32gui.GetForegroundWindow())
                        if active_window_title == "Idle Slayer":
                            buying()
                            if settings.getboolean("Settings", "paused"):
                                update_settings("paused")
                
                # Bonus Stage
                print("Checking For Bonus Stage...")
                if pyautogui.pixelMatchesColor(window.left + 660, window.top + 254, (255, 231, 55)):  
                    if pyautogui.pixelMatchesColor(window.left + 638, window.top + 236, (255, 187, 49)):
                        if pyautogui.pixelMatchesColor(window.left + 775, window.top + 448, (255, 255, 255)):
                            bonus_stage(settings.getboolean("Settings", "skipbonusstagestate"))
                            if settings.getboolean("Settings", "skipbonusstagestate") is True:
                                increment_stat("Failed/Skipped Bonus Stages") 

                # Collect Silver boxes
                print("Checking For Silver Boxes...")
                pixel_position = PixelSearchWindow((255, 192, 0), 560, 730, 30, 55,shade=10)
                if pixel_position:
                    pyautogui.moveTo(window.left + pixel_position[0], window.top + pixel_position[1])
                    pyautogui.leftClick()
                    write_log_entry(f"Silver Box Collected")
                    increment_stat("Collected Silver Boxes") 
                
                # Get Total Slayer Points
                if settings.get("Settings","autoascensionstate") and total_slayer_points is None:
                    get_total_slayer_points()
        
                # Check Auto Ascension
                auto_ascension()
                
                time.sleep(0.20) # Currently to reduce cpu usage. Will reduce when this function has more code and pixel searches to run
            else:
                time.sleep(0.5)
        else:
            time.sleep(1)

@timer
# Auto Ascension
def auto_ascension():
    global slayer_points, total_slayer_points, timer_start_time, last_check_time, occurrences
    window = get_idle_slayer_window()
    settings = load_settings()
    if slayer_points:
        if timer_start_time is None:
            timer_start_time = time.time()
            last_check_time = timer_start_time
    
    if settings.getboolean("Settings", "slayerpoints"):
        # If it's been 5 minutes since the last check, reset slayer_points and the setting
        if time.time() - last_check_time >= 5 * 60:
            slayer_points = None
            occurrences = {}
            update_settings("slayerpoints")
    
    if not settings.getboolean("Settings", "slayerpoints"):
        if pyautogui.pixelMatchesColor(window.left + 1100, window.top + 90, (61, 52, 165)):
            possible_slayer_points = get_image_text(1100, 73, 1184, 99)
            
            # Use regular expressions to find matching text
            matches = re.findall(pattern, possible_slayer_points)
            
            if occurrences.__len__() >= 10:
                occurrences.clear()
            
            for match in matches:
                # If the match is not in the occurrences dictionary, add it
                if match not in occurrences:
                    occurrences[match] = 1
                else:
                    occurrences[match] += 1
                    
                    # Check if the same text has been found 20 times
                    if occurrences[match] == 20:
                        slayer_points = match  # Save the text to slayer_points
                        update_settings("slayerpoints")
                        print(slayer_points)
                        last_check_time = time.time()  # Update the last_check_time
                        write_log_entry(f"Slayer Points: {slayer_points}")
            
            # Print the occurrences
            for text, count in occurrences.items():
                print(f"Found: {text} {count} times")
    
    if slayer_points is not None and total_slayer_points is not None:
        # Extract the number and abbreviation
        number = int(slayer_points[:-1])  # Remove the last character and convert to a int
        abbreviation = slayer_points[-1]

        if abbreviation in notation_table:
            # Convert the number based on the abbreviation
            converted_value = number * notation_table[abbreviation]

            print("Original Value:", number)
            print("Converted Value:", converted_value)
        else:
            print("Unknown Abbreviation:", abbreviation)

        print(f"Slayer Points Needed: {(int((total_slayer_points) * (settings.getint("Settings", "autoascensionslider") / 100)))}")
        if converted_value > (int((total_slayer_points) * (settings.getint("Settings", "autoascensionslider") / 100))):
            print(int((total_slayer_points * (settings.getint("Settings", "autoascensionslider") / 100))))
            print("Auto Ascending...")
            write_log_entry(f"Auto Ascending")
            increment_stat("Auto Ascensions")
            
            # Click ascension button
            pyautogui.click(window.left + 95, window.top + 90)
            time.sleep(0.4)
            
            # Click ascension tab
            pyautogui.click(window.left + 93, window.top + 680)
            time.sleep(0.2)
            
            # Click ascend button
            pyautogui.click(window.left + 185, window.top + 595)
            time.sleep(0.5)
            
            # Click yes button
            pyautogui.click(window.left + 550, window.top + 580)
            time.sleep(3)
            
            slayer_points = None
            last_check_time = None
            timer_start_time = None
            update_settings("slayerpoints")
            
            get_total_slayer_points()
            time.sleep(5)
            buying()

# Find and save total slayer points
@timer
def get_total_slayer_points():
    global total_slayer_points
    found = False
    window = get_idle_slayer_window()
    update_settings("paused")
    # Close Shop window if open
    pyautogui.click(window.left + 1244, window.top + 712)
    time.sleep(0.15)
    
    # Open shop window
    pyautogui.click(window.left + 1163, window.top + 655)
    time.sleep(0.15)
    
    # Open stats window
    pyautogui.click(window.left + 1150, window.top + 690)
    time.sleep(0.15)
    
    # Scroll to top of scrollbar
    pyautogui.click(window.left + 1254, window.top + 168, clicks=10, interval=0.005)
    time.sleep(0.2)
    
    while True:
        for i in range(5):
            pyautogui.vscroll(-1)
        
        possible_total_slayer_points = get_image_text(840, 165, 1235, 645)
        
        # Search for "totalslayerpoints:"
        if "totalslayerpoints:" in possible_total_slayer_points.lower():
            # Split the text by newlines to extract individual lines
            lines = possible_total_slayer_points.split('\n')
            for line in lines:
                if found is True:
                    update_settings("paused")
                    
                    # Close Shop window
                    pyautogui.click(window.left + 1244, window.top + 712)
                    time.sleep(0.15)
                    
                    total_slayer_points = line.replace(",", "")
                    if total_slayer_points.isdigit():
                        total_slayer_points = int(total_slayer_points)
                        print("Total Slayer Points:", total_slayer_points)
                        return  total_slayer_points
                    else:
                        found = False
                    write_log_entry(f"Total Slayer Points: {total_slayer_points}")
                    print("Total Slayer Points:", total_slayer_points)
                    
                    
                else:
                    # Check if the line contains "totalslayerpoints:"
                    if "totalslayerpoints:" in line.lower():
                        # Extract the value after "totalslayerpoints:"
                        total_slayer_points = line.split(":")[1].strip()
                        if total_slayer_points == "":
                            found = True
                        else:
                            update_settings("paused")
                            
                            # Close Shop window
                            pyautogui.click(window.left + 1244, window.top + 712)
                            time.sleep(0.15)
                            
                            total_slayer_points = int(''.join(i for i in total_slayer_points if i.isdigit()))
                            write_log_entry(f"Total Slayer Points: {total_slayer_points}")
                            print("Total Slayer Points:", total_slayer_points)
                            
                            return  total_slayer_points

# Collect & Send Minions
@timer
def collect_minion():
    window = get_idle_slayer_window()
    # Click ascension button
    pyautogui.click(window.left + 95, window.top + 90)
    time.sleep(0.4)
    
    # Click ascension tab
    pyautogui.click(window.left + 93, window.top + 680)
    time.sleep(0.2)
    
    # Click ascension tree tab
    pyautogui.click(window.left + 193, window.top + 680)
    time.sleep(0.2)
    
    # ????
    pyautogui.click(window.left + 691, window.top + 680)
    time.sleep(0.2)
    
    # Click minion tab
    pyautogui.click(window.left + 332, window.top + 680)
    time.sleep(0.2)
    
    # Check if Daily Bonus is available
    if PixelSearchWindow((17, 170, 35), 370, 910, 410, 470, shade=9) is not None:
        # Click Claim All
        pyautogui.click(window.left + 320, window.top + 280, clicks=5, interval=0.01)
        time.sleep(0.2)
        # Click Send All
        pyautogui.click(window.left + 320, window.top + 280, clicks=5, interval=0.01)
        time.sleep(0.2)
        # Claim Daily Bonus
        pyautogui.click(window.left + 320, window.top + 180, clicks=5, interval=0.01)
        time.sleep(0.2)
        write_log_entry("Minions Collect with Daily Bonus")
    else:
        # Click Claim All
        pyautogui.click(window.left + 318, window.top + 182, clicks=5)
        time.sleep(0.4)
        # Click Send All
        pyautogui.click(window.left + 318, window.top + 182, clicks=5)
        time.sleep(0.2)
        write_log_entry("Minions Collect")
    
    # Click Exit
    pyautogui.click(window.left + 570, window.top + 694)      

# Claim quests
@timer
def claim_quests():
    window = get_idle_slayer_window()
    write_log_entry("Claiming Quests")
    
    settings = load_settings()
    if not settings.getboolean("Settings", "paused"):
        update_settings("paused")

    # Close Shop window if open
    pyautogui.click(window.left + 1244, window.top + 712)
    time.sleep(0.15)
    
    # Open shop window
    pyautogui.click(window.left + 1163, window.top + 655)
    time.sleep(0.15)
    
    # Click on armor tab
    pyautogui.click(window.left + 850, window.top + 690)
    
    # Click on upgrade tab
    pyautogui.click(window.left + 927, window.top + 683)
    time.sleep(0.15)
    
    # Click on quest tab
    pyautogui.click(window.left + 1000, window.top + 690)
    time.sleep(0.05)
    
    # Scroll to top of scrollbar
    pyautogui.click(window.left + 1254, window.top + 272, clicks=10, interval=0.005)
    time.sleep(0.2)
    
    while True:
        # Check if there is any green buy boxes
        location = PixelSearchWindow((17, 170, 35), 1160, 1161, 270, 590, shade=0)
        if not location:
            # Move mouse on ScrollBar
            pyautogui.moveTo(window.left + 1253, window.top + 270)
            for i in range(4):
                pyautogui.vscroll(-100)
            
            # Check gray scroll bar is there
            if not pyautogui.pixelMatchesColor(window.left + 1253, window.top + 645, (214, 214, 214)):
                break
            #time.sleep(0.01)
        else:
            # Click Green buy box
            write_log_entry("Quest Claimed")
            pyautogui.leftClick(window.left + location[0], window.top + location[1])
    
    # Close Shop
    pyautogui.click(window.left + 1244, window.top + 712)
    update_settings("paused")

# Auto Rage
@timer
def Rage_When_Horde():
    settings = load_settings()
    SoulBonusActive = Check_Soul_Bonus()
    
    if SoulBonusActive:
        if settings.getboolean("Settings", "craftragepillstate"):
            Craft_Temporary_Item((135, 22, 70))
            write_log_entry("Crafted Rage Pill")
        if settings.getboolean("Settings", "craftsoulbonusstate"):
            Craft_Temporary_Item((125, 85, 216))
            write_log_entry("Crafted Soul Compass")
            
    if settings.getint("Settings", "ragestate") == 1:
        if SoulBonusActive:
            write_log_entry("MegaHorde Rage with SoulBonus")
            increment_stat("Rage with MegaHorde and Soul Bonus")
            Rage()
    elif settings.getint("Settings", "ragestate") == 2:
        write_log_entry(f"Rage MegaHorde")
        increment_stat("Rage with only MegaHorde")
        Rage()

@timer
def Rage():
    settings = load_settings()
    if settings.getboolean("Settings", "craftdimensionalstaffstate"):
        Craft_Temporary_Item((243, 124, 85))
        update_settings("craftdimensionalstaffstate")
        write_log_entry("Crafted Dimensional Staff")
    if settings.getboolean("Settings", "craftbidimensionalstaffstate"):
        Craft_Temporary_Item((82, 102, 41))
        update_settings("craftbidimensionalstaffstate")
        write_log_entry("Crafted BiDimensional Staff")
    keyboard.press_and_release('e')
    
# Checks Soul Bonus
@timer
def Check_Soul_Bonus():
    print("Checking for Soul Bonus")
    if PixelSearchWindow((168, 109, 10), 625, 629, 143, 214, shade=0) is not None:
        write_log_entry("MegaHorde Rage with SoulBonus")
        return True 

@timer
def Craft_Temporary_Item(color):
    update_settings("paused")
    window = get_idle_slayer_window()
    
    # Open the menu
    pyautogui.click(window.left + 160, window.top + 100)
    time.sleep(0.15)
    
    # Click the temp item tab
    pyautogui.click(window.left + 260, window.top + 690)
    time.sleep(0.15)
    
    # Click the top of the scrollbar
    pyautogui.click(window.left + 482, window.top + 150, clicks=5)
    time.sleep(0.45)
    
    while True:
        # Search for the pixel with the specified color
        found_pixel = PixelSearchWindow(color, 65, 66, 180, 630, shade=10)
        found_pixel = PixelSearchWindow((0,0,0), 65, 66, 180, 630, shade=10)
        if found_pixel == color:
            pyautogui.click(window.left + 385, window.top + found_pixel[1])
            time.sleep(0.05)
            break
        
        pyautogui.scroll(-5)  # Scroll down
        time.sleep(0.05)
        
        # Check for the exit condition
        exit_pixel = pyautogui.pixel(window.left + 484, window.top + 647)
        if exit_pixel == (color):
            break
    
    # Click the final location
    pyautogui.click(window.left + 440, window.top + 690)
    time.sleep(0.1)
    update_settings("paused")

# Cycle Portals
@timer
def CyclePortals():
    settings = load_settings()
    if settings.getboolean("Settings", "cycleportalsstate") and not settings.getboolean("Settings", "chesthuntactivestate"):  
        print("Checking For Portal...")
        window = get_idle_slayer_window()
        
        portal_found = 0
        if not pyautogui.pixelMatchesColor(window.left + 1180, window.top + 180, (131, 3, 153)):
            portal_found += 1
        if not pyautogui.pixelMatchesColor(window.left + 1180, window.top + 180, (41, 1, 48)):
            portal_found += 1
        if portal_found == 2:
            return
        
        if PixelSearchWindow((255, 255, 255), 1154, 1210, 144, 155, shade=9) is None:
            pyautogui.leftClick(window.left + 1180, window.top + 150)
            time.sleep(0.3)
            
            pyautogui.moveTo(window.left + 867, window.top + 300)
            time.sleep(0.2)
            while pyautogui.pixelMatchesColor(window.left + 875, window.top + 275, (214, 214, 214)):
                pyautogui.scroll(20)
            time.sleep(0.4)
            
            color = (255, 255, 255)
            cycle_portal_count = settings.getint("Settings", "cycleportalcount")
            match cycle_portal_count:
                case 1:
                    color = (114, 251, 255)
                case 2:
                    color = (81, 0, 137)
                case 3:
                    color = (0, 208, 255)
                case 4:
                    color = (0, 161, 151)
                case 5:
                    color = (0, 1, 123)
                case 6:
                    color = (231, 156, 196)
                case 7:
                    color = (0, 255, 186)
                case 8:
                    color = (202, 72, 77)
            
            while 1:
                location = PixelSearchWindow((color), 491, 492, 266, 540, shade=0)
                if location is None:
                    if not pyautogui.pixelMatchesColor(window.left + 875, window.top + 536, (214, 214, 214)):
                        break
                    time.sleep(0.01)
                    
                    pyautogui.moveTo(window.left + 867, window.top + 300)
                    pyautogui.scroll(-1)
                else:
                    pyautogui.leftClick(window.left + location[0], window.top + location[1])
                    time.sleep(0.3)
                    break
            
            cycle_portal_count += 1
            if cycle_portal_count > 8:
                cycle_portal_count = 1
            
            settings = load_settings()
            
            settings.set("Settings", "cycleportalcount", str(cycle_portal_count))
            with open(settings_file_path, "w") as configfile:
                settings.write(configfile)
            
            write_log_entry(f"Portal Activated")
            increment_stat("Portals Cycled")
            time.sleep(10)

# Chest Hunt Minigame   
@timer   
def chest_hunt():
    settings = load_settings()
    update_settings("chesthuntactivestate")
            
    write_log_entry(f"Chesthunt")
    
    window = get_idle_slayer_window()
    
    if settings.getboolean("Settings", "nolockpicking100state"):
        time.sleep(6)
    else:
        time.sleep(3)
    
    saver_x = 0
    saver_y = 0
    pixel_x = window.left + 185
    pixel_y = window.top + 325
    
    # Locate saver
    for y in range(3):
        for x in range(10):
            pixel_position = PixelSearchWindow((255, 235, 4), 171, 1114, 240, 520, shade=0)
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
    
    if saver_y == 826:
        adjusted_saver_y = saver_y - 27
    else:
        adjusted_saver_y = saver_y + 43
    
    adjusted_saver_x = saver_x + 32
    
    print(f"Saver Chest: {adjusted_saver_x}, {adjusted_saver_y}")
    
    for y in range(3):
        for x in range(10):
            #adjusted_saver_y = saver_y + 43 if saver_y != 850 or saver_y != 950 or saver_y != 859 else saver_y - 27
            # After opening 2 chests, open saver
            if count == 2 and saver_x > 0:
                pyautogui.click(adjusted_saver_x, adjusted_saver_y)
                if settings.getboolean("Settings", "nolockpicking100state"):
                    time.sleep(1.5)
                else:
                    time.sleep(0.55)
            
            # Skip saver no matter what
            if (pixel_y - 23) == adjusted_saver_y and (pixel_x + 33) == (adjusted_saver_x):
                if count < 2:  # Go to the next chest if saver is the first two chests
                    print("count less than 2: Skipping saver")
                    pixel_x += 95
                elif x == 10:
                    break
                else:
                    print("Saver already collected")
                    pixel_x += 95
                    continue
            
            # Open chest
            pyautogui.click(pixel_x + 33, pixel_y - 23)
            if settings.getboolean("Settings", "nolockpicking100state"):
                time.sleep(1)
            else:
                time.sleep(0.5)
            
            print(f"{count} Pixel x: {pixel_x}, Pixel y: {pixel_y}")
            print(f"{count} Chest Opened: {pixel_x + 33}, {pixel_y - 23}")
            
            # Check if chest hunt ended
            if PixelSearchWindow((179, 0, 0), 300, 500, 650, 700, shade=1) or PixelSearchWindow((180, 0, 0), 300, 500, 650, 700, shade=1) is not None:
                print("exit x")
                break
            
            time.sleep(0.75)
            # Wait more based on conditions
            sleep_time = 0
            if PixelSearchWindow((255,0,0), 470, 810, 180, 230, shade=1) is not None:
                sleep_time = 2.5 if settings.getboolean("Settings", "nolockpicking100state") else 1.25
                print("mimic")
            elif PixelSearchWindow((106,190,48), 580, 680, 650, 720, shade=1) is not None:
                print("2x")
                pyautogui.click()
            
            time.sleep(sleep_time)
            pixel_x += 95
            count += 1     
        
        if PixelSearchWindow((179, 0, 0), 300, 500, 650, 700, shade=1) or PixelSearchWindow((180, 0, 0), 300, 500, 650, 700, shade=1) is not None:
            print("exit y")
            break
        
        pixel_y += 95
        pixel_x = window.left + 185

    # Look for close button until found
    while PixelSearchWindow((179, 0, 0), 300, 500, 650, 700, shade=1) or PixelSearchWindow((180, 0, 0), 300, 500, 650, 700, shade=1) is not None:
        print("exit chesthunt")
        pyautogui.click(window.left + 643, window.top + 693)
        break
    
    update_settings("chesthuntactivestate")

@timer
def buying():
    buy_equipment()
    write_log_entry(f"Buy Equipment/Upgrades")
    
    settings = load_settings()
    if settings.getboolean("Settings", "paused"):
        update_settings("paused")

# Auto Buy Equipment
def buy_equipment():   
    settings = load_settings()
    if not settings.getboolean("Settings", "paused"):
        update_settings("paused")
        
    window = get_idle_slayer_window()
    # Close Shop window if open
    pyautogui.click(window.left + 1244, window.top + 712)
    time.sleep(0.15)
    
    # Open shop window
    pyautogui.click(window.left + 1163, window.top + 655)
    time.sleep(0.15)
    
    # Search for the white pixel to confirm shop window is open
    if pyautogui.pixelMatchesColor(window.left + 807, window.top + 142, (255, 255, 255)):
        # Click on armor tab
        pyautogui.click(window.left + 850, window.top + 690)
        time.sleep(0.05)
        
        # Click Max buy
        pyautogui.click(window.left + 1180, window.top + 636, clicks=4, interval=0.01)
        
        # Check if green buy box is present
        if pyautogui.pixelMatchesColor(window.left + 1257, window.top + 340, (17, 170, 35)):
            # Buy sword
            pyautogui.click(window.left + 1200, window.top + 200, clicks=5, interval=0.005)
        else:
            # Click Bottom of scroll bar
            pyautogui.click(window.left + 1253, window.top + 592, clicks=5, interval=0.005)
            time.sleep(0.5)
            
            # Buy last item
            pyautogui.click(window.left + 1200, window.top + 590, clicks=5, interval=0.005)
            time.sleep(0.3)
            
            # Click top of scroll bar
            pyautogui.click(window.left + 1253, window.top + 170, clicks=5, interval=0.005)
            time.sleep(0.3)
        
        # Buy 50 items
        pyautogui.click(window.left + 1100, window.top + 636, clicks=5, interval=0.005)
        
        # Move to Scroll Bar
        pyautogui.moveTo(window.left + 1253, window.top + 170)
            
        while True:
            # Check for green buy boxes
            green_location = PixelSearchWindow(((17, 170, 35)), 1160, 1160, 170, 600, shade=0)
            if green_location is not None:
                # Click Green buy box
                pyautogui.click(window.left + green_location[0], window.top + green_location[1], clicks=5, interval=0.005)
            elif not pyautogui.pixelMatchesColor(window.left + 1253, window.top + 597, (214, 214, 214)):
                break
            else:
                # Scroll
                for i in range(2):
                    pyautogui.vscroll(-100)
            
        # Update the "paused" setting in the settings file
        update_settings("paused")
            
        buy_upgrade()

# Auto Buy Upgrades       
def buy_upgrade():
    window = get_idle_slayer_window()
    # Navigate to upgrade and scroll up
    pyautogui.click(window.left + 927, window.top + 683)
    time.sleep(0.15)
    # Top of scrollbar
    pyautogui.click(window.left + 1253, window.top + 170)
    time.sleep(0.4)
    something_bought = False
    y = 170
    while True:
        # Check if RandomBox Magnet is next upgrade
        if pyautogui.pixelMatchesColor(window.left + 888, window.top + (y + 25), (244, 180, 27)):
            y += 96
            print("RandomBox Magnet")
        # Check if RandomBox Magnet is next upgrade
        elif pyautogui.pixelMatchesColor(window.left + 888, window.top + (y + 25), (228, 120, 255)):
            y += 96
            print("RandomBox Magnet 2")
        elif not pyautogui.pixelMatchesColor(window.left + 1180, window.top + (y + 10), (17, 170, 35)) and not pyautogui.pixelMatchesColor(window.left + 1180, window.top + (y + 10), (16, 163, 34)):
            print("Break")
            break
        else:
            #print("Buy Upgrade")
            something_bought = True
            # Click green buy
            pyautogui.click(window.left + 1180, window.top + y)
    if something_bought:
        buy_equipment()
    else:
        pyautogui.click(window.left + 1222, window.top + 677)
        
    if settings.getboolean("Settings", "paused"):
        update_settings("paused")

def stop_threads():
    os._exit(0)

def main():
    app = GUI.App()  # Create an instance of the App class
    app.mainloop()   # Start the main loop of the GUI
    

if __name__ == "__main__":
    settings = load_settings()

    if settings.getboolean("Settings", "chesthuntactivestate"):
        update_settings("chesthuntactivestate")
    
    if settings.getboolean("Settings", "paused"):
        update_settings("paused")
    
    main_thread = threading.Thread(target=main)
    main_thread.start()
    
    #time.sleep(2)  # Allow some time for the GUI to start
    
    window = get_idle_slayer_window()
    while True:
        try:
            window_to_position = gw.getWindowsWithTitle(f"AutoSlayer {version}")[0]
            if window_to_position is not None and window_to_position.title == f"AutoSlayer {version}": # window_to_position.title is so that it does not consider the AutoSlayer.py file open in an editor as the window it is looking for
                print("Not None")
                window_to_position.moveTo(window.left + 175, window.top + 751)
                break
            else:
                print("None")
                time.sleep(0.01)
        except IndexError:
            # Handle the case when the window is not found, retry after a delay
            print("Window not found. Retrying...")
            time.sleep(0.01)
    
    
    arrow_keys_thread = threading.Thread(target=arrow_keys)
    arrow_keys_thread.daemon = True
    arrow_keys_thread.start()
    
    general_gameplay_thread = threading.Thread(target=general_gameplay)
    general_gameplay_thread.start()
    
    # Wait for all threads to complete before exiting the program
    main_thread.join()
    arrow_keys_thread.join()
    general_gameplay_thread.join()