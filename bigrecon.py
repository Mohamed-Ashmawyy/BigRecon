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

BANNER = r"""{color_cyan}{bold}
   ____  _       ____                            
  | __ )(_) __ _|  _ \ ___  ___ ___  _ __      
  |  _ \| |/ _` | |_) / _ \/ __/ _ \| '_ \     
  | |_) | | (_| |  _ <  __/ (_| (_) | | | |    
  |____/|_|\__, |_| \_\___|\___\___/|_| |_|    
           |___/                                
{color_yellow}  >> Advanced Subdomain Enumeration & Filtering <<
{color_end}""".format(color_cyan=Colors.CYAN, bold=Colors.BOLD, color_yellow=Colors.YELLOW, color_end=Colors.END)

SHODAN_API_KEY = "Xk5QmB4c0gcsrh8oUvBjdduNbmM2wmBL"

def run_command(command):
    try:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()
        return stdout
    except Exception as e:
        print(f"{Colors.RED}[!] Error: {e}{Colors.END}")
        return ""

def get_subdomains_subfinder(domain):
    print(f"{Colors.BLUE}[*] Running Subfinder for {domain}...{Colors.END}")
    output_file = "subs_subfinder.txt"
    run_command(f"subfinder -d {domain} -silent -o {output_file}")
    subs = set()
    if os.path.exists(output_file):
        with open(output_file, 'r') as f:
            subs = {line.strip() for line in f if line.strip()}
        os.remove(output_file)
    return subs

def get_subdomains_shodan(domain):
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
    except:
        pass
    return subs

def filter_live_httpx(subdomains_file, output_file):
    print(f"{Colors.BLUE}[*] Running httpx for filtering & data extraction...{Colors.END}")
    json_output = "temp_httpx_results.json"
    
    # Improved httpx command for maximum results:
    # -sc: status-code
    # -server: server header
    # -title: page title
    # -json: output in JSON format for reliable parsing
    # -follow-redirects: get final status/title
    # -t 50: concurrency for speed
    cmd = f"httpx -l {subdomains_file} -silent -sc -server -title -json -o {json_output} -follow-redirects -t 50"
    run_command(cmd)
    
    lines_processed = 0
    if os.path.exists(json_output):
        with open(json_output, 'r') as f_in, open(output_file, 'w') as f_out:
            # Table Header (IP removed for better clarity as requested)
            header = f"{'URL':<60} | {'STATUS':<8} | {'SERVER':<20} | {'TITLE'}\n"
            f_out.write(header)
            f_out.write("-" * 135 + "\n")
            
            for line in f_in:
                try:
                    data = json.loads(line)
                    url = data.get('url', 'N/A')
                    status = str(data.get('status_code', data.get('status-code', 'N/A')))
                    server = data.get('webserver', data.get('server', 'N/A'))
                    title = data.get('title', 'N/A').replace('\n', ' ').strip()
                    
                    if url.endswith('/'):
                        url = url[:-1]
                        
                    f_out.write(f"{url:<60} | {status:<8} | {server:<20} | {title}\n")
                    lines_processed += 1
                except:
                    continue
        os.remove(json_output)
    return lines_processed

def main():
    print(BANNER)
    parser = argparse.ArgumentParser(description="BigRecon - Advanced Subdomain Enumeration & Filtering")
    parser.add_argument("domain", help="Domain to scan (e.g., example.com)")
    parser.add_argument("-o", "--output", default="bigrecon_results.txt", help="Output file name")
    args = parser.parse_args()
    
    subfinder_subs = get_subdomains_subfinder(args.domain)
    shodan_subs = get_subdomains_shodan(args.domain)
    all_subs = subfinder_subs.union(shodan_subs)
    
    if not all_subs:
        print(f"{Colors.RED}[!] No subdomains found.{Colors.END}")
        return

    print(f"{Colors.GREEN}[+] Unique Subdomains: {len(all_subs)}{Colors.END}")
    
    temp_file = "temp_subs.txt"
    with open(temp_file, 'w') as f:
        for sub in sorted(all_subs):
            f.write(sub + "\n")
    
    live_count = filter_live_httpx(temp_file, args.output)
    
    if os.path.exists(temp_file):
        os.remove(temp_file)
        
    if live_count > 0:
        print(f"{Colors.GREEN}[+] Found {live_count} live hosts. Results: {args.output}{Colors.END}")
    else:
        print(f"{Colors.RED}[!] No live hosts found.{Colors.END}")

if __name__ == "__main__":
    main()
