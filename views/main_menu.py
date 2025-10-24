"""
Main Control Panel - Button-based UI for server control
"""

import discord
from discord.ui import Button, View


class MainControlPanel(View):
    """
    Main control panel with Start, Stop, User Config, View Credits, and Exit buttons
    """
    
    def __init__(self, bot):
        super().__init__(timeout=None)  # No timeout for persistent UI
        self.bot = bot
    
    @discord.ui.button(label="▶️ Start", style=discord.ButtonStyle.success, custom_id="btn_start", row=0)
    async def start_button(self, button: Button, interaction: discord.Interaction):
        """Start ComfyUI server"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Import here to avoid circular imports
            from ..modal_manager import modal_manager
            from ..account_manager import account_manager
            from .. import config
            
            # Get active account
            active_account = account_manager.get_active_account()
            if not active_account:
                await interaction.followup.send(
                    "❌ No active account! Please add an account first.",
                    ephemeral=True
                )
                return
            
            username = active_account['username']
            gpu = active_account.get('selected_gpu', 'H100')
            
            # Check if already running
            if modal_manager.current_deployment:
                await interaction.followup.send(
                    f"⚠️ ComfyUI is already running on `{username}`!",
                    ephemeral=True
                )
                return
            
            # Send starting message
            await interaction.followup.send(
                f"🚀 Starting ComfyUI on `{username}` with GPU: **{gpu}**...\n"
                f"⏳ This will take 2-3 minutes. Please wait...",
                ephemeral=True
            )
            
            # Start ComfyUI
            success, message = await modal_manager.start_comfyui(username, gpu)
            
            if success:
                embed = discord.Embed(
                    title="✅ ComfyUI Started Successfully!",
                    description=f"Server is now running on **{gpu}**",
                    color=discord.Color.green()
                )
                embed.add_field(
                    name="🔗 Access Links",
                    value=f"**JupyterLab:** {config.CLOUDFLARE_URLS['jupyter']}\n"
                          f"**ComfyUI:** {config.CLOUDFLARE_URLS['comfyui']}",
                    inline=False
                )
                embed.add_field(name="👤 Account", value=f"`{username}`", inline=True)
                embed.add_field(name="🖥️ GPU", value=gpu, inline=True)
                
                await interaction.followup.send(embed=embed, ephemeral=False)
            else:
                await interaction.followup.send(
                    f"❌ Failed to start ComfyUI: {message}",
                    ephemeral=True
                )
                
        except Exception as e:
            await interaction.followup.send(
                f"❌ Error starting server: {str(e)}",
                ephemeral=True
            )
    
    @discord.ui.button(label="⏹️ Stop", style=discord.ButtonStyle.danger, custom_id="btn_stop", row=0)
    async def stop_button(self, button: Button, interaction: discord.Interaction):
        """Stop ComfyUI server"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            from ..modal_manager import modal_manager
            
            # Check if running
            if not modal_manager.current_deployment:
                await interaction.followup.send(
                    "⚠️ No ComfyUI server is currently running.",
                    ephemeral=True
                )
                return
            
            # Stop the server
            success, message = await modal_manager.stop_comfyui()
            
            if success:
                await interaction.followup.send(
                    "✅ ComfyUI server stopped successfully!",
                    ephemeral=False
                )
            else:
                await interaction.followup.send(
                    f"❌ Failed to stop server: {message}",
                    ephemeral=True
                )
                
        except Exception as e:
            await interaction.followup.send(
                f"❌ Error stopping server: {str(e)}",
                ephemeral=True
            )
    
    @discord.ui.button(label="👤 User Config", style=discord.ButtonStyle.primary, custom_id="btn_user_config", row=1)
    async def user_config_button(self, button: Button, interaction: discord.Interaction):
        """Open user configuration menu"""
        from .user_config import UserConfigMenu
        
        await interaction.response.send_message(
            "👤 **User Configuration**\nChoose an action:",
            view=UserConfigMenu(self.bot),
            ephemeral=True
        )
    
    @discord.ui.button(label="💰 View Credits", style=discord.ButtonStyle.primary, custom_id="btn_view_credits", row=1)
    async def view_credits_button(self, button: Button, interaction: discord.Interaction):
        """View credits for active account"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            from ..account_manager import account_manager
            from .credits import get_credits_from_tracker
            
            # Get active account
            active_account = account_manager.get_active_account()
            if not active_account:
                await interaction.followup.send(
                    "❌ No active account selected!",
                    ephemeral=True
                )
                return
            
            username = active_account['username']
            
            # Try to get credits from CreditTracker
            credits = await get_credits_from_tracker()
            
            if credits is not None:
                embed = discord.Embed(
                    title="💰 Account Credits",
                    description=f"Account: **{username}**",
                    color=discord.Color.blue()
                )
                embed.add_field(name="💵 Balance", value=f"${credits:.2f}", inline=True)
                
                # Color based on balance
                if credits < 2:
                    embed.color = discord.Color.red()
                    embed.add_field(name="⚠️ Warning", value="Low balance!", inline=False)
                elif credits < 10:
                    embed.color = discord.Color.orange()
                
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.followup.send(
                    f"💰 **Account:** `{username}`\n"
                    f"⚠️ Credits information not available.\n"
                    f"(Server must be running to check credits from CreditTracker)",
                    ephemeral=True
                )
                
        except Exception as e:
            await interaction.followup.send(
                f"❌ Error retrieving credits: {str(e)}",
                ephemeral=True
            )
    
    @discord.ui.button(label="🚪 Exit", style=discord.ButtonStyle.secondary, custom_id="btn_exit", row=2)
    async def exit_button(self, button: Button, interaction: discord.Interaction):
        """Close the control panel"""
        await interaction.response.send_message(
            "👋 Control panel closed!",
            ephemeral=True
        )
        # Disable all buttons
        for item in self.children:
            item.disabled = True
        await interaction.message.edit(view=self)
