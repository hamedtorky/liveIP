# Live Network Scanner 🔍

A comprehensive real-time network monitoring tool that scans and displays all alive devices on your local network with detailed information including ping speeds, SSH availability, MAC addresses, and more.

![Python](https://img.shields.io/badge/Python-3.6+-blue.svg)
![Platform](https://img.shields.io/badge/Platform-macOS%20%7C%20Linux-lightgrey.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 🚀 Features

✅ **Live Real-time Updates** - Continuously scans and auto-refreshes the display  
✅ **Ping Speed Measurement** - Shows latency for each device with quality indicators (⚡✓~⚠)  
✅ **SSH Port Detection** - Automatically checks which devices have SSH (port 22) available  
✅ **New Device Highlighting** - Newly discovered devices are highlighted with green background until another device joins  
✅ **MAC Address Display** - Shows MAC addresses retrieved from ARP cache  
✅ **Hostname Resolution** - Displays device names when available  
✅ **Status Indicators** - Color-coded online/recent/old status (🟢🟡🔴)  
✅ **Network Statistics** - Shows average ping and SSH availability count  
✅ **Concurrent Scanning** - Fast multi-threaded scanning of entire subnet  
✅ **Customizable Refresh Rate** - Set your own scan interval (3-60 seconds)  

---

## 📦 Installation

### Prerequisites
- Python 3.6 or higher
- macOS or Linux (uses `ping` and `arp` commands)
- Network access

### Setup

1. **Clone or download the scripts:**
```bash
cd /Users/hamed/Documents/ws/liveIP
```

2. **Make scripts executable:**
```bash
chmod +x live_scan.py
chmod +x scan_network.py
chmod +x quick_ssh_check.py
```

3. **Run immediately - no dependencies to install!**

All scripts use Python standard library only.

---

## 🎯 Usage

### 1. Live Network Monitor (Recommended)

Continuously monitors your network with real-time updates.

**Basic usage (10 second refresh):**
```bash
python3 live_scan.py
```

**Fast refresh (3 seconds):**
```bash
python3 live_scan.py 3
```

**Moderate refresh (5 seconds):**
```bash
python3 live_scan.py 5
```

**Slow refresh (30 seconds):**
```bash
python3 live_scan.py 30
```

**Or run as executable:**
```bash
./live_scan.py 5
```

**Stop monitoring:** Press `Ctrl+C`

---

### 2. One-Time Network Scan

Performs a single comprehensive scan and displays results.

```bash
python3 scan_network.py
```

Shows:
- All alive hosts
- IP addresses and hostnames
- MAC addresses
- Scan duration

---

### 3. Quick SSH Check

Focused scan to identify which devices have SSH available.

```bash
python3 quick_ssh_check.py
```

Provides:
- Devices with SSH open (🔓)
- Devices with SSH closed (🔒)
- Summary statistics

---

## 📊 Display Information

### Example Live Monitor Output

```
============================================================================================================
🔴 LIVE NETWORK MONITOR - Real-time IP Scanner with SSH Detection
============================================================================================================
⏰ Current Time: 2025-11-13 22:49:52
🔄 Scan #5 | Duration: 5.13s | Refresh: 10s
✅ Alive Hosts: 11
📊 Average Ping: 58.7ms | 🔓 SSH Available: 1/11
============================================================================================================

#    IP Address        Hostname                  MAC Address          Ping         SSH    Status    
------------------------------------------------------------------------------------------------------------
1    192.168.1.1       iopsys.lan                58:xx:xx:c2:29:e4    ✓ 18ms       🔒 No  🟢 Online  
2    192.168.1.165     node.lan                  d8:xx:dd:2e:e7:85    ✓ 13ms       🔓 Yes 🟢 Online  
3    192.168.1.172     mac.lan                   4a:xx:82:c2:94:xx    ⚡0.07ms      🔒 No  🟢 Online  
4    192.168.1.193     esp-733c0f.lan            xx:f9:e0:xx:3c:0f    ~ 61ms       🔒 No  🟢 Online  
5    192.168.1.201     esp32s3-642b7c.lan        84:xx:e6:6x:2b:7c    ⚠ 168ms      🔒 No  🟢 Online  
🆕  6    192.168.1.225     iphone.lan                9a:xx:a0:xx:31:8e    ⚡9.0ms       🔒 No  🟢 Online  
============================================================================================================

💡 Press Ctrl+C to stop monitoring...
```

---

## 🎨 Indicators & Symbols

### Ping Quality Indicators
| Symbol | Range | Quality |
|--------|-------|----------|
| ⚡ | < 10ms | Excellent (lightning fast) |
| ✓ | 10-50ms | Good |
| ~ | 50-100ms | Fair |
| ⚠ | > 100ms | Slow (warning) |

### Status Indicators
| Symbol | Meaning | Description |
|--------|---------|-------------|
| 🟢 Online | Active | Seen in the last 10 seconds |
| 🟡 Recent | Recent | Seen within 30 seconds |
| 🔴 Old | Stale | Last seen over 30 seconds ago |

### SSH Availability
| Symbol | Status | Description |
|--------|--------|-------------|
| 🔓 Yes | Open | SSH port (22) is accessible |
| 🔒 No | Closed | SSH port is closed or filtered |

### New Device Alert
| Symbol | Meaning |
|--------|----------|
| 🆕 + Green Background | Newly discovered device (highlighted until another device joins) |

---

## 📋 What Each Script Does

### `live_scan.py` - Live Network Monitor
**Best for:** Real-time monitoring and detecting network changes

- Continuously scans the network
- Auto-refreshes the display
- Shows ping speeds, SSH status, MAC addresses
- Highlights new devices
- Displays network statistics
- Customizable refresh interval

### `scan_network.py` - One-Time Scanner
**Best for:** Quick network overview

- Single comprehensive scan
- Detailed device information
- Fast concurrent scanning
- Shows MAC addresses and hostnames
- No continuous monitoring

### `quick_ssh_check.py` - SSH Checker
**Best for:** Finding SSH-accessible devices

- Focuses on SSH availability
- Separates devices with/without SSH
- Quick identification of accessible hosts
- Summary statistics

---

## ⚙️ Configuration

### Network Range
By default, scans `/24` subnet (255 IPs) based on your local IP.

To change, edit the `get_network_range()` function:
```python
def get_network_range(local_ip):
    # Change /24 to /16 for larger networks
    network = ipaddress.IPv4Network(f"{local_ip}/24", strict=False)
    return network
```

### Scan Speed
Adjust `max_workers` in `scan_network()` function:
```python
def scan_network(network, max_workers=50):  # Increase for faster scanning
```

### SSH Timeout
Modify timeout in `check_ssh_port()` function:
```python
def check_ssh_port(ip, port=22, timeout=1):  # Increase for slower networks
```

---

## 🔧 Troubleshooting

### "Permission Denied" when running scripts
```bash
chmod +x live_scan.py scan_network.py quick_ssh_check.py
```

### Slow scanning
- Decrease refresh interval: `python3 live_scan.py 10`
- Increase max_workers in the code
- Check network connectivity

### SSH shows all "No"
- Verify devices actually have SSH enabled
- Check firewall settings
- Some devices may filter port scans

### No devices found
- Confirm you're connected to the network
- Check if your subnet is different from 192.168.1.0/24
- Try pinging a known device manually: `ping 192.168.1.1`

---

## 💡 Tips & Best Practices

1. **Optimal Refresh Rate**: Use 5-10 seconds for live monitoring
2. **Network Load**: Faster refresh rates create more network traffic
3. **SSH Security**: Use SSH keys instead of passwords for devices with SSH
4. **Firewall**: Some devices may not respond to pings or port scans
5. **Privacy**: Be respectful - only scan networks you own or have permission to scan

---

## 📝 Example Use Cases

### Detect New Devices Joining Network
```bash
./live_scan.py 3
```
Watch for the 🆕 indicator when devices connect.

### Find SSH-Enabled Devices
```bash
python3 quick_ssh_check.py
```
Quickly identify which devices you can SSH into.

### Monitor Network Performance
```bash
./live_scan.py 10
```
Watch ping times and detect connectivity issues.

### Daily Network Snapshot
```bash
python3 scan_network.py > network_$(date +%Y%m%d).txt
```
Save daily network state for comparison.

---

## 🛡️ Security & Privacy

- **Local Use Only**: These tools are designed for monitoring your own network
- **No Data Collection**: All information stays on your local machine
- **Passive Scanning**: Uses standard ping and port checks
- **Responsible Use**: Only scan networks you own or have explicit permission to scan
- **SSH Security**: Finding open SSH ports helps identify security configurations

---

## 🐛 Known Limitations

- Requires devices to respond to ICMP (ping) requests
- Some devices may hide from network scans
- MAC addresses only available after ARP cache population
- SSH detection only checks if port 22 is open (not if SSH is actually running)
- Works best on `/24` networks (254 hosts)

---

## 📄 License

MIT License - Free to use and modify

---

## 🤝 Contributing

Feel free to:
- Report bugs
- Suggest features
- Submit improvements
- Share your use cases

---

## 📚 Technical Details

### Technologies Used
- **Python 3** - Core programming language
- **socket** - Network connections and SSH port checking
- **subprocess** - Ping commands and ARP queries
- **concurrent.futures** - Multi-threaded scanning for speed
- **ipaddress** - Network range calculations
- **ANSI escape codes** - Terminal colors and highlighting

### Network Protocols
- **ICMP** - Ping for device discovery
- **ARP** - MAC address resolution
- **TCP** - SSH port checking (port 22)
- **DNS** - Hostname resolution

---

## 📞 Support

If you find this useful or have questions:
- Check the troubleshooting section
- Review example use cases
- Ensure Python 3.6+ is installed

---

**Happy Network Monitoring! 🚀**
