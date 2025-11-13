#!/usr/bin/env python3
"""
Live Network Scanner - Real-time monitoring of alive IP addresses
Press Ctrl+C to stop
"""

import socket
import ipaddress
import concurrent.futures
from datetime import datetime
import subprocess
import platform
import time
import os

def clear_screen():
    """Clear the terminal screen"""
    os.system('clear' if os.name != 'nt' else 'cls')

def get_local_ip():
    """Get the local IP address of this machine"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "192.168.1.1"

def get_network_range(local_ip):
    """Get the network range based on local IP"""
    network = ipaddress.IPv4Network(f"{local_ip}/24", strict=False)
    return network

def check_ssh_port(ip, port=22, timeout=1):
    """Check if SSH port is open on the given IP"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((str(ip), port))
        sock.close()
        return result == 0
    except Exception:
        return False

def ping_ip(ip):
    """Ping an IP address to check if it's alive and measure response time"""
    try:
        param = "-n" if platform.system().lower() == "windows" else "-c"
        timeout_param = "-w" if platform.system().lower() == "windows" else "-W"
        
        command = ["ping", param, "1", timeout_param, "1", str(ip)]
        
        # Measure ping time
        start_time = time.time()
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=2,
            text=True
        )
        ping_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        if result.returncode == 0:
            # Try to extract actual ping time from output
            output = result.stdout
            actual_ping_time = None
            
            # Parse ping output for accurate time
            if "time=" in output:
                try:
                    time_str = output.split("time=")[1].split()[0]
                    actual_ping_time = float(time_str.replace("ms", ""))
                except (IndexError, ValueError):
                    actual_ping_time = ping_time
            else:
                actual_ping_time = ping_time
            
            # Get hostname
            try:
                hostname = socket.gethostbyaddr(str(ip))[0]
            except (socket.herror, socket.gaierror):
                hostname = "Unknown"
            
            # Check SSH availability
            has_ssh = check_ssh_port(ip)
            
            return {
                "ip": str(ip), 
                "hostname": hostname, 
                "alive": True, 
                "last_seen": datetime.now(),
                "ping_time": actual_ping_time,
                "ssh_available": has_ssh
            }
    except (subprocess.TimeoutExpired, Exception):
        pass
    
    return None

def get_mac_address(ip):
    """Try to get MAC address from ARP cache"""
    try:
        result = subprocess.run(
            ["arp", "-n", str(ip)],
            capture_output=True,
            text=True,
            timeout=1
        )
        lines = result.stdout.split('\n')
        for line in lines:
            if str(ip) in line:
                parts = line.split()
                if len(parts) >= 3:
                    mac = parts[2]
                    if mac != "(incomplete)" and ":" in mac:
                        return mac
    except Exception:
        pass
    return "N/A"

def scan_network(network, max_workers=50):
    """Scan the network for alive hosts"""
    alive_hosts = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_ip = {executor.submit(ping_ip, ip): ip for ip in network.hosts()}
        
        for future in concurrent.futures.as_completed(future_to_ip):
            result = future.result()
            if result:
                alive_hosts.append(result)
    
    return alive_hosts

def display_live_results(hosts, scan_count, scan_duration, interval):
    """Display scan results in real-time"""
    clear_screen()
    
    print("=" * 108)
    print("🔴 LIVE NETWORK MONITOR - Real-time IP Scanner with SSH Detection")
    print("=" * 108)
    print(f"⏰ Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔄 Scan #{scan_count} | Duration: {scan_duration:.2f}s | Refresh: {interval}s")
    print(f"✅ Alive Hosts: {len(hosts)}")
    
    # Calculate average ping time and SSH count
    if hosts:
        avg_ping = sum(h.get('ping_time', 0) for h in hosts) / len(hosts)
        ssh_count = sum(1 for h in hosts if h.get('ssh_available', False))
        print(f"📊 Average Ping: {avg_ping:.1f}ms | 🔓 SSH Available: {ssh_count}/{len(hosts)}")
    
    print("=" * 108)
    
    if not hosts:
        print("\n❌ No hosts found!")
        print("\n💡 Tip: Make sure devices are powered on and connected to the network.")
    else:
        # Sort by IP address
        hosts.sort(key=lambda x: ipaddress.IPv4Address(x['ip']))
        
        # Print header
        print(f"\n{'#':<4} {'IP Address':<17} {'Hostname':<25} {'MAC Address':<20} {'Ping':<12} {'SSH':<6} {'Status':<10}")
        print("-" * 108)
        
        # Print each host with status indicator
        for idx, host in enumerate(hosts, 1):
            ip = host['ip']
            hostname = host['hostname'][:23] + ".." if len(host['hostname']) > 25 else host['hostname']
            mac = get_mac_address(ip)
            
            # Format ping time
            ping_time = host.get('ping_time', 0)
            if ping_time < 1:
                ping_str = f"{ping_time:.2f}ms"
            elif ping_time < 10:
                ping_str = f"{ping_time:.1f}ms"
            else:
                ping_str = f"{ping_time:.0f}ms"
            
            # Add ping quality indicator
            if ping_time < 10:
                ping_display = f"⚡{ping_str}"
            elif ping_time < 50:
                ping_display = f"✓ {ping_str}"
            elif ping_time < 100:
                ping_display = f"~ {ping_str}"
            else:
                ping_display = f"⚠ {ping_str}"
            
            # Check SSH availability
            ssh_available = host.get('ssh_available', False)
            ssh_indicator = "🔓 Yes" if ssh_available else "🔒 No"
            
            # Get time since last seen
            time_diff = (datetime.now() - host['last_seen']).total_seconds()
            if time_diff < 10:
                status = "🟢 Online"
            elif time_diff < 30:
                status = "🟡 Recent"
            else:
                status = "🔴 Old"
            
            # Check if this is a newly added device
            is_new = host.get('is_new', False)
            
            # ANSI color codes for highlighting
            if is_new:
                # Bright green background with black text for new device
                highlight_start = "\033[42m\033[30m"  # Green background, black text
                highlight_end = "\033[0m"  # Reset
                new_indicator = "🆕 "
            else:
                highlight_start = ""
                highlight_end = ""
                new_indicator = "   "
            
            line = f"{idx:<4} {ip:<17} {hostname:<25} {mac:<20} {ping_display:<12} {ssh_indicator:<6} {status:<10}"
            print(f"{highlight_start}{new_indicator}{line}{highlight_end}")
        
        print("=" * 108)
    
    print("\n💡 Press Ctrl+C to stop monitoring...")

def live_monitor(interval=10):
    """Continuously monitor the network"""
    local_ip = get_local_ip()
    network = get_network_range(local_ip)
    scan_count = 0
    previous_ips = set()
    newly_added_ip = None  # Track the most recently added device
    
    print(f"\n🚀 Starting live network monitor...")
    print(f"📍 Your IP: {local_ip}")
    print(f"🌐 Network: {network}")
    print(f"⏱️  Refresh interval: {interval} seconds\n")
    time.sleep(2)
    
    try:
        while True:
            scan_count += 1
            start_time = time.time()
            
            # Scan the network
            alive_hosts = scan_network(network)
            
            # Detect new devices
            current_ips = {host['ip'] for host in alive_hosts}
            new_devices = current_ips - previous_ips
            
            # Update newly_added_ip: if there's a new device, highlight it
            if new_devices:
                newly_added_ip = list(new_devices)[0]  # Highlight the first new device
            
            # Mark the new device in the hosts data
            for host in alive_hosts:
                host['is_new'] = (host['ip'] == newly_added_ip)
            
            previous_ips = current_ips
            scan_duration = time.time() - start_time
            
            # Display results
            display_live_results(alive_hosts, scan_count, scan_duration, interval)
            
            # Wait before next scan
            time.sleep(interval)
            
    except KeyboardInterrupt:
        clear_screen()
        print("\n" + "=" * 108)
        print("👋 Live monitoring stopped!")
        print("=" * 108)
        print(f"📊 Total scans performed: {scan_count}")
        print(f"⏰ Session ended at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

def main():
    """Main function"""
    import sys
    
    # Get refresh interval from command line argument (default 10 seconds)
    interval = 10
    if len(sys.argv) > 1:
        try:
            interval = int(sys.argv[1])
            if interval < 3:
                print("⚠️  Minimum interval is 3 seconds. Using 3 seconds.")
                interval = 3
        except ValueError:
            print("⚠️  Invalid interval. Using default 10 seconds.")
    
    live_monitor(interval)

if __name__ == "__main__":
    main()
