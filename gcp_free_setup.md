# Google Cloud Platform Free Tier - VOS Tool Setup

## Free Tier Benefits
- **$300 Credit**: For first 90 days
- **Always Free**: f1-micro instance (1 vCPU, 0.6GB RAM)
- **After Credits**: Always Free tier continues

## Quick Setup

### 1. Create GCP Account
- Go to: https://cloud.google.com/free
- Get $300 credit (requires credit card)

### 2. Create VM Instance
```bash
# Using gcloud CLI:
gcloud compute instances create vos-tool \
    --zone=us-central1-a \
    --machine-type=f1-micro \
    --image-family=ubuntu-2004-lts \
    --image-project=ubuntu-os-cloud \
    --boot-disk-size=30GB \
    --tags=http-server,https-server

# Allow port 8501
gcloud compute firewall-rules create allow-vos-tool \
    --allow tcp:8501 \
    --source-ranges 0.0.0.0/0 \
    --description "Allow VOS Tool access"
```

### 3. Install VOS Tool
```bash
# SSH to instance
gcloud compute ssh vos-tool --zone=us-central1-a

# Run setup
curl -sSL https://raw.githubusercontent.com/mohamedabd404/vos-tool-professional/main/vps_setup.sh | bash
```

### 4. Access
- Get external IP: `gcloud compute instances describe vos-tool --zone=us-central1-a --format='get(networkInterfaces[0].accessConfigs[0].natIP)'`
- URL: `http://EXTERNAL_IP:8501`

## Cost After Free Credits
- **Always Free**: f1-micro instance = $0/month
- **Limitations**: 0.6GB RAM (2-5 users max)
- **Upgrade**: To e2-micro for $6/month (1GB RAM)
