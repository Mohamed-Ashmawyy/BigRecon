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
  |  _ \| |/ _` | |_) / _ \/ __/ _ \| '_ \    
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

# Default timeout (seconds) for each external tool
TOOL_TIMEOUT = 300


def check_tool(tool):
    """Check if a tool is installed and available in PATH using shutil.which."""
    # On Kali, httpx may be installed as 'httpx-toolkit'
    if tool == "httpx" and shutil.which("httpx") is None:
        return shutil.which("httpx-toolkit") is not None
    return shutil.which(tool) is not None


def get_httpx_binary():
    """Return the correct httpx binary name available on this system."""
    if shutil.which("httpx"):
        return "httpx"
    if shutil.which("httpx-toolkit"):
        return "httpx-toolkit"
    return None


def run_command(command, timeout=TOOL_TIMEOUT):
    """Executes a shell command and returns its output."""
    try:
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        try:
            stdout, stderr = process.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            process.kill()
            process.communicate()
            logger.warning(
                f"{Colors.YELLOW}[!] Command timed out after {timeout}s: "
                f"{command[:60]}...{Colors.END}"
            )
            return ""

        if process.returncode != 0 and stderr:
            logger.debug(f"Command stderr: {stderr.strip()}")
        return stdout
    except Exception as e:
        logger.error(f"{Colors.RED}[!] Error executing command: {e}{Colors.END}")
        return ""


def get_subdomains_subfinder(domain):
    if not check_tool("subfinder"):
        logger.warning(f"{Colors.YELLOW}[!] subfinder not found. Skipping...{Colors.END}")
        return set()
    logger.info(f"{Colors.BLUE}[*] Running subfinder for {domain}...{Colors.END}")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
        output_file = tmp.name

    try:
        run_command(f"subfinder -d {domain} -silent -o {output_file}")
        subs = set()
        if os.path.exists(output_file):
            with open(output_file, 'r') as f:
                subs = {line.strip() for line in f if line.strip()}
        return subs
    finally:
        if os.path.exists(output_file):
            os.remove(output_file)


def get_subdomains_assetfinder(domain):
    if not check_tool("assetfinder"):
        logger.warning(f"{Colors.YELLOW}[!] assetfinder not found. Skipping...{Colors.END}")
        return set()
    logger.info(f"{Colors.BLUE}[*] Running assetfinder for {domain}...{Colors.END}")
    output = run_command(f"assetfinder --subs-only {domain}")
    return {line.strip() for line in output.splitlines() if line.strip()}


def get_subdomains_crtsh(domain):
    """Query crt.sh (Certificate Transparency logs) - no external tool needed."""
    logger.info(f"{Colors.BLUE}[*] Querying crt.sh for {domain}...{Colors.END}")
    subs = set()
    try:
        import urllib.request
        import urllib.parse
        url = f"https://crt.sh/?q=%25.{urllib.parse.quote(domain)}&output=json"
        req = urllib.request.Request(url, headers={"User-Agent": "BigRecon/1.0"})
        with urllib.request.urlopen(req, timeout=20) as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                for entry in data:
                    name = entry.get("name_value", "")
                    # crt.sh can return multiple names separated by newlines
                    for sub in name.splitlines():
                        sub = sub.strip().lower()
                        # Skip wildcards and entries not belonging to the domain
                        if sub and not sub.startswith("*") and sub.endswith(domain):
                            subs.add(sub)
    except Exception as e:
        logger.warning(f"{Colors.YELLOW}[!] crt.sh error: {e}{Colors.END}")
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
                for sub in data.get('subdomains', []):
                    if sub:
                        subs.add(f"{sub}.{domain}")
    except Exception as e:
        logger.warning(f"{Colors.YELLOW}[!] Shodan API error: {e}{Colors.END}")
    return subs


def filter_live_httpx(subdomains_file, output_file):
    httpx_bin = get_httpx_binary()
    if not httpx_bin:
        logger.error(
            f"{Colors.RED}[!] httpx not found. "
            f"Saving all subdomains without live-host filtering.{Colors.END}"
        )
        shutil.copy(subdomains_file, output_file)
        return 0

    logger.info(f"{Colors.BLUE}[*] Running {httpx_bin} to probe live hosts...{Colors.END}")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp:
        json_output = tmp.name

    try:
        cmd = (
            f"{httpx_bin} -l {subdomains_file} -silent -sc -server -title "
            f"-json -o {json_output} -follow-redirects -t 50"
        )
        run_command(cmd, timeout=600)

        lines_processed = 0
        if os.path.exists(json_output) and os.path.getsize(json_output) > 0:
            with open(json_output, 'r') as f_in, open(output_file, 'w') as f_out:
                header = f"{'URL':<60} | {'STATUS':<8} | {'SERVER':<20} | {'TITLE'}\n"
                f_out.write(header)
                f_out.write("-" * 135 + "\n")

                for line in f_in:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)

                        url = data.get('url', 'N/A')
                        # Support both newer (status_code) and older (status-code) httpx output
                        status = str(
                            data.get('status_code') or
                            data.get('status-code') or
                            'N/A'
                        )
                        # Support both newer (webserver) and older (server) httpx output
                        server = (
                            data.get('webserver') or
                            data.get('server') or
                            'N/A'
                        )
                        title = (data.get('title') or 'N/A').replace('\n', ' ').strip()

                        url = url.rstrip('/')

                        f_out.write(f"{url:<60} | {status:<8} | {server:<20} | {title}\n")
                        lines_processed += 1
                    except json.JSONDecodeError:
                        continue
        else:
            logger.warning(
                f"{Colors.YELLOW}[!] httpx produced no output. "
                f"Saving raw subdomain list.{Colors.END}"
            )
            shutil.copy(subdomains_file, output_file)

        return lines_processed
    finally:
        if os.path.exists(json_output):
            os.remove(json_output)


def main():
    print(BANNER)

    parser = argparse.ArgumentParser(
        description="BigRecon - Advanced Subdomain Enumeration & Filtering"
    )
    parser.add_argument("domain", help="Target domain (e.g., example.com)")
    parser.add_argument(
        "-o", "--output",
        help="Output file name (default: <domain>_results.txt)"
    )
    parser.add_argument(
        "-t", "--threads",
        type=int,
        default=4,
        help="Number of concurrent discovery threads (default: 4)"
    )
    args = parser.parse_args()

    domain = args.domain.strip().lower()
    output_file = args.output if args.output else f"{domain}_results.txt"

    # Validate that at least one discovery source is available
    # crt.sh is always available (pure HTTP), so we only warn if external tools are missing
    tools_available = any([
        check_tool("subfinder"),
        check_tool("assetfinder"),
        True,  # crt.sh is always available
    ])
    if not tools_available and not SHODAN_API_KEY:
        logger.error(
            f"{Colors.RED}[!] No discovery tools found and SHODAN_API_KEY is not set.{Colors.END}"
        )
        logger.info(
            f"{Colors.YELLOW}[*] Run 'sudo ./setup.sh' to install required tools.{Colors.END}"
        )
        sys.exit(1)

    logger.info(f"{Colors.CYAN}[*] Target : {domain}{Colors.END}")
    logger.info(f"{Colors.CYAN}[*] Output : {output_file}{Colors.END}")

    # Run all discovery functions in parallel
    discovery_funcs = [
        get_subdomains_subfinder,
        get_subdomains_assetfinder,
        get_subdomains_crtsh,
        get_subdomains_shodan,
    ]

    # Cap threads to number of functions to avoid idle workers
    max_workers = min(args.threads, len(discovery_funcs))
    all_subs = set()

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(func, domain): func.__name__ for func in discovery_funcs}
        for future in as_completed(futures):
            func_name = futures[future]
            try:
                result = future.result()
                if result:
                    logger.info(
                        f"{Colors.GREEN}[+] {func_name}: {len(result)} subdomains found{Colors.END}"
                    )
                all_subs.update(result)
            except Exception as e:
                logger.error(f"{Colors.RED}[!] Error in {func_name}: {e}{Colors.END}")

    if not all_subs:
        logger.error(f"{Colors.RED}[!] No subdomains found. Exiting.{Colors.END}")
        return

    logger.info(f"{Colors.GREEN}[+] Total unique subdomains: {len(all_subs)}{Colors.END}")

    # Write deduplicated subdomains to a temp file for httpx
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=".txt") as tmp:
        temp_file = tmp.name
        for sub in sorted(all_subs):
            tmp.write(sub + "\n")

    try:
        live_count = filter_live_httpx(temp_file, output_file)

        if live_count > 0:
            logger.info(
                f"{Colors.GREEN}[+] {live_count} live hosts found. "
                f"Results saved to: {output_file}{Colors.END}"
            )
        else:
            if get_httpx_binary():
                logger.warning(f"{Colors.YELLOW}[!] No live hosts responded.{Colors.END}")
            logger.info(
                f"{Colors.YELLOW}[*] Raw subdomains saved to: {output_file}{Colors.END}"
            )
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)


if __name__ == "__main__":
    main()
