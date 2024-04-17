import subprocess
import sys
target_ips = sys.argv[1:]

def list_rules():
    command = ['sudo', 'iptables', '-t', 'nat', '-L', 'PREROUTING', '--line-numbers']
    result = subprocess.run(command, capture_output=True, text=True)
    return result.stdout

def find_rule(rules, target_ip):
    for line in rules.split('\n'):
        if target_ip in line:
            print(line)
            parts = line.split()
            print(parts)
            if 'to:' in line and 'PREROUTING' in parts:
                print(parts[0])
                line_number = parts[0]
                return line_number
    return None

def delete_rule(line_number):
    command = ['sudo', 'iptables', '-t', 'nat', '-D', 'PREROUTING', line_number]
    result = subprocess.run(command, capture_output=True, text=True)
    return result.stdout

def main():
    for ip in target_ips:
        target_ip = ip
        rules = list_rules()
        line_number = find_rule(rules, target_ip)

        if line_number:
            print(f"Deleting rule with destination {target_ip} at line {line_number}")
            output = delete_rule(line_number)
            print("Rule deleted:", output)
        else:
            print(f"No rule found for destination {target_ip}")

if __name__ == "__main__":
    main()
