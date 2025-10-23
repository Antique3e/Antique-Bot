"""
UI Configuration File
=====================
This file controls ALL visual elements of the Discord bot.
Change colors, icons, layouts, and text here - no need to touch other files!

To modify UI: Send ONLY this file to any AI and ask for changes.
"""

# ============================================================================
# COLOR PALETTE (Discord Hex Colors)
# ============================================================================

COLORS = {
    # Account Status Colors
    'active': 0x57F287,        # Bright Green - Currently running account
    'ready': 0x5865F2,         # Discord Blurple - Account with credits
    'dead': 0x747F8D,          # Gray - Account with < $2
    'building': 0xFEE75C,      # Yellow - Account being set up
    
    # Message Types
    'success': 0x57F287,       # Green - Success messages
    'warning': 0xFEE75C,       # Yellow - Warnings
    'error': 0xED4245,         # Red - Errors
    'info': 0x5865F2,          # Blue - Information
    'progress': 0xEB459E,      # Pink - Progress updates
    
    # Special Elements
    'embed_background': 0x2B2D31,   # Dark gray for embed backgrounds
    'button_primary': 0x5865F2,     # Primary button color
    'button_success': 0x57F287,     # Success button color
    'button_danger': 0xED4245,      # Danger button color
}

# ============================================================================
# EMOJIS & ICONS
# ============================================================================

ICONS = {
    # Status Icons
    'active': '✅',           # Active account
    'ready': '🟢',            # Ready account
    'dead': '⚫',             # Dead account
    'building': '🔧',         # Building/Setup in progress
    'switching': '🔄',        # Switching accounts
    
    # Action Icons
    'start': '▶️',            # Start server
    'stop': '⏹️',             # Stop server
    'restart': '🔁',          # Restart server
    'settings': '⚙️',         # Settings
    'add': '➕',              # Add account
    'remove': '➖',           # Remove account
    'edit': '✏️',             # Edit
    'save': '💾',             # Save
    
    # Progress Icons
    'loading': '⏳',          # Loading/Processing
    'success': '✅',          # Success
    'warning': '⚠️',          # Warning
    'error': '❌',            # Error
    'clock': '⏱️',            # Timer
    
    # GPU Icons
    'gpu': '🖥️',             # GPU selector
    'fire': '🔥',             # High-end GPU
    'bolt': '⚡',             # Fast GPU
    
    # Credit Icons
    'credits': '💰',          # Credits/Money
    'low_balance': '⚠️',      # Low balance warning
    
    # Output Icons
    'image': '🖼️',           # Generated image
    'video': '🎬',            # Generated video
    'folder': '📁',           # Output folder
    'download': '⬇️',         # Download file
}

# Battery Icons (Credit Display)
BATTERY_ICONS = {
    'full': '🔋🔋🔋🔋🔋',      # 80-100%
    'high': '🔋🔋🔋🔋⚪',      # 60-79%
    'medium': '🔋🔋🔋⚪⚪',    # 40-59%
    'low': '🔋🔋⚪⚪⚪',        # 20-39%
    'critical': '🔋⚪⚪⚪⚪',    # 0-19%
}

# ============================================================================
# TEXT FORMATTING
# ============================================================================

FONTS = {
    'title': '**{}**',                    # Bold
    'subtitle': '*{}*',                    # Italic
    'code': '`{}`',                        # Inline code
    'code_block': '```{}```',              # Code block
    'bold_italic': '***{}***',             # Bold + Italic
    'underline': '__{}__',                 # Underline
    'strikethrough': '~~{}~~',             # Strikethrough
}

# Text Sizes (using Discord markdown)
TEXT_SIZE = {
    'large': '# {}',          # Heading 1
    'medium': '## {}',        # Heading 2
    'small': '### {}',        # Heading 3
}

# ============================================================================
# BUTTON CONFIGURATIONS
# ============================================================================

BUTTON_STYLE = {
    'primary': 'blurple',     # Discord's primary color (blue)
    'success': 'green',       # Green buttons
    'danger': 'red',          # Red buttons
    'secondary': 'gray',      # Gray buttons
}

BUTTON_POSITIONS = {
    'cancel': 'left',         # Cancel button position
    'submit': 'right',        # Submit button position
}

# Button Labels
BUTTON_LABELS = {
    'start_comfy': 'Start ComfyUI',
    'stop_comfy': 'Stop ComfyUI',
    'add_account': 'Add Account',
    'list_accounts': 'View Accounts',
    'switch_account': 'Switch Account',
    'select_gpu': 'Select GPU',
    'change_gpu': 'Change GPU',
    'generate': 'Generate Image',
    'list_outputs': 'View Outputs',
    'cancel': 'Cancel',
    'submit': 'Submit',
    'confirm': 'Confirm',
}

# ============================================================================
# EMBED LAYOUTS
# ============================================================================

EMBED_CONFIG = {
    # Standard embed settings
    'show_timestamp': True,           # Show timestamp on embeds
    'show_footer': True,              # Show footer on embeds
    'footer_text': 'ComfyUI Control Panel',
    'footer_icon': '🤖',
    
    # Thumbnail settings
    'show_thumbnail': True,
    'thumbnail_url': None,            # Set to image URL if you have a logo
    
    # Author settings
    'show_author': False,
    'author_name': 'ComfyUI Bot',
    'author_icon': None,
}

# Account List Layout
ACCOUNT_LIST_LAYOUT = {
    'max_accounts_per_page': 6,       # Show 6 accounts max (your limit)
    'show_balance': True,             # Show credit balance
    'show_battery': True,             # Show battery icon
    'show_status': True,              # Show status (active/ready/dead)
    'separator': '─' * 40,            # Visual separator
}

# GPU Selector Layout
GPU_SELECTOR_LAYOUT = {
    'show_price': True,               # Show price per hour
    'show_description': False,        # Show GPU description
    'highlight_selected': True,       # Highlight currently selected GPU
    'sort_by': 'price',              # Sort by: 'price', 'name', or 'performance'
}

# ============================================================================
# NOTIFICATION MESSAGES
# ============================================================================

MESSAGES = {
    # Success Messages
    'comfy_started': '{icon} **ComfyUI Started!**\n\n{jupyter} JupyterLab: {jupyter_url}\n{comfy} ComfyUI: {comfy_url}',
    'comfy_stopped': '{icon} ComfyUI stopped successfully.',
    'account_added': '{icon} Account **{username}** added successfully!',
    'account_switched': '{icon} Switched to account **{username}**.',
    'gpu_changed': '{icon} GPU changed to **{gpu}** (${price}/h)',
    
    # Warning Messages
    'low_balance': '{icon} **Warning: Low Balance!**\n\nAccount **{username}** has ${balance} left.\n{clock} You have **20 minutes** before automatic switch.',
    'switching_soon': '{icon} **Switching in {minutes} minutes...**\n\nFinish your current work!',
    
    # Progress Messages
    'building_account': '{icon} **Building on {username}...**\n\n{progress} Setup Progress: {percent}%\n{clock} Estimated time: {time_left}',
    'setup_complete': '{icon} **Setup Complete!**\n\nAccount **{username}** is ready.\nUse `/start` to begin.',
    
    # Error Messages
    'max_accounts': '{icon} Cannot add more accounts. Maximum limit: **6 accounts**.',
    'account_not_found': '{icon} Account **{username}** not found.',
    'insufficient_credits': '{icon} Account **{username}** has insufficient credits (${balance}).',
    'comfy_not_running': '{icon} ComfyUI is not running. Use `/start` first.',
    
    # Info Messages
    'checking_credits': '{icon} Checking account balances...',
    'generating_image': '{icon} Generating image with workflow **{workflow}**...',
    'image_ready': '{icon} **Image Generated!**\n\nWorkflow: {workflow}\nTime: {time}s',
}

# ============================================================================
# PROGRESS BAR
# ============================================================================

PROGRESS_BAR = {
    'length': 20,                     # Number of characters in progress bar
    'filled_char': '█',               # Character for filled portion
    'empty_char': '░',                # Character for empty portion
    'show_percentage': True,          # Show percentage number
    'style': '[{bar}] {percent}%',    # Progress bar format
}

# ============================================================================
# CREDIT DISPLAY
# ============================================================================

CREDIT_CONFIG = {
    'currency_symbol': '$',           # Currency symbol
    'decimal_places': 2,              # Number of decimal places
    'show_battery': True,             # Show battery icon
    'battery_thresholds': {           # When to show which battery level
        'full': 64,      # > $64 (80% of $80)
        'high': 48,      # > $48 (60% of $80)
        'medium': 32,    # > $32 (40% of $80)
        'low': 16,       # > $16 (20% of $80)
        'critical': 0,   # <= $16
    },
    'low_balance_threshold': 2.0,     # Trigger warning at $2
}

# ============================================================================
# MODAL (POPUP) CONFIGURATIONS
# ============================================================================

MODAL_CONFIG = {
    # Add Account Modal
    'add_account': {
        'title': 'Add Modal Account',
        'fields': [
            {
                'label': 'Username',
                'placeholder': 'account_name',
                'required': True,
                'max_length': 50,
            },
            {
                'label': 'Token ID',
                'placeholder': 'ak-xxxxxxxxxxxxx',
                'required': True,
                'max_length': 100,
            },
            {
                'label': 'Token Secret',
                'placeholder': 'as-xxxxxxxxxxxxx',
                'required': True,
                'max_length': 100,
            },
        ],
    },
    
    # Generate Image Modal
    'generate': {
        'title': 'Generate Image',
        'fields': [
            {
                'label': 'Workflow Name',
                'placeholder': 'seedream',
                'required': True,
                'max_length': 50,
            },
            {
                'label': 'Prompt',
                'placeholder': 'a beautiful sunset over mountains',
                'required': True,
                'max_length': 1000,
                'style': 'paragraph',  # Multi-line input
            },
        ],
    },
}

# ============================================================================
# TIMING CONFIGURATIONS
# ============================================================================

TIMING = {
    'credit_check_interval': 3600,    # Check credits every 1 hour (in seconds)
    'switch_warning_time': 1200,      # Warn 20 minutes before switch (20 * 60)
    'setup_estimate_step1': 7200,     # Step 1 takes ~2 hours (in seconds)
    'setup_estimate_step2': 1200,     # Step 2 takes ~20 minutes (in seconds)
    'comfy_startup_timeout': 300,     # Wait max 5 minutes for ComfyUI to start
}

# ============================================================================
# GPU CONFIGURATIONS
# ============================================================================

GPU_OPTIONS = [
    {'name': 'T4', 'price': 0.59, 'emoji': '💚'},
    {'name': 'L4', 'price': 0.80, 'emoji': '💙'},
    {'name': 'A10', 'price': 1.10, 'emoji': '💜'},
    {'name': 'L40S', 'price': 1.95, 'emoji': '🧡'},
    {'name': 'A100, 40 GB', 'price': 2.10, 'emoji': '❤️'},
    {'name': 'A100, 80 GB', 'price': 2.50, 'emoji': '💗'},
    {'name': 'H100', 'price': 3.95, 'emoji': '🔥'},
    {'name': 'H200', 'price': 4.54, 'emoji': '⚡'},
    {'name': 'B200', 'price': 6.25, 'emoji': '💎'},
]

# Default GPU for setup
DEFAULT_SETUP_GPU = 'T4'

# ============================================================================
# CHANNEL CONFIGURATIONS
# ============================================================================

CHANNEL_CONFIG = {
    'auto_create': True,              # Auto-create workflow channels
    'channel_prefix': '',             # Prefix for channel names (e.g., 'wf-')
    'channel_category': 'ComfyUI Outputs',  # Category name for workflow channels
    'use_lowercase': True,            # Convert workflow names to lowercase
    'replace_spaces': '-',            # Replace spaces in workflow names with this
}

# ============================================================================
# HELPER FUNCTIONS (DO NOT EDIT UNLESS YOU KNOW WHAT YOU'RE DOING)
# ============================================================================

def get_battery_icon(balance, max_balance=80.0):
    """Get battery icon based on credit balance."""
    percentage = (balance / max_balance) * 100
    
    thresholds = CREDIT_CONFIG['battery_thresholds']
    if percentage >= thresholds['full']:
        return BATTERY_ICONS['full']
    elif percentage >= thresholds['high']:
        return BATTERY_ICONS['high']
    elif percentage >= thresholds['medium']:
        return BATTERY_ICONS['medium']
    elif percentage >= thresholds['low']:
        return BATTERY_ICONS['low']
    else:
        return BATTERY_ICONS['critical']

def format_currency(amount):
    """Format currency with symbol and decimal places."""
    symbol = CREDIT_CONFIG['currency_symbol']
    places = CREDIT_CONFIG['decimal_places']
    return f"{symbol}{amount:.{places}f}"

def create_progress_bar(current, total):
    """Create a visual progress bar."""
    config = PROGRESS_BAR
    percentage = int((current / total) * 100)
    filled = int((current / total) * config['length'])
    bar = config['filled_char'] * filled + config['empty_char'] * (config['length'] - filled)
    
    if config['show_percentage']:
        return config['style'].format(bar=bar, percent=percentage)
    return f"[{bar}]"

def get_status_color(status):
    """Get color for account status."""
    status_colors = {
        'active': COLORS['active'],
        'ready': COLORS['ready'],
        'dead': COLORS['dead'],
        'building': COLORS['building'],
    }
    return status_colors.get(status, COLORS['info'])

def get_status_icon(status):
    """Get icon for account status."""
    status_icons = {
        'active': ICONS['active'],
        'ready': ICONS['ready'],
        'dead': ICONS['dead'],
        'building': ICONS['building'],
    }
    return status_icons.get(status, ICONS['info'])

# ============================================================================
# END OF UI CONFIGURATION
# ============================================================================
