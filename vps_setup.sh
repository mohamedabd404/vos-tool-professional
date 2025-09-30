#!/bin/bash
# VOS Tool VPS Setup Script
# Run this on Ubuntu 20.04+ server

echo "🚀 Setting up VOS Tool with full ReadyMode automation..."

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip python3-venv -y

# Install Chrome and ChromeDriver
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt update
sudo apt install google-chrome-stable -y

# Install ChromeDriver
CHROME_DRIVER_VERSION=$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE)
wget -N http://chromedriver.storage.googleapis.com/$CHROME_DRIVER_VERSION/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
sudo mv chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver
rm chromedriver_linux64.zip

# Create app directory
mkdir -p /opt/vos-tool
cd /opt/vos-tool

# Clone your repository
git clone https://github.com/mohamedabd404/vos-tool-professional.git .

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Create systemd service
sudo tee /etc/systemd/system/vos-tool.service > /dev/null <<EOF
[Unit]
Description=VOS Tool - Professional Call Auditor
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/vos-tool
Environment=PATH=/opt/vos-tool/venv/bin
ExecStart=/opt/vos-tool/venv/bin/streamlit run app.py --server.port 8501 --server.address 0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable vos-tool
sudo systemctl start vos-tool

# Setup firewall
sudo ufw allow 8501
sudo ufw --force enable

echo "✅ VOS Tool setup complete!"
echo "🌐 Access your app at: http://YOUR_SERVER_IP:8501"
echo "🔧 To check status: sudo systemctl status vos-tool"
