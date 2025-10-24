"""
Simple Bot Configuration
=========================
Just Discord token - Modal tokens added via Discord buttons!
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# ============================================================================
# DISCORD SETTINGS (ONLY THING YOU NEED!)
# ============================================================================

DISCORD_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
OWNER_ID = os.getenv('DISCORD_OWNER_ID')

# ============================================================================
# MODAL SETTINGS
# ============================================================================

# Modal volume name
MODAL_VOLUME_NAME = "workspace"

# Modal app names
MODAL_APP_NAMES = {
    'step1': 'setup-step1',
    'step2': 'setup-step2', 
    'runtime': 'comfyui-antique'
}

# ============================================================================
# CLOUDFLARE URLS
# ============================================================================

CLOUDFLARE_URLS = {
    'jupyter': 'https://jupyter.tensorart.site/',
    'comfyui': 'https://comfyui.tensorart.site/',
}

# ============================================================================
# TIMEOUTS (in seconds)
# ============================================================================

SETUP_TIME = {
    'step1': 10800,  # 3 hours
    'step2': 3600,   # 1 hour
}

# ============================================================================
# FILE PATHS
# ============================================================================

BASE_DIR = Path(__file__).parent
DATABASE_FILE = BASE_DIR / "accounts.db"
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# ============================================================================
# VALIDATION
# ============================================================================

if not DISCORD_TOKEN:
    raise ValueError("❌ DISCORD_BOT_TOKEN not found in .env file!")

print("✅ Config loaded successfully!")
