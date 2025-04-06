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
import socket

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

def check_python_deps():
    """Ensure required Python dependencies are installed."""
    try:
        import socks  # PySocks
    except ImportError:
        print("Error: Missing Python dependencies for SOCKS support.")
        print("Installing 'requests' and 'pysocks'...")
        try:
            subprocess.run(["pip3", "install", "requests", "pysocks"], check=True)
            print("Dependencies installed. Please rerun the script.")
            sys.exit(0)
        except subprocess.CalledProcessError:
            print("Error: Failed to install dependencies. Run 'sudo pip3 install requests pysocks' manually.")
            sys.exit(1)

def install_packages():
    """Install curl, tor, and nc if missing, based on the Linux distro."""
    distro = get_linux_distro()
    print(f"Detected Linux distribution: {distro}")

    missing = []
    if not is_command_available("curl"):
        missing.append("curl")
    if not is_command_available("tor"):
        missing.append("tor")
    if not is_command_available("nc"):  # Netcat for SIGNAL NEWNYM
        missing.append("netcat-openbsd" if "Arch" in distro else "netcat")

    if not missing:
        print("Dependencies (curl, tor, nc) already installed.")
        return

    print(f"Installing missing packages: {', '.join(missing)}")
    try:
        if "Ubuntu" in distro or "Debian" in distro or "Kali" in distro:
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

def get_tor_socks_port():
    """Detect an active Tor SOCKS port (prefers 9050, falls back to others)."""
    ports_to_check = [("127.0.0.1", 9050), ("192.168.0.1", 9100)]
    for host, port in ports_to_check:
        try:
            with socket.create_connection((host, port), timeout=2):
                print(f"Found active Tor SOCKS proxy at {host}:{port}")
                return host, port
        except (ConnectionRefusedError, socket.timeout):
            print(f"No Tor proxy at {host}:{port}")
    print("Error: No active Tor SOCKS proxy found (tried 127.0.0.1:9050, 192.168.0.1:9100).")
    sys.exit(1)

def manage_tor(action):
    """Start Tor service or request a new circuit."""
    try:
        if action == "start":
            if subprocess.run(["systemctl", "is-active", "--quiet", "tor.service"]).returncode != 0:
                print("Starting Tor service...")
                subprocess.run(["systemctl", "start", "tor.service"], check=True)
                time.sleep(5)
                if subprocess.run(["systemctl", "is-active", "--quiet", "tor.service"]).returncode != 0:
                    raise subprocess.CalledProcessError(1, "systemctl start tor.service")
            else:
                print("Tor service already running.")
        elif action == "new_circuit":
            print("Requesting new Tor circuit...")
            try:
                # Use netcat to send SIGNAL NEWNYM to control port
                subprocess.run(
                    ["sh", "-c", 'echo -e "AUTHENTICATE \\\"\\\"\\nSIGNAL NEWNYM\\nQUIT" | nc 127.0.0.1 9051'],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                time.sleep(5)  # Wait for circuit to stabilize
            except subprocess.CalledProcessError:
                print("Warning: Failed to use control port (9051), restarting Tor...")
                subprocess.run(["systemctl", "restart", "tor.service"], check=True)
                time.sleep(10)
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to {action} Tor: {e}")
        sys.exit(1)

def is_tor_proxy_ready(host, port):
    """Check if Tor's SOCKS5 proxy is accepting connections."""
    for _ in range(10):
        try:
            with socket.create_connection((host, port), timeout=2):
                return True
        except (ConnectionRefusedError, socket.timeout):
            print(f"Waiting for Tor proxy ({host}:{port}) to be ready...")
            time.sleep(1)
    print(f"Error: Tor proxy ({host}:{port}) not responding after retries.")
    return False

def get_ip(host, port):
    """Fetch the current IP address via Tor with retries."""
    if not is_tor_proxy_ready(host, port):
        return "Unknown"
    proxy_url = f"socks5h://{host}:{port}"
    for attempt in range(3):
        try:
            response = requests.get(
                "https://checkip.amazonaws.com",
                proxies={"http": proxy_url, "https": proxy_url},
                timeout=10
            )
            ip = re.search(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", response.text)
            return ip.group(0) if ip else "Unknown"
        except requests.RequestException as e:
            print(f"Warning: Failed to fetch IP (attempt {attempt+1}/3): {e}")
            time.sleep(2)
    print("Error: Could not fetch IP after retries.")
    return "Unknown"

def change_ip(host, port):
    """Change the IP and display the new one."""
    manage_tor("new_circuit")
    new_ip = get_ip(host, port)
    print(f"\033[34mNew IP: {new_ip}\033[0m")
    print("Note: Refresh your browser to see the new IP.")

def clear_screen():
    """Clear the terminal."""
    os.system("clear")

def main():
    check_root()
    check_python_deps()

    parser = argparse.ArgumentParser(description="Change your IP using Tor at specified intervals (Linux only).")
    parser.add_argument("-s", "--seconds", type=int, default=None, help="Seconds between IP changes (e.g., -s 10)")
    parser.add_argument("-t", "--times", type=int, default=None, help="Number of IP changes (default: infinite)")
    args = parser.parse_args()

    install_packages()
    manage_tor("start")

    tor_host, tor_port = get_tor_socks_port()

    clear_screen()
    print("=== IP Changer by so1icitx ===")
    print("Press Ctrl+C to stop at any time.\n")

    if args.seconds is not None:
        interval = args.seconds
        times = args.times if args.times is not None else 0
        if interval <= 0:
            print("Error: Interval must be a positive number (e.g., -s 10).")
            sys.exit(1)
    else:
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

    try:
        if times == 0:
            print(f"Changing IP every {interval} seconds (infinite mode) using {tor_host}:{tor_port}...")
            while True:
                change_ip(tor_host, tor_port)
                time.sleep(interval)
        else:
            print(f"Changing IP {times} times, every {interval} seconds using {tor_host}:{tor_port}...")
            for i in range(times):
                print(f"Change {i+1}/{times}")
                change_ip(tor_host, tor_port)
                if i < times - 1:
                    time.sleep(interval)
            print("IP changing complete!")
    except KeyboardInterrupt:
        print("\nStopped by user.")
    except Exception as e:
        print(f"Error: An unexpected issue occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
