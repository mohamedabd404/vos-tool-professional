# Oracle Cloud Always Free - Complete Step-by-Step Guide

## Overview
This guide will help you deploy VOS Tool with full ReadyMode automation on Oracle Cloud's **Always Free tier** ($0/month forever).

**Time Required**: 15-20 minutes  
**Technical Level**: Beginner-friendly  
**Cost**: $0/month permanently

---

## Step 1: Create Oracle Cloud Account

### 1.1 Sign Up
1. Go to: **https://cloud.oracle.com/free**
2. Click **"Start for free"** button
3. Select your **Country/Territory**
4. Enter your email address
5. Click **"Verify my email"**

### 1.2 Email Verification
1. Check your email inbox
2. Click the verification link
3. You'll be redirected back to Oracle Cloud

### 1.3 Account Information
Fill in the form:
- **Account Type**: Select "Individual" (unless you're a company)
- **Cloud Account Name**: Choose a unique name (e.g., `vos-tool-2024`)
- **Home Region**: Choose closest to your location (e.g., `US East (Ashburn)`)
  - ⚠️ **Important**: You cannot change this later!

### 1.4 Personal Information
- Full Name
- Address
- Phone Number (for verification)

### 1.5 Payment Verification
- Add a credit/debit card
- ⚠️ **Note**: This is ONLY for verification - you won't be charged
- Oracle requires this to prevent abuse
- You'll see a small temporary hold (~$1) that will be refunded

### 1.6 Complete Setup
- Agree to terms
- Click **"Start my free trial"**
- Wait for account activation (1-2 minutes)

---

## Step 2: Access Oracle Cloud Console

### 2.1 Sign In
1. Go to: **https://cloud.oracle.com**
2. Click **"Sign in to Cloud"**
3. Enter your **Cloud Account Name** (from Step 1.3)
4. Click **"Next"**
5. Enter your **email** and **password**

### 2.2 Verify Dashboard
- You should see the Oracle Cloud dashboard
- Top right shows your region
- Left menu shows various services

---

## Step 3: Create Your Virtual Machine

### 3.1 Navigate to Compute
1. Click the **☰ (hamburger menu)** in top-left
2. Select **"Compute"**
3. Click **"Instances"**

### 3.2 Create Instance
1. Click **"Create Instance"** (big blue button)

### 3.3 Configure Basic Settings
**Name**: `vos-tool-server` (or any name you prefer)

**Placement**:
- Leave default compartment
- Availability Domain: Leave default

### 3.4 Image and Shape
**Image**:
1. Click **"Change Image"**
2. Select **"Canonical Ubuntu"**
3. Choose **"Canonical Ubuntu 20.04"** or **"22.04"**
4. Click **"Select Image"**

**Shape**:
1. Click **"Change Shape"**
2. Select **"Ampere"** (ARM processor)
3. Choose **"VM.Standard.A1.Flex"** (Always Free eligible)
4. Set:
   - **Number of OCPUs**: 1
   - **Amount of memory (GB)**: 6 (you get up to 6GB free!)
5. Click **"Select Shape"**

> 💡 **Tip**: The A1.Flex gives you MORE than the minimum 1GB RAM!

### 3.5 Networking
**Primary VNIC information**:
- Leave **"Create in compartment"** as default
- **Virtual cloud network**: Create new (if first time) or select existing
- **Subnet**: Select public subnet
- ✅ **Assign a public IPv4 address**: Make sure this is CHECKED

### 3.6 Add SSH Keys
**Very Important for Access!**

**Option A: Generate SSH Key Pair (Recommended for Windows)**
1. Select **"Generate a key pair for me"**
2. Click **"Save Private Key"** - downloads `ssh-key-[date].key`
3. Click **"Save Public Key"** (optional backup)
4. ⚠️ **IMPORTANT**: Save this file safely - you need it to access your server!

**Option B: Use Your Own Key (If you already have one)**
1. Select **"Upload public key files"**
2. Upload your `.pub` file

### 3.7 Boot Volume
- Leave default (47GB - Always Free)
- No need to change anything

### 3.8 Create the Instance
1. Review all settings
2. Click **"Create"** (big blue button at bottom)
3. Wait 1-2 minutes for provisioning
4. Status will change from "Provisioning" → "Running" (orange → green)

---

## Step 4: Configure Network Security

### 4.1 Open Instance Details
1. Click on your instance name (`vos-tool-server`)
2. You'll see instance details page

### 4.2 Find Your Public IP
- Look for **"Public IP address"** in the Instance Information section
- Copy this IP address (e.g., `152.70.xxx.xxx`)
- 📝 **Save this - you'll need it!**

### 4.3 Configure Security Rules
1. Scroll down to **"Primary VNIC"** section
2. Click on the **Subnet** link (e.g., `subnet-xxx`)
3. Click on **"Default Security List for vcn-xxx"**
4. Click **"Add Ingress Rules"**

**Add Rule for Port 8501**:
- **Stateless**: Leave unchecked
- **Source Type**: CIDR
- **Source CIDR**: `0.0.0.0/0` (allows access from anywhere)
- **IP Protocol**: TCP
- **Source Port Range**: Leave blank
- **Destination Port Range**: `8501`
- **Description**: `VOS Tool Access`
- Click **"Add Ingress Rules"**

**Add Rule for Port 80 (Optional - for future HTTPS)**:
- Repeat above but use port `80`
- Description: `HTTP Access`

---

## Step 5: Connect to Your Server

### 5.1 Windows Connection (Using PowerShell)

1. **Move your SSH key**:
   - Move the downloaded `.key` file to a safe location
   - Example: `C:\Users\YourName\.ssh\oracle-key.key`

2. **Set Key Permissions**:
   ```powershell
   # Open PowerShell as Administrator
   # Navigate to your key location
   cd C:\Users\YourName\.ssh
   
   # Set permissions (Windows)
   icacls oracle-key.key /inheritance:r
   icacls oracle-key.key /grant:r "%username%:R"
   ```

3. **Connect via SSH**:
   ```powershell
   ssh -i C:\Users\YourName\.ssh\oracle-key.key ubuntu@YOUR_PUBLIC_IP
   ```
   - Replace `YOUR_PUBLIC_IP` with the IP from Step 4.2
   - Type `yes` when asked to continue connecting
   - You should now be logged into your Ubuntu server!

### 5.2 Alternative: Use PuTTY (Windows)

If SSH command doesn't work:

1. **Download PuTTY**: https://www.putty.org/
2. **Convert Key**:
   - Open **PuTTYgen**
   - Load your `.key` file
   - Click **"Save private key"** (saves as `.ppk`)
3. **Connect**:
   - Open **PuTTY**
   - Host Name: `ubuntu@YOUR_PUBLIC_IP`
   - Port: `22`
   - Go to **Connection → SSH → Auth**
   - Browse and select your `.ppk` file
   - Click **"Open"**

---

## Step 6: Install VOS Tool

### 6.1 Update System
Once connected via SSH, run:

```bash
# Update package list
sudo apt update

# Upgrade packages
sudo apt upgrade -y
```

### 6.2 Download Setup Script
```bash
# Download the automated setup script
wget https://raw.githubusercontent.com/mohamedabd404/vos-tool-professional/main/vps_setup.sh

# Make it executable
chmod +x vps_setup.sh
```

### 6.3 Run Installation
```bash
# Run the setup script
sudo ./vps_setup.sh
```

**What this script does**:
- Installs Python 3 and pip
- Installs Google Chrome and ChromeDriver
- Clones your VOS Tool repository
- Installs all Python dependencies
- Sets up VOS Tool as a system service
- Configures firewall
- Starts the application

**Installation time**: 5-10 minutes

### 6.4 Verify Installation
Once complete, you should see:
```
✅ VOS Tool setup complete!
🌐 Access your app at: http://YOUR_SERVER_IP:8501
🔧 To check status: sudo systemctl status vos-tool
```

---

## Step 7: Configure Ubuntu Firewall

The setup script handles most of this, but let's verify:

```bash
# Check firewall status
sudo ufw status

# If not enabled, enable it
sudo ufw enable

# Allow port 8501 (should already be done by script)
sudo ufw allow 8501

# Allow SSH (important!)
sudo ufw allow 22
```

---

## Step 8: Access Your VOS Tool

### 8.1 Open in Browser
1. Open your web browser
2. Go to: `http://YOUR_PUBLIC_IP:8501`
3. You should see the VOS Tool interface!

### 8.2 Test All Features
1. **Upload & Analyze Tab**: Upload an MP3 file
2. **Agent Audit Tab**: Should show input fields (no error)
3. **Campaign Audit Tab**: Should be accessible

---

## Step 9: Configure ReadyMode Credentials (Optional)

If you want to set environment variables for ReadyMode:

```bash
# SSH to your server
ssh -i your-key.key ubuntu@YOUR_PUBLIC_IP

# Edit the service file
sudo nano /etc/systemd/system/vos-tool.service

# Add environment variables in [Service] section:
# Environment="READYMODE_USER=your_username"
# Environment="READYMODE_PASSWORD=your_password"

# Save (Ctrl+X, Y, Enter)

# Restart service
sudo systemctl daemon-reload
sudo systemctl restart vos-tool
```

---

## Step 10: Share with Your Users

### 10.1 Create User Instructions
Create a simple document for your users:

```
VOS Tool Access Instructions

1. Open your web browser
2. Go to: http://YOUR_PUBLIC_IP:8501
3. You'll see three tabs:
   - Upload & Analyze: For manual MP3 uploads
   - Agent Audit: For automated ReadyMode agent analysis
   - Campaign Audit: For automated ReadyMode campaign analysis

4. All features are now available with full automation!
```

### 10.2 Optional: Set Up Custom Domain

If you have a domain name:
1. Point an A record to your server IP
2. Install nginx and SSL certificate
3. Access via: `https://vos-tool.yourdomain.com`

---

## Troubleshooting

### Issue: Can't Connect via SSH
**Solution**:
- Verify you're using the correct private key
- Check that you saved the key during instance creation
- Verify you're using `ubuntu` as username (not `root`)

### Issue: Can't Access Port 8501
**Solution**:
- Check Oracle Cloud security list has ingress rule for port 8501
- Verify Ubuntu firewall: `sudo ufw status`
- Check service status: `sudo systemctl status vos-tool`

### Issue: Service Not Running
**Solution**:
```bash
# Check logs
sudo journalctl -u vos-tool -n 50

# Restart service
sudo systemctl restart vos-tool

# Check status
sudo systemctl status vos-tool
```

### Issue: Out of Memory
**Solution**:
- Reduce concurrent processing
- Process smaller batches
- Monitor: `free -h`

---

## Maintenance Commands

### Check Service Status
```bash
sudo systemctl status vos-tool
```

### View Logs
```bash
sudo journalctl -u vos-tool -f
```

### Restart Service
```bash
sudo systemctl restart vos-tool
```

### Update VOS Tool
```bash
cd /opt/vos-tool
git pull
sudo systemctl restart vos-tool
```

### Check Disk Space
```bash
df -h
```

### Clean Up Old Recordings
```bash
# Delete old recordings (be careful!)
rm -rf /opt/vos-tool/Recordings/*
```

---

## Next Steps

1. ✅ **Test thoroughly**: Upload files, test ReadyMode integration
2. ✅ **Share with team**: Give them the URL and instructions
3. ✅ **Monitor usage**: Check logs occasionally
4. ✅ **Set up backups**: Important data should be backed up
5. ✅ **Consider domain**: Makes URL easier to remember

---

## Cost Summary

- **Setup**: $0
- **Monthly**: $0 (Always Free tier)
- **Duration**: Forever (as long as Oracle maintains Always Free)
- **Resources**: 1-6GB RAM, 1-2 OCPUs, 47GB storage
- **Users**: 3-10 concurrent users (depending on RAM chosen)

---

## Support

If you encounter issues:
1. Check troubleshooting section above
2. Review installation logs
3. Check Oracle Cloud documentation
4. Verify all security rules are correct

**Congratulations! Your VOS Tool is now deployed with full ReadyMode automation for FREE!** 🎉
