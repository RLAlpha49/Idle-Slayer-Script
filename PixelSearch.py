import pygetwindow as gw
from PIL import ImageGrab
from Wrapper import timer


def search_pixel_in_column(screenshot, color, x, top, bottom, shade):
    for y in range(top, bottom):
        pixel_color = screenshot.getpixel((x, y))
        # Used to find different pixel rgb values within a certain area. I use this for finding out what rgb values to search for in the script.
        if color == (0, 0, 0):
            print(f"Pixel at ({x}, {y}) - Color: {pixel_color}")

        if color_match(pixel_color, color, shade):
            return x, y
    return None


@timer
def PixelSearchWindow(color, left, right, top, bottom, shade=None):
    idle_slayer_windows = gw.getWindowsWithTitle("Idle Slayer")
    window = idle_slayer_windows[0]
    screenshot = ImageGrab.grab(
        bbox=(window.left, window.top, window.left + 1280, window.top + 720)
    )

    for x in range(left, right + 1):
        result = search_pixel_in_column(screenshot, color, x, top, bottom, shade)
        if result is not None:
            return result
    return None


def color_match(actual_color, target_color, shade):
    for i in range(3):
        if abs(actual_color[i] - target_color[i]) > shade:
            return False
    return True
