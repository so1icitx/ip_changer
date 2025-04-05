#!/usr/bin/env python3
# IP Changer Script by so1icitx
# Changes your IP address using Tor at specified intervals (Linux only)

import os
import sys
import time
import subprocess
import random
import requests
import re
import argparse

def check_root():
    """Ensure the script runs as root."""
    if os.geteuid() != 0:
        print("Error: This script must be run as root (e.g., sudo python3 ip_changer.py).")
        sys.exit(1)

def get_linux_distro():
    """Detect the Linux distribution name."""
    try:
        with open("/etc/os-release", "r") as f:
            for line in f:
                if line.startswith("NAME="):
                    return line.split("=")[1].strip().strip('"')
        return "Unknown"
    except FileNotFoundError:
        return "Unknown"

def is_command_available(command):
    """Check if a command exists on the system."""
    return subprocess.call(["which", command], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0

def install_packages():
    """Install curl and tor if missing, based on the Linux distro."""
    distro = get_linux_distro()
    print(f"Detected Linux distribution: {distro}")

    missing = []
    if not is_command_available("curl"):
        missing.append("curl")
    if not is_command_available("tor"):
        missing.append("tor")

    if not missing:
        print("Dependencies (curl, tor) already installed.")
        return

    print(f"Installing missing packages: {', '.join(missing)}")
    try:
        if "Ubuntu" in distro or "Debian" in distro:
            subprocess.run(["apt-get", "update"], check=True)
            subprocess.run(["apt-get", "install", "-y"] + missing, check=True)
        elif "Fedora" in distro or "CentOS" in distro or "Red Hat" in distro or "Amazon Linux" in distro:
            subprocess.run(["yum", "install", "-y"] + missing, check=True)
        elif "Arch" in distro:
            print("Arch Linux detected: Performing full system update to install packages...")
            subprocess.run(["pacman", "-Syu", "--noconfirm"] + missing, check=True)
        else:
            print(f"Error: Unsupported distribution '{distro}'. Install {', '.join(missing)} manually.")
            sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to install packages: {e}")
        sys.exit(1)

def manage_tor(action):
    """Start or reload the Tor service."""
    try:
        if action == "start":
            if subprocess.run(["systemctl", "is-active", "--quiet", "tor.service"]).returncode != 0:
                print("Starting Tor service...")
                subprocess.run(["systemctl", "start", "tor.service"], check=True)
                time.sleep(2)  # Wait for Tor to initialize
                if subprocess.run(["systemctl", "is-active", "--quiet", "tor.service"]).returncode != 0:
                    raise subprocess.CalledProcessError(1, "systemctl start tor.service")
            else:
                print("Tor service already running.")
        elif action == "reload":
            print("Reloading Tor to change IP...")
            subprocess.run(["systemctl", "reload", "tor.service"], check=True)
            time.sleep(2)  # Wait for new circuit
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to {action} Tor service: {e}")
        sys.exit(1)

def get_ip():
    """Fetch the current IP address via Tor."""
    try:
        response = requests.get(
            "https://checkip.amazonaws.com",
            proxies={"http": "socks5h://127.0.0.1:9050", "https": "socks5h://127.0.0.1:9050"},
            timeout=5
        )
        ip = re.search(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", response.text)
        return ip.group(0) if ip else "Unknown"
    except requests.RequestException as e:
        print(f"Warning: Failed to fetch IP: {e}")
        return "Unknown"

def change_ip():
    """Change the IP and display the new one."""
    manage_tor("reload")
    new_ip = get_ip()
    print(f"\033[34mNew IP: {new_ip}\033[0m")

def clear_screen():
    """Clear the terminal."""
    os.system("clear")

def main():
    # Check root privileges
    check_root()

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Change your IP using Tor at specified intervals (Linux only).")
    parser.add_argument("-s", "--seconds", type=int, default=None, help="Seconds between IP changes (e.g., -s 10)")
    parser.add_argument("-t", "--times", type=int, default=None, help="Number of IP changes (default: infinite)")
    args = parser.parse_args()

    # Install dependencies
    install_packages()

    # Start Tor
    manage_tor("start")

    # Clear screen and show header
    clear_screen()
    print("=== IP IP Changer by so1icitx ===")
    print("Press Ctrl+C to stop at any time.\n")

    # Determine interval and times
    if args.seconds is not None:
        interval = args.seconds
        times = args.times if args.times is not None else 0  # 0 means infinite
        if interval <= 0:
            print("Error: Interval must be a positive number (e.g., -s 10).")
            sys.exit(1)
    else:
        # Interactive mode
        while True:
            try:
                interval_str = input("\033[34mEnter time interval in seconds (e.g., 10): \033[0m")
                interval = int(interval_str)
                if interval <= 0:
                    print("Please enter a positive number.")
                    continue
                times_str = input("\033[34mEnter number of changes (0 for infinite): \033[0m")
                times = int(times_str)
                if times < 0:
                    print("Please enter a non-negative number.")
                    continue
                break
            except ValueError:
                print("Error: Enter valid numbers (e.g., 10 for seconds, 5 for times).")

    # Execute IP changes
    try:
        if times == 0:
            print(f"Changing IP every {interval} seconds (infinite mode)...")
            while True:
                change_ip()
                time.sleep(interval)
        else:
            print(f"Changing IP {times} times, every {interval} seconds...")
            for i in range(times):
                print(f"Change {i+1}/{times}")
                change_ip()
                if i < times - 1:  # No sleep after the last change
                    time.sleep(interval)
            print("IP changing complete!")
    except KeyboardInterrupt:
        print("\nStopped by user.")
    except Exception as e:
        print(f"Error: An unexpected issue occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
