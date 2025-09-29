#!/usr/bin/env python3
"""
Process Logger Utility
----------------------

This script monitors running processes on the system and creates
timestamped log files containing process details.

Features:
- Scans all running processes (PID, Name, User, Memory usage).
- Creates a new log file at regular intervals.
- Stores logs in a user-defined folder.
- Supports both interactive input and command-line arguments.
- Gracefully handles missing processes and permission errors.

Usage:
    Interactive mode:
        python process_logger.py

    Command-line mode:
        python process_logger.py <FolderName> <IntervalInMinutes>

Example:
    python process_logger.py logs 2
    -> Creates a new log every 2 minutes inside the "logs/" folder.
"""

import psutil
import os
import time
import schedule
import sys
from datetime import datetime


def scan_processes():
    """
    Scan running processes and collect information.

    Returns:
        list of dict: Each dictionary contains PID, process name,
                      username, and memory usage (in MB).
    """
    processes = []
    for proc in psutil.process_iter():
        try:
            info = proc.as_dict(attrs=['pid', 'name', 'username'])
            info['Memory_MB'] = proc.memory_info().vms / (1024 * 1024)
            processes.append(info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            # Ignore processes that can't be accessed
            pass
    return processes


def create_log(folder_name):
    """
    Create a log file with details of running processes.

    Args:
        folder_name (str): Directory where log files will be stored.
    """
    os.makedirs(folder_name, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = os.path.join(folder_name, f"process_log_{timestamp}.log")

    with open(file_path, "w") as log_file:
        border = "-" * 80
        log_file.write(border + "\n")
        log_file.write("            System Process Log\n")
        log_file.write(f"    Log created at : {time.ctime()}\n")
        log_file.write(border + "\n\n")

        for proc in scan_processes():
            log_file.write(
                f"PID: {proc['pid']:<8} "
                f"Name: {proc['name']:<25} "
                f"User: {proc['username']:<15} "
                f"Memory: {proc['Memory_MB']:.2f} MB\n"
            )

        log_file.write("\n" + border + "\n")

    print(f"[+] Log created: {file_path}")


def main():
    """
    Main entry point of the program.
    Accepts folder name and interval either interactively
    or via command-line arguments.
    """
    if len(sys.argv) == 3:
        folder_name = sys.argv[1]
        interval = int(sys.argv[2])
    else:
        print("Enter folder name to store logs:")
        folder_name = input().strip()

        print("Enter time interval (in minutes):")
        interval = int(input().strip())

    # Schedule logging task
    schedule.every(interval).minutes.do(create_log, folder_name)

    print(f"\n[✓] Logging started. Logs will be saved in '{folder_name}' every {interval} minutes.")
    print("Press Ctrl+C to stop.\n")

    # Run indefinitely until stopped by user
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[!] Logging stopped by user.")


if __name__ == "__main__":
    main()
