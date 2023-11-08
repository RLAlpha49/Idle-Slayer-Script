import os
import sys
import time
#import pygetwindow as gw
import pyautogui
import platform
import subprocess
from configparser import ConfigParser
from Wrapper import timer

base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
logs_dir = os.path.join(base_dir, "AutoSlayerLogs")
settings_file_path = os.path.join(logs_dir, "settings.txt")

@timer
def load_settings():
    settings = ConfigParser()
    settings_file_path = os.path.join(logs_dir, "settings.txt")
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
    if get_operating_system == "Linux":
        while True:
            # Find the Idle Slayer window by its title using xdotool
            try:
                xdotool_output = subprocess.check_output(['xdotool', 'search', '--name', 'Idle Slayer']).decode('utf-8')
                window_id = xdotool_output.strip().split('\n')[0]
                return window_id
            except subprocess.CalledProcessError:
                pass
        
            time.sleep(1)  # Wait for 1 second before checking again
    elif get_operating_system == "Windows":
        while True:
            import pygetwindow as gw
            # Find the Idle Slayer window by its title
            idle_slayer_windows = gw.getWindowsWithTitle("Idle Slayer")
            if idle_slayer_windows:
                return idle_slayer_windows[0]
            time.sleep(1)  # Wait for 1 second before checking again

@timer
def get_focused_window():
    print(sys.platform)
    if get_operating_system == "Linux":
        from Xlib import display
        
        def get_focused_window_title():
            root = display.Display().screen().root
            window_id = root.get_full_property(display.Xatom.WM_NAME, 0).value
            return window_id.decode('utf-8')

        focused_window_title = get_focused_window_title()

    elif get_operating_system == "Windows":
        import win32gui
        focused_window_title = win32gui.GetWindowText(win32gui.GetForegroundWindow())
    else:
        focused_window_title = "Unsupported platform"
    return focused_window_title

# Function to get the active window title based on the operating system
def get_active_window_title():
    print(get_operating_system())
    if get_operating_system() == "Windows":
        command = 'powershell -Command "(Get-Process | Where-Object { $_.MainWindowTitle }).MainWindowTitle"'
        result = subprocess.run(command, capture_output=True, text=True, shell=True)
        return result.stdout.strip()
    elif get_operating_system() == "Linux":
        from ewmh import EWMH
        wm = EWMH()
        win = wm.getActiveWindow()
        win_name = win.get_wm_name()
        
        print(win_name)

        return win_name
    else:
        return None  # Unsupported platform
    
def move_window_by_name(window_title, x, y):
    try:
        # Get the window ID by its title using wmctrl
        window_id_command = f"wmctrl -l | grep '{window_title}' | awk '{{print $1}}'"
        window_id = subprocess.check_output(window_id_command, shell=True).decode().strip()

        if window_id:
            # Move the window to a specific position using wmctrl
            move_command = f"wmctrl -ir {window_id} -e 0,{x},{y},-1,-1"
            subprocess.run(move_command, shell=True)
            return True
    except subprocess.CalledProcessError:
        pass

    return False

def get_operating_system():
    print(f"Platform: {platform.system()}")
    return platform.system()