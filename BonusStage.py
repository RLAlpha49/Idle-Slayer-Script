import time
import pyautogui
import os
import sys
import keyboard
from Log import write_log_entry, increment_stat
from Wrapper import timer
from SettingsAndWindow import update_settings, get_idle_slayer_window

base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
logs_dir = os.path.join(base_dir, "AutoSlayerLogs")

@timer
def bonus_stage(skip_bonus_stage_state):
    update_settings("paused")
        
    write_log_entry("Start of BonusStage")
    while True:
        slider()
        time.sleep(0.5)
        if not pyautogui.pixelMatchesColor(660, 254, (255, 231, 55)):
            break
    time.sleep(3.9)
    if skip_bonus_stage_state:
        bonus_stage_do_nothing()
    else:
        if not pyautogui.pixelMatchesColor(454, 91, (225, 224, 226)):  # if Spirit Boost, do nothing until close appears
            bonus_stage_nsp()
        else:
            bonus_stage_nsp()

@timer
def bonus_stage_do_nothing():
    write_log_entry("Do nothing BonusStage Active")
    while not bonus_stage_fail():
        time.sleep(0.2)
        
    update_settings("paused")

@timer
def bonus_stage_fail():
    window = get_idle_slayer_window()
    print("Checking for exit button")
    if pyautogui.pixelMatchesColor(window.left + 775, window.top + 600, (180, 0, 0), tolerance=10):
        pyautogui.leftClick(window.left + 721, window.top + 577)
        print("Exit button found")
        
        write_log_entry("BonusStage Failed")
        increment_stat("Failed/Skipped Bonus Stages")
        
        update_settings("paused")
        
        return True
    return False

def c_send(press_delay, post_press_delay=0, key="w"):
    keyboard.press(key)
    time.sleep((press_delay / 1000))
    keyboard.release(key)
    time.sleep((post_press_delay / 1000))

@timer
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

@timer
def find_pixel_until_found(x1, y1, x2, y2, color):
    window = get_idle_slayer_window()
    if x1 == x2 and y1 == y2:
        a_pos = None
        while True:
            a_pos = pyautogui.pixelMatchesColor(window.left + x1, window.top + y1, color)
            if a_pos is not False:
                print(a_pos)
                return a_pos
    else:
        a_pos = None
        while True:
            for x in range(x1, x2):
                for y in range(y1, y2):
                    a_pos = pyautogui.pixelMatchesColor(window.left + x, window.top + y, color)
                    if a_pos is not False:
                        print(a_pos)
                        return a_pos
                    else:
                        print("No match found")

@timer
def bonus_stage_sp():
    write_log_entry("BonusStageSpiritBoost")

    # Section 1 sync
    find_pixel_until_found(220, 465, 220, 465(160, 147, 142))
    time.sleep(0.2)

    # Section 1 start
    c_send(162, 1177) #1
    c_send(73, 2452) #2
    c_send(66, 1688) #3
    c_send(84, 867) #4
    c_send(85, 2576) #5
    c_send(80, 740) #1
    c_send(90, 781) #2
    c_send(108, 2899) #3
    c_send(57, 722) #4
    c_send(83, 717) #5
    c_send(94, 5000) #1


    if bonus_stage_fail():
        return

    # Section 1 Collection
    c_send(40, 2500)
    for _ in range(19):
        pyautogui.press("w")
        time.sleep(0.4)

    if bonus_stage_fail():
        return

    write_log_entry("BonusStageSpiritBoost Section 1 Complete")

    # Section 2 sync
    find_pixel_until_found(780, 536, 780, 536, (187, 38, 223))

    # Section 2 start
    c_send(156, 719) #1
    c_send(47, 687) #2
    c_send(360, 1390) #3
    c_send(485, 344) #4
    c_send(406, 859) #5
    c_send(78, 600) #6
    c_send(94, 900) #7
    c_send(109, 954) #8
    c_send(31, 672) #9
    c_send(515, 1344) #10
    c_send(484, 297) #11
    c_send(406, 859) #12
    c_send(78, 600) #13
    c_send(94, 900) #14
    c_send(109, 954) #15
    c_send(31, 672) #16
    c_send(515, 1344) #17
    c_send(469, 219) #18
    c_send(297, 1000) #19
    c_send(156, 500) #20
    c_send(110, 3000) #21
    c_send(360, 2984) #22
    c_send(531, 2313) #23


    if bonus_stage_fail():
        return

    # Section 2 Collection
    c_send(350, 1000)
    for _ in range(20):
        pyautogui.press("w")
        time.sleep(0.4)

    if bonus_stage_fail():
        return

    write_log_entry("BonusStageSpiritBoost Section 2 Complete")

    # Stage 3 sync
    find_pixel_until_found(220, 465, 220, 465, (160, 147, 142))

    # Section 3 Start
    c_send(109, 1203) #1
    c_send(31, 641) #2
    c_send(47, 1200) #3
    c_send(1, 3100) #4
    #repeat
    c_send(109, 1203) #5
    c_send(31, 641) #6
    c_send(47, 1200) #7
    c_send(1, 3100) #8
    #repeat
    c_send(109, 1203) #9
    c_send(31, 641) #10
    c_send(47, 1200) #11
    c_send(1, 3100) #12
    #repeat
    c_send(109, 1203) #13
    c_send(31, 641) #14
    c_send(47, 5125) #15


    if bonus_stage_fail():
        return

    # Section 3 Collection
    c_send(900, 200)
    for _ in range(20):
        pyautogui.press("w")
        time.sleep(0.4)

    if bonus_stage_fail():
        return

    write_log_entry("BonusStageSpiritBoost Section 3 Complete")

    # Section 4 sync
    find_pixel_until_found(250, 472, 100, 250, (13, 32, 48))
    time.sleep(0.2)

    # Section 4 Start
    c_send(32, 2800) #1
    c_send(31, 809) #2
    c_send(41, 1200) #3
    c_send(100, 900) #4
    c_send(641, 500) #5

    c_send(31, 850) #6
    c_send(41, 770) #7
    c_send(641, 400) #8

    c_send(31, 850) #9
    c_send(41, 870) #10
    c_send(641, 300) #11

    c_send(31, 850) #12
    c_send(41, 790) #13
    c_send(641, 400) #14

    c_send(31, 850) #15
    c_send(41, 840) #16
    c_send(641, 300) #17

    c_send(31, 850) #18
    c_send(41, 840) #19
    c_send(641, 300) #20

    # Section 4 Collection
    for _ in range(23):
        pyautogui.press("w")
        time.sleep(0.4)

    if bonus_stage_fail():
        return

    update_settings("paused")

    write_log_entry("BonusStageSpiritBoost Section 4 Complete")

@timer
def bonus_stage_nsp():
    write_log_entry("BonusStage")
    # Section 1 sync
    find_pixel_until_found(220, 465, 220, 465,  (160, 147, 142))
    time.sleep(0.2)

    # Section 1 start
    c_send(94, 1640) #1
    c_send(32, 1218) #2
    c_send(94, 600) #3
    c_send(109, 1828) #4
    c_send(63, 640) #5
    c_send(47, 688) #6
    c_send(78, 1906) #7
    c_send(141, 1625) #8
    c_send(47, 3187) #9
    c_send(47, 734) #10
    c_send(47, 750) #11
    c_send(78, 1203) #12
    c_send(110, 5000) #13

    if bonus_stage_fail():
        return

    # Section 1 Collection
    c_send(40, 5000)
    for _ in range(17):
        pyautogui.press("w")
        time.sleep(0.4)
    if bonus_stage_fail():
        return
    else:
        increment_stat("Stage 2 Section 1 Completed")
        write_log_entry("BonusStage Section 1 Complete")

    # Section 2 sync
    find_pixel_until_found(780, 536, 780, 536, (187, 38, 223))

    # Section 2 start
    c_send(156, 719) #1
    c_send(47, 687) #2
    c_send(360, 1390) #3
    c_send(485, 344) #4
    c_send(406, 859) #5
    c_send(78, 600) #6
    c_send(94, 900) #7
    c_send(109, 954) #8
    c_send(31, 672) #9
    c_send(515, 1344) #10
    c_send(484, 297) #11
    c_send(406, 859) #12
    c_send(78, 600) #13
    c_send(94, 900) #14
    c_send(109, 954) #15
    c_send(31, 672) #16
    c_send(515, 1344) #17
    c_send(469, 219) #18
    c_send(297, 1000) #19
    c_send(156, 500) #20
    c_send(110, 3000) #21
    c_send(360, 2984) #22
    c_send(531, 2313) #23

    if bonus_stage_fail():
        return

    # Section 2 Collection
    c_send(350, 1000)
    for _ in range(20):
        pyautogui.press("w")
        time.sleep(0.4)
    if bonus_stage_fail():
        return
    else:
        increment_stat("Stage 2 Section 2 Completed")
        write_log_entry("BonusStage Section 2 Complete")

    # Stage 3 sync
    find_pixel_until_found(220, 465, 220, 465, (160, 147, 142))

    # Section 3 Start
    c_send(109, 1203) #1
    c_send(31, 641) #2
    c_send(47, 1578) #3
    c_send(47, 2437) #4
    #repeat
    c_send(109, 1203) #5
    c_send(31, 641) #6
    c_send(47, 1578) #7
    c_send(47, 2437) #8
    #repeat
    c_send(109, 1203) #9
    c_send(31, 641) #10
    c_send(47, 1578) #11
    c_send(47, 2437) #12
    #repeat
    c_send(109, 1203) #13
    c_send(31, 641) #14
    c_send(47, 5125) #15
    if bonus_stage_fail():
        return

    # Section 3 Collection
    c_send(900, 200)
    for _ in range(20):
        pyautogui.press("w")
        time.sleep(0.4)
    if bonus_stage_fail():
        return
    else:
        increment_stat("Stage 2 Section 3 Completed")
        write_log_entry("BonusStage Section 3 Complete")

    # Section 4 sync
    find_pixel_until_found(100, 250, 250, 472, (13, 32, 48))
    time.sleep(0.2)

    # Section 4 Start
    c_send(32, 1375) #1
    c_send(641, 690) #2
    c_send(41, 1375) #3
    c_send(41, 1374) #4
    c_send(641, 690) #5
    c_send(41, 1373) #6
    c_send(41, 2500) #7
    c_send(31, 809) #8
    c_send(41, 1375) #9
    c_send(41, 1374) #10
    c_send(641, 690) #11
    c_send(41, 1373) #12
    c_send(41, 1372) #13
    c_send(641, 690) #14
    c_send(41, 1371) #15
    # extra jump just in case
    c_send(41) #16

    # Section 4 Collection
    for _ in range(23):
        pyautogui.press("w")
        time.sleep(0.4)
    if bonus_stage_fail():
        return
    else:
        increment_stat("Stage 2 Section 4 Completed")
        write_log_entry("BonusStage Section 4 Complete")
        increment_stat("Bonus Stages")

    update_settings("paused")