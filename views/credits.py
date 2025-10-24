"""
Credits View - Functions for checking credits from CreditTracker
"""

import discord
import aiohttp
import json
from pathlib import Path


async def get_credits_from_tracker():
    """
    Get credits from ComfyUI-CreditTracker balance.json
    
    Returns:
        float: Credit balance, or None if not available
    """
    try:
        from .. import config
        
        # Check if ComfyUI is running
        from ..modal_manager import modal_manager
        if not modal_manager.current_deployment:
            return None
        
        # URL to balance.json on running server
        comfyui_url = config.CLOUDFLARE_URLS['comfyui']
        
        # The balance.json should be accessible at:
        # https://comfyui.tensorart.site/custom_nodes/ComfyUI-CreditTracker/balance.json
        balance_url = f"{comfyui_url.rstrip('/')}/custom_nodes/ComfyUI-CreditTracker/balance.json"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(balance_url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # The balance.json structure should be: {"balance": 12.34}
                    # Adjust this based on actual structure
                    balance = data.get('balance', None)
                    
                    if balance is not None:
                        return float(balance)
        
        return None
        
    except Exception as e:
        print(f"Error getting credits from tracker: {e}")
        return None


async def get_credits_from_modal_api(username):
    """
    Fallback: Get credits from Modal API (if available)
    
    Args:
        username: Modal account username
        
    Returns:
        float: Credit balance, or None if not available
    """
    try:
        # This would require Modal API access
        # For now, return None (not implemented)
        return None
        
    except Exception as e:
        print(f"Error getting credits from Modal API: {e}")
        return None


class CreditsView(discord.ui.View):
    """View for displaying credits with refresh button"""
    
    def __init__(self, username, credits):
        super().__init__(timeout=180)
        self.username = username
        self.credits = credits
    
    @discord.ui.button(label="🔄 Refresh", style=discord.ButtonStyle.primary, custom_id="btn_refresh_credits")
    async def refresh_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        """Refresh credits"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Get fresh credits
            credits = await get_credits_from_tracker()
            
            if credits is not None:
                self.credits = credits
                
                embed = discord.Embed(
                    title="💰 Account Credits (Refreshed)",
                    description=f"Account: **{self.username}**",
                    color=discord.Color.blue()
                )
                embed.add_field(name="💵 Balance", value=f"${credits:.2f}", inline=True)
                
                if credits < 2:
                    embed.color = discord.Color.red()
                    embed.add_field(name="⚠️ Warning", value="Low balance!", inline=False)
                elif credits < 10:
                    embed.color = discord.Color.orange()
                
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.followup.send(
                    "⚠️ Could not refresh credits. Server may not be running.",
                    ephemeral=True
                )
                
        except Exception as e:
            await interaction.followup.send(
                f"❌ Error refreshing credits: {str(e)}",
                ephemeral=True
            )
