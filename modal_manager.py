"""
Modal Manager Module
====================
Handles all Modal.com operations:
- Profile management (create, activate, switch)
- Token authentication
- App deployment and control
- Credit balance checking
- Volume operations
"""

import logging
import asyncio
from typing import Optional, Dict, Any, Tuple
from pathlib import Path
import config
import utils
from account_manager import account_manager

logger = logging.getLogger(__name__)

# ============================================================================
# MODAL MANAGER CLASS
# ============================================================================

class ModalManager:
    """Manages Modal CLI operations and app deployments."""
    
    def __init__(self):
        """Initialize Modal manager."""
        self.current_deployment = None  # Track current deployment info
    
    # ========================================================================
    # PROFILE MANAGEMENT
    # ========================================================================
    
    async def create_profile(self, username: str, token_id: str, token_secret: str) -> Tuple[bool, str]:
        """
        Create a new Modal profile.
        
        Args:
            username: Profile name
            token_id: Modal token ID
            token_secret: Modal token secret
        
        Returns:
            (success, message)
        """
        logger.info(f"Creating Modal profile: {username}")
        
        # First, create the profile
        command = config.get_modal_command('profile_create', profile_name=username)
        return_code, stdout, stderr = await utils.run_command(command)
        
        if return_code != 0:
            error_msg = f"Failed to create profile: {stderr}"
            logger.error(error_msg)
            return False, error_msg
        
        # Then, activate it to set tokens
        success, msg = await self.activate_profile(username)
        if not success:
            return False, f"Profile created but failed to activate: {msg}"
        
        # Set the tokens
        command = config.get_modal_command(
            'token_set',
            token_id=token_id,
            token_secret=token_secret
        )
        return_code, stdout, stderr = await utils.run_command(command)
        
        if return_code != 0:
            error_msg = f"Failed to set tokens: {stderr}"
            logger.error(error_msg)
            return False, error_msg
        
        logger.info(f"Modal profile '{username}' created and configured successfully")
        return True, f"Profile '{username}' created successfully!"
    
    async def activate_profile(self, username: str) -> Tuple[bool, str]:
        """
        Activate a Modal profile (switch to it).
        
        Args:
            username: Profile name to activate
        
        Returns:
            (success, message)
        """
        logger.info(f"Activating Modal profile: {username}")
        
        command = config.get_modal_command('profile_activate', profile_name=username)
        return_code, stdout, stderr = await utils.run_command(command)
        
        if return_code != 0:
            error_msg = f"Failed to activate profile: {stderr}"
            logger.error(error_msg)
            return False, error_msg
        
        logger.info(f"Modal profile '{username}' activated")
        return True, f"Profile '{username}' activated!"
    
    async def get_current_profile(self) -> Optional[str]:
        """
        Get the currently active Modal profile.
        
        Returns:
            Profile name or None if failed
        """
        command = config.get_modal_command('profile_current')
        return_code, stdout, stderr = await utils.run_command(command)
        
        if return_code != 0:
            logger.error(f"Failed to get current profile: {stderr}")
            return None
        
        # Parse output to get profile name
        profile_name = stdout.strip()
        return profile_name if profile_name else None
    
    async def list_profiles(self) -> list[str]:
        """
        List all Modal profiles.
        
        Returns:
            List of profile names
        """
        command = config.get_modal_command('profile_list')
        return_code, stdout, stderr = await utils.run_command(command)
        
        if return_code != 0:
            logger.error(f"Failed to list profiles: {stderr}")
            return []
        
        # Parse output (each line is a profile name)
        profiles = [line.strip() for line in stdout.split('\n') if line.strip()]
        return profiles
    
    # ========================================================================
    # ACCOUNT SWITCHING
    # ========================================================================
    
    async def switch_to_account(self, username: str) -> Tuple[bool, str]:
        """
        Switch to a different Modal account.
        
        This will:
        1. Stop current ComfyUI if running
        2. Get credentials for new account
        3. Activate the new profile
        4. Update database
        
        Args:
            username: Account to switch to
        
        Returns:
            (success, message)
        """
        logger.info(f"Switching to account: {username}")
        
        # Get account from database
        account = account_manager.get_account_by_username(username)
        if not account:
            return False, f"Account '{username}' not found in database"
        
        # Check if account has sufficient balance
        if account['balance'] < config.MIN_CREDIT_THRESHOLD:
            return False, f"Account '{username}' has insufficient balance (${account['balance']:.2f})"
        
        # Get current active account
        current_account = account_manager.get_active_account()
        
        # Stop current ComfyUI if running
        if current_account and self.current_deployment:
            logger.info(f"Stopping ComfyUI on account '{current_account['username']}'")
            await self.stop_comfyui()
        
        # Get decrypted credentials
        creds = account_manager.get_decrypted_credentials(username)
        if not creds:
            return False, f"Failed to decrypt credentials for '{username}'"
        
        # Check if profile exists, if not create it
        profiles = await self.list_profiles()
        if username not in profiles:
            logger.info(f"Profile '{username}' doesn't exist, creating it...")
            success, msg = await self.create_profile(
                username,
                creds['token_id'],
                creds['token_secret']
            )
            if not success:
                return False, f"Failed to create profile: {msg}"
        else:
            # Profile exists, just activate it
            success, msg = await self.activate_profile(username)
            if not success:
                return False, f"Failed to activate profile: {msg}"
        
        # Update database - set as active account
        success = account_manager.set_active_account(username)
        if not success:
            return False, "Failed to update database"
        
        # Update status
        if current_account:
            account_manager.update_status(current_account['username'], 'ready')
        account_manager.update_status(username, 'active')
        
        logger.info(f"Successfully switched to account '{username}'")
        return True, f"Switched to account '{username}'"
    
    async def switch_to_next_available_account(self) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Automatically switch to the next available account with sufficient balance.
        
        Returns:
            (success, message, new_account_dict)
        """
        logger.info("Finding next available account...")
        
        # Get next available account
        next_account = account_manager.get_next_available_account()
        
        if not next_account:
            return False, "No available accounts with sufficient balance", None
        
        # Switch to it
        success, msg = await self.switch_to_account(next_account['username'])
        
        if success:
            return True, msg, next_account
        else:
            return False, msg, None
    
    # ========================================================================
    # BALANCE CHECKING
    # ========================================================================
    
    async def check_balance(self, username: str) -> Optional[float]:
        """
        Check credit balance for an account.
        
        Reads from balance.json in the Modal volume.
        
        Args:
            username: Account username
        
        Returns:
            Balance amount or None if failed
        """
        logger.info(f"Checking balance for account '{username}'")
        
        # First, make sure this account is active
        current_profile = await self.get_current_profile()
        if current_profile != username:
            logger.info(f"Activating profile '{username}' to check balance")
            success, msg = await self.activate_profile(username)
            if not success:
                logger.error(f"Failed to activate profile for balance check: {msg}")
                return None
        
        # Read balance from volume
        balance = await utils.read_balance_from_volume(config.MODAL_VOLUME_NAME)
        
        if balance is not None:
            # Update database
            account_manager.update_balance(username, balance)
            logger.info(f"Balance for '{username}': ${balance:.2f}")
            
            # Update status based on balance
            if balance < config.MIN_CREDIT_THRESHOLD:
                account_manager.update_status(username, 'dead')
            elif account_manager.get_active_account()['username'] == username:
                account_manager.update_status(username, 'active')
            else:
                account_manager.update_status(username, 'ready')
        
        return balance
    
    async def check_all_balances(self) -> Dict[str, float]:
        """
        Check balances for all accounts.
        
        Returns:
            Dict mapping username to balance
        """
        logger.info("Checking balances for all accounts")
        
        balances = {}
        accounts = account_manager.get_all_accounts()
        
        for account in accounts:
            balance = await self.check_balance(account['username'])
            if balance is not None:
                balances[account['username']] = balance
        
        return balances
    
    # ========================================================================
    # COMFYUI DEPLOYMENT
    # ========================================================================
    
    async def deploy_setup_step1(self, username: str) -> Tuple[bool, str]:
        """
        Deploy Modal setup step 1 (download models).
        
        Uses T4 GPU, takes ~2 hours.
        
        Args:
            username: Account to deploy on
        
        Returns:
            (success, message)
        """
        logger.info(f"Deploying setup step 1 for '{username}'")
        
        # Make sure account is active
        success, msg = await self.switch_to_account(username)
        if not success:
            return False, f"Failed to switch account: {msg}"
        
        # Update status
        account_manager.update_status(username, 'building')
        
        # Deploy step 1
        script_path = config.MODAL_FILES['setup_step1']
        command = config.get_modal_command('deploy', file_path=str(script_path))
        
        return_code, stdout, stderr = await utils.run_command(command, timeout=7200)  # 2 hour timeout
        
        if return_code != 0:
            error_msg = f"Setup step 1 failed: {stderr}"
            logger.error(error_msg)
            account_manager.update_status(username, 'ready')
            return False, error_msg
        
        logger.info(f"Setup step 1 completed for '{username}'")
        return True, "Setup step 1 completed! JupyterLab should be available."
    
    async def deploy_setup_step2(self, username: str) -> Tuple[bool, str]:
        """
        Deploy Modal setup step 2 (install dependencies and start ComfyUI).
        
        Uses T4 GPU, takes ~20 minutes.
        
        Args:
            username: Account to deploy on
        
        Returns:
            (success, message)
        """
        logger.info(f"Deploying setup step 2 for '{username}'")
        
        # Make sure account is active
        success, msg = await self.switch_to_account(username)
        if not success:
            return False, f"Failed to switch account: {msg}"
        
        # Update status
        account_manager.update_status(username, 'building')
        
        # Deploy step 2
        script_path = config.MODAL_FILES['setup_step2']
        command = config.get_modal_command('deploy', file_path=str(script_path))
        
        return_code, stdout, stderr = await utils.run_command(command, timeout=1800)  # 30 min timeout
        
        if return_code != 0:
            error_msg = f"Setup step 2 failed: {stderr}"
            logger.error(error_msg)
            account_manager.update_status(username, 'ready')
            return False, error_msg
        
        logger.info(f"Setup step 2 completed for '{username}'")
        
        # Update status to active
        account_manager.update_status(username, 'active')
        
        # Mark as deployed
        self.current_deployment = {
            'username': username,
            'jupyter_url': config.CLOUDFLARE_URLS['jupyter'],
            'comfyui_url': config.CLOUDFLARE_URLS['comfyui'],
        }
        
        return True, "Setup step 2 completed! ComfyUI should be available."
    
    async def start_comfyui(self, username: str, gpu: str = None) -> Tuple[bool, str]:
        """
        Start ComfyUI on a configured account.
        
        Args:
            username: Account to start on
            gpu: GPU to use (defaults to account's selected GPU or H100)
        
        Returns:
            (success, message)
        """
        logger.info(f"Starting ComfyUI for '{username}' on GPU: {gpu}")
        
        # Make sure account is active
        success, msg = await self.switch_to_account(username)
        if not success:
            return False, f"Failed to switch account: {msg}"
        
        # Get account
        account = account_manager.get_account_by_username(username)
        
        # Determine GPU to use
        if gpu is None:
            gpu = account.get('selected_gpu') or 'H100'
        
        # Update selected GPU
        account_manager.update_selected_gpu(username, gpu)
        
        # TODO: Modify modal_comfyui_run.py to use the selected GPU
        # This requires dynamically modifying the Python file or passing GPU as env var
        
        # Deploy the run script
        script_path = config.MODAL_FILES['comfyui_run']
        command = config.get_modal_command('run', file_path=str(script_path))
        
        # Run in background (don't wait for completion)
        # We'll check if it's ready using the URL
        asyncio.create_task(utils.run_command(command, timeout=86400))  # 24 hour max
        
        # Wait a bit for the process to start
        await asyncio.sleep(10)
        
        # Wait for ComfyUI to become ready
        comfyui_url = config.CLOUDFLARE_URLS['comfyui']
        is_ready = await utils.wait_for_comfyui(comfyui_url, max_wait=300)
        
        if not is_ready:
            return False, "ComfyUI failed to start (timeout)"
        
        # Mark as deployed
        self.current_deployment = {
            'username': username,
            'gpu': gpu,
            'jupyter_url': config.CLOUDFLARE_URLS['jupyter'],
            'comfyui_url': config.CLOUDFLARE_URLS['comfyui'],
        }
        
        account_manager.update_status(username, 'active')
        
        logger.info(f"ComfyUI started successfully for '{username}' on {gpu}")
        return True, f"ComfyUI started on {gpu}!"
    
    async def stop_comfyui(self) -> Tuple[bool, str]:
        """
        Stop the currently running ComfyUI app.
        
        Returns:
            (success, message)
        """
        if not self.current_deployment:
            return False, "No ComfyUI deployment is running"
        
        logger.info("Stopping ComfyUI...")
        
        # Stop the Modal app
        command = config.get_modal_command('app_stop', app_name=config.MODAL_APP_NAME)
        return_code, stdout, stderr = await utils.run_command(command)
        
        if return_code != 0:
            logger.warning(f"Failed to stop app gracefully: {stderr}")
            # Don't return False - still clear deployment
        
        # Clear deployment info
        username = self.current_deployment.get('username')
        self.current_deployment = None
        
        # Update account status
        if username:
            account_manager.update_status(username, 'ready')
        
        logger.info("ComfyUI stopped")
        return True, "ComfyUI stopped successfully"
    
    # ========================================================================
    # VOLUME OPERATIONS
    # ========================================================================
    
    async def list_workflows(self) -> list[str]:
        """
        List all workflow files in the ComfyUI workflows directory.
        
        Returns:
            List of workflow filenames
        """
        logger.info("Listing workflows from Modal volume")
        
        files = await utils.list_modal_volume_files(
            config.MODAL_VOLUME_NAME,
            config.MODAL_PATHS['workflows']
        )
        
        # Filter for .json files
        workflows = [f for f in files if f.endswith('.json')]
        return workflows
    
    async def list_outputs(self) -> list[str]:
        """
        List all output files in the ComfyUI output directory.
        
        Returns:
            List of output filenames
        """
        logger.info("Listing outputs from Modal volume")
        
        files = await utils.list_modal_volume_files(
            config.MODAL_VOLUME_NAME,
            config.MODAL_PATHS['outputs']
        )
        
        # Filter for valid output extensions
        outputs = [f for f in files if utils.is_valid_output_file(f)]
        return outputs
    
    async def get_workflow(self, workflow_name: str) -> Optional[Dict[Any, Any]]:
        """
        Download and read a workflow JSON file.
        
        Args:
            workflow_name: Workflow filename (e.g., "seedream.json")
        
        Returns:
            Workflow dict or None if failed
        """
        logger.info(f"Downloading workflow: {workflow_name}")
        
        # Ensure .json extension
        if not workflow_name.endswith('.json'):
            workflow_name += '.json'
        
        # Download to temp
        temp_file = config.TEMP_DIR / workflow_name
        remote_path = f"{config.MODAL_PATHS['workflows']}/{workflow_name}"
        
        success = await utils.download_from_modal_volume(
            config.MODAL_VOLUME_NAME,
            remote_path,
            temp_file
        )
        
        if not success:
            logger.error(f"Failed to download workflow: {workflow_name}")
            return None
        
        # Read JSON
        return utils.read_json_file(temp_file)
    
    async def get_output_file(self, filename: str) -> Optional[Path]:
        """
        Download an output file from Modal volume.
        
        Args:
            filename: Output filename
        
        Returns:
            Local path to downloaded file or None if failed
        """
        logger.info(f"Downloading output: {filename}")
        
        # Download to temp
        temp_file = config.TEMP_DIR / filename
        remote_path = f"{config.MODAL_PATHS['outputs']}/{filename}"
        
        success = await utils.download_from_modal_volume(
            config.MODAL_VOLUME_NAME,
            remote_path,
            temp_file
        )
        
        if not success:
            logger.error(f"Failed to download output: {filename}")
            return None
        
        return temp_file

# ============================================================================
# GLOBAL INSTANCE
# ============================================================================

# Create a global instance for easy access
modal_manager = ModalManager()

# ============================================================================
# END OF MODAL MANAGER
# ============================================================================
