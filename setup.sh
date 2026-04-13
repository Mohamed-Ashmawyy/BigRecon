#!/bin/bash

# BigRecon Setup Script for Kali Linux / Debian-based systems
# Author: B1g0x411

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}[*] Starting BigRecon Setup...${NC}"

# ── Root check ────────────────────────────────────────────────────────────────
if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}[!] Please run as root: sudo ./setup.sh${NC}"
  exit 1
fi

# ── Update package list ───────────────────────────────────────────────────────
echo -e "${BLUE}[*] Updating package list...${NC}"
apt-get update -y

# ── Go ────────────────────────────────────────────────────────────────────────
if ! command -v go &> /dev/null; then
    echo -e "${BLUE}[*] Installing Go...${NC}"
    apt-get install golang -y
else
    echo -e "${GREEN}[+] Go is already installed: $(go version)${NC}"
fi

# ── Python3 ───────────────────────────────────────────────────────────────────
echo -e "${BLUE}[*] Installing Python3 and pip...${NC}"
apt-get install python3 python3-pip -y

# ── Core recon tools ──────────────────────────────────────────────────────────
echo -e "${BLUE}[*] Installing subfinder, assetfinder, amass, and httpx...${NC}"
apt-get install -y subfinder assetfinder amass httpx-toolkit

# ── httpx symlink ─────────────────────────────────────────────────────────────
# On Kali the binary is called 'httpx-toolkit'; create a 'httpx' symlink so
# other tools and scripts can call it by its canonical name.
if command -v httpx-toolkit &> /dev/null && ! command -v httpx &> /dev/null; then
    echo -e "${BLUE}[*] Creating httpx symlink...${NC}"
    ln -sf "$(command -v httpx-toolkit)" /usr/local/bin/httpx
    echo -e "${GREEN}[+] Symlink created: httpx -> httpx-toolkit${NC}"
fi

# ── Python dependencies ───────────────────────────────────────────────────────
if [ -f "requirements.txt" ]; then
    echo -e "${BLUE}[*] Installing Python dependencies...${NC}"
    pip3 install -r requirements.txt --break-system-packages 2>/dev/null || \
    pip3 install -r requirements.txt
fi

# ── Make script executable ────────────────────────────────────────────────────
chmod +x bigrecon.py

# ── Verify installations ──────────────────────────────────────────────────────
echo ""
echo -e "${BLUE}[*] Verifying installations...${NC}"
ALL_OK=true
for tool in subfinder assetfinder amass httpx; do
    if command -v "$tool" &> /dev/null; then
        echo -e "${GREEN}[+] $tool ... OK${NC}"
    else
        echo -e "${RED}[!] $tool ... NOT FOUND (installation may have failed)${NC}"
        ALL_OK=false
    fi
done

echo ""
if $ALL_OK; then
    echo -e "${GREEN}[+] Setup complete! All tools are ready.${NC}"
else
    echo -e "${YELLOW}[!] Setup finished with warnings. Some tools are missing.${NC}"
    echo -e "${YELLOW}    BigRecon will still run using whatever tools are available.${NC}"
fi

echo -e "${BLUE}[*] Usage: python3 bigrecon.py <domain>${NC}"
echo -e "${BLUE}[*] Example: python3 bigrecon.py example.com${NC}"
