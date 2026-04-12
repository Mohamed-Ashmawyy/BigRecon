import os
import sys
import subprocess
import argparse
import json
import logging
import tempfile
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed

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
  |  _ \| |/ _` | |_) / _ \/ __/ _ \| itz_ \     
  | |_) | | (_| |  _ <  __/ (_| (_) | | | |    
  |____/|_|\__, |_| \_\___|\___\___/|_| |_|    
           |___/                                
{color_yellow}  >> Advanced Subdomain Enumeration & Filtering <<
{color_end}""".format(color_cyan=Colors.CYAN, bold=Colors.BOLD, color_yellow=Colors.YELLOW, color_end=Colors.END)

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# Shodan API Key - Priority: Environment Variable
SHODAN_API_KEY = os.getenv("SHODAN_API_KEY")

def check_tool(tool):
    """Check if a tool is installed and available in PATH."""
    try:
        if tool == "amass":
            subprocess.run([tool, "enum", "-h"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        else:
            subprocess.run([tool, "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        return True
    except FileNotFoundError:
        return False

def run_command(command):
    """Executes a shell command and returns its output."""
    try:
        # Using list for subprocess to avoid shell=True security risks where possible
        # However, for complex piped commands, we might still need shell=True
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()
        if process.returncode != 0 and stderr:
            logger.debug(f"Command error: {stderr.strip()}")
        return stdout
    except Exception as e:
        logger.error(f"{Colors.RED}[!] Error executing command: {e}{Colors.END}")
        return ""

def get_subdomains_subfinder(domain):
    if not check_tool("subfinder"):
        logger.warning(f"{Colors.YELLOW}[!] Subfinder not found. Skipping...{Colors.END}")
        return set()
    logger.info(f"{Colors.BLUE}[*] Running Subfinder for {domain}...{Colors.END}")
    
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        output_file = tmp.name
    
    run_command(f"subfinder -d {domain} -silent -o {output_file}")
    
    subs = set()
    if os.path.exists(output_file):
        with open(output_file, 'r') as f:
            subs = {line.strip() for line in f if line.strip()}
        os.remove(output_file)
    return subs

def get_subdomains_assetfinder(domain):
    if not check_tool("assetfinder"):
        logger.warning(f"{Colors.YELLOW}[!] Assetfinder not found. Skipping...{Colors.END}")
        return set()
    logger.info(f"{Colors.BLUE}[*] Running Assetfinder for {domain}...{Colors.END}")
    output = run_command(f"assetfinder --subs-only {domain}")
    return {line.strip() for line in output.splitlines() if line.strip()}

def get_subdomains_amass(domain):
    if not check_tool("amass"):
        logger.warning(f"{Colors.YELLOW}[!] Amass not found. Skipping...{Colors.END}")
        return set()
    logger.info(f"{Colors.BLUE}[*] Running Amass for {domain}...{Colors.END}")
    
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        output_file = tmp.name
        
    run_command(f"amass enum -passive -d {domain} -o {output_file}")
    
    subs = set()
    if os.path.exists(output_file):
        with open(output_file, 'r') as f:
            subs = {line.strip() for line in f if line.strip()}
        os.remove(output_file)
    return subs

def get_subdomains_shodan(domain):
    if not SHODAN_API_KEY:
        logger.warning(f"{Colors.YELLOW}[!] SHODAN_API_KEY not set. Skipping Shodan...{Colors.END}")
        return set()
        
    logger.info(f"{Colors.BLUE}[*] Querying Shodan API for {domain}...{Colors.END}")
    subs = set()
    try:
        import urllib.request
        url = f"https://api.shodan.io/dns/domain/{domain}?key={SHODAN_API_KEY}"
        with urllib.request.urlopen(url, timeout=15) as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                if 'subdomains' in data:
                    for sub in data['subdomains']:
                        subs.add(f"{sub}.{domain}")
    except Exception as e:
        logger.debug(f"Shodan API error: {e}")
    return subs

def filter_live_httpx(subdomains_file, output_file):
    if not check_tool("httpx"):
        logger.error(f"{Colors.RED}[!] httpx not found. Cannot filter live hosts.{Colors.END}")
        logger.info(f"{Colors.YELLOW}[*] All found subdomains saved to: {output_file}{Colors.END}")
        shutil.copy(subdomains_file, output_file)
        return 0
        
    logger.info(f"{Colors.BLUE}[*] Running httpx for filtering & data extraction...{Colors.END}")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp:
        json_output = tmp.name
    
    cmd = f"httpx -l {subdomains_file} -silent -sc -server -title -json -o {json_output} -follow-redirects -t 50"
    run_command(cmd)
    
    lines_processed = 0
    if os.path.exists(json_output):
        try:
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
                    except json.JSONDecodeError:
                        continue
        finally:
            if os.path.exists(json_output):
                os.remove(json_output)
    return lines_processed

def main():
    print(BANNER)
    
    parser = argparse.ArgumentParser(description="BigRecon - Advanced Subdomain Enumeration & Filtering")
    parser.add_argument("domain", help="Domain to scan (e.g., example.com)")
    parser.add_argument("-o", "--output", help="Output file name (default: domain_results.txt)")
    parser.add_argument("-t", "--threads", type=int, default=4, help="Number of concurrent discovery tools (default: 4)")
    args = parser.parse_args()
    
    domain = args.domain
    output_file = args.output if args.output else f"{domain}_results.txt"
    
    # Check for core tools
    if not any([check_tool("subfinder"), check_tool("assetfinder"), check_tool("amass")]) and not SHODAN_API_KEY:
        logger.error(f"{Colors.RED}[!] No discovery tools found and no Shodan API key provided.{Colors.END}")
        logger.info(f"{Colors.YELLOW}[*] Please run 'sudo ./setup.sh' to install dependencies.{Colors.END}")
        sys.exit(1)
    
    # Parallel Discovery
    discovery_funcs = [
        get_subdomains_subfinder,
        get_subdomains_assetfinder,
        get_subdomains_amass,
        get_subdomains_shodan
    ]
    
    all_subs = set()
    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        futures = {executor.submit(func, domain): func.__name__ for func in discovery_funcs}
        for future in as_completed(futures):
            try:
                result = future.result()
                all_subs.update(result)
            except Exception as e:
                logger.error(f"{Colors.RED}[!] Error in {futures[future]}: {e}{Colors.END}")
    
    if not all_subs:
        logger.error(f"{Colors.RED}[!] No subdomains found.{Colors.END}")
        return

    logger.info(f"{Colors.GREEN}[+] Unique Subdomains Found: {len(all_subs)}{Colors.END}")
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
        temp_file = tmp.name
        for sub in sorted(all_subs):
            tmp.write(sub + "\n")
    
    try:
        live_count = filter_live_httpx(temp_file, output_file)
        
        if live_count > 0:
            logger.info(f"{Colors.GREEN}[+] Found {live_count} live hosts. Results saved to: {output_file}{Colors.END}")
        elif check_tool("httpx"):
            logger.warning(f"{Colors.RED}[!] No live hosts found.{Colors.END}")
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)

if __name__ == "__main__":
    main()
