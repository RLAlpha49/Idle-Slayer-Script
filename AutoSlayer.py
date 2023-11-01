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
from Log import write_log_entry, increment_stat
from BonusStage import bonus_stage
from PixelSearch import PixelSearchWindow

running_threads = True
event = threading.Event()

base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
logs_dir = os.path.join(base_dir, "AutoSlayerLogs")

def load_settings():
    settings = ConfigParser()
    settings_file_path = os.path.join(logs_dir, "settings.txt")
    settings.read(settings_file_path)
    return settings

def update_settings(setting):
    settings = load_settings()
    state = settings.getboolean("Settings", str(setting))
    state = not state
    
    settings.set("Settings", str(setting), str(state))
    with open(settings_file_path, "w") as configfile:
        settings.write(configfile)
    
def get_idle_slayer_window():
    while True:
        # Find the Idle Slayer window by its title
        idle_slayer_windows = gw.getWindowsWithTitle("Idle Slayer")
        if idle_slayer_windows:
            return idle_slayer_windows[0]
        time.sleep(1)  # Wait for 1 second before checking again

def color_match(actual_color, target_color, shade):
    for i in range(3):
        if abs(actual_color[i] - target_color[i]) > shade:
            return False
    return True
    
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
    settings = load_settings()
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
                    
                # Collect Minions
                print("Checking For Minions...")
                if pyautogui.pixelMatchesColor(window.left + 99, window.top + 113, (255, 255, 122)):
                    collect_minion()
                
                # Chesthunt
                print("Checking For Chesthunt...")
                if PixelSearchWindow((255, 255, 255), 470, 810, 180, 230,shade=0) is not None:
                    if PixelSearchWindow((246, 143, 55), 180, 260, 265, 330,shade=1) is not None:
                        if PixelSearchWindow((173, 78, 26), 170, 260, 265, 330,shade=1) is not None:
                            print("Start Chest Hunt...")
                            chest_hunt()
                
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
                            buy_equipment()
                            if settings.getboolean("Settings", "paused"):
                                update_settings("paused")
                
                # Bonus Stage
                print("Checking For Bonus Stage...")
                if pyautogui.pixelMatchesColor(window.left + 660, window.top + 254, (255, 231, 55)):  
                    if pyautogui.pixelMatchesColor(window.left + 638, window.top + 236, (255, 187, 49)):
                        if pyautogui.pixelMatchesColor(window.left + 775, window.top + 448, (255, 255, 255)):
                            bonus_stage(settings.getboolean("Settings", "skipbonusstagestate"))

                # Collect Silver boxes
                print("Checking For Silver Boxes...")
                pixel_position = PixelSearchWindow((255, 192, 0), 560, 730, 30, 55,shade=10)
                if pixel_position:
                    pyautogui.moveTo(window.left + pixel_position[0], window.top + pixel_position[1])
                    pyautogui.leftClick()
                    write_log_entry(f"Silver Box Collected")
                
                time.sleep(0.25) # Currently to reduce cpu usage. Will reduce when this function has more code and pixel searches to run
        else:
            time.sleep(1)

# Collect & Send Minions
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
        time.sleep(0.2)
        # Click Send All
        pyautogui.click(window.left + 318, window.top + 182, clicks=5)
        time.sleep(0.2)
        write_log_entry("Minions Collect")
    
    # Click Exit
    pyautogui.click(window.left + 570, window.top + 694)      

# Claim quests
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
def Check_Soul_Bonus():
    print("Checking for Soul Bonus")
    if PixelSearchWindow((168, 109, 10), 625, 629, 143, 214, shade=0) is not None:
        write_log_entry("MegaHorde Rage with SoulBonus")
        return True 

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
            time.sleep(10)
      
# Chest Hunt Minigame      
def chest_hunt():
    settings = load_settings()
    update_settings("chesthuntactivestate")
            
    write_log_entry(f"Chesthunt")
    
    window = get_idle_slayer_window()
    
    if settings.getboolean("Settings", "nolockpicking100state"):
        time.sleep(5)
    else:
        time.sleep(2.5)
    
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
    
    if saver_y == 599 or saver_y == 694 or saver_y == 789 or saver_y == 489 or saver_y == 584:
        adjusted_saver_y = saver_y + 43
    elif saver_y == 584:
        adjusted_saver_y = saver_y + 66
    else:
        adjusted_saver_y = saver_y - 27
    
    print(f"Saver Chest: {saver_x + 33}, {adjusted_saver_y}")
    
    for y in range(3):
        for x in range(10):
            #adjusted_saver_y = saver_y + 43 if saver_y != 850 or saver_y != 950 or saver_y != 859 else saver_y - 27
            # After opening 2 chests, open saver
            if count == 2 and saver_x > 0:
                pyautogui.click(saver_x + 33, adjusted_saver_y)
                if settings.getboolean("Settings", "nolockpicking100state"):
                    time.sleep(1.5)
                else:
                    time.sleep(0.55)
            
            # Skip saver no matter what
            if (pixel_y - 23) == adjusted_saver_y and (pixel_x + 33) == (saver_x + 33):
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
                sleep_time = 2.5 if settings.getboolean("Settings", "nolockpicking100state") else 1.25
            
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
    #os._exit(0) # Used to close program when coding. Compiled script does not need this
    event.set()  # Set the event to stop the threads 

def main():
    app = GUI.App()  # Create an instance of the App class
    app.mainloop()   # Start the main loop of the GUI
    

if __name__ == "__main__":
    settings = load_settings()
    settings_file_path = os.path.join(logs_dir, "settings.txt")

    if settings.getboolean("Settings", "chesthuntactivestate"):
        update_settings("chesthuntactivestate")
    
    if settings.getboolean("Settings", "paused"):
        update_settings("paused")
    
    main_thread = threading.Thread(target=main)
    main_thread.start()
    
    time.sleep(2)  # Allow some time for the GUI to start
    
    arrow_keys_thread = threading.Thread(target=arrow_keys)
    arrow_keys_thread.daemon = True
    arrow_keys_thread.start()
    
    general_gameplay_thread = threading.Thread(target=general_gameplay)
    general_gameplay_thread.start()