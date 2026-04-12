#!/bin/bash

# BigRecon Setup Script for Kali Linux & Ubuntu
echo -e "\e[94m[*] Starting BigRecon Setup...\e[0m"

# 1. Install System Dependencies
echo -e "\e[94m[*] Installing system dependencies (Go, Python3, Pip)...\e[0m"
sudo apt update
sudo apt install -y golang python3-pip git

# 2. Install Python dependencies
echo -e "\e[94m[*] Installing Python dependencies...\e[0m"
if [[ -f /etc/kali-community-wallpapers ]]; then
    pip3 install -r requirements.txt --break-system-packages --quiet
else
    pip3 install -r requirements.txt --quiet
fi

# 3. Setup Go Environment
export GOPATH=$HOME/go
export PATH=$PATH:$GOPATH/bin
mkdir -p $GOPATH/bin

# 4. Install Go Tools
install_go_tool() {
    local name=$1
    local repo=$2
    echo -e "\e[94m[*] Installing $name...\e[0m"
    go install -v "$repo"
    
    # Try to find the binary and move it to /usr/local/bin
    local bin_path=$(find $HOME/go/bin -name "$name" -type f | head -n 1)
    if [ -f "$bin_path" ]; then
        sudo cp "$bin_path" /usr/local/bin/
        echo -e "\e[92m[+] $name installed successfully.\e[0m"
    else
        echo -e "\e[91m[!] Could not find $name binary after installation.\e[0m"
    fi
}

install_go_tool "subfinder" "github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest"
install_go_tool "httpx" "github.com/projectdiscovery/httpx/cmd/httpx@latest"
install_go_tool "assetfinder" "github.com/tomnomnom/assetfinder@latest"
install_go_tool "amass" "github.com/owasp-amass/amass/v4/...@master"

# 5. Final Check
echo -e "\e[94m[*] Verifying installations...\e[0m"
for tool in subfinder httpx assetfinder amass; do
    if command -v $tool &> /dev/null; then
        echo -e "\e[92m[+] $tool is ready.\e[0m"
    else
        echo -e "\e[91m[!] $tool is still missing from PATH.\e[0m"
    fi
done

echo -e "\e[92m[+] Setup complete! Try running: python3 bigrecon.py example.com\e[0m"
