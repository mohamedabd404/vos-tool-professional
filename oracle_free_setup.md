# Oracle Cloud Always Free - VOS Tool Setup

## Why Oracle Cloud?
- **Permanent Free**: Never expires (unlike AWS/GCP 12-month trials)
- **Generous Resources**: 2 VMs with 1GB RAM each OR 1 VM with 4GB RAM
- **Full Linux Access**: Can install Chrome/ChromeDriver
- **No Credit Card Required**: After initial verification

## Setup Steps

### 1. Create Oracle Cloud Account
- Go to: https://cloud.oracle.com/free
- Sign up for Always Free account
- Verify with credit card (won't be charged)

### 2. Create Compute Instance
```bash
# Instance Configuration:
- Image: Ubuntu 20.04
- Shape: VM.Standard.E2.1.Micro (Always Free)
- Memory: 1GB RAM, 1 OCPU
- Storage: 47GB Boot Volume (Always Free)
- Network: Assign public IP
```

### 3. Configure Security Rules
```bash
# Add Ingress Rule for port 8501:
- Source CIDR: 0.0.0.0/0
- Destination Port: 8501
- Protocol: TCP
```

### 4. Connect and Install
```bash
# SSH to your instance
ssh ubuntu@YOUR_PUBLIC_IP

# Run VOS Tool setup
wget https://raw.githubusercontent.com/mohamedabd404/vos-tool-professional/main/vps_setup.sh
chmod +x vps_setup.sh
sudo ./vps_setup.sh
```

### 5. Access Your App
- URL: `http://YOUR_PUBLIC_IP:8501`
- **Cost**: $0/month forever
- **Users**: 3-8 concurrent (limited by 1GB RAM)

## Performance Optimization for 1GB RAM

Add this to your app startup:
```bash
# Optimize for low memory
export STREAMLIT_SERVER_MAX_UPLOAD_SIZE=200
export STREAMLIT_SERVER_ENABLE_CORS=false
```

## Limitations
- **RAM**: 1GB (can handle 3-8 users)
- **CPU**: 1 OCPU (slower processing)
- **Bandwidth**: 10TB/month (more than enough)

## Upgrade Path
- Can combine 2 free instances for more resources
- Or upgrade to paid tier later if needed
