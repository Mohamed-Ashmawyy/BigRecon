#!/bin/bash

# BigRecon Setup Script for Kali Linux
# Author: B1g0x411 (Updated by Manus)

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}[*] Starting BigRecon Setup...${NC}"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}[!] Please run as root (sudo ./setup.sh)${NC}"
  exit 1
fi

# Update package list
echo -e "${BLUE}[*] Updating package list...${NC}"
apt-get update -y

# Install Go if not installed
if ! command -v go &> /dev/null; then
    echo -e "${BLUE}[*] Installing Go...${NC}"
    apt-get install golang -y
else
    echo -e "${GREEN}[+] Go is already installed.${NC}"
fi

# Install Python3 and Pip if not installed
echo -e "${BLUE}[*] Installing Python3 and Pip...${NC}"
apt-get install python3 python3-pip -y

# Install Core Tools via apt (Kali repos have these)
echo -e "${BLUE}[*] Installing subfinder, assetfinder, amass, and httpx via apt...${NC}"
apt-get install subfinder assetfinder amass httpx-toolkit -y

# Create a symlink for httpx-toolkit to httpx if needed
if command -v httpx-toolkit &> /dev/null && ! command -v httpx &> /dev/null; then
    ln -s /usr/bin/httpx-toolkit /usr/bin/httpx
fi

# Install Python dependencies (if any)
if [ -f "requirements.txt" ]; then
    echo -e "${BLUE}[*] Installing Python dependencies...${NC}"
    pip3 install -r requirements.txt
fi

# Final check
echo -e "${BLUE}[*] Verifying installations...${NC}"
tools=("subfinder" "assetfinder" "amass" "httpx")
for tool in "${tools[@]}"; do
    if command -v "$tool" &> /dev/null; then
        echo -e "${GREEN}[+] $tool is installed.${NC}"
    else
        echo -e "${RED}[!] $tool installation failed or not in PATH.${NC}"
    fi
done

echo -e "${GREEN}[+] Setup complete! You can now run BigRecon.${NC}"
echo -e "${BLUE}[*] Usage: python3 bigrecon.py example.com${NC}"

chmod +x bigrecon.py
