import time
import inspect
import os
import sys

# Decorator function
def timer(func):
    def wrapper(*args, **kwargs):
        before = time.time()
        result = func(*args, **kwargs)
        after = time.time()

        # Capture the current frame for the caller's line number
        frame_info = inspect.currentframe()
        caller_file = os.path.basename(frame_info.f_back.f_code.co_filename)
        caller_line = frame_info.f_back.f_lineno
        frame_info = None  # Release the frame reference

        output = f"{func.__name__:30} Function took: {(after - before):.15f} seconds. Called from {caller_file:14} line {caller_line}"

        # Check if the current line has anything on it
        current_line = sys.stdout.write("\r" + " " * 80)  # Clear the current line
        sys.stdout.flush()
        print("\r" + output)  # Print the output on the cleared line

        return result

    # Check if the function has already been decorated to prevent double decoration
    if not hasattr(wrapper, "_is_decorated"):
        wrapper._is_decorated = True  # Mark the function as decorated

    return wrapper
