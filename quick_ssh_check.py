#!/usr/bin/env python3
"""
Quick SSH checker - Test which devices on network have SSH available
"""

import socket
import subprocess
import concurrent.futures

def check_ssh(ip, port=22, timeout=1):
    """Check if SSH port is open"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, port))
        sock.close()
        return result == 0
    except Exception:
        return False

def get_hostname(ip):
    """Get hostname for IP"""
    try:
        return socket.gethostbyaddr(ip)[0]
    except:
        return "Unknown"

def check_device(ip):
    """Check if device is alive and has SSH"""
    # Quick ping check
    result = subprocess.run(
        ["ping", "-c", "1", "-W", "1", ip],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        timeout=2
    )
    
    if result.returncode == 0:
        has_ssh = check_ssh(ip)
        hostname = get_hostname(ip)
        return {"ip": ip, "hostname": hostname, "ssh": has_ssh}
    return None

def main():
    print("\n" + "="*70)
    print("🔍 Quick SSH Availability Check")
    print("="*70)
    print("Scanning 192.168.1.0/24 network...\n")
    
    # Generate IPs to check
    ips = [f"192.168.1.{i}" for i in range(1, 255)]
    
    devices_with_ssh = []
    devices_without_ssh = []
    
    # Check devices concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        futures = {executor.submit(check_device, ip): ip for ip in ips}
        
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                if result['ssh']:
                    devices_with_ssh.append(result)
                else:
                    devices_without_ssh.append(result)
    
    # Display results
    print("\n" + "="*70)
    print(f"✅ DEVICES WITH SSH AVAILABLE ({len(devices_with_ssh)})")
    print("="*70)
    
    if devices_with_ssh:
        print(f"{'IP Address':<17} {'Hostname':<30} {'SSH':<10}")
        print("-"*70)
        for device in sorted(devices_with_ssh, key=lambda x: x['ip']):
            print(f"{device['ip']:<17} {device['hostname'][:28]:<30} 🔓 Open")
    else:
        print("❌ No devices with SSH found")
    
    print("\n" + "="*70)
    print(f"🔒 DEVICES WITHOUT SSH ({len(devices_without_ssh)})")
    print("="*70)
    
    if devices_without_ssh:
        print(f"{'IP Address':<17} {'Hostname':<30} {'SSH':<10}")
        print("-"*70)
        for device in sorted(devices_without_ssh, key=lambda x: x['ip']):
            print(f"{device['ip']:<17} {device['hostname'][:28]:<30} 🔒 Closed")
    
    print("\n" + "="*70)
    print(f"📊 Summary: {len(devices_with_ssh)} with SSH, {len(devices_without_ssh)} without SSH")
    print("="*70 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Scan interrupted!")
