# 🎉 HYBRID BOT - COMPLETE UPGRADE SUMMARY

## ✅ What Was Done

I've successfully created a **hybrid bot** combining:
- **Your friend's execution method** (`modal run app.py::run`)
- **Your complete functionality** (all 9 commands, credit tracking, auto-switching)
- **Button-based UI** (no more typing `/command` repeatedly!)
- **Modular app files** (app1.py, app2.py, app.py - ready for your code)

---

## 📁 New Files Created

### 1. **Modal App Files** (Empty Templates - You Add Code)

**`app1.py`** - Setup Step 1 (2 hour timeout)
- Clone repositories
- Download large model files  
- Initial workspace setup
- Uses `GPU_NAME` placeholder → bot replaces with actual GPU

**`app2.py`** - Setup Step 2 (20 minute timeout)
- Install Python dependencies
- Configure ComfyUI custom nodes
- **Important:** Does NOT start JupyterLab/ComfyUI (only setup)
- Uses `GPU_NAME` placeholder

**`app.py`** - Runtime (24 hour timeout)
- Start JupyterLab (background)
- Start ComfyUI (background)
- Start Cloudflare tunnel (blocking - keeps container running)
- Uses `GPU_NAME` placeholder

### 2. **Button UI System** (`views/` directory)

**`views/__init__.py`** - Module exports

**`views/main_menu.py`** - Main Control Panel
- ▶️ Start button
- ⏹️ Stop button
- 👤 User Config button
- 💰 View Credits button
- 🚪 Exit button

**`views/user_config.py`** - User Management
- ➕ Add Account (popup modal for tokens)
- 🔄 Switch Account (dropdown with checkboxes)
- ⬅️ Go Back

**`views/credits.py`** - Credit Tracking
- Reads from `custom_nodes/ComfyUI-CreditTracker/balance.json`
- Color-coded warnings (red < $2, orange < $10)
- Auto-refresh capability

### 3. **Updated Core Files**

**`modal_manager.py`**
- ✅ Uses `modal run app.py::run` pattern (friend's method)
- ✅ New `deploy_setup()` runs app1.py → app2.py sequentially
- ✅ New `start_comfyui()` uses `modal run app.py::run`
- ✅ Removed hardcoded timeouts, uses config values
- ✅ Background execution with `asyncio.create_task()`

**`discord_bot.py`**
- ✅ Imported button views
- ✅ `/start` now opens button-based control panel
- ✅ `/setup` runs app1.py + app2.py automatically (2h 20m total)
- ✅ All other commands preserved (/generate, /status, etc.)
- ✅ Updated notification messages for new timeouts

---

## 🎮 How The New UI Works

### Command Flow:

```
/start
  └─> Opens Control Panel with buttons:
      ├─ [▶️ Start] ────────> Starts app.py::run with selected GPU
      ├─ [⏹️ Stop] ─────────> Stops Modal app
      ├─ [👤 User Config] ──> Opens sub-menu:
      │                        ├─ [➕ Add Account] ──> Popup form
      │                        ├─ [🔄 Switch Account] ─> Dropdown list
      │                        └─ [⬅️ Go Back]
      ├─ [💰 View Credits] ──> Shows balance from CreditTracker
      └─ [🚪 Exit] ──────────> Closes panel

/setup
  └─> Runs app1.py (2h) → app2.py (20m) automatically
      └─> Sends notifications when complete

/generate
  └─> Original UI (unchanged)

/status
  └─> Shows current server status (command-based)
```

### Switch Account UI:
```
┌────────────────────────────────┐
│  Select Account:               │
│  ☐ account1 ($15.50 • ready)   │
│  ☑ account2 ($80.00 • active)  │ ← Checkbox shows selected
│  ☐ account3 ($5.20 • ready)    │
│                                │
│  [⬅️ Go Back]                  │
└────────────────────────────────┘
```

---

## 🔧 What You Need To Do

### 1. **Add Your Code to App Files**

**app1.py** (Line 59-72):
```python
# Example code structure:
print("\n[1/3] Cloning ComfyUI...")
os.system("git clone https://github.com/comfyanonymous/ComfyUI /root/workspace/ComfyUI")

print("\n[2/3] Downloading models...")
os.system("wget https://huggingface.co/your-model.safetensors -P /root/workspace/models")

print("\n[3/3] Setting up workspace...")
os.system("mkdir -p /root/workspace/custom_nodes")
```

**app2.py** (Line 61-74):
```python
# Example code structure:
print("\n[1/3] Installing ComfyUI requirements...")
os.system("pip install -r /root/workspace/ComfyUI/requirements.txt")

print("\n[2/3] Installing custom node dependencies...")
os.system("pip install sageattention some-other-package")

print("\n[3/3] Creating setup marker...")
os.system("touch /root/workspace/.setup_complete")
```

**app.py** (Line 75-92):
```python
# Example code structure:
print("\n[1/4] Installing Cloudflare...")
os.system("wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O cloudflared")
os.system("chmod +x cloudflared && mv cloudflared /usr/local/bin/")

print("\n[2/4] Starting JupyterLab...")
os.system("jupyter lab --ip=0.0.0.0 --port=5000 --no-browser --allow-root --NotebookApp.token='' &")
time.sleep(5)

print("\n[3/4] Starting ComfyUI...")
os.system("cd /root/workspace/ComfyUI && python main.py --listen 0.0.0.0 --port=8188 &")
time.sleep(5)

print("\n[4/4] Starting Cloudflare tunnel (keeps running)...")
os.system("cloudflared tunnel run your-tunnel-name")  # ← This must be LAST (blocking)
```

### 2. **Replace GPU_NAME Placeholder**

In all three files (app1.py, app2.py, app.py), find line ~48:
```python
gpu=GPU_NAME,  # ← This will be replaced by bot with actual GPU (H100, A100, etc.)
```

**Replace `GPU_NAME` with your actual GPU choice:**
- `"H100"` - Most powerful
- `"A100"` - Good balance
- `"A10G"` - Budget option
- `"T4"` - Cheapest (good for setup)

Example:
```python
gpu="H100",  # For production runtime
```

Or keep it dynamic:
```python
gpu=GPU_TYPE,  # Uses environment variable from bot (recommended)
```

### 3. **Upload to Ubuntu Server**

Once you've added your code:

```bash
# Option A: Use Google Drive
# 1. Upload app1.py, app2.py, app.py to Google Drive
# 2. Get shareable links
# 3. On Ubuntu:
wget "YOUR_GDRIVE_LINK_1" -O ~/Antique-Bot/app1.py
wget "YOUR_GDRIVE_LINK_2" -O ~/Antique-Bot/app2.py
wget "YOUR_GDRIVE_LINK_3" -O ~/Antique-Bot/app.py

# Option B: Use SCP (from Windows PowerShell)
scp C:\Users\User\Downloads\whatever\Antique-Bot\app1.py ubuntu@3.109.182.173:~/Antique-Bot/
scp C:\Users\User\Downloads\whatever\Antique-Bot\app2.py ubuntu@3.109.182.173:~/Antique-Bot/
scp C:\Users\User\Downloads\whatever\Antique-Bot\app.py ubuntu@3.109.182.173:~/Antique-Bot/
scp C:\Users\User\Downloads\whatever\Antique-Bot\modal_manager.py ubuntu@3.109.182.173:~/Antique-Bot/
scp C:\Users\User\Downloads\whatever\Antique-Bot\discord_bot.py ubuntu@3.109.182.173:~/Antique-Bot/
scp -r C:\Users\User\Downloads\whatever\Antique-Bot\views ubuntu@3.109.182.173:~/Antique-Bot/
```

### 4. **Restart Bot on Ubuntu**

```bash
ssh ubuntu@3.109.182.173

cd ~/Antique-Bot

# Kill old bot
pkill -f discord_bot.py

# Start new bot
nohup python3 discord_bot.py > bot.log 2>&1 &

# Check if running
ps aux | grep discord_bot.py

# View logs
tail -f bot.log
```

---

## 🚀 Testing Your New Bot

### Test Flow:

1. **In Discord, type: `/start`**
   - Should see control panel with 5 buttons
   - Should show current account and status

2. **Click: 👤 User Config**
   - Should see Add Account and Switch Account buttons

3. **Click: ➕ Add Account**
   - Should see popup form for tokens
   - Add a test account

4. **Click: 🔄 Switch Account**
   - Should see dropdown with checkbox
   - Select an account

5. **Click: ▶️ Start** (from main panel)
   - Should start app.py::run
   - Should show "Starting ComfyUI..." message
   - Should provide links after 2-3 minutes

6. **Test: `/setup`**
   - Should run app1.py then app2.py automatically
   - Should send progress notifications

7. **Test: `/status`**
   - Should show current server info

8. **Test: `/generate`** (if you have workflows)
   - Should work as before

---

## 📊 Key Improvements

| Feature | Old | New |
|---------|-----|-----|
| **Modal Command** | `modal deploy` | `modal run app.py::run` ✅ |
| **Setup Steps** | Separate commands | Auto-sequential ✅ |
| **Setup Time** | 4h 40m | 2h 20m ✅ |
| **UI** | Slash commands | Buttons ✅ |
| **Account Switch** | Text input | Dropdown + checkbox ✅ |
| **Credits** | Modal API | CreditTracker balance.json ✅ |
| **App Files** | Hardcoded | Modular templates ✅ |
| **GPU Selection** | In code | Variable (GPU_NAME) ✅ |

---

## ⚠️ Important Notes

1. **GPU_NAME Placeholder:**
   - The app files use `gpu=GPU_NAME` as a placeholder
   - Replace with actual GPU (`"H100"`, `"A100"`, etc.)
   - OR use `gpu=GPU_TYPE` to keep it dynamic (bot sets via environment)

2. **Last Command Must Be Blocking:**
   - In `app.py`, the final command MUST keep container running
   - Usually: `os.system("cloudflared tunnel run your-tunnel")`
   - If you remove cloudflared, use: `while True: time.sleep(3600)`

3. **Setup Does NOT Start Services:**
   - `app2.py` should only install dependencies
   - Do NOT start JupyterLab/ComfyUI in app2.py
   - Only `app.py` starts services

4. **Timeout Safety:**
   - app1.py: 2 hour timeout (but Modal allows 24h)
   - app2.py: 20 minute timeout
   - app.py: 24 hour timeout
   - If step finishes early, next step starts immediately

5. **All Original Features Preserved:**
   - Credit checking ✅
   - Auto account switching ✅
   - 6-account system ✅
   - Workflow manager ✅
   - /generate command ✅
   - Background tasks ✅

---

## 📝 Command Reference

### Active Commands:

| Command | Description | UI Type |
|---------|-------------|---------|
| `/start` | Open control panel | **Buttons** 🎮 |
| `/setup` | Run app1.py + app2.py | Command (with notifications) |
| `/status` | Check server status | Command |
| `/generate` | Generate image | Original UI |
| `/list_outputs` | List outputs | Original UI |
| `/get_output` | Download output | Original UI |
| `/refresh_channels` | Refresh workflows | Command |
| `/check_balance` | View all balances | Command |

### Deprecated (Replaced by Buttons):

- ❌ `/add_account` → Use User Config button
- ❌ `/switch_account` → Use User Config button
- ❌ `/list_accounts` → Use Switch Account dropdown
- ❌ `/stop` → Use Stop button (but command still works)

---

## 🎯 Next Steps

1. ✅ Add your code to app1.py, app2.py, app.py
2. ✅ Replace GPU_NAME with actual GPU or keep as GPU_TYPE
3. ✅ Test files locally (optional): `modal run app1.py::run`
4. ✅ Upload all files to Ubuntu server
5. ✅ Restart Discord bot
6. ✅ Test button UI in Discord
7. ✅ Run `/setup` to test sequential execution
8. ✅ Run `/start` to test app.py
9. ✅ Verify credits show from CreditTracker
10. ✅ Enjoy your hybrid bot! 🎉

---

## 🐛 Troubleshooting

**Buttons don't appear:**
- Check views/ folder uploaded correctly
- Restart bot: `pkill -f discord_bot.py && nohup python3 discord_bot.py > bot.log 2>&1 &`

**Import errors:**
- Make sure views/__init__.py exists
- Check all view files uploaded

**Modal commands fail:**
- Verify app1.py, app2.py, app.py have `def run():` function
- Check GPU_NAME replaced with actual GPU
- Verify Modal CLI updated: `modal --version`

**Credits don't show:**
- Server must be running first
- Check balance.json path: `custom_nodes/ComfyUI-CreditTracker/balance.json`
- Adjust path in views/credits.py if different

---

**You're all set! 🚀 Let me know if you need any clarifications!**
