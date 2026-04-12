# BigRecon 🚀

**BigRecon** is an advanced and high-performance subdomain enumeration and filtering tool, specifically designed for security researchers, penetration testers, and bug bounty hunters. This tool streamlines the reconnaissance process by integrating multiple passive discovery sources with rapid HTTP probing and detailed data extraction.

## 🌟 Key Features

-   **Multi-Source Discovery:** Integrates `subfinder`, `assetfinder`, and `amass` to gather subdomains from dozens of passive sources simultaneously.
-   **Shodan API Integration:** Leverages the power of Shodan's DNS database to uncover hidden subdomains.
-   **Advanced Filtering:** Utilizes `httpx` for fast probing of live hosts, ensuring you focus only on active targets.
-   **Rich Data Extraction:** Automatically retrieves critical information such as:
    -   **Status Codes:** (200, 404, 500, etc.)
    -   **Content-Length**
    -   **Web Server Headers:** (Apache, Nginx, Cloudflare, etc.)
    -   **CNAME Records**
    -   **Page Titles**
-   **Clean Output:** Generates a structured, easy-to-read text file for further analysis or automation.

## 🛠️ Prerequisites

To fully utilize BigRecon, ensure the following tools are installed and available in your system's PATH:

1.  **Python 3.x**
2.  **[subfinder](https://github.com/projectdiscovery/subfinder)**
3.  **[httpx](https://github.com/projectdiscovery/httpx)**
4.  **[assetfinder](https://github.com/tomnomnom/assetfinder)**
5.  **[amass](https://github.com/owasp-amass/amass)**

## 🚀 Installation & Setup (Recommended for New Users)

To make BigRecon easy to install and use, a `setup.sh` script has been provided. This script will automatically install all necessary dependencies (Go, subfinder, httpx, assetfinder, amass, and Python libraries).

1.  **Clone the repository and navigate to the BigRecon directory:**
    ```bash
    git clone https://github.com/Mohamed-Ashmawyy/BigRecon.git
    cd BigRecon
    ```
2.  **Make the setup script executable and run it:**
    ```bash
    chmod +x setup.sh
    ./setup.sh
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

To use your own Shodan API Key, set it as an environment variable before running the script:

```bash
export SHODAN_API_KEY="YOUR_SHODAN_API_KEY"
python3 bigrecon.py example.com
```

## ✨ Improvements & Review Report

The current version of `bigrecon.py` has been updated to include multiple discovery sources and improved dependency checking. A detailed review report, `Review_Report.md`, is also available in this repository, outlining the observations, improvements, and future recommendations.

---
### *Made by B1g0x411*
### *If you find this repository useful, please star it and send me your feedback on my LinkedIn*
[www.linkedin.com/in/mohamedashmawyy](https://www.linkedin.com/in/mohamedashmawyy)
