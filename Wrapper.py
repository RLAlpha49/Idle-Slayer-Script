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

        output = f"{func.__name__:30} Function took: {(after - before):.15f} seconds. Called from {caller_file:21} line {caller_line}"

        try:
            if sys.stdout:
                # Check if sys.stdout is available before calling flush
                sys.stdout.flush()
                print("\r" + output)  # Print the output on the cleared line
        except Exception as e:
            # Handle any exceptions related to sys.stdout
            print("An error occurred while printing timing information:", str(e))

        return result

    # Check if the function has already been decorated to prevent double decoration
    if not hasattr(wrapper, "_is_decorated"):
        wrapper._is_decorated = True  # Mark the function as decorated

    return wrapper
