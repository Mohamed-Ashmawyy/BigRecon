import os
import sys
import subprocess
import argparse
import json

# ANSI Colors for Terminal
class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

BANNER = f"""{Colors.CYAN}{Colors.BOLD}
   ____  _       ____                            
  | __ )(_) __ _|  _ \ ___  ___ ___  _ __      
  |  _ \| |/ _` | |_) / _ \/ __/ _ \| '_ \     
  | |_) | | (_| |  _ <  __/ (_| (_) | | | |    
  |____/|_|\__, |_| \_\___|\___\___/|_| |_|    
           |___/                                
{Colors.YELLOW}  >> Advanced Subdomain Enumeration & Filtering <<
{Colors.END}"""

SHODAN_API_KEY = "Xk5QmB4c0gcsrh8oUvBjdduNbmM2wmBL"

def run_command(command):
    """Run a shell command and return output"""
    try:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()
        return stdout
    except Exception as e:
        print(f"{Colors.RED}[!] Error running command: {e}{Colors.END}")
        return ""

def get_subdomains_subfinder(domain):
    """Run subfinder for passive enumeration"""
    print(f"{Colors.BLUE}[*] Running Subfinder for {domain}...{Colors.END}")
    output_file = "subs_subfinder.txt"
    run_command(f"subfinder -d {domain} -silent -o {output_file}")
    if os.path.exists(output_file):
        with open(output_file, 'r') as f:
            subs = [line.strip() for line in f if line.strip()]
        os.remove(output_file)
        return set(subs)
    return set()

def get_subdomains_shodan(domain):
    """Fetch subdomains from Shodan API"""
    print(f"{Colors.BLUE}[*] Querying Shodan API for {domain}...{Colors.END}")
    subs = set()
    try:
        import requests
        url = f"https://api.shodan.io/dns/domain/{domain}?key={SHODAN_API_KEY}"
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if 'subdomains' in data:
                for sub in data['subdomains']:
                    subs.add(f"{sub}.{domain}")
        elif response.status_code == 401:
            print(f"{Colors.RED}[!] Shodan API Key is invalid or expired.{Colors.END}")
    except Exception as e:
        print(f"{Colors.RED}[!] Shodan API Error: {e}{Colors.END}")
    return subs

def filter_live_httpx(subdomains_file, output_file):
    """Run httpx for filtering and info extraction"""
    print(f"{Colors.BLUE}[*] Running httpx for filtering & data extraction...{Colors.END}")
    # Extracting: status-code, content-length, ip, server, cname, title
    cmd = f"httpx -l {subdomains_file} -silent -sc -cl -ip -sr -cname -title -o {output_file}"
    run_command(cmd)

def main():
    print(BANNER)
    parser = argparse.ArgumentParser(description="BigRecon - Professional Recon Tool")
    parser.add_argument("domain", help="Target domain (e.g., example.com)")
    parser.add_argument("-o", "--output", default="bigrecon_results.txt", help="Output file (default: bigrecon_results.txt)")
    
    args = parser.parse_args()
    domain = args.domain
    
    # 1. Passive Enumeration
    subs_subfinder = get_subdomains_subfinder(domain)
    subs_shodan = get_subdomains_shodan(domain)
    
    all_subs = subs_subfinder.union(subs_shodan)
    
    if not all_subs:
        print(f"{Colors.RED}[!] No subdomains found for {domain}{Colors.END}")
        return

    print(f"{Colors.GREEN}[+] Total Unique Subdomains Found: {len(all_subs)}{Colors.END}")
    
    # Save all found subs to a temp file for httpx
    temp_subs_file = "temp_all_subs.txt"
    with open(temp_subs_file, 'w') as f:
        for sub in sorted(all_subs):
            f.write(sub + "\n")
    
    # 2. Filtering & Info Extraction
    filter_live_httpx(temp_subs_file, args.output)
    
    # 3. Cleanup and Final Report
    if os.path.exists(temp_subs_file):
        os.remove(temp_subs_file)
        
    if os.path.exists(args.output):
        with open(args.output, 'r') as f:
            lines = f.readlines()
            print(f"{Colors.GREEN}[+] Filtering Completed! Found {len(lines)} live subdomains.{Colors.END}")
            print(f"{Colors.YELLOW}[*] Results saved in: {Colors.BOLD}{args.output}{Colors.END}")
    else:
        print(f"{Colors.RED}[!] No live subdomains found during filtering.{Colors.END}")

if __name__ == "__main__":
    main()
