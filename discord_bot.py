"""
ComfyUI Discord Bot
===================
Main Discord bot that controls Modal ComfyUI deployments.

Features:
- Add/manage multiple Modal accounts
- Auto-switch accounts when credits low
- Start/stop ComfyUI with GPU selection
- Generate images via workflows
- Auto-create workflow channels
"""

import discord
from discord import option
from discord.ext import commands, tasks
import asyncio
import logging
import sys
from datetime import datetime, timedelta
from typing import Optional
from pathlib import Path

# Import our modules
import config
import utils
from ui_config import COLORS, ICONS, MESSAGES, BUTTON_LABELS, get_battery_icon, format_currency
from account_manager import account_manager
from modal_manager import modal_manager
from workflow_manager import initialize_workflow_manager, workflow_manager as wf_manager

# Setup logging
logging.config.dictConfig(config.LOGGING)
logger = logging.getLogger(__name__)

# ============================================================================
# BOT INITIALIZATION
# ============================================================================

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = discord.Bot(intents=intents)

# Initialize workflow manager with bot
workflow_manager = None

# Track warnings sent (to avoid spam)
warning_sent = {}
switch_timers = {}

# ============================================================================
# BOT EVENTS
# ============================================================================

@bot.event
async def on_ready():
    """Called when bot is ready."""
    global workflow_manager
    
    logger.info(f"Bot logged in as {bot.user}")
    logger.info(f"Connected to {len(bot.guilds)} guild(s)")
    
    # Initialize workflow manager
    workflow_manager = initialize_workflow_manager(bot)
    
    # Validate configuration
    try:
        config.validate_config()
        logger.info("Configuration validated successfully")
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    
    # Start background tasks
    if config.FEATURES['auto_credit_check']:
        credit_checker.start()
        logger.info("Credit checker task started")
    
    # Refresh workflow channels on startup
    for guild in bot.guilds:
        try:
            await workflow_manager.refresh_workflow_channels(guild)
            logger.info(f"Refreshed workflow channels for {guild.name}")
        except Exception as e:
            logger.error(f"Failed to refresh channels for {guild.name}: {e}")
    
    logger.info("Bot is ready!")

@bot.event
async def on_application_command_error(ctx: discord.ApplicationContext, error: discord.DiscordException):
    """Handle command errors."""
    logger.error(f"Command error in {ctx.command.name}: {error}")
    
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.respond(f"⏱️ Command on cooldown. Try again in {error.retry_after:.1f}s", ephemeral=True)
    elif isinstance(error, commands.MissingPermissions):
        await ctx.respond("❌ You don't have permission to use this command.", ephemeral=True)
    else:
        await ctx.respond(f"❌ An error occurred: {str(error)}", ephemeral=True)

# ============================================================================
# BACKGROUND TASKS
# ============================================================================

@tasks.loop(seconds=config.CREDIT_CHECK_INTERVAL)
async def credit_checker():
    """Background task to check account credits periodically."""
    logger.info("Running credit check...")
    
    try:
        active_account = account_manager.get_active_account()
        
        if not active_account:
            logger.info("No active account, skipping credit check")
            return
        
        # Check balance
        balance = await modal_manager.check_balance(active_account['username'])
        
        if balance is None:
            logger.warning(f"Failed to check balance for {active_account['username']}")
            return
        
        logger.info(f"Account '{active_account['username']}' balance: ${balance:.2f}")
        
        # Check if below threshold
        if balance < config.MIN_CREDIT_THRESHOLD:
            logger.warning(f"Account '{active_account['username']}' below threshold!")
            
            # Check if we already sent a warning
            username = active_account['username']
            if username not in warning_sent:
                # Send warning and start timer
                await send_low_balance_warning(active_account, balance)
                warning_sent[username] = True
                
                # Start 20-minute countdown
                asyncio.create_task(handle_auto_switch(active_account))
        
    except Exception as e:
        logger.error(f"Error in credit checker: {e}")

async def send_low_balance_warning(account: dict, balance: float):
    """Send low balance warning to owner."""
    try:
        owner = await bot.fetch_user(int(config.OWNER_ID))
        
        embed = discord.Embed(
            title=f"{ICONS['warning']} Low Balance Warning",
            description=MESSAGES['low_balance'].format(
                icon=ICONS['warning'],
                username=account['username'],
                balance=format_currency(balance),
                clock=ICONS['clock']
            ),
            color=COLORS['warning']
        )
        
        embed.add_field(
            name="Next Action",
            value=f"In **20 minutes**, the bot will:\n"
                  f"1. Stop ComfyUI on `{account['username']}`\n"
                  f"2. Switch to next available account\n"
                  f"3. Start setup on new account",
            inline=False
        )
        
        if config.FEATURES['send_dm_alerts']:
            await owner.send(embed=embed)
            logger.info("Sent low balance warning to owner")
        
    except Exception as e:
        logger.error(f"Failed to send warning: {e}")

async def handle_auto_switch(account: dict):
    """Handle automatic account switching after 20 minute timer."""
    username = account['username']
    logger.info(f"Starting 20-minute countdown for account '{username}'")
    
    # Wait 20 minutes
    await asyncio.sleep(config.SWITCH_WARNING_TIME)
    
    logger.info(f"Timer expired for '{username}', switching accounts...")
    
    try:
        # Stop current ComfyUI
        await modal_manager.stop_comfyui()
        logger.info(f"Stopped ComfyUI on '{username}'")
        
        # Update status
        account_manager.update_status(username, 'dead')
        
        # Find next available account
        success, msg, next_account = await modal_manager.switch_to_next_available_account()
        
        if not success:
            logger.error(f"No available accounts to switch to: {msg}")
            await notify_owner(
                "❌ No Available Accounts",
                f"Failed to switch from `{username}`: {msg}\n\n"
                "Please add more accounts or add credits to existing accounts.",
                COLORS['error']
            )
            return
        
        # Notify owner about switch
        await notify_owner(
            f"{ICONS['switching']} Account Switched",
            f"Switched from `{username}` to `{next_account['username']}`\n\n"
            f"Starting setup on new account...",
            COLORS['info']
        )
        
        # Start setup on new account
        await run_full_setup(next_account['username'])
        
        # Clear warning flag
        if username in warning_sent:
            del warning_sent[username]
        
    except Exception as e:
        logger.error(f"Error during auto-switch: {e}")
        await notify_owner(
            "❌ Auto-Switch Failed",
            f"Error switching from `{username}`: {str(e)}",
            COLORS['error']
        )

async def run_full_setup(username: str):
    """Run full setup (step 1 + step 2) on an account."""
    logger.info(f"Running full setup for '{username}'")
    
    try:
        # Notify setup started
        await notify_owner(
            f"{ICONS['building']} Setup Started",
            f"Starting setup on account `{username}`...\n\n"
            f"⏱️ Estimated time: 2 hours 20 minutes\n"
            f"Step 1: Download models (2h)\n"
            f"Step 2: Install dependencies (20m)",
            COLORS['building']
        )
        
        # Run step 1
        success, msg = await modal_manager.deploy_setup_step1(username)
        if not success:
            await notify_owner(
                "❌ Setup Step 1 Failed",
                f"Account: `{username}`\nError: {msg}",
                COLORS['error']
            )
            return
        
        logger.info(f"Setup step 1 completed for '{username}'")
        
        # Run step 2
        success, msg = await modal_manager.deploy_setup_step2(username)
        if not success:
            await notify_owner(
                "❌ Setup Step 2 Failed",
                f"Account: `{username}`\nError: {msg}",
                COLORS['error']
            )
            return
        
        logger.info(f"Setup step 2 completed for '{username}'")
        
        # Notify completion
        jupyter_url = config.CLOUDFLARE_URLS['jupyter']
        comfyui_url = config.CLOUDFLARE_URLS['comfyui']
        
        await notify_owner(
            f"{ICONS['success']} Setup Complete!",
            f"Account `{username}` is ready!\n\n"
            f"{ICONS['success']} JupyterLab: {jupyter_url}\n"
            f"{ICONS['success']} ComfyUI: {comfyui_url}\n\n"
            f"Use `/start` to begin using ComfyUI.",
            COLORS['success']
        )
        
    except Exception as e:
        logger.error(f"Error during setup for '{username}': {e}")
        await notify_owner(
            "❌ Setup Failed",
            f"Account: `{username}`\nError: {str(e)}",
            COLORS['error']
        )

async def notify_owner(title: str, description: str, color: int):
    """Send notification to bot owner."""
    try:
        owner = await bot.fetch_user(int(config.OWNER_ID))
        embed = discord.Embed(title=title, description=description, color=color)
        await owner.send(embed=embed)
    except Exception as e:
        logger.error(f"Failed to notify owner: {e}")

# ============================================================================
# MODAL MANAGEMENT COMMANDS
# ============================================================================

@bot.slash_command(name="add_account", description="Add a new Modal account")
async def add_account(ctx: discord.ApplicationContext):
    """Add a new Modal account via popup form."""
    
    # Check if max accounts reached
    if account_manager.get_account_count() >= config.MAX_ACCOUNTS:
        await ctx.respond(
            f"{ICONS['error']} Maximum account limit reached ({config.MAX_ACCOUNTS} accounts).",
            ephemeral=True
        )
        return
    
    # Create modal popup
    class AddAccountModal(discord.ui.Modal):
        def __init__(self):
            super().__init__(title="Add Modal Account")
            
            self.add_item(discord.ui.InputText(
                label="Username",
                placeholder="account_name",
                required=True,
                max_length=50
            ))
            
            self.add_item(discord.ui.InputText(
                label="Token ID",
                placeholder="ak-xxxxxxxxxxxxx",
                required=True,
                max_length=100
            ))
            
            self.add_item(discord.ui.InputText(
                label="Token Secret",
                placeholder="as-xxxxxxxxxxxxx",
                required=True,
                max_length=100
            ))
        
        async def callback(self, interaction: discord.Interaction):
            username = self.children[0].value
            token_id = self.children[1].value
            token_secret = self.children[2].value
            
            # Add account
            success, msg = account_manager.add_account(username, token_id, token_secret)
            
            if success:
                # Create Modal profile
                success2, msg2 = await modal_manager.create_profile(username, token_id, token_secret)
                
                if success2:
                    embed = discord.Embed(
                        title=f"{ICONS['success']} Account Added",
                        description=f"Account `{username}` added successfully!\n\n"
                                    f"Balance: {format_currency(config.INITIAL_BALANCE)}\n"
                                    f"Status: Ready",
                        color=COLORS['success']
                    )
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                else:
                    await interaction.response.send_message(
                        f"{ICONS['warning']} Account added to database but Modal profile creation failed: {msg2}",
                        ephemeral=True
                    )
            else:
                await interaction.response.send_message(
                    f"{ICONS['error']} {msg}",
                    ephemeral=True
                )
    
    await ctx.send_modal(AddAccountModal())

@bot.slash_command(name="list_accounts", description="View all Modal accounts")
async def list_accounts(ctx: discord.ApplicationContext):
    """List all Modal accounts with balances."""
    await ctx.defer()
    
    accounts = account_manager.get_all_accounts()
    
    if not accounts:
        await ctx.respond("No accounts found. Use `/add_account` to add one!", ephemeral=True)
        return
    
    # Create embed
    embed = discord.Embed(
        title=f"{ICONS['credits']} Modal Accounts",
        color=COLORS['info']
    )
    
    for account in accounts:
        username = account['username']
        balance = account['balance']
        status = account['status']
        is_active = account['is_active']
        selected_gpu = account['selected_gpu'] or 'Not set'
        
        # Get status icon and color
        status_icon = ICONS['active'] if is_active else ICONS[status]
        battery = get_battery_icon(balance)
        
        # Format status text
        status_text = "**ACTIVE**" if is_active else status.upper()
        
        value = (
            f"{status_icon} Status: {status_text}\n"
            f"{battery} Balance: {format_currency(balance)}\n"
            f"{ICONS['gpu']} GPU: {selected_gpu}"
        )
        
        embed.add_field(name=username, value=value, inline=True)
    
    # Add total balance
    total = account_manager.get_total_balance()
    embed.set_footer(text=f"Total Balance: {format_currency(total)}")
    
    await ctx.respond(embed=embed)

@bot.slash_command(name="switch_account", description="Switch to a different Modal account")
@option("username", description="Account to switch to", required=True)
async def switch_account(ctx: discord.ApplicationContext, username: str):
    """Manually switch to a different account."""
    await ctx.defer()
    
    success, msg = await modal_manager.switch_to_account(username)
    
    if success:
        embed = discord.Embed(
            title=f"{ICONS['switching']} Account Switched",
            description=f"Switched to account `{username}`",
            color=COLORS['success']
        )
        await ctx.respond(embed=embed)
    else:
        await ctx.respond(f"{ICONS['error']} {msg}", ephemeral=True)

@bot.slash_command(name="check_balance", description="Check credit balance for all accounts")
async def check_balance(ctx: discord.ApplicationContext):
    """Check credit balances for all accounts."""
    await ctx.defer()
    
    embed = discord.Embed(
        title=f"{ICONS['loading']} Checking Balances...",
        description="This may take a moment...",
        color=COLORS['info']
    )
    message = await ctx.respond(embed=embed)
    
    # Check all balances
    balances = await modal_manager.check_all_balances()
    
    if not balances:
        await message.edit(content=f"{ICONS['error']} Failed to check balances", embed=None)
        return
    
    # Update embed with results
    embed = discord.Embed(
        title=f"{ICONS['credits']} Account Balances",
        color=COLORS['success']
    )
    
    for username, balance in balances.items():
        battery = get_battery_icon(balance)
        account = account_manager.get_account_by_username(username)
        status_icon = ICONS[account['status']]
        
        embed.add_field(
            name=username,
            value=f"{status_icon} {battery} {format_currency(balance)}",
            inline=True
        )
    
    total = sum(balances.values())
    embed.set_footer(text=f"Total Balance: {format_currency(total)}")
    
    await message.edit(embed=embed)

# ============================================================================
# COMFYUI CONTROL COMMANDS
# ============================================================================

@bot.slash_command(name="start", description="Start ComfyUI")
async def start_comfyui(ctx: discord.ApplicationContext):
    """Start ComfyUI with GPU selection."""
    await ctx.defer()
    
    active_account = account_manager.get_active_account()
    
    if not active_account:
        await ctx.respond(
            f"{ICONS['error']} No active account. Use `/switch_account` to activate one.",
            ephemeral=True
        )
        return
    
    # Create GPU selection view
    class GPUSelectView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=60)
            
            # Create select menu
            from ui_config import GPU_OPTIONS
            
            options = []
            for gpu in GPU_OPTIONS:
                options.append(discord.SelectOption(
                    label=f"{gpu['name']} - ${gpu['price']}/h",
                    value=gpu['name'],
                    emoji=gpu['emoji'],
                    description=f"${gpu['price']} per hour"
                ))
            
            select = discord.ui.Select(
                placeholder="Select GPU...",
                options=options
            )
            select.callback = self.select_callback
            self.add_item(select)
            self.selected_gpu = None
        
        async def select_callback(self, interaction: discord.Interaction):
            self.selected_gpu = interaction.data['values'][0]
            
            await interaction.response.edit_message(
                content=f"{ICONS['loading']} Starting ComfyUI on {self.selected_gpu}...",
                view=None
            )
            
            # Start ComfyUI
            success, msg = await modal_manager.start_comfyui(active_account['username'], self.selected_gpu)
            
            if success:
                jupyter_url = config.CLOUDFLARE_URLS['jupyter']
                comfyui_url = config.CLOUDFLARE_URLS['comfyui']
                
                embed = discord.Embed(
                    title=f"{ICONS['success']} ComfyUI Started!",
                    description=MESSAGES['comfy_started'].format(
                        icon=ICONS['success'],
                        jupyter=ICONS['success'],
                        jupyter_url=jupyter_url,
                        comfy=ICONS['success'],
                        comfy_url=comfyui_url
                    ),
                    color=COLORS['success']
                )
                embed.add_field(name="GPU", value=self.selected_gpu, inline=True)
                embed.add_field(name="Account", value=active_account['username'], inline=True)
                
                await interaction.edit_original_response(content=None, embed=embed)
            else:
                await interaction.edit_original_response(
                    content=f"{ICONS['error']} {msg}",
                    embed=None
                )
    
    view = GPUSelectView()
    embed = discord.Embed(
        title=f"{ICONS['gpu']} Select GPU",
        description=f"Account: `{active_account['username']}`\n\n"
                    "Choose a GPU to start ComfyUI:",
        color=COLORS['info']
    )
    
    await ctx.respond(embed=embed, view=view)

@bot.slash_command(name="stop", description="Stop ComfyUI")
async def stop_comfyui(ctx: discord.ApplicationContext):
    """Stop the currently running ComfyUI."""
    await ctx.defer()
    
    success, msg = await modal_manager.stop_comfyui()
    
    if success:
        embed = discord.Embed(
            title=f"{ICONS['stop']} ComfyUI Stopped",
            description=msg,
            color=COLORS['success']
        )
        await ctx.respond(embed=embed)
    else:
        await ctx.respond(f"{ICONS['error']} {msg}", ephemeral=True)

@bot.slash_command(name="status", description="Check ComfyUI status")
async def status(ctx: discord.ApplicationContext):
    """Check current ComfyUI status."""
    await ctx.defer()
    
    active_account = account_manager.get_active_account()
    
    if not active_account:
        await ctx.respond("No active account.", ephemeral=True)
        return
    
    embed = discord.Embed(
        title=f"{ICONS['info']} ComfyUI Status",
        color=COLORS['info']
    )
    
    embed.add_field(name="Active Account", value=active_account['username'], inline=True)
    embed.add_field(name="Balance", value=format_currency(active_account['balance']), inline=True)
    embed.add_field(name="Status", value=active_account['status'].upper(), inline=True)
    
    if active_account['selected_gpu']:
        embed.add_field(name="Selected GPU", value=active_account['selected_gpu'], inline=True)
    
    # Check if ComfyUI is reachable
    comfyui_url = config.CLOUDFLARE_URLS['comfyui']
    is_ready = await utils.check_comfyui_ready(comfyui_url)
    
    embed.add_field(
        name="ComfyUI Status",
        value=f"{ICONS['success']} Running" if is_ready else f"{ICONS['error']} Not Running",
        inline=True
    )
    
    if is_ready:
        embed.add_field(name="ComfyUI URL", value=comfyui_url, inline=False)
        embed.add_field(name="JupyterLab URL", value=config.CLOUDFLARE_URLS['jupyter'], inline=False)
    
    await ctx.respond(embed=embed)

# ============================================================================
# IMAGE GENERATION COMMANDS
# ============================================================================

@bot.slash_command(name="generate", description="Generate an image with ComfyUI")
async def generate(ctx: discord.ApplicationContext):
    """Generate an image using a workflow."""
    
    # Create modal for generation
    class GenerateModal(discord.ui.Modal):
        def __init__(self):
            super().__init__(title="Generate Image")
            
            self.add_item(discord.ui.InputText(
                label="Workflow Name",
                placeholder="seedream",
                required=True,
                max_length=50
            ))
            
            self.add_item(discord.ui.InputText(
                label="Prompt",
                placeholder="a beautiful sunset over mountains",
                required=True,
                style=discord.InputTextStyle.paragraph,
                max_length=1000
            ))
        
        async def callback(self, interaction: discord.Interaction):
            workflow_name = self.children[0].value
            prompt = self.children[1].value
            
            await interaction.response.defer()
            
            # Generate
            success, msg, response = await workflow_manager.generate_with_workflow(workflow_name, prompt)
            
            if success:
                embed = discord.Embed(
                    title=f"{ICONS['loading']} Generating...",
                    description=f"Workflow: `{workflow_name}`\n"
                                f"Prompt: {prompt[:100]}...",
                    color=COLORS['progress']
                )
                await interaction.followup.send(embed=embed)
                
                # Note: In real implementation, you'd need to poll ComfyUI
                # for completion and then download the output
            else:
                await interaction.followup.send(f"{ICONS['error']} {msg}", ephemeral=True)
    
    await ctx.send_modal(GenerateModal())

@bot.slash_command(name="list_outputs", description="List generated outputs")
async def list_outputs(ctx: discord.ApplicationContext):
    """List all output files."""
    await ctx.defer()
    
    outputs = await workflow_manager.list_all_outputs()
    
    if not outputs:
        await ctx.respond("No outputs found.", ephemeral=True)
        return
    
    # Create embed with list of outputs
    embed = discord.Embed(
        title=f"{ICONS['folder']} Generated Outputs",
        description=f"Total: {len(outputs)} files",
        color=COLORS['info']
    )
    
    # Show first 25 (Discord field limit)
    for output in outputs[:25]:
        embed.add_field(name=output, value="Use `/get_output` to download", inline=False)
    
    if len(outputs) > 25:
        embed.set_footer(text=f"Showing 25 of {len(outputs)} files")
    
    await ctx.respond(embed=embed)

@bot.slash_command(name="get_output", description="Download an output file")
@option("filename", description="Output filename", required=True)
async def get_output(ctx: discord.ApplicationContext, filename: str):
    """Download an output file."""
    await ctx.defer()
    
    # Download file
    file_path = await modal_manager.get_output_file(filename)
    
    if not file_path:
        await ctx.respond(f"{ICONS['error']} File not found: {filename}", ephemeral=True)
        return
    
    # Check size
    size_mb = utils.get_file_size_mb(file_path)
    if size_mb > config.MAX_DISCORD_FILE_SIZE:
        await ctx.respond(
            f"{ICONS['error']} File too large: {size_mb:.1f}MB (max: {config.MAX_DISCORD_FILE_SIZE}MB)",
            ephemeral=True
        )
        return
    
    # Send file
    try:
        file = discord.File(file_path)
        await ctx.respond(file=file)
    except Exception as e:
        logger.error(f"Failed to send file: {e}")
        await ctx.respond(f"{ICONS['error']} Failed to send file", ephemeral=True)

# ============================================================================
# SETUP COMMANDS
# ============================================================================

@bot.slash_command(name="setup", description="Run full setup on current account")
async def setup(ctx: discord.ApplicationContext):
    """Run full setup (step 1 + step 2) on the active account."""
    await ctx.defer()
    
    active_account = account_manager.get_active_account()
    
    if not active_account:
        await ctx.respond(
            f"{ICONS['error']} No active account. Use `/switch_account` first.",
            ephemeral=True
        )
        return
    
    embed = discord.Embed(
        title=f"{ICONS['building']} Setup Started",
        description=f"Starting setup on account `{active_account['username']}`\n\n"
                    f"⏱️ Estimated time: 2 hours 20 minutes",
        color=COLORS['building']
    )
    await ctx.respond(embed=embed)
    
    # Run setup in background
    asyncio.create_task(run_full_setup(active_account['username']))

# ============================================================================
# ADMIN COMMANDS
# ============================================================================

@bot.slash_command(name="refresh_channels", description="Refresh workflow channels")
async def refresh_channels(ctx: discord.ApplicationContext):
    """Manually refresh workflow channels."""
    await ctx.defer()
    
    try:
        await workflow_manager.refresh_workflow_channels(ctx.guild)
        await ctx.respond(f"{ICONS['success']} Workflow channels refreshed!")
    except Exception as e:
        logger.error(f"Failed to refresh channels: {e}")
        await ctx.respond(f"{ICONS['error']} Failed to refresh channels", ephemeral=True)

# ============================================================================
# RUN BOT
# ============================================================================

def main():
    """Main entry point."""
    # Check token
    if not config.DISCORD_TOKEN:
        logger.error("DISCORD_BOT_TOKEN not set in environment variables")
        sys.exit(1)
    
    # Initialize config
    config.initialize()
    
    # Run bot
    logger.info("Starting bot...")
    bot.run(config.DISCORD_TOKEN)

if __name__ == "__main__":
    main()

# ============================================================================
# END OF DISCORD BOT
# ============================================================================
