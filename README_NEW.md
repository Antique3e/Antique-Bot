# 🤖 ComfyUI Discord Bot - Hybrid Edition

A powerful Discord bot for managing ComfyUI deployments on Modal.com with a beautiful button-based UI.

## ✨ Features

- 🎮 **Button-Based UI** - No more typing commands! Click buttons to control everything
- 🚀 **Modal.com Integration** - Deploy ComfyUI on cloud GPUs (H100, A100, A10G, T4)
- 👥 **Multi-Account Support** - Manage up to 6 Modal accounts with auto-failover
- 💰 **Credit Tracking** - Monitor credits from ComfyUI-CreditTracker
- 🔄 **Auto Account Switching** - Automatically switches when credits run low
- 🎨 **Workflow Manager** - Auto-create Discord channels for workflows
- 📊 **Real-time Status** - Check server status, GPU usage, and balances
- 🔧 **Modular App Files** - Easy to customize your setup and runtime code

## 🎮 UI Preview

```
/start → 🎮 Control Panel
         ┌─────────────────────────┐
         │  [▶️ Start]  [⏹️ Stop]  │
         │  [👤 User Config]       │
         │  [💰 View Credits]      │
         │  [🚪 Exit]              │
         └─────────────────────────┘
```

## 📋 Requirements

- Python 3.10+
- Discord Bot Token
- Modal.com Account(s)
- Ubuntu Server (recommended) or any Linux environment

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME
```

### 2. Install Dependencies

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
nano .env  # Edit with your Discord token and owner ID
```

Required environment variables:
```env
DISCORD_BOT_TOKEN=your_discord_bot_token
DISCORD_OWNER_ID=your_discord_user_id
```

### 4. Add Your Code to App Files

**Important:** The app files are templates. You need to add your actual code:

- **`app1.py`** (Line 59-72) - Setup Step 1: Model downloads, repo clones
- **`app2.py`** (Line 61-74) - Setup Step 2: Dependency installation
- **`app.py`** (Line 75-92) - Runtime: Start JupyterLab, ComfyUI, Cloudflare

See [QUICK_START.md](QUICK_START.md) for detailed examples.

### 5. Replace GPU_NAME Placeholder

In all three app files (app1.py, app2.py, app.py), find line ~48:

```python
# Change from:
gpu=GPU_NAME,

# To:
gpu=GPU_TYPE,  # Recommended - bot sets via environment
# OR
gpu="H100",    # Specific GPU
```

### 6. Run the Bot

```bash
python3 discord_bot.py
```

Or run in background:
```bash
nohup python3 discord_bot.py > bot.log 2>&1 &
```

## 📚 Documentation

- **[QUICK_START.md](QUICK_START.md)** - Step-by-step setup guide with code examples
- **[UPGRADE_COMPLETE.md](UPGRADE_COMPLETE.md)** - Complete feature documentation

## 🎯 Commands

| Command | Description | Type |
|---------|-------------|------|
| `/start` | Open control panel | Button UI |
| `/setup` | Run complete setup (app1.py → app2.py) | Command |
| `/status` | Check server status | Command |
| `/generate` | Generate image with workflow | Command |
| `/check_balance` | View all account balances | Command |
| `/list_outputs` | List generated outputs | Command |
| `/get_output` | Download output file | Command |
| `/refresh_channels` | Refresh workflow channels | Command |

## 🔧 Configuration

Edit `config.py` to customize:

- Credit thresholds (`MIN_CREDIT_THRESHOLD`)
- Maximum accounts (`MAX_ACCOUNTS`)
- Cloudflare URLs (`CLOUDFLARE_URLS`)
- GPU options (`GPU_OPTIONS`)
- Timeout settings (`COMFYUI_STARTUP_TIMEOUT`)

## 🏗️ Architecture

```
├── discord_bot.py          # Main bot file
├── modal_manager.py        # Modal operations
├── account_manager.py      # Account management
├── config.py               # Configuration
├── utils.py                # Utilities
├── workflow_manager.py     # Workflow handling
├── ui_config.py            # UI settings
├── app1.py                 # Setup Step 1 (your code)
├── app2.py                 # Setup Step 2 (your code)
├── app.py                  # Runtime (your code)
└── views/                  # Button UI components
    ├── __init__.py
    ├── main_menu.py        # Control panel
    ├── user_config.py      # Account management UI
    └── credits.py          # Credit tracking
```

## 💡 How It Works

### Setup Flow
```
/setup
  └─> Runs app1.py::run (2 hours) - Downloads models, clones repos
      └─> Then runs app2.py::run (20 minutes) - Installs dependencies
          └─> Sends notification when complete
```

### Runtime Flow
```
/start (opens control panel)
  └─> Click [▶️ Start]
      └─> Runs app.py::run with selected GPU
          └─> Starts JupyterLab + ComfyUI + Cloudflare tunnel
              └─> Provides access links
```

### Modal Execution Method
Uses the proven `modal run app.py::run` pattern:
```python
# In modal_manager.py:
command = f"GPU_TYPE={gpu} modal run {app_path}::run"
asyncio.create_task(utils.run_command(command, timeout=None))
```

This keeps the Modal container running until you stop it.

## 🔐 Security

- **Never commit `.env` file** - Contains sensitive tokens
- **Database is encrypted** - Uses Fernet encryption for Modal tokens
- **Secrets in environment** - All sensitive data in environment variables

## 🐛 Troubleshooting

### Buttons Don't Appear
```bash
# Check views folder exists
ls -la views/

# Restart bot
pkill -f discord_bot.py
nohup python3 discord_bot.py > bot.log 2>&1 &
```

### Modal Commands Fail
```bash
# Verify app files have run() function
grep "def run():" app1.py app2.py app.py

# Check GPU_NAME replaced
grep "GPU_NAME" app*.py
```

### Import Errors
```bash
# Check all files present
ls -la views/

# Reinstall dependencies
pip install -r requirements.txt
```

See [QUICK_START.md](QUICK_START.md) for more troubleshooting.

## 📊 Credit System

The bot automatically:
- ✅ Checks credits every hour
- ✅ Warns when balance < $10
- ✅ Auto-switches accounts when balance < $2
- ✅ Provides 20-minute grace period before switching
- ✅ Reads credits from ComfyUI-CreditTracker balance.json

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

See [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [py-cord](https://github.com/Pycord-Development/pycord)
- Powered by [Modal](https://modal.com)
- Inspired by [ComfyUI](https://github.com/comfyanonymous/ComfyUI)
- UI pattern from [jekverse/yanmodal](https://github.com/jekverse/yanmodal)

## 📞 Support

If you encounter issues:
1. Check [QUICK_START.md](QUICK_START.md)
2. Check [UPGRADE_COMPLETE.md](UPGRADE_COMPLETE.md)
3. Review `bot.log` for errors
4. Open an issue on GitHub

## ⚠️ Important Notes

1. **Add your code to app files** - The app1.py, app2.py, app.py are templates
2. **Replace GPU_NAME** - Change to `GPU_TYPE` or specific GPU like `"H100"`
3. **Last command must block** - In app.py, use `cloudflared tunnel run` or `while True: time.sleep(3600)`
4. **Setup doesn't start services** - app2.py should only install dependencies, not start ComfyUI/JupyterLab
5. **Backup your .env** - Never commit it to GitHub

---

**Made with ❤️ for the ComfyUI community**
