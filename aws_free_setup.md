# AWS Free Tier - VOS Tool Setup

## Free Tier Benefits
- **12 Months Free**: t2.micro instance
- **750 Hours/Month**: Enough for 24/7 operation
- **1GB RAM**: Better than GCP free tier

## Setup Steps

### 1. Create AWS Account
- Go to: https://aws.amazon.com/free
- Sign up (requires credit card)

### 2. Launch EC2 Instance
```bash
# Instance Configuration:
- AMI: Ubuntu Server 20.04 LTS
- Instance Type: t2.micro (Free tier eligible)
- Storage: 30GB gp2 (Free tier: up to 30GB)
- Security Group: Allow SSH (22) and Custom TCP (8501)
```

### 3. Connect and Setup
```bash
# SSH to instance
ssh -i your-key.pem ubuntu@your-instance-ip

# Install VOS Tool
wget https://raw.githubusercontent.com/mohamedabd404/vos-tool-professional/main/vps_setup.sh
chmod +x vps_setup.sh
sudo ./vps_setup.sh
```

### 4. Access
- URL: `http://YOUR_EC2_IP:8501`
- **Free Duration**: 12 months
- **After Free Tier**: ~$8-12/month

## Security Group Rules
```
Type: Custom TCP
Port: 8501
Source: 0.0.0.0/0
Description: VOS Tool Access
```
