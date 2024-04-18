import subprocess
import time
import sys

vm_ips = sys.argv[1:]
max_failures = 2
failure_counts = {ip: 0 for ip in vm_ips}

def ping_vm(ip_address):
    try:
        response = subprocess.run(["ping", "-c", "1", ip_address], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if response.returncode == 0:
            return True
        else:
            return False
    except Exception as e:
        print(f"Failed to ping {ip_address}: {e}")
        return False

def list_rules():
    command = ['sudo', 'iptables', '-t', 'nat', '-L', 'PREROUTING', '--line-numbers']
    result = subprocess.run(command, capture_output=True, text=True)
    return result.stdout

def find_rule(rules, target_ip):
    for line in rules.split('\n'):
        if target_ip in line:
            # print(line)
            parts = line.split()
            print(parts)
            if f'to:{target_ip}:80' in parts:
                print(parts[0])
                line_number = parts[0]
                return line_number
    return None

def delete_rule(line_number):
    command = ['sudo', 'iptables', '-t', 'nat', '-D', 'PREROUTING', line_number]
    result = subprocess.run(command, capture_output=True, text=True)
    return result.stdout

def update_rules(target_ips):
    for ip in target_ips:
        target_ip = ip
        rules = list_rules()
        line_number = find_rule(rules, target_ip)
        print(line_number)
        if line_number:
            print(f"Deleting rule with destination {target_ip} at line {line_number}")
            output = delete_rule(line_number)
            print("Rule deleted..")
            vm_ips.remove(target_ip)
            print(f"Updated the Monitoring IPs:{vm_ips}")
        else:
            print(f"No rule found for destination {target_ip}")



def health_check():
    for ip in vm_ips:
        if ping_vm(ip):
            print(f"{ip} is up.")
            failure_counts[ip] = 0
        else:
            failure_counts[ip] += 1
            print(f"{ip} failed to respond to ping.")
            if failure_counts[ip] > max_failures:
                print(f"{ip} is not healthy. Failed to respond {failure_counts[ip]} times.")
                update_rules([ip])
                # exit(0)

while True:
    print(vm_ips)
    health_check()
    time.sleep(1)

# iptables -A PREROUTING -t nat -p tcp -d 10.10.10.6 --dport 8080 -m statistic --mode random --probability 1 -j DNAT --to-destination 10.1.1.5:80
# sudo iptables -A INPUT -p icmp --icmp-type echo-request -j DROP

    
