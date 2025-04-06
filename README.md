
# IP Changer by so1icitx

A **faster, better Python version** of the famous [gr33n37-ip-changer](https://github.com/gr33n37/gr33n37-ip-changer)! This lightweight script rotates your IP address using Tor on Linux. Perfect for **privacy**, **testing**, or **ethical hacking**. Run `sudo python3 ip_changer.py -s 10` to change your IP every 10 seconds—automatically installs `curl` and `tor` on Ubuntu, Debian, Fedora, CentOS, Arch, and more! TESTED ONLY ON ARCH, UPDATE COMING SOON!


## Installation

### Step 1: Get Python
You need Python 3. Check if it’s installed:
```bash
python3 --version
```
If not, install it (e.g., `sudo apt install python3` on Ubuntu).

### Step 2: Download the Script
Pick your method:

#### With Git:
```bash
git clone https://github.com/so1icitx/ip_changer.git
cd ip-changer
```

### Step 3: Install the Requests Library

### Arch Linux
```bash
sudo pacman -Syu python python-pip tor openbsd-netcat curl
sudo pip3 install requests pysocks
```

The script will install `curl` and `tor` automatically (as root) for supported Linux distros.

## Firefox Setup
To see IP changes in Firefox:
1. Go to `Settings > General > Network Settings > Settings...`.
2. Select `Manual proxy configuration`.
3. Set:
   - SOCKS Host: `127.0.0.1`
   - Port: `9050`
   - SOCKS v5
   - Check `Proxy DNS when using SOCKS v5`
4. Leave other fields blank, click `OK`.
5. Refresh pages manually, or use a extension like 'tab reloader'.
## Usage

Run it as root since it manages Tor:

### Quick Command
Change IP every X seconds (e.g., 10 seconds, forever):
```bash
sudo python3 ip_changer.py -s 10
```

Change IP X times (e.g., 5 times, every 10 seconds):
```bash
sudo python3 ip_changer.py -s 10 -t 5
```

### Interactive Mode
Just run it and follow the prompts:
```bash
sudo python3 ip_changer.py
```

### Options
- `-s SECONDS`: Set the interval between changes (e.g., `-s 10` for 10 seconds).
- `-t TIMES`: Set how many times to change (e.g., `-t 5` for 5 changes; omit for infinite).

## Examples
- **Every 10 seconds, forever**:
  ```bash
  sudo python3 ip_changer.py -s 10
  ```
  ```
  === IP Changer by so1icitx ===
  Press Ctrl+C to stop at any time.
  Changing IP every 10 seconds (infinite mode)...
  Reloading Tor to change IP...
  New IP: 185.220.101.12
  [10 seconds]
  Reloading Tor to change IP...
  New IP: 91.47.233.87
  ```

- **3 changes, every 5 seconds**:
  ```bash
  sudo python3 ip_changer.py -s 5 -t 3
  ```
  ```
  === IP Changer by so1icitx ===
  Press Ctrl+C to stop at any time.
  Changing IP 3 times, every 5 seconds...
  Change 1/3
  Reloading Tor to change IP...
  New IP: 109.70.100.23
  Change 2/3
  Reloading Tor to change IP...
  New IP: 185.220.101.12
  Change 3/3
  Reloading Tor to change IP...
  New IP: 91.47.233.87
  IP changing complete!
  ```

## Troubleshooting
- **"Must be run as root"**: Use `sudo`.
- **Tor not working?**: Check it with `systemctl status tor.service`.
- **IP not changing?**: Test Tor with `curl -x socks5h://127.0.0.1:9050 https://checkip.amazonaws.com`.
- **Install failed?**: Ensure internet access and try again.

## Supported Distros
- Tested only on Arch Linux , will test on other distros soon!
- Others? Report issues if it fails!

## Notes
- For educational use only—stay legal!
- Inspired by [gr33n37-ip-changer](https://github.com/gr33n37/gr33n37-ip-changer)—credit to the OG!

Got questions? Open an issue on GitHub or send a email at 'so1citix.zone242@passinbox.com'. Enjoy your anonymity!

---



