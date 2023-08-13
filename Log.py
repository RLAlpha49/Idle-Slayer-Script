import os
import time
import sys

base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
logs_dir = os.path.join(base_dir, "AutoSlayerLogs")

# Use the logs_dir to construct file path
log_file_path = os.path.join(logs_dir, "log.txt")

def write_log_entry(log_entry):
    with open(log_file_path, "a") as log_file:
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        formatted_log_entry = f"{current_time} : {log_entry}\n"
        log_file.write(formatted_log_entry)