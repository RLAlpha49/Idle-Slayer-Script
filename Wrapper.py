import time
import inspect
import os


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

        print("\r" + output)  # Print the output on the cleared line

        return result

    return wrapper
