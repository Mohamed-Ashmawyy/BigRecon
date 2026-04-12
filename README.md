# BigRecon 🚀

**BigRecon** is an advanced and high-performance subdomain enumeration and filtering tool, specifically designed for security researchers, penetration testers, and bug bounty hunters. This updated version streamlines the reconnaissance process by integrating multiple passive discovery sources with rapid HTTP probing and detailed data extraction, with improved security, performance, and ease of use.

## 🌟 Key Features

-   **Multi-Source Discovery:** Integrates `subfinder`, `assetfinder`, and `amass` to gather subdomains from dozens of passive sources simultaneously.
-   **Shodan API Integration:** Leverages the power of Shodan's DNS database to uncover hidden subdomains. (Requires `SHODAN_API_KEY` environment variable).
-   **Advanced Filtering:** Utilizes `httpx` for fast probing of live hosts, ensuring you focus only on active targets.
-   **Rich Data Extraction:** Automatically retrieves critical information such as:
    -   **Status Codes:** (200, 404, 500, etc.)
    -   **Web Server Headers:** (Apache, Nginx, Cloudflare, etc.)
    -   **Page Titles**
-   **Parallel Execution:** Subdomain discovery tools now run in parallel for faster results.
-   **Improved Error Handling:** More informative messages for missing tools or API issues.
-   **Clean Output:** Generates a structured, easy-to-read text file for further analysis or automation.

## 🛠️ Prerequisites

To fully utilize BigRecon, ensure the following tools are installed and available in your system's PATH. The `setup.sh` script will handle most of these for you:

1.  **Python 3.x**
2.  **Go Language** (for installing some tools)
3.  **[subfinder](https://github.com/projectdiscovery/subfinder)**
4.  **[httpx](https://github.com/projectdiscovery/httpx)**
5.  **[assetfinder](https://github.com/tomnomnom/assetfinder)**
6.  **[amass](https://github.com/owasp-amass/amass)**

## 🚀 Installation & Setup (Recommended)

To make BigRecon easy to install and use, a `setup.sh` script has been provided. This script will automatically install all necessary dependencies (Go, subfinder, httpx, assetfinder, amass, and Python libraries) on Kali Linux.

1.  **Clone the repository and navigate to the BigRecon directory:**
    ```bash
    git clone https://github.com/Mohamed-Ashmawyy/BigRecon.git
    cd BigRecon
    ```
2.  **Make the setup script executable and run it as root:**
    ```bash
    chmod +x setup.sh
    sudo ./setup.sh
    ```

## 💻 Usage

To run a basic scan against a target domain:

```bash
python3 bigrecon.py example.com
```

To specify a custom output file:

```bash
python3 bigrecon.py example.com -o results.txt
```

To use your own Shodan API Key, set it as an environment variable before running the script. **It is highly recommended to use an environment variable instead of hardcoding your API key.**

1.  **Obtain your Shodan API Key** from [Shodan](https://www.shodan.io/)
2.  **Set the environment variable:**
    ```bash
    export SHODAN_API_KEY="YOUR_SHODAN_API_KEY"
    ```
3.  **Run BigRecon:**
    ```bash
    python3 bigrecon.py example.com
    ```

To specify the number of concurrent threads for discovery (default is 4):

```bash
python3 bigrecon.py example.com -t 8
```

## 📝 Review Report

A detailed review report, `Review_Report.md`, is available in this repository, outlining the observations, improvements, and future recommendations for BigRecon.

---
### *Made by B1g0x411*
### *If you find this repository useful, please star it and send me your feedback on my LinkedIn*
[www.linkedin.com/in/mohamedashmawyy](https://www.linkedin.com/in/mohamedashmawyy)
