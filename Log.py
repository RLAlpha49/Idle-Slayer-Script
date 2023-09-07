import os
import time
import sys

base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
logs_dir = os.path.join(base_dir, "AutoSlayerLogs")

# Use the logs_dir to construct file path
log_file_path = os.path.join(logs_dir, "log.txt")
stats_file_path = os.path.join(logs_dir, "stats.txt")

def write_log_entry(log_entry):
    with open(log_file_path, "a") as log_file:
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        formatted_log_entry = f"{current_time} : {log_entry}\n"
        log_file.write(formatted_log_entry)

def increment_stat(stat_name):
    # Read the existing stats from the file
    stats = {}
    with open(stats_file_path, "r") as configfile:
        for line in configfile:
            line = line.strip()
            if line:
                stat, value = line.split(": ")
                stats[stat] = int(value)  # Convert the value to an integer

    # Increment the specific stat by 1
    if stat_name in stats:
        stats[stat_name] += 1
    else:
        # If the stat doesn't exist, create it with a value of 1
        stats[stat_name] = 1

    # Write the updated stats back to the file
    with open(stats_file_path, "w") as configfile:
        for stat, value in stats.items():
            configfile.write(f"{stat}: {value}\n")
