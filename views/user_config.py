"""
User Configuration Menu - Add account, Switch account, Go back
"""

import discord
from discord.ui import Button, View, Select

# Note: TextInput/Modal features removed for compatibility
# Users will add accounts via slash command instead


class AddAccountModal_DISABLED:
    """Modal for adding a new Modal.com account"""
    
    def __init__(self):
        super().__init__(title="➕ Add New Account")
        
        self.username = TextInput(
            label="Account Username",
            placeholder="Enter a unique name for this account",
            required=True,
            max_length=50
        )
        
        self.token_id = TextInput(
            label="Modal Token ID",
            placeholder="ak-xxxxxxxx",
            required=True,
            max_length=100
        )
        
        self.token_secret = TextInput(
            label="Modal Token Secret",
            placeholder="as-xxxxxxxx",
            required=True,
            max_length=200
        )
        
        self.add_item(self.username)
        self.add_item(self.token_id)
        self.add_item(self.token_secret)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        try:
            from ..account_manager import account_manager
            from ..modal_manager import modal_manager
            
            username = self.username.value.strip()
            token_id = self.token_id.value.strip()
            token_secret = self.token_secret.value.strip()
            
            # Validate inputs
            if not username or not token_id or not token_secret:
                await interaction.followup.send(
                    "❌ All fields are required!",
                    ephemeral=True
                )
                return
            
            # Check if username already exists
            if account_manager.get_account_by_username(username):
                await interaction.followup.send(
                    f"❌ Account `{username}` already exists!",
                    ephemeral=True
                )
                return
            
            # Check max accounts
            from .. import config
            if len(account_manager.list_accounts()) >= config.MAX_ACCOUNTS:
                await interaction.followup.send(
                    f"❌ Maximum number of accounts ({config.MAX_ACCOUNTS}) reached!",
                    ephemeral=True
                )
                return
            
            # Add account
            success = account_manager.add_account(username, token_id, token_secret)
            if not success:
                await interaction.followup.send(
                    "❌ Failed to add account!",
                    ephemeral=True
                )
                return
            
            # Create Modal profile
            success, message = await modal_manager.create_profile(username, token_id, token_secret)
            
            if success:
                await interaction.followup.send(
                    f"✅ Account `{username}` added successfully!\n"
                    f"💡 Use 'Switch Account' to activate it.",
                    ephemeral=True
                )
            else:
                # Rollback
                account_manager.delete_account(username)
                await interaction.followup.send(
                    f"❌ Failed to create Modal profile: {message}",
                    ephemeral=True
                )
                
        except Exception as e:
            await interaction.followup.send(
                f"❌ Error adding account: {str(e)}",
                ephemeral=True
            )


class SwitchAccountView(View):
    """View for switching between accounts with checkboxes"""
    
    def __init__(self, accounts, current_username):
        super().__init__(timeout=180)  # 3 minute timeout
        self.accounts = accounts
        self.current_username = current_username
        
        # Create select menu for accounts
        options = []
        for account in accounts:
            username = account['username']
            credits = account.get('credits', 0)
            status = account.get('status', 'unknown')
            
            # Emoji based on status
            emoji = "✅" if username == current_username else "⚪"
            
            options.append(
                discord.SelectOption(
                    label=username,
                    description=f"${credits:.2f} • {status}",
                    emoji=emoji,
                    value=username,
                    default=(username == current_username)
                )
            )
        
        select = Select(
            placeholder="Choose an account to switch to...",
            options=options,
            custom_id="account_select"
        )
        select.callback = self.account_selected
        self.add_item(select)
        
        # Add go back button
        go_back_btn = Button(
            label="⬅️ Go Back",
            style=discord.ButtonStyle.secondary,
            custom_id="btn_go_back"
        )
        go_back_btn.callback = self.go_back
        self.add_item(go_back_btn)
    
    async def account_selected(self, interaction: discord.Interaction):
        """Handle account selection"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            from ..modal_manager import modal_manager
            from ..account_manager import account_manager
            
            selected_username = interaction.data['values'][0]
            
            # Check if already active
            if selected_username == self.current_username:
                await interaction.followup.send(
                    f"⚠️ Account `{selected_username}` is already active!",
                    ephemeral=True
                )
                return
            
            # Switch account
            success, message = await modal_manager.switch_to_account(selected_username)
            
            if success:
                # Update account status
                account_manager.set_active_account(selected_username)
                
                await interaction.followup.send(
                    f"✅ Switched to account: `{selected_username}`\n"
                    f"💡 Use `/start` to start ComfyUI with this account.",
                    ephemeral=True
                )
                
                # Disable the view
                for item in self.children:
                    item.disabled = True
                await interaction.message.edit(view=self)
            else:
                await interaction.followup.send(
                    f"❌ Failed to switch account: {message}",
                    ephemeral=True
                )
                
        except Exception as e:
            await interaction.followup.send(
                f"❌ Error switching account: {str(e)}",
                ephemeral=True
            )
    
    async def go_back(self, interaction: discord.Interaction):
        """Go back to user config menu"""
        await interaction.response.send_message(
            "👤 **User Configuration**\nChoose an action:",
            view=UserConfigMenu(interaction.client),
            ephemeral=True
        )
        
        # Disable this view
        for item in self.children:
            item.disabled = True
        await interaction.message.edit(view=self)


class UserConfigMenu(View):
    """User configuration sub-menu with Add Account, Switch Account, and Go Back"""
    
    def __init__(self, bot):
        super().__init__(timeout=180)  # 3 minute timeout
        self.bot = bot
    
    @discord.ui.button(label="➕ Add Account", style=discord.ButtonStyle.success, custom_id="btn_add_account")
    async def add_account_button(self, button: Button, interaction: discord.Interaction):
        """Open modal to add new account"""
        modal = AddAccountModal()
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="🔄 Switch Account", style=discord.ButtonStyle.primary, custom_id="btn_switch_account")
    async def switch_account_button(self, button: Button, interaction: discord.Interaction):
        """Show account selection menu"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            from ..account_manager import account_manager
            
            # Get all accounts
            accounts = account_manager.list_accounts()
            
            if not accounts:
                await interaction.followup.send(
                    "❌ No accounts available! Please add an account first.",
                    ephemeral=True
                )
                return
            
            # Get current active account
            active_account = account_manager.get_active_account()
            current_username = active_account['username'] if active_account else None
            
            # Show account selection view
            view = SwitchAccountView(accounts, current_username)
            
            await interaction.followup.send(
                "🔄 **Switch Account**\n"
                "Select an account from the dropdown below:",
                view=view,
                ephemeral=True
            )
            
        except Exception as e:
            await interaction.followup.send(
                f"❌ Error loading accounts: {str(e)}",
                ephemeral=True
            )
    
    @discord.ui.button(label="⬅️ Go Back", style=discord.ButtonStyle.secondary, custom_id="btn_go_back_main")
    async def go_back_button(self, button: Button, interaction: discord.Interaction):
        """Go back to main control panel"""
        from .main_menu import MainControlPanel
        
        await interaction.response.send_message(
            "🎮 **Main Control Panel**\nChoose an action:",
            view=MainControlPanel(self.bot),
            ephemeral=True
        )
        
        # Disable this view
        for item in self.children:
            item.disabled = True
        await interaction.message.edit(view=self)
