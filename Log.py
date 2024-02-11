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


# Function to write to a file
def write_to_file(file_path, mode, content):
    with open(file_path, mode) as file:
        file.write(content)


@timer
def write_log_entry(log_entry):
    current_time = time.strftime("%Y-%m-%d %H:%M:%S")
    formatted_log_entry = f"{current_time} : {log_entry}\n"
    write_to_file(log_file_path, "a", formatted_log_entry)
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
    stats_content = "\n".join(f"{stat}: {value}" for stat, value in stats.items())
    write_to_file(stats_file_path, "w", stats_content)


# Function to parse the date from the log line
def parse_date(log_line):
    date_str = log_line.split(" : ")[0]
    return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")


def parse_message(line):
    return line.split(" : ")[1]


from datetime import timedelta


@timer
def remove_extra_lines():
    # Read the log file
    with open(log_file_path, "r") as file:
        lines = file.readlines()

    # Initialize variables for the first line
    prev_line = lines[0]
    prev_date = parse_date(prev_line)
    prev_message = parse_message(prev_line)

    # Create a new list to store filtered lines
    filtered_lines = [prev_line]

    # Iterate over the remaining lines
    for line in lines[1:]:
        current_date = parse_date(line)
        current_message = parse_message(line)

        # Check if the message is the same and the time difference is less than 1 minute and 30 seconds
        if current_message != prev_message or (current_date - prev_date) > timedelta(
            minutes=1, seconds=30
        ):
            # Append the line to the filtered list if the message is different or the time difference is more than 1 minute and 30 seconds
            filtered_lines.append(line)

        prev_line = line
        prev_date = current_date
        prev_message = current_message

    # Write the filtered lines back to the file
    filtered_lines_content = "".join(filtered_lines)
    write_to_file(log_file_path, "w", filtered_lines_content)
