#!/usr/bin/env python3
"""
Network Scanner - Shows all alive IP addresses on your local network
"""

import socket
import ipaddress
import concurrent.futures
from datetime import datetime
import subprocess
import platform

def get_local_ip():
    """Get the local IP address of this machine"""
    try:
        # Create a socket to find local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "192.168.1.1"

def get_network_range(local_ip):
    """Get the network range based on local IP"""
    # Assume /24 subnet (most common for home networks)
    network = ipaddress.IPv4Network(f"{local_ip}/24", strict=False)
    return network

def ping_ip(ip):
    """Ping an IP address to check if it's alive"""
    try:
        # Use platform-specific ping command
        param = "-n" if platform.system().lower() == "windows" else "-c"
        timeout_param = "-w" if platform.system().lower() == "windows" else "-W"
        
        # Run ping command with 1 packet and 1 second timeout
        command = ["ping", param, "1", timeout_param, "1", str(ip)]
        result = subprocess.run(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=2
        )
        
        if result.returncode == 0:
            # Try to get hostname
            try:
                hostname = socket.gethostbyaddr(str(ip))[0]
            except (socket.herror, socket.gaierror):
                hostname = "Unknown"
            
            return {"ip": str(ip), "hostname": hostname, "alive": True}
    except (subprocess.TimeoutExpired, Exception):
        pass
    
    return None

def get_mac_address(ip):
    """Try to get MAC address from ARP cache (macOS/Linux)"""
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
                    return parts[2]
    except Exception:
        pass
    return "N/A"

def scan_network(network, max_workers=50):
    """Scan the network for alive hosts"""
    alive_hosts = []
    total_ips = network.num_addresses
    
    print(f"🔍 Scanning network: {network}")
    print(f"📊 Total IPs to scan: {total_ips}")
    print(f"⏳ Please wait...\n")
    
    # Use ThreadPoolExecutor for concurrent pinging
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all ping tasks
        future_to_ip = {executor.submit(ping_ip, ip): ip for ip in network.hosts()}
        
        # Collect results as they complete
        completed = 0
        for future in concurrent.futures.as_completed(future_to_ip):
            completed += 1
            result = future.result()
            if result:
                alive_hosts.append(result)
            
            # Show progress
            if completed % 50 == 0:
                print(f"Progress: {completed}/{total_ips} IPs scanned...")
    
    return alive_hosts

def display_results(hosts):
    """Display scan results in a formatted table"""
    print("\n" + "="*80)
    print("🌐 ALIVE HOSTS ON NETWORK")
    print("="*80)
    print(f"⏰ Scan completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"✅ Found {len(hosts)} alive host(s)\n")
    
    if not hosts:
        print("❌ No hosts found!")
        return
    
    # Sort by IP address
    hosts.sort(key=lambda x: ipaddress.IPv4Address(x['ip']))
    
    # Print header
    print(f"{'IP Address':<20} {'Hostname':<30} {'MAC Address':<20}")
    print("-" * 80)
    
    # Print each host
    for host in hosts:
        ip = host['ip']
        hostname = host['hostname'][:28] + ".." if len(host['hostname']) > 30 else host['hostname']
        mac = get_mac_address(ip)
        print(f"{ip:<20} {hostname:<30} {mac:<20}")
    
    print("="*80)

def main():
    """Main function"""
    print("\n" + "="*80)
    print("🔍 NETWORK SCANNER - Python Edition")
    print("="*80 + "\n")
    
    # Get local IP and network range
    local_ip = get_local_ip()
    print(f"📍 Your IP: {local_ip}")
    
    network = get_network_range(local_ip)
    
    # Scan the network
    start_time = datetime.now()
    alive_hosts = scan_network(network)
    end_time = datetime.now()
    
    # Display results
    display_results(alive_hosts)
    
    # Show scan duration
    duration = (end_time - start_time).total_seconds()
    print(f"\n⏱️  Scan duration: {duration:.2f} seconds\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Scan interrupted by user!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
