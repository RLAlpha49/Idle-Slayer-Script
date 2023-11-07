import os
import time
import sys
from datetime import datetime, timedelta
from Wrapper import timer

base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
logs_dir = os.path.join(base_dir, "AutoSlayerLogs")

# Use the logs_dir to construct file path
log_file_path = os.path.join(logs_dir, "log.txt")
stats_file_path = os.path.join(logs_dir, "stats.txt")

@timer
def write_log_entry(log_entry):
    with open(log_file_path, "a") as log_file:
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        formatted_log_entry = f"{current_time} : {log_entry}\n"
        log_file.write(formatted_log_entry)
        time.sleep(0.1)
        remove_extra_lines()

@timer
def increment_stat(stat_name):
    # Read the existing stats from the file
    stats = {}
    with open(stats_file_path, "r") as configfile:
        time.sleep(0.1)
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

# Function to parse the date from the log line
def parse_date(log_line):
    date_str = log_line.split(' : ')[0]
    return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')

@timer
def remove_extra_lines():
    # Read the log file
    with open(log_file_path, 'r') as file:
        lines = file.readlines()

    # Initialize variables for the first line
    prev_line = lines[0]
    prev_date = parse_date(prev_line)

    # Create a new list to store filtered lines
    filtered_lines = [prev_line]

    # Define a threshold (1 minute) for ignoring repeated entries
    threshold = timedelta(minutes=1)

    # Iterate over the remaining lines
    for line in lines[1:]:
        current_date = parse_date(line)
        time_difference = current_date - prev_date

        if time_difference >= threshold:
            # Append the line to the filtered list if the time difference is more than 1 minute
            filtered_lines.append(line)

        prev_line = line
        prev_date = current_date

    # Write the filtered lines back to the file
    with open(log_file_path, 'w') as file:
        file.writelines(filtered_lines)