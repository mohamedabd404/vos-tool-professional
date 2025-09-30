# Expose Your Local VOS Tool to Internet

## ⚠️ Important Notes
- This makes your PC accessible from the internet
- Only do this if you understand the security implications
- Your PC must stay on for users to access the tool
- Your IP address may change (unless you have static IP)

---

## Option A: Using ngrok (Easiest, Recommended)

### What is ngrok?
ngrok creates a secure tunnel from the internet to your local PC.

### Setup Steps:

#### 1. Download ngrok
- Go to: https://ngrok.com/download
- Download for Windows
- Extract the zip file

#### 2. Sign Up (Free)
- Create account at: https://dashboard.ngrok.com/signup
- Get your authtoken from dashboard

#### 3. Configure ngrok
```powershell
# Open PowerShell in ngrok folder
cd C:\path\to\ngrok

# Add your authtoken (from ngrok dashboard)
.\ngrok config add-authtoken YOUR_AUTH_TOKEN
```

#### 4. Start VOS Tool
```powershell
# In your VOS Tool directory
cd "C:\Users\almisria\Desktop\Final tools\VOS TOOL - final"

# Start Streamlit
streamlit run app.py
```

#### 5. Start ngrok Tunnel
```powershell
# In another PowerShell window, in ngrok folder
.\ngrok http 8501
```

#### 6. Get Your Public URL
- ngrok will show you a URL like: `https://abc123.ngrok-free.app`
- Share this URL with your users
- They can access from anywhere!

### Free Tier Limits:
- ✅ 1 online tunnel
- ✅ 40 connections/minute
- ✅ HTTPS enabled
- ❌ URL changes each time you restart ngrok
- ❌ Session timeout after 2 hours (need to restart)

### Paid ngrok ($8/month):
- ✅ Custom domain (permanent URL)
- ✅ No session timeout
- ✅ More connections

---

## Option B: Port Forwarding (Free but Complex)

### Requirements:
- Access to your router admin panel
- Static IP or Dynamic DNS service

### Steps:

#### 1. Find Your Local IP
```powershell
ipconfig
# Look for "IPv4 Address" (e.g., 192.168.1.100)
```

#### 2. Configure Router Port Forwarding
1. Open router admin panel (usually http://192.168.1.1)
2. Find "Port Forwarding" or "Virtual Server" section
3. Add new rule:
   - **Service Name**: VOS Tool
   - **External Port**: 8501
   - **Internal IP**: Your PC's local IP (from step 1)
   - **Internal Port**: 8501
   - **Protocol**: TCP
4. Save settings

#### 3. Configure Windows Firewall
```powershell
# Open PowerShell as Administrator
# Allow port 8501
New-NetFirewallRule -DisplayName "VOS Tool" -Direction Inbound -LocalPort 8501 -Protocol TCP -Action Allow
```

#### 4. Find Your Public IP
- Go to: https://whatismyipaddress.com/
- Note your public IP (e.g., 203.0.113.45)

#### 5. Start VOS Tool
```powershell
cd "C:\Users\almisria\Desktop\Final tools\VOS TOOL - final"
streamlit run app.py --server.address 0.0.0.0
```

#### 6. Share URL
- Users access: `http://YOUR_PUBLIC_IP:8501`

### Issues with Port Forwarding:
- ⚠️ **Dynamic IP**: Your public IP may change (ISP dependent)
- ⚠️ **Security**: Your PC is directly exposed to internet
- ⚠️ **ISP Restrictions**: Some ISPs block incoming connections
- ⚠️ **Uptime**: PC must stay on 24/7

---

## Option C: Cloudflare Tunnel (Free, Secure)

### What is Cloudflare Tunnel?
Similar to ngrok but with more features and better free tier.

### Setup Steps:

#### 1. Install cloudflared
- Download: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/
- Windows installer available

#### 2. Authenticate
```powershell
cloudflared tunnel login
```

#### 3. Create Tunnel
```powershell
cloudflared tunnel create vos-tool
```

#### 4. Configure Tunnel
Create file: `config.yml`
```yaml
tunnel: YOUR_TUNNEL_ID
credentials-file: C:\Users\YourName\.cloudflared\YOUR_TUNNEL_ID.json

ingress:
  - hostname: vos-tool.yourdomain.com
    service: http://localhost:8501
  - service: http_status:404
```

#### 5. Run Tunnel
```powershell
cloudflared tunnel run vos-tool
```

### Benefits:
- ✅ Free forever
- ✅ HTTPS included
- ✅ DDoS protection
- ✅ No session timeout
- ⚠️ Requires domain name (can use Cloudflare's free subdomain)

---

## Comparison Table

| Method | Cost | Setup Time | Permanent URL | Security | Uptime Dependency |
|--------|------|------------|---------------|----------|-------------------|
| **ngrok (free)** | $0 | 5 min | ❌ | ✅ Good | Your PC |
| **ngrok (paid)** | $8/mo | 5 min | ✅ | ✅ Good | Your PC |
| **Port Forward** | $0 | 15 min | ⚠️ Maybe | ⚠️ Lower | Your PC |
| **Cloudflare** | $0 | 20 min | ✅ | ✅ Excellent | Your PC |
| **Oracle Cloud** | $0 | 20 min | ✅ | ✅ Excellent | ✅ 24/7 |

---

## My Recommendation

### For Quick Testing (1-2 days):
**Use ngrok** - Super easy, works immediately

### For Long-term Remote Access:
**Use Oracle Cloud Always Free** - Better in every way:
- ✅ Doesn't depend on your PC being on
- ✅ Permanent public IP
- ✅ Better performance
- ✅ Professional setup
- ✅ No security concerns about exposing your PC

---

## Quick Start with ngrok (5 minutes)

```powershell
# 1. Download ngrok from https://ngrok.com/download
# 2. Extract to a folder

# 3. Open PowerShell in VOS Tool folder
cd "C:\Users\almisria\Desktop\Final tools\VOS TOOL - final"
streamlit run app.py

# 4. Open another PowerShell in ngrok folder
cd C:\path\to\ngrok
.\ngrok http 8501

# 5. Copy the https URL shown (e.g., https://abc123.ngrok-free.app)
# 6. Share with your users!
```

**Users access**: The ngrok URL (e.g., `https://abc123.ngrok-free.app`)

---

## Security Best Practices

If exposing your PC:
1. ✅ Use ngrok/Cloudflare (not direct port forwarding)
2. ✅ Keep Windows updated
3. ✅ Use strong passwords
4. ✅ Monitor access logs
5. ✅ Consider adding authentication to your app
6. ⚠️ Don't expose if you have sensitive data on your PC

**Better Alternative**: Just use Oracle Cloud - it's free and much safer!
