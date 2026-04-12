#!/bin/bash

# BigRecon Setup Script
# This script installs the necessary dependencies for BigRecon

echo -e "\e[94m[*] Starting BigRecon Setup...\e[0m"

# Check for Python3
if ! command -v python3 &> /dev/null; then
    echo -e "\e[91m[!] Python3 is not installed. Please install it first.\e[0m"
    exit 1
fi

# Install Python dependencies
echo -e "\e[94m[*] Installing Python dependencies...\e[0m"
pip3 install -r requirements.txt

# Install Go (required for subfinder, httpx, assetfinder, and amass)
if ! command -v go &> /dev/null; then
    echo -e "\e[94m[*] Installing Go...\e[0m"
    sudo apt update
    sudo apt install -y golang
fi

# Install subfinder
if ! command -v subfinder &> /dev/null; then
    echo -e "\e[94m[*] Installing subfinder...\e[0m"
    go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
    sudo cp ~/go/bin/subfinder /usr/local/bin/
fi

# Install httpx
if ! command -v httpx &> /dev/null; then
    echo -e "\e[94m[*] Installing httpx...\e[0m"
    go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
    sudo cp ~/go/bin/httpx /usr/local/bin/
fi

# Install assetfinder
if ! command -v assetfinder &> /dev/null; then
    echo -e "\e[94m[*] Installing assetfinder...\e[0m"
    go install -v github.com/tomnomnom/assetfinder@latest
    sudo cp ~/go/bin/assetfinder /usr/local/bin/
fi

# Install amass
if ! command -v amass &> /dev/null; then
    echo -e "\e[94m[*] Installing amass...\e[0m"
    # Amass is often better installed via snap or pre-built binary, but we'll try go install first
    # If go install fails or is slow, we recommend manual install for amass as it's heavy
    go install -v github.com/owasp-amass/amass/v4/...@master
    sudo cp ~/go/bin/amass /usr/local/bin/
fi

echo -e "\e[92m[+] Setup complete! You can now run BigRecon.\e[0m"
echo -e "\e[93mUsage: python3 bigrecon.py example.com\e[0m"
