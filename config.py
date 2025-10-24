"""
Configuration File
==================
Non-UI settings for the Discord bot.
This file contains paths, limits, timings, and technical settings.

For visual/UI changes, edit ui_config.py instead.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ============================================================================
# PROJECT PATHS
# ============================================================================

# Base directory (where this config.py file is located)
BASE_DIR = Path(__file__).parent.absolute()

# Database file (stores encrypted account credentials)
DATABASE_FILE = BASE_DIR / "accounts.db"

# Logs directory
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Temp directory for file downloads
TEMP_DIR = BASE_DIR / "temp"
TEMP_DIR.mkdir(exist_ok=True)

# ============================================================================
# MODAL CONFIGURATION
# ============================================================================

# Modal volume name (must match your Modal code)
MODAL_VOLUME_NAME = "workspace"

# Modal app name
MODAL_APP_NAME = "comfyui-antique"

# Modal volume paths
MODAL_PATHS = {
    'comfyui_root': '/root/workspace/ComfyUI',
    'models': '/root/workspace/ComfyUI/models',
    'outputs': '/root/workspace/ComfyUI/output',
    'workflows': '/root/workspace/ComfyUI/user/default/workflows',
    'balance_json': '/root/workspace/ComfyUI/custom_nodes/ModalCredits/balance.json',
}

# Modal Python files
MODAL_FILES = {
    'setup_step1': BASE_DIR / 'modal_setup_step1.py',
    'setup_step2': BASE_DIR / 'modal_setup_step2.py',
    'comfyui_run': BASE_DIR / 'modal_comfyui_run.py',
}

# ============================================================================
# CLOUDFLARE TUNNEL URLS
# ============================================================================

CLOUDFLARE_URLS = {
    'jupyter': 'https://jupyter.tensorart.site/',
    'comfyui': 'https://comfyui.tensorart.site/',
}

# ComfyUI API endpoints (relative to comfyui URL)
COMFYUI_API = {
    'system_stats': '/system_stats',
    'prompt': '/prompt',
    'history': '/history',
    'queue': '/queue',
    'view': '/view',
}

# ============================================================================
# ACCOUNT MANAGEMENT
# ============================================================================

# Maximum number of Modal accounts allowed
MAX_ACCOUNTS = 6

# Minimum credit balance threshold (switch accounts when below this)
MIN_CREDIT_THRESHOLD = 2.0

# Initial balance for new accounts (Modal promotional credit)
INITIAL_BALANCE = 80.0

# ============================================================================
# TIMING CONFIGURATION
# ============================================================================

# How often to check credits (in seconds)
# Default: 3600 seconds = 1 hour
CREDIT_CHECK_INTERVAL = 3600

# Warning time before auto-switch (in seconds)
# Default: 1200 seconds = 20 minutes
SWITCH_WARNING_TIME = 1200

# Setup time estimates (in seconds)
SETUP_TIME = {
    'step1': 14400,   # 4 hours for model downloads (100GB+ on slower connections)
    'step2': 2400,    # 40 minutes for dependency installation
}

# ComfyUI startup timeout (in seconds)
# How long to wait for ComfyUI to become ready
COMFYUI_STARTUP_TIMEOUT = 900  # 15 minutes (increased for slower GPU spin-up)

# How often to check if ComfyUI is ready (in seconds)
COMFYUI_CHECK_INTERVAL = 5

# ============================================================================
# GPU CONFIGURATION
# ============================================================================

# Default GPU for setup phases (always T4 for cost savings)
SETUP_GPU = "T4"

# GPU code mapping (Modal GPU names)
GPU_MAPPING = {
    'T4': 'T4',
    'L4': 'L4',
    'A10': 'A10',
    'L40S': 'L40S',
    'A100, 40 GB': 'A100',
    'A100, 80 GB': 'A100-80GB',
    'H100': 'H100',
    'H200': 'H200',
    'B200': 'B200',
}

# ============================================================================
# DISCORD CONFIGURATION
# ============================================================================

# Discord bot token (loaded from environment variable)
DISCORD_TOKEN = os.getenv('DISCORD_BOT_TOKEN')

# Discord bot command prefix (if using text commands)
COMMAND_PREFIX = '!'

# Owner Discord user ID (your Discord user ID)
# To get your ID: Enable Developer Mode in Discord settings,
# then right-click your name and select "Copy ID"
OWNER_ID = os.getenv('DISCORD_OWNER_ID')

# Discord channel settings
DISCORD_CHANNELS = {
    'category_name': 'ComfyUI Outputs',  # Category for workflow channels
    'alerts_channel': None,  # Set to channel ID for dedicated alerts channel (optional)
}

# ============================================================================
# SECURITY CONFIGURATION
# ============================================================================

# Encryption key for storing Modal tokens
# This will be generated automatically on first run
ENCRYPTION_KEY_FILE = BASE_DIR / ".encryption_key"

# Allowed file extensions for outputs
ALLOWED_OUTPUT_EXTENSIONS = ['.png', '.jpg', '.jpeg', '.gif', '.mp4', '.webm', '.webp']

# Maximum file size for Discord uploads (in MB)
MAX_DISCORD_FILE_SIZE = 25  # Discord limit is 25MB for regular users

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'standard',
            'stream': 'ext://sys.stdout',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'standard',
            'filename': str(LOGS_DIR / 'bot.log'),
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
        },
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console', 'file'],
    },
}

# ============================================================================
# WORKFLOW CONFIGURATION
# ============================================================================

# Workflow channel naming
WORKFLOW_CHANNEL = {
    'auto_create': True,           # Auto-create channels for new workflows
    'prefix': '',                  # Prefix for channel names (e.g., 'wf-')
    'use_lowercase': True,         # Convert workflow names to lowercase
    'replace_spaces': '-',         # Replace spaces with this character
    'max_name_length': 100,        # Maximum channel name length
}

# Workflow file extensions
WORKFLOW_EXTENSIONS = ['.json']

# ============================================================================
# MODAL CLI COMMANDS
# ============================================================================

# Modal CLI command templates
MODAL_COMMANDS = {
    'profile_list': 'modal profile list',
    'profile_current': 'modal profile current',
    'profile_activate': 'modal profile activate {profile_name}',
    'profile_create': 'modal profile create {profile_name}',
    'token_set': 'modal token set --token-id {token_id} --token-secret {token_secret}',
    'deploy': 'modal deploy {file_path}',
    'run': 'modal run {file_path}',
    'app_stop': 'modal app stop {app_name}',
    'volume_ls': 'modal volume ls {volume_name} {path}',
    'volume_get': 'modal volume get {volume_name} {remote_path} {local_path}',
}

# ============================================================================
# API REQUEST CONFIGURATION
# ============================================================================

# HTTP request timeout (in seconds)
REQUEST_TIMEOUT = 30

# Maximum retries for failed requests
MAX_RETRIES = 3

# Retry delay (in seconds)
RETRY_DELAY = 5

# ============================================================================
# FEATURE FLAGS
# ============================================================================

# Enable/disable features (useful for testing)
FEATURES = {
    'auto_credit_check': True,      # Automatically check credits every hour
    'auto_switch_accounts': True,   # Automatically switch accounts when low
    'auto_create_channels': True,   # Auto-create workflow channels
    'send_dm_alerts': True,         # Send DM alerts to owner
    'track_usage_stats': True,      # Track generation statistics
}

# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def validate_config():
    """Validate configuration settings on startup."""
    errors = []
    
    # Check Discord token
    if not DISCORD_TOKEN:
        errors.append("DISCORD_BOT_TOKEN environment variable not set")
    
    # Check owner ID
    if not OWNER_ID:
        errors.append("DISCORD_OWNER_ID environment variable not set")
    
    # Check Modal files exist
    for name, path in MODAL_FILES.items():
        if not path.exists():
            errors.append(f"Modal file not found: {path}")
    
    # Check credit threshold is valid
    if MIN_CREDIT_THRESHOLD < 0:
        errors.append("MIN_CREDIT_THRESHOLD must be positive")
    
    # Check max accounts is valid
    if MAX_ACCOUNTS < 1 or MAX_ACCOUNTS > 10:
        errors.append("MAX_ACCOUNTS must be between 1 and 10")
    
    if errors:
        raise ValueError("Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors))
    
    return True

def get_modal_command(command_name, **kwargs):
    """Get a formatted Modal CLI command."""
    template = MODAL_COMMANDS.get(command_name)
    if not template:
        raise ValueError(f"Unknown Modal command: {command_name}")
    return template.format(**kwargs)

# ============================================================================
# INITIALIZATION
# ============================================================================

def initialize():
    """Initialize configuration (create directories, etc.)."""
    # Create required directories
    LOGS_DIR.mkdir(exist_ok=True)
    TEMP_DIR.mkdir(exist_ok=True)
    
    # Generate encryption key if it doesn't exist
    if not ENCRYPTION_KEY_FILE.exists():
        from cryptography.fernet import Fernet
        key = Fernet.generate_key()
        ENCRYPTION_KEY_FILE.write_bytes(key)
        print(f"Generated encryption key: {ENCRYPTION_KEY_FILE}")
    
    print("Configuration initialized successfully!")

# ============================================================================
# ENVIRONMENT VARIABLE HELPERS
# ============================================================================

def load_env_file():
    """Load environment variables from .env file if it exists."""
    env_file = BASE_DIR / '.env'
    if env_file.exists():
        from dotenv import load_dotenv
        load_dotenv(env_file)
        print(f"Loaded environment variables from {env_file}")
    else:
        print("No .env file found. Make sure to set environment variables manually.")

# Auto-load .env on import
load_env_file()

# ============================================================================
# END OF CONFIGURATION
# ============================================================================
