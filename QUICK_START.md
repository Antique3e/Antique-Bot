# 🚀 QUICK START GUIDE

## Step 1: Add Your Code to App Files

### app1.py (Setup Step 1 - ~2 hours)
**Location:** Line 59-72

**What to add:** Your model downloads, repo clones, large file operations

**Example from your OLD modal_setup_step1.py:**
```python
# Clone ComfyUI
print("\n[1/5] Cloning ComfyUI...")
os.system("git clone https://github.com/comfyanonymous/ComfyUI /root/workspace/ComfyUI")

# Download Wan 2.2 model (14GB)
print("\n[2/5] Downloading Wan 2.2 model...")
os.system("wget https://huggingface.co/your-model-path/wan2.2-14b.safetensors -P /root/workspace/ComfyUI/models/checkpoints/")

# Download VAE
print("\n[3/5] Downloading VAE...")
os.system("wget https://huggingface.co/stabilityai/sd-vae-ft-mse/vae.safetensors -P /root/workspace/ComfyUI/models/vae/")

# Clone custom nodes
print("\n[4/5] Cloning custom nodes...")
os.system("git clone https://github.com/ltdrdata/ComfyUI-Manager /root/workspace/ComfyUI/custom_nodes/ComfyUI-Manager")

# Download LoRAs
print("\n[5/5] Downloading LoRAs...")
os.system("wget https://civitai.com/your-lora.safetensors -P /root/workspace/ComfyUI/models/loras/")
```

---

### app2.py (Setup Step 2 - ~20 minutes)
**Location:** Line 61-74

**What to add:** Dependency installation, configuration

**Example from your OLD modal_setup_step2.py:**
```python
# Install ComfyUI requirements
print("\n[1/4] Installing ComfyUI requirements...")
os.system("cd /root/workspace/ComfyUI && pip install -r requirements.txt")

# Install Manager requirements
print("\n[2/4] Installing Manager requirements...")
os.system("cd /root/workspace/ComfyUI/custom_nodes/ComfyUI-Manager && pip install -r requirements.txt")

# Restore custom node dependencies
print("\n[3/4] Restoring custom node dependencies...")
os.system("python /root/workspace/ComfyUI/custom_nodes/ComfyUI-Manager/cm-cli.py restore-dependencies")

# Install additional packages
print("\n[4/4] Installing sageattention...")
os.system("pip install sageattention")

# Create marker file
print("\n✅ Creating setup marker...")
os.system("touch /root/workspace/.setup_complete")
```

---

### app.py (Runtime - runs until you stop it)
**Location:** Line 75-92

**What to add:** Service startup commands (JupyterLab, ComfyUI, Cloudflare)

**Example from your OLD modal_comfyui_run.py:**
```python
# Install Cloudflare tunnel
print("\n[1/4] Installing Cloudflare tunnel...")
os.system("wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O cloudflared")
os.system("chmod +x cloudflared && mv cloudflared /usr/local/bin/")
os.system("git clone https://tensorart-site:YOUR_TOKEN@github.com/tensorart-site/cf-bypass-login.git")
os.system("cd cf-bypass-login && cp -r .cloudflared /root")

# Start JupyterLab
print("\n[2/4] Starting JupyterLab...")
os.system("jupyter lab --ip=0.0.0.0 --port=5000 --no-browser --allow-root --NotebookApp.token='' --NotebookApp.password='' &")
time.sleep(5)

# Start ComfyUI
print("\n[3/4] Starting ComfyUI...")
os.system("cd /root/workspace/ComfyUI && python main.py --listen 0.0.0.0 --port=8188 &")
time.sleep(5)

print("\n✅ Services started!")
print("📍 JupyterLab: https://jupyter.tensorart.site/")
print("📍 ComfyUI: https://comfyui.tensorart.site/")

# Start Cloudflare tunnel (MUST BE LAST - keeps container running)
print("\n[4/4] Starting Cloudflare tunnel...")
os.system("cloudflared tunnel run tensorart")
```

---

## Step 2: Replace GPU_NAME

In all three files, find this line (around line 48):

```python
gpu=GPU_NAME,  # ← This will be replaced by bot with actual GPU
```

**Option A: Use specific GPU**
```python
gpu="H100",  # For production
```

**Option B: Keep dynamic (recommended)**
```python
gpu=GPU_TYPE,  # Bot sets via environment variable
```

Available GPUs:
- `"H100"` - Most powerful ($3-4/hour)
- `"A100"` - Strong ($2-3/hour)  
- `"A10G"` - Budget ($1-2/hour)
- `"T4"` - Cheapest ($0.50-1/hour, good for setup)

---

## Step 3: Upload Files to Ubuntu

### From Windows PowerShell:

```powershell
# Navigate to your folder
cd C:\Users\User\Downloads\whatever\Antique-Bot

# Upload app files
scp app1.py ubuntu@3.109.182.173:~/Antique-Bot/
scp app2.py ubuntu@3.109.182.173:~/Antique-Bot/
scp app.py ubuntu@3.109.182.173:~/Antique-Bot/

# Upload updated core files
scp modal_manager.py ubuntu@3.109.182.173:~/Antique-Bot/
scp discord_bot.py ubuntu@3.109.182.173:~/Antique-Bot/

# Upload views folder
scp -r views ubuntu@3.109.182.173:~/Antique-Bot/
```

**OR use Google Drive:**

1. Upload files to Google Drive
2. Get shareable link (anyone with link can view)
3. On Ubuntu:
```bash
wget "YOUR_GDRIVE_LINK" -O ~/Antique-Bot/app1.py
wget "YOUR_GDRIVE_LINK" -O ~/Antique-Bot/app2.py
wget "YOUR_GDRIVE_LINK" -O ~/Antique-Bot/app.py
# etc...
```

---

## Step 4: Restart Bot on Ubuntu

```bash
# SSH into server
ssh ubuntu@3.109.182.173

# Go to bot directory
cd ~/Antique-Bot

# Stop old bot
pkill -f discord_bot.py

# Verify stopped
ps aux | grep discord_bot.py

# Start new bot
nohup python3 discord_bot.py > bot.log 2>&1 &

# Check it's running
ps aux | grep discord_bot.py

# Watch logs (Ctrl+C to exit)
tail -f bot.log
```

---

## Step 5: Test in Discord

### Test 1: Button UI
```
Type: /start

Expected:
- Control panel with 5 buttons appears
- Shows your active account
- Shows server status
```

### Test 2: User Config
```
1. Click: 👤 User Config
2. Click: ➕ Add Account
3. Fill in form with Modal tokens
4. Submit

Expected:
- Account added successfully
- Can switch between accounts
```

### Test 3: Switch Account
```
1. Click: 👤 User Config
2. Click: 🔄 Switch Account
3. Select account from dropdown

Expected:
- Dropdown shows all accounts with balances
- Checkbox shows current selection
- Can switch successfully
```

### Test 4: Setup
```
Type: /setup

Expected:
- Shows "Setup Started" message
- Runs app1.py (2 hours)
- Then runs app2.py (20 minutes)
- Sends notification when complete
```

### Test 5: Start Server
```
1. Type: /start (to open panel)
2. Click: ▶️ Start

Expected:
- Shows "Starting ComfyUI..." message
- Waits 2-3 minutes
- Provides JupyterLab and ComfyUI links
```

### Test 6: View Credits
```
1. Make sure server is running first
2. Click: 💰 View Credits

Expected:
- Shows current balance from CreditTracker
- Color-coded (red if low)
```

### Test 7: Stop Server
```
Click: ⏹️ Stop

Expected:
- Server stops
- "Stopped successfully" message
```

---

## Troubleshooting

### Buttons Don't Show

**Check 1:** Views folder uploaded?
```bash
ls -la ~/Antique-Bot/views/
# Should show: __init__.py, main_menu.py, user_config.py, credits.py
```

**Check 2:** Restart bot
```bash
pkill -f discord_bot.py
nohup python3 discord_bot.py > bot.log 2>&1 &
```

**Check 3:** View logs
```bash
tail -50 bot.log
# Look for import errors
```

---

### Modal Commands Fail

**Check 1:** App files have run() function?
```bash
grep "def run():" ~/Antique-Bot/app1.py
grep "def run():" ~/Antique-Bot/app2.py
grep "def run():" ~/Antique-Bot/app.py
```

**Check 2:** GPU_NAME replaced?
```bash
grep "GPU_NAME" ~/Antique-Bot/app1.py
# Should NOT show "gpu=GPU_NAME" (should be "gpu=GPU_TYPE" or "gpu=\"H100\"")
```

**Check 3:** Modal CLI version
```bash
modal --version
# Should be 0.64+ or newer
```

---

### Credits Don't Show

**Check 1:** Server running?
```
Use /status command to check
```

**Check 2:** CreditTracker path correct?
- Edit `views/credits.py` line 23
- Check your actual path to balance.json
- Default: `custom_nodes/ComfyUI-CreditTracker/balance.json`

**Check 3:** Test URL manually
- Go to: https://comfyui.tensorart.site/custom_nodes/ComfyUI-CreditTracker/balance.json
- Should see JSON with balance

---

### Import Errors

**Missing views module:**
```bash
# On Ubuntu
cd ~/Antique-Bot
ls -la views/

# Should see:
# __init__.py
# main_menu.py
# user_config.py
# credits.py
```

**Fix:** Re-upload views folder
```powershell
# From Windows
scp -r C:\Users\User\Downloads\whatever\Antique-Bot\views ubuntu@3.109.182.173:~/Antique-Bot/
```

---

## 🎯 Quick Checklist

Before testing:

- [ ] Added code to app1.py (lines 59-72)
- [ ] Added code to app2.py (lines 61-74)
- [ ] Added code to app.py (lines 75-92)
- [ ] Replaced GPU_NAME with GPU_TYPE or specific GPU
- [ ] Uploaded all files to Ubuntu
- [ ] Uploaded views/ folder to Ubuntu
- [ ] Restarted Discord bot
- [ ] Checked bot.log for errors
- [ ] Bot shows as online in Discord

Testing:

- [ ] /start shows control panel
- [ ] Buttons are clickable
- [ ] Can add account via popup
- [ ] Can switch account via dropdown
- [ ] /setup runs both steps
- [ ] Start button works
- [ ] Links provided after start
- [ ] Credits show correctly
- [ ] Stop button works

---

**You're ready to go! 🚀**

If you get stuck, check:
1. bot.log file on Ubuntu
2. Discord bot status (online?)
3. Modal CLI authenticated?
4. Files uploaded correctly?

Need help? Share the specific error message from bot.log!
