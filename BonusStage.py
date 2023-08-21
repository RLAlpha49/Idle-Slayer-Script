import time
import pyautogui
from configparser import ConfigParser
import os
import pygetwindow as gw
import sys
from PIL import ImageGrab
from Log import write_log_entry

base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
logs_dir = os.path.join(base_dir, "AutoSlayerLogs")

def load_settings():
    settings = ConfigParser()
    settings_file_path = os.path.join(logs_dir, "settings.txt")
    settings.read(settings_file_path)
    return settings

def get_idle_slayer_window():
    while True:
        # Find the Idle Slayer window by its title
        idle_slayer_windows = gw.getWindowsWithTitle("Idle Slayer")
        if idle_slayer_windows:
            return idle_slayer_windows[0]
        time.sleep(1)  # Wait for 1 second before checking again

def bonus_stage(skip_bonus_stage_state):
    settings = load_settings()
    paused = settings.getboolean("Settings", "paused")
    paused = not paused
        
    # Update the "paused" setting in the settings file
    settings_file_path = os.path.join(logs_dir, "settings.txt")
    settings.set("Settings", "paused", str(paused))
    with open(settings_file_path, "w") as configfile:
        settings.write(configfile)
        
    write_log_entry("Start of BonusStage")
    while True:
        slider()
        time.sleep(0.5)
        pixel_search(660, 254, 660, 254, (255, 231, 55))
        if not pixel_found:
            break
    time.sleep(3.9)
    pixel_search(454, 91, 454, 91, (225, 224, 226))
    if skip_bonus_stage_state:
        bonus_stage_do_nothing()
    else:
        if not pixel_found:  # if Spirit Boost, do nothing until close appears
            bonus_stage_sp()
        else:
            bonus_stage_nsp()

def bonus_stage_do_nothing():
    write_log_entry("Do nothing BonusStage Active")
    while not bonus_stage_fail():
        time.sleep(0.2)
        
    settings = load_settings()
    paused = settings.getboolean("Settings", "paused")
    paused = not paused
        
    # Update the "paused" setting in the settings file
    settings_file_path = os.path.join(logs_dir, "settings.txt")
    settings.set("Settings", "paused", str(paused))
    with open(settings_file_path, "w") as configfile:
        settings.write(configfile)

def bonus_stage_fail():
    window = get_idle_slayer_window()
    print("Checking for exit button")
    if pyautogui.pixelMatchesColor(window.left + 775, window.top + 600, (180, 0, 0), tolerance=10):
        pyautogui.leftClick(window.left + 721, window.top + 577)
        print("Exit button found")
        write_log_entry("BonusStage Failed")
        return True
    return False

def c_send(press_delay, post_press_delay=0, key="w"):
    pyautogui.keyDown(key)
    time.sleep(press_delay)
    pyautogui.keyUp(key)
    time.sleep(post_press_delay)

def slider():
    window = get_idle_slayer_window()
    # Top left
    if pyautogui.pixelMatchesColor(window.left + 443, window.top + 560, (0, 126, 0)):
        pyautogui.moveTo(window.left + 840, window.top + 560)
        pyautogui.click(window.left + 840, window.top + 560)
        pyautogui.dragTo(window.left + 450, window.top + 560, button='left', duration=0.5)
        print("Top Left")
        return
    
    # Bottom left
    if pyautogui.pixelMatchesColor(window.left + 443, window.top + 620, (0, 126, 0)):
        pyautogui.moveTo(window.left + 840, window.top + 620)
        pyautogui.click(window.left + 840, window.top + 620)
        pyautogui.dragTo(window.left + 450, window.top + 620, button='left', duration=0.5)
        print("Bottom Left")
        return
    
    # Top right
    if pyautogui.pixelMatchesColor(window.left + 850, window.top + 560, (0, 126, 0)):
        pyautogui.moveTo(window.left + 450, window.top + 560)
        pyautogui.click(window.left + 450, window.top + 560)
        pyautogui.dragTo(window.left + 840, window.top + 560, button='left', duration=0.5)
        print("Top Right")
        return
    
    # Bottom right
    if pyautogui.pixelMatchesColor(window.left + 850, window.top + 620, (0, 126, 0)):
        pyautogui.moveTo(window.left + 450, window.top + 620)
        pyautogui.click(window.left + 450, window.top + 620)
        pyautogui.dragTo(window.left + 840, window.top + 620, button='left', duration=0.5)
        print("Bottom Right")
        return

def pixel_search(left, top, right, bottom, color, tolerance=0):
    global pixel_found
    pixel_found = False
    window = get_idle_slayer_window()
    screenshot = ImageGrab.grab(bbox=(window.left, window.top, window.left + 1280, window.top + 720))
    for x in range(left, right):
        for y in range(top, bottom):
            pixel_color = screenshot.getpixel((x, y))
            if color_match(pixel_color, color, tolerance):
                pixel_found = True
                return

def color_match(actual_color, target_color, tolerance):
    for i in range(3):
        if abs(actual_color[i] - target_color[i]) > tolerance:
            return False
    return True

def find_pixel_until_found(x1, y1, color, timer=15):
    window = get_idle_slayer_window()
    time_start = time.time()
    a_pos = None
    while True:
        a_pos = pyautogui.pixelMatchesColor(window.left + x1, window.top + y1, color)
        if a_pos is not None or timer < (time.time() - time_start):
            break
    if timer < (time.time() - time_start):
        return False
    else:
        return a_pos

def bonus_stage_sp():
    write_log_entry("BonusStageSpiritBoost")
    
    # Section 1 sync
    window = get_idle_slayer_window()
    #while 1:
    #    if pyautogui.pixelMatchesColor(window.left + 220, window.top + 465, (160, 147, 142)):
    #        break
    find_pixel_until_found(220, 465, (160, 147, 142))
    time.sleep(0.2)
    time.sleep(9)
    
    # Section 1 start
    c_send(0.94, 1.64)  # 1
    print("# 1")
    c_send(0.47, 2.072)  # 2
    print("# 2")
    c_send(1.87, 0.688)  # 3
    print("# 3")
    c_send(0.31, 0.672)  # 4
    print("# 4")
    c_send(0.31, 1.7)  # 5
    print("# 5")
    c_send(0.94, 1.64)  # 1
    print("# 1")
    c_send(0.47, 2.072)  # 2
    print("# 2")
    c_send(1.87, 0.688)  # 3
    print("# 3")
    c_send(0.31, 0.672)  # 4
    print("# 4")
    c_send(0.31, 1.7)  # 5
    print("# 5")
    c_send(0.94, 5)  # 1
    print("# 1")

    
    if bonus_stage_fail():
        return
    
    # Section 1 Collection
    c_send(0.4, 2.5)
    for _ in range(19):
        pyautogui.press("up")
        time.sleep(0.5)
    
    if bonus_stage_fail():
        return
    
    write_log_entry("BonusStageSpiritBoost Section 1 Complete")
    
    # Section 2 sync
    #while 1:
    #    if pyautogui.pixelMatchesColor(window.left + 780, window.top + 536, (187, 38, 223)):
    #        break
    find_pixel_until_found(780, 536, (187, 38, 223))
    
    # Section 2 start
    c_send(1.56, 0.719)  # 1
    print("# 1")
    c_send(0.47, 0.687)  # 2
    print("# 2")
    c_send(3.6, 1.39)  # 3
    print("# 3")
    c_send(4.85, 0.344)  # 4
    print("# 4")
    c_send(4.06, 0.859)  # 5
    print("# 5")
    c_send(0.78, 0.6)  # 6
    print("# 6")
    c_send(0.94, 0.9)  # 7
    print("# 7")
    c_send(1.09, 0.954)  # 8
    print("# 8")
    c_send(0.31, 0.672)  # 9
    print("# 9")
    c_send(5.15, 1.344)  # 10
    print("# 10")
    c_send(4.84, 0.297)  # 11
    print("# 11")
    c_send(4.06, 0.859)  # 12
    print("# 12")
    c_send(0.78, 0.6)  # 13
    print("# 13")
    c_send(0.94, 0.9)  # 14
    print("# 14")
    c_send(1.09, 0.954)  # 15
    print("# 15")
    c_send(0.31, 0.672)  # 16
    print("# 16")
    c_send(5.15, 1.344)  # 17
    print("# 17")
    c_send(4.69, 0.219)  # 18
    print("# 18")
    c_send(2.97, 1)  # 19
    print("# 19")
    c_send(1.56, 0.5)  # 20
    print("# 20")
    c_send(1.1, 3)  # 21
    print("# 21")
    c_send(3.6, 2.984)  # 22
    print("# 22")
    c_send(5.31, 2.313)  # 23
    print("# 23")

    
    if bonus_stage_fail():
        return
    
    # Section 2 Collection
    c_send(3.5, 1)
    for _ in range(20):
        pyautogui.press("up")
        time.sleep(0.5)
    
    if bonus_stage_fail():
        return
    
    write_log_entry("BonusStageSpiritBoost Section 2 Complete")
    
    # Stage 3 sync
    #while 1:
    #    if pyautogui.pixelMatchesColor(window.left + 220, window.top + 465, (160, 147, 142)):
    #        break
    find_pixel_until_found(220, 465, (160, 147, 142))
    
    # Section 3 Start
    c_send(1.09, 1.203)  # 1
    print("# 1")
    c_send(0.31, 0.641)  # 2
    print("# 2")
    c_send(0.47, 1.2)  # 3
    print("# 3")
    c_send(0.01, 3.1)  # 4
    print("# 4")

    # repeat
    c_send(1.09, 1.203)  # 5
    print("# 5")
    c_send(0.31, 0.641)  # 6
    print("# 6")
    c_send(0.47, 1.2)  # 7
    print("# 7")
    c_send(0.01, 3.1)  # 8
    print("# 8")

    # repeat
    c_send(1.09, 1.203)  # 9
    print("# 9")
    c_send(0.31, 0.641)  # 10
    print("# 10")
    c_send(0.47, 1.2)  # 11
    print("# 11")
    c_send(0.01, 3.1)  # 12
    print("# 12")

    # repeat
    c_send(1.09, 1.203)  # 13
    print("# 13")
    c_send(0.31, 0.641)  # 14
    print("# 14")
    c_send(0.47, 5.125)  # 15
    print("# 15")

    
    if bonus_stage_fail():
        return
    
    # Section 3 Collection
    c_send(9, 0.2)
    for _ in range(20):
        pyautogui.press("up")
        time.sleep(0.5)
    
    if bonus_stage_fail():
        return
    
    write_log_entry("BonusStageSpiritBoost Section 3 Complete")
    
    # Section 4 sync
    #while 1:
    #    if pyautogui.pixelMatchesColor(window.left + 250, window.top + 465, (160, 147, 142)) is not None:
    #        break
    pixel_search(250, 472, 100, 250, (13, 32, 48))
    #find_pixel_until_found(250, 472, 100, 250, (13, 32, 48))
    time.sleep(0.2)
    
    # Section 4 Start
    c_send(0.32, 2.8)  # 1
    print("# 1")
    c_send(0.31, 0.809)  # 2
    print("# 2")
    c_send(0.41, 1.2)  # 3
    print("# 3")
    c_send(1, 0.9)  # 4
    print("# 4")
    c_send(6.41, 0.5)  # 5
    print("# 5")

    c_send(0.31, 0.85)  # 6
    print("# 6")
    c_send(0.41, 0.77)  # 7
    print("# 7")
    c_send(6.41, 0.4)  # 8
    print("# 8")

    c_send(0.31, 0.85)  # 9
    print("# 9")
    c_send(0.41, 0.87)  # 10
    print("# 10")
    c_send(6.41, 0.3)  # 11
    print("# 11")

    c_send(0.31, 0.85)  # 12
    print("# 12")
    c_send(0.41, 0.79)  # 13
    print("# 13")
    c_send(6.41, 0.4)  # 14
    print("# 14")

    c_send(0.31, 0.85)  # 15
    print("# 15")
    c_send(0.41, 0.84)  # 16
    print("# 16")
    c_send(6.41, 0.3)  # 17
    print("# 17")

    c_send(0.31, 0.85)  # 18
    print("# 18")
    c_send(0.41, 0.84)  # 19
    print("# 19")
    c_send(6.41, 0.3)  # 20
    print("# 20")

    # Section 4 Collection
    for _ in range(23):
        pyautogui.press("up")
        time.sleep(0.5)
    
    if bonus_stage_fail():
        return
    
    settings = load_settings()
    paused = settings.getboolean("Settings", "paused")
    paused = not paused
        
    # Update the "paused" setting in the settings file
    settings_file_path = os.path.join(logs_dir, "settings.txt")
    settings.set("Settings", "paused", str(paused))
    with open(settings_file_path, "w") as configfile:
        settings.write(configfile)
    
    write_log_entry("BonusStageSpiritBoost Section 4 Complete")

def bonus_stage_nsp():
    write_log_entry("BonusStage")
    # Section 1 sync
    find_pixel_until_found(220, 465, (160, 147, 142))
    time.sleep(0.2)
    # Section 1 start
    c_send(94, 1.64)  # 1
    c_send(32, 1.218)  # 2
    c_send(94, 0.6)  # 3
    c_send(109, 1.828)  # 4
    c_send(63, 0.64)  # 5
    c_send(47, 0.688)  # 6
    c_send(78, 1.906)  # 7
    c_send(141, 1.625)  # 8
    c_send(47, 3.187)  # 9
    c_send(47, 0.734)  # 10
    c_send(47, 0.75)  # 11
    c_send(78, 1.203)  # 12
    c_send(110, 5)  # 13
    if bonus_stage_fail():
        return
    # Section 1 Collection
    c_send(40, 5)
    for _ in range(17):
        pyautogui.press("up")
        time.sleep(0.5)
    if bonus_stage_fail():
        return
    write_log_entry("BonusStage Section 1 Complete")
    # Section 2 sync
    find_pixel_until_found(780, 536, (187, 38, 223))
    # Section 2 start
    c_send(156, 0.719)  # 1
    c_send(47, 0.687)  # 2
    c_send(360, 1.39)  # 3
    c_send(485, 0.344)  # 4
    c_send(406, 0.859)  # 5
    c_send(78, 0.6)  # 6
    c_send(94, 0.9)  # 7
    c_send(109, 0.954)  # 8
    c_send(31, 0.672)  # 9
    c_send(515, 1.344)  # 10
    c_send(484, 0.297)  # 11
    c_send(406, 0.859)  # 12
    c_send(78, 0.6)  # 13
    c_send(94, 0.9)  # 14
    c_send(109, 0.954)  # 15
    c_send(31, 0.672)  # 16
    c_send(515, 1.344)  # 17
    c_send(469, 0.219)  # 18
    c_send(297, 1)  # 19
    c_send(156, 0.5)  # 20
    c_send(110, 3)  # 21
    c_send(360, 2.984)  # 22
    c_send(531, 2.313)  # 23
    if bonus_stage_fail():
        return
    # Section 2 Collection
    c_send(350, 1)
    for _ in range(20):
        pyautogui.press("up")
        time.sleep(0.5)
    if bonus_stage_fail():
        return
    write_log_entry("BonusStage Section 2 Complete")
    # Stage 3 sync
    find_pixel_until_found(220, 465, (160, 147, 142))
    # Section 3 Start
    c_send(109, 1.203)  # 1
    c_send(31, 0.641)  # 2
    c_send(47, 1.578)  # 3
    c_send(47, 2.437)  # 4
    # repeat
    c_send(109, 1.203)  # 5
    c_send(31, 0.641)  # 6
    c_send(47, 1.578)  # 7
    c_send(47, 2.437)  # 8
    # repeat
    c_send(109, 1.203)  # 9
    c_send(31, 0.641)  # 10
    c_send(47, 1.578)  # 11
    c_send(47, 2.437)  # 12
    # repeat
    c_send(109, 1.203)  # 13
    c_send(31, 0.641)  # 14
    c_send(47, 5.125)  # 15
    if bonus_stage_fail():
        return
    # Section 3 Collection
    c_send(9, 0.2)
    for _ in range(20):
        pyautogui.press("up")
        time.sleep(0.5)
    if bonus_stage_fail():
        return
    write_log_entry("BonusStage Section 3 Complete")
    # Section 4 sync
    pixel_search(250, 472, 100, 250, (13, 32, 48))
    #find_pixel_until_found(250, 472, 100, 250, (13, 32, 48))
    time.sleep(0.2)
    # Section 4 Start
    c_send(32, 2.5)  # 1
    c_send(31, 0.809)  # 2
    c_send(41, 1.375)  # 3
    c_send(41, 1.374)  # 4
    c_send(641, 0.69)  # 5
    c_send(41, 1.373)  # 6
    c_send(41, 2.5)  # 7
    c_send(31, 0.809)  # 8
    c_send(41, 1.375)  # 9
    c_send(41, 1.374)  # 10
    c_send(641, 0.69)  # 11
    c_send(41, 1.373)  # 12
    c_send(41, 1.372)  # 13
    c_send(641, 0.69)  # 14
    c_send(41, 1.371)  # 15
    # extra jump just in case
    c_send(41)  # 16
    # Section 4 Collection
    for _ in range(23):
        pyautogui.press("up")
        time.sleep(0.5)
    if bonus_stage_fail():
        return
    
    settings = load_settings()
    paused = settings.getboolean("Settings", "paused")
    paused = not paused
        
    # Update the "paused" setting in the settings file
    settings_file_path = os.path.join(logs_dir, "settings.txt")
    settings.set("Settings", "paused", str(paused))
    with open(settings_file_path, "w") as configfile:
        settings.write(configfile)
    
    write_log_entry("BonusStage Section 4 Complete")