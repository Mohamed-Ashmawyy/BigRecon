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
  |  _ \| |/ _` | |_) / _ \/ __/ _ \| 
itz_ \     
  | |_) | | (_| |  _ <  __/ (_| (_) | | | |    
  |____/|_|\__, |_| \_\___|\___\___/|_| |_|    
           |___/                                
{color_yellow}  >> Advanced Subdomain Enumeration & Filtering <<
{color_end}""".format(color_cyan=Colors.CYAN, bold=Colors.BOLD, color_yellow=Colors.YELLOW, color_end=Colors.END)

# Shodan API Key - Priority: Environment Variable > Hardcoded (Fallback)
SHODAN_API_KEY = os.getenv("SHODAN_API_KEY", "Xk5QmB4c0gcsrh8oUvBjdduNbmM2wmBL")

def check_dependencies():
    """Check if required external tools are installed."""
    missing = []
    for tool in ["subfinder", "httpx", "assetfinder", "amass"]:
        try:
            # For amass, we check for 'amass enum' as 'amass -version' might not work directly
            if tool == "amass":
                subprocess.run([tool, "enum", "-h"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            else:
                subprocess.run([tool, "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            missing.append(tool)
    
    if missing:
        print(f"{Colors.RED}[!] Missing dependencies: {", ".join(missing)}{Colors.END}")
        print(f"{Colors.YELLOW}[*] Please run 'bash setup.sh' to install them.{Colors.END}")
        return False
    return True

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
    output_file = f"subs_subfinder_{domain}.txt"
    run_command(f"subfinder -d {domain} -silent -o {output_file}")
    subs = set()
    if os.path.exists(output_file):
        with open(output_file, 'r') as f:
            subs = {line.strip() for line in f if line.strip()}
        os.remove(output_file)
    return subs

def get_subdomains_assetfinder(domain):
    print(f"{Colors.BLUE}[*] Running Assetfinder for {domain}...{Colors.END}")
    output = run_command(f"assetfinder --subs-only {domain}")
    return {line.strip() for line in output.splitlines() if line.strip()}

def get_subdomains_amass(domain):
    print(f"{Colors.BLUE}[*] Running Amass for {domain}...{Colors.END}")
    # Amass can be very verbose, so we'll try to get a clean list
    output_file = f"subs_amass_{domain}.txt"
    run_command(f"amass enum -d {domain} -o {output_file}")
    subs = set()
    if os.path.exists(output_file):
        with open(output_file, 'r') as f:
            subs = {line.strip() for line in f if line.strip()}
        os.remove(output_file)
    return subs

def get_subdomains_shodan(domain):
    if not SHODAN_API_KEY:
        print(f"{Colors.YELLOW}[!] Shodan API Key not found. Skipping Shodan...{Colors.END}")
        return set()
        
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
            print(f"{Colors.RED}[!] Shodan API Key is invalid.{Colors.END}")
    except Exception as e:
        print(f"{Colors.RED}[!] Shodan Error: {e}{Colors.END}")
    return subs

def filter_live_httpx(subdomains_file, output_file):
    print(f"{Colors.BLUE}[*] Running httpx for filtering & data extraction...{Colors.END}")
    json_output = f"temp_httpx_{os.getpid()}.json"
    
    # Improved httpx command for maximum results
    cmd = f"httpx -l {subdomains_file} -silent -sc -server -title -json -o {json_output} -follow-redirects -t 50"
    run_command(cmd)
    
    lines_processed = 0
    if os.path.exists(json_output):
        with open(json_output, 'r') as f_in, open(output_file, 'w') as f_out:
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
    if not check_dependencies():
        sys.exit(1)
        
    parser = argparse.ArgumentParser(description="BigRecon - Advanced Subdomain Enumeration & Filtering")
    parser.add_argument("domain", help="Domain to scan (e.g., example.com)")
    parser.add_argument("-o", "--output", help="Output file name (default: domain_results.txt)")
    args = parser.parse_args()
    
    domain = args.domain
    output_file = args.output if args.output else f"{domain}_results.txt"
    
    subfinder_subs = get_subdomains_subfinder(domain)
    assetfinder_subs = get_subdomains_assetfinder(domain)
    amass_subs = get_subdomains_amass(domain)
    shodan_subs = get_subdomains_shodan(domain)
    
    all_subs = subfinder_subs.union(assetfinder_subs, amass_subs, shodan_subs)
    
    if not all_subs:
        print(f"{Colors.RED}[!] No subdomains found.{Colors.END}")
        return

    print(f"{Colors.GREEN}[+] Unique Subdomains Found: {len(all_subs)}{Colors.END}")
    
    temp_file = f"temp_subs_{os.getpid()}.txt"
    with open(temp_file, 'w') as f:
        for sub in sorted(all_subs):
            f.write(sub + "\n")
    
    live_count = filter_live_httpx(temp_file, output_file)
    
    if os.path.exists(temp_file):
        os.remove(temp_file)
        
    if live_count > 0:
        print(f"{Colors.GREEN}[+] Found {live_count} live hosts. Results saved to: {output_file}{Colors.END}")
    else:
        print(f"{Colors.RED}[!] No live hosts found.{Colors.END}")

if __name__ == "__main__":
    main()
