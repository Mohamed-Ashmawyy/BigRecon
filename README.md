# BigRecon 🚀

**BigRecon** is a high-performance subdomain enumeration and filtering tool designed for security researchers, penetration testers, and bug bounty hunters. It streamlines the reconnaissance process by combining multiple passive discovery sources with fast HTTP probing and detailed data extraction.

## 🌟 Key Features

- **Multi-Source Discovery:** Integrates `subfinder` to pull subdomains from dozens of passive sources simultaneously.
- **Shodan API Integration:** Leverages the power of Shodan's DNS database to uncover hidden subdomains.
- **Advanced Filtering:** Uses `httpx` for rapid probing of live hosts, ensuring you only focus on active targets.
- **Rich Data Extraction:** Automatically retrieves critical information:
  - **Status Codes** (200, 404, 500, etc. )
  - **Content-Length**
  - **IP Addresses**
  - **Web Server Headers** (Apache, Nginx, Cloudflare, etc.)
  - **CNAME Records**
  - **Page Titles**
- **Clean Output:** Generates a structured, easy-to-read text file for further analysis or automation.

## 🛠️ Prerequisites

To use BigRecon, ensure the following tools are installed and available in your system's PATH:

1.  **Python 3.x**
2.  **[subfinder](https://github.com/projectdiscovery/subfinder )**
3.  **[httpx](https://github.com/projectdiscovery/httpx )**

## 🚀 Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Mohamed-Ashmawyy/BigRecon.git
    cd BigRecon
    ```

2.  **Install Python dependencies:**
    ```bash
    pip3 install -r requirements.txt
    ```

## 💻 Usage

Running a basic scan against a target domain:
```bash
python3 bigrecon.py example.com
