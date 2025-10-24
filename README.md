# ComfyUI Discord Bot 🤖

A powerful Discord bot that manages and controls ComfyUI deployments on Modal.com cloud platform. Automatically switches between multiple Modal accounts to maximize free credits, with intelligent credit monitoring and seamless failover.

---

## 🌟 Features

- **💳 Multi-Account Management**: Support up to 6 Modal accounts with automatic switching
- **🔄 Auto-Failover**: Automatically switches accounts when credits drop below $2
- **⏰ 20-Minute Warning**: Get notified before account switching happens
- **🎮 GPU Selection**: Choose from 9 different GPU types (T4 to B200)
- **🖼️ Image Generation**: Generate images via Discord commands
- **📁 Auto-Channel Creation**: Automatically creates Discord channels for each workflow
- **🔒 Secure**: All tokens encrypted, never stored in plain text
- **📊 Credit Tracking**: Real-time balance monitoring with battery icons
- **🚀 Easy Setup**: Two-step Modal setup process

---

## 📋 Requirements

### System Requirements
- **Python**: 3.10 or higher
- **Operating System**: Linux, macOS, or Windows
- **RAM**: 512MB minimum (for the bot, not ComfyUI)
- **Storage**: 1GB for bot files

### Accounts Needed
1. **Discord Bot Account**: [Create one here](https://discord.com/developers/applications)
2. **Modal.com Accounts**: 2-6 accounts (each with $80 free credits)
3. **Cloudflare Tunnel**: For exposing ComfyUI URLs (already configured)

---

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd comfyui-discord-bot
```

### 2. Create Virtual Environment

```bash
# Create venv
python -m venv venv

# Activate it
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt

# Or use uv for faster installation
pip install uv
uv pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your tokens
nano .env  # or use your favorite editor
```

**Required variables in `.env`:**
```bash
DISCORD_BOT_TOKEN=your_discord_bot_token_here
DISCORD_OWNER_ID=your_discord_user_id_here
```

**How to get Discord Bot Token:**
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create New Application
3. Go to "Bot" section
4. Click "Reset Token" and copy it
5. Enable these Privileged Gateway Intents:
   - ✅ MESSAGE CONTENT INTENT
   - ✅ SERVER MEMBERS INTENT
   - ✅ PRESENCE INTENT

**How to get your Discord User ID:**
1. Enable Developer Mode (Settings → Advanced → Developer Mode)
2. Right-click your username
3. Click "Copy ID"

### 5. Invite Bot to Your Server

Generate OAuth2 URL:
1. Go to OAuth2 → URL Generator
2. Select scopes:
   - ✅ `bot`
   - ✅ `applications.commands`
3. Select bot permissions:
   - ✅ Send Messages
   - ✅ Manage Channels
   - ✅ Attach Files
   - ✅ Embed Links
   - ✅ Read Message History
   - ✅ Use Slash Commands
4. Copy the generated URL and open in browser
5. Select your server and authorize

### 6. Run the Bot

```bash
python discord_bot.py
```

You should see:
```
Bot logged in as YourBotName#1234
Connected to 1 guild(s)
Bot is ready!
```

---

## 🎯 First-Time Setup Guide

### Step 1: Add Your First Modal Account

In Discord, use the `/add_account` command:

1. Type `/add_account`
2. Fill in the popup form:
   - **Username**: `account_one` (any name you like)
   - **Token ID**: Your Modal token ID (starts with `ak-`)
   - **Token Secret**: Your Modal token secret (starts with `as-`)
3. Click **Submit**

**How to get Modal tokens:**
1. Go to [Modal.com](https://modal.com)
2. Sign up / Log in
3. Go to Settings → API Tokens
4. Create new token
5. Copy Token ID and Token Secret

### Step 2: Run Initial Setup on Modal

The setup happens in **TWO steps** (total ~2 hours 20 minutes):

**Step 1: Download Models (2 hours)**
```bash
modal deploy modal_setup_step1.py
```

This will:
- Clone ComfyUI
- Clone 30+ custom nodes
- Download all models (~100GB)
- Start JupyterLab

**Wait for completion message**, then run:

**Step 2: Install Dependencies (20 minutes)**
```bash
modal deploy modal_setup_step2.py
```

This will:
- Install Python dependencies
- Install custom node requirements
- Start ComfyUI
- Give you both URLs

### Step 3: Start Using ComfyUI

In Discord:
1. Type `/start`
2. Select a GPU (e.g., H100)
3. Wait ~2 minutes for startup
4. Get your URLs:
   - 📍 JupyterLab: https://jupyter.tensorart.site/
   - 📍 ComfyUI: https://comfyui.tensorart.site/

---

## 🎮 Discord Commands

### Account Management

| Command | Description |
|---------|-------------|
| `/add_account` | Add a new Modal account (opens popup form) |
| `/list_accounts` | View all accounts with balances and status |
| `/switch_account <name>` | Manually switch to a different account |
| `/check_balance` | Check credit balance for all accounts |

### ComfyUI Control

| Command | Description |
|---------|-------------|
| `/start` | Start ComfyUI (opens GPU selector) |
| `/stop` | Stop the currently running ComfyUI |
| `/status` | Check current ComfyUI status |
| `/setup` | Run full setup on active account |

### Image Generation

| Command | Description |
|---------|-------------|
| `/generate` | Generate an image (opens form for workflow + prompt) |
| `/list_outputs` | List all generated outputs |
| `/get_output <filename>` | Download a specific output file |

### Admin

| Command | Description |
|---------|-------------|
| `/refresh_channels` | Manually refresh workflow channels |

---

## 🔄 How Auto-Switching Works

### Credit Monitoring
- Bot checks all account balances **every hour**
- Reads from `balance.json` in Modal volume
- Updates internal database

### When Balance Drops Below $2

1. **Warning Sent** (20 minutes before switch)
   ```
   ⚠️ Low Balance Warning
   
   Account account_one has $1.85 left.
   ⏱️ You have 20 minutes before automatic switch.
   ```

2. **20-Minute Timer Starts**
   - You have time to finish current work
   - Timer runs even if you manually stop

3. **After 20 Minutes**
   - Bot stops current ComfyUI
   - Finds next available account (balance ≥ $2)
   - Switches to new account
   - Runs full setup (2h 20min)
   - Sends completion notification

4. **Ready to Use**
   ```
   ✅ Setup Complete!
   
   Account account_two is ready!
   Use /start to begin using ComfyUI.
   ```

**Important**: Bot does NOT auto-start ComfyUI after switching. You must manually use `/start`.

---

## 🎨 UI Configuration

All visual elements can be customized in `ui_config.py`:

```python
# Change colors
COLORS = {
    'active': 0x57F287,  # Green
    'ready': 0x5865F2,   # Blue
    'dead': 0x747F8D,    # Gray
}

# Change icons
ICONS = {
    'active': '✅',
    'ready': '🟢',
    'dead': '⚫',
}

# Change battery display
BATTERY_ICONS = {
    'full': '🔋🔋🔋🔋🔋',
    'low': '🔋⚪⚪⚪⚪',
}
```

**To modify UI**: Edit ONLY `ui_config.py`. No need to touch other files!

---

## 🖥️ GPU Pricing

| GPU | Price/Hour | Best For |
|-----|-----------|----------|
| **T4** | $0.59 | Testing, low-res images |
| **L4** | $0.80 | Basic workflows |
| **A10** | $1.10 | Standard workflows |
| **L40S** | $1.95 | High-quality images |
| **A100 (40GB)** | $2.10 | Advanced workflows |
| **A100 (80GB)** | $2.50 | Large models |
| **H100** | $3.95 | Premium performance |
| **H200** | $4.54 | Cutting-edge |
| **B200** | $6.25 | Maximum power |

**Setup always uses T4** to minimize costs during installation.

---

## 📁 Project Structure

```
comfyui-discord-bot/
├── discord_bot.py              # Main bot file
├── config.py                   # Configuration settings
├── ui_config.py                # UI customization (colors, icons)
├── account_manager.py          # Account management
├── modal_manager.py            # Modal operations
├── workflow_manager.py         # Workflow & channel management
├── utils.py                    # Helper functions
├── modal_setup_step1.py        # Modal setup: download models
├── modal_setup_step2.py        # Modal setup: install dependencies
├── modal_comfyui_run.py        # Modal runtime with GPU selection
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore file
├── README.md                   # This file
├── accounts.db                 # Database (auto-created)
├── .encryption_key             # Encryption key (auto-created)
├── logs/                       # Log files
└── temp/                       # Temporary downloads
```

---

## 🔒 Security

### What's Protected
- ✅ Discord bot token (in `.env`)
- ✅ Modal tokens (encrypted in database)
- ✅ Encryption key (in `.encryption_key`)
- ✅ Account credentials (never in code)

### Files That Should NEVER Be Committed
- `.env`
- `.encryption_key`
- `accounts.db`
- `logs/`
- `temp/`

All these are in `.gitignore` for your safety!

### If You Accidentally Commit a Secret
1. **Rotate it immediately** (get new token)
2. **Don't just delete and commit** (it's in Git history!)
3. **Clean Git history** using:
   ```bash
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch .env" \
     --prune-empty --tag-name-filter cat -- --all
   ```

---

## 🐛 Troubleshooting

### Bot Won't Start

**Problem**: `Configuration error: DISCORD_BOT_TOKEN environment variable not set`

**Solution**: 
```bash
# Check if .env exists
ls -la .env

# Verify .env has your token
cat .env

# Make sure you're in the correct directory
pwd
```

---

### Modal Commands Fail

**Problem**: `modal: command not found`

**Solution**:
```bash
# Install Modal CLI
pip install modal

# Authenticate Modal
modal setup
```

---

### Can't Check Balances

**Problem**: `Failed to check balance for account_one`

**Solution**:
1. Make sure setup step 2 is complete
2. Verify `balance.json` exists in volume:
   ```bash
   modal volume ls workspace /root/workspace/ComfyUI/custom_nodes/ModalCredits/
   ```
3. Check if ModalCredits extension is installed

---

### Bot Shows "No Active Account"

**Problem**: Bot says no active account after adding one

**Solution**:
```bash
# In Discord, switch to the account
/switch_account account_one
```

---

### ComfyUI Won't Start

**Problem**: `/start` command times out

**Solution**:
1. Check if setup is complete: `/status`
2. Verify Cloudflare tunnel is configured
3. Try stopping and starting again:
   ```bash
   /stop
   /start
   ```

---

## 🎓 Advanced Usage

### Running Multiple Bots

You can run multiple bot instances for different servers:

```bash
# Bot 1
DISCORD_BOT_TOKEN=token1 python discord_bot.py

# Bot 2
DISCORD_BOT_TOKEN=token2 python discord_bot.py
```

Each bot needs its own `.env` or pass tokens directly.

---

### Hosting Options

#### Oracle Cloud Free Tier (Recommended)
- **Cost**: FREE forever
- **Specs**: 4 ARM CPUs, 24GB RAM
- **Perfect for**: This bot (very lightweight)

#### Raspberry Pi (One-time cost)
- **Cost**: $15-35 one-time
- **Power**: ~$2/year electricity
- **Perfect for**: 24/7 home hosting

#### AWS EC2 Free Tier
- **Cost**: FREE for 12 months
- **Specs**: t2.micro (1 vCPU, 1GB RAM)
- **Perfect for**: Testing

---

### Custom Workflows

1. Create workflow in ComfyUI
2. Save it in ComfyUI (File → Save)
3. Bot auto-detects it
4. New Discord channel created automatically
5. Use `/generate` to use the workflow

---

## 📊 Cost Estimation

### Example Usage Scenario

**Setup (one-time per account):**
- Step 1: 2 hours × $0.59 = $1.18
- Step 2: 20 min × $0.59 = $0.20
- **Total**: ~$1.40 per account

**Daily Usage (4 hours on H100):**
- 4 hours × $3.95 = $15.80/day

**With 2 Accounts ($80 each):**
- Account 1: ($80 - $1.40) / $15.80 = ~5 days
- Account 2: ($80 - $1.40) / $15.80 = ~5 days
- **Total**: ~10 days of usage

**With 6 Accounts ($80 each):**
- **Total**: ~30 days of usage!

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

## 📝 License

[Your License Here - e.g., MIT License]

---

## 🙏 Acknowledgments

- [ComfyUI](https://github.com/comfyanonymous/ComfyUI) - Amazing Stable Diffusion UI
- [Modal.com](https://modal.com) - Cloud platform
- [py-cord](https://github.com/Pycord-Development/pycord) - Discord bot library

---

## 📧 Support

- **Issues**: [GitHub Issues](your-repo-url/issues)
- **Discord**: [Your Discord Server]
- **Email**: [Your Email]

---

## ⭐ Star this project if it helped you!

Made with ❤️ by [Your Name]

---

**Last Updated**: October 2025
