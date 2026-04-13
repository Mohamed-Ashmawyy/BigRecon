# BigRecon 🚀

**BigRecon** is an advanced, high-performance subdomain enumeration and filtering tool built for security researchers, penetration testers, and bug bounty hunters. It integrates multiple passive discovery sources with rapid HTTP probing and detailed data extraction.

---

## 🌟 Features

| Feature | Details |
|---|---|
| **Multi-Source Discovery** | Runs `subfinder`, `assetfinder`, and `amass` in parallel |
| **Shodan Integration** | Queries Shodan DNS API (requires `SHODAN_API_KEY`) |
| **Live-Host Filtering** | Uses `httpx` to probe every subdomain for liveness |
| **Rich Data Extraction** | Captures status code, web server header, and page title |
| **Parallel Execution** | All discovery tools run concurrently via ThreadPoolExecutor |
| **Timeout Protection** | Every external tool call has a configurable timeout |
| **Kali-Friendly** | Auto-detects `httpx-toolkit` as a fallback for `httpx` |
| **Graceful Degradation** | Runs with whatever tools are available; skips missing ones |

---

## 🛠️ Prerequisites

- Python 3.6+
- One or more of the following tools (installed automatically by `setup.sh`):

| Tool | Source |
|---|---|
| [subfinder](https://github.com/projectdiscovery/subfinder) | ProjectDiscovery |
| [assetfinder](https://github.com/tomnomnom/assetfinder) | tomnomnom |
| [amass](https://github.com/owasp-amass/amass) | OWASP |
| [httpx](https://github.com/projectdiscovery/httpx) | ProjectDiscovery |

---

## 🚀 Installation

```bash
git clone https://github.com/Mohamed-Ashmawyy/BigRecon.git
cd BigRecon
chmod +x setup.sh
sudo ./setup.sh
```

> **Note:** `setup.sh` targets Kali Linux / Debian-based systems.  
> On other distros, install the tools manually using their respective Go install commands.

---

## 💻 Usage

### Basic scan
```bash
python3 bigrecon.py example.com
```

### Custom output file
```bash
python3 bigrecon.py example.com -o my_results.txt
```

### Adjust concurrent threads (default: 4)
```bash
python3 bigrecon.py example.com -t 4
```

### Enable Shodan integration
```bash
export SHODAN_API_KEY="YOUR_API_KEY_HERE"
python3 bigrecon.py example.com
```

> ⚠️ Never hard-code your API key in the script. Always use an environment variable.

---

## 📄 Output Format

Results are saved as a structured text file:

```
URL                                                          | STATUS   | SERVER               | TITLE
---------------------------------------------------------------------------------------------------------------------------------------
https://mail.example.com                                     | 200      | nginx/1.18.0         | Webmail Login
https://dev.example.com                                      | 403      | Apache/2.4.51        | 403 Forbidden
```

---

## ⚙️ How It Works

```
Domain Input
     │
     ▼
┌────────────────────────────────────────────┐
│        Parallel Discovery Phase            │
│  subfinder │ assetfinder │ amass │ shodan  │
└────────────────────────────────────────────┘
     │
     ▼
  Deduplicate subdomains
     │
     ▼
┌──────────────────────┐
│   httpx Probing      │  ← status code, server, title
└──────────────────────┘
     │
     ▼
  Structured output file
```

---

## 📜 License

For educational and authorized security testing only. Do not use against systems you do not own or have explicit permission to test.

---

### *Made by B1g0x411*
### *If you find this repository useful, please star it and send me your feedback on my LinkedIn*
[www.linkedin.com/in/mohamedashmawyy](https://www.linkedin.com/in/mohamedashmawyy)
