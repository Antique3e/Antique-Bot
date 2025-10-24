"""
Workflow Manager Module
=======================
Manages ComfyUI workflows and Discord channels:
- Auto-creates Discord channels for workflows
- Sends generated images to correct channels
- Tracks workflow usage
"""

import logging
import discord
from typing import Optional, Dict, Any, List
from pathlib import Path
import config
from modal_manager import modal_manager

logger = logging.getLogger(__name__)

# ============================================================================
# WORKFLOW MANAGER CLASS
# ============================================================================

class WorkflowManager:
    """Manages workflows and their corresponding Discord channels."""
    
    def __init__(self, bot: discord.Bot = None):
        """
        Initialize workflow manager.
        
        Args:
            bot: Discord bot instance
        """
        self.bot = bot
        self.workflow_channels = {}  # Maps workflow_name -> channel_id
        self.category_id = None  # Category for workflow channels
    
    # ========================================================================
    # CHANNEL MANAGEMENT
    # ========================================================================
    
    async def ensure_category(self, guild: discord.Guild) -> Optional[discord.CategoryChannel]:
        """
        Ensure the workflow category exists.
        
        Args:
            guild: Discord guild
        
        Returns:
            Category channel or None if failed
        """
        category_name = config.CHANNEL_CONFIG['channel_category']
        
        # Check if category already exists
        for category in guild.categories:
            if category.name == category_name:
                self.category_id = category.id
                logger.info(f"Found existing category: {category_name}")
                return category
        
        # Create new category
        try:
            category = await guild.create_category(category_name)
            self.category_id = category.id
            logger.info(f"Created new category: {category_name}")
            return category
        except discord.Forbidden:
            logger.error("Bot lacks permission to create category")
            return None
        except Exception as e:
            logger.error(f"Failed to create category: {e}")
            return None
    
    def format_channel_name(self, workflow_name: str) -> str:
        """
        Format workflow name into valid Discord channel name.
        
        Args:
            workflow_name: Original workflow name
        
        Returns:
            Formatted channel name
        """
        # Remove .json extension if present
        if workflow_name.endswith('.json'):
            workflow_name = workflow_name[:-5]
        
        # Apply formatting rules
        name = workflow_name
        
        if config.CHANNEL_CONFIG['use_lowercase']:
            name = name.lower()
        
        if config.CHANNEL_CONFIG['replace_spaces']:
            name = name.replace(' ', config.CHANNEL_CONFIG['replace_spaces'])
        
        # Add prefix if configured
        prefix = config.CHANNEL_CONFIG['channel_prefix']
        if prefix:
            name = f"{prefix}{name}"
        
        # Ensure length limit
        max_length = config.CHANNEL_CONFIG['max_name_length']
        if len(name) > max_length:
            name = name[:max_length]
        
        # Discord channel name restrictions
        # Only lowercase letters, numbers, and hyphens
        name = ''.join(c if c.isalnum() or c == '-' else '-' for c in name)
        name = name.strip('-')  # Remove leading/trailing hyphens
        
        return name
    
    async def get_or_create_channel(
        self,
        guild: discord.Guild,
        workflow_name: str
    ) -> Optional[discord.TextChannel]:
        """
        Get existing channel or create new one for a workflow.
        
        Args:
            guild: Discord guild
            workflow_name: Workflow name
        
        Returns:
            Text channel or None if failed
        """
        if not config.CHANNEL_CONFIG['auto_create']:
            logger.info("Auto-create channels is disabled")
            return None
        
        channel_name = self.format_channel_name(workflow_name)
        
        # Check if channel already exists in cache
        if workflow_name in self.workflow_channels:
            channel_id = self.workflow_channels[workflow_name]
            channel = guild.get_channel(channel_id)
            if channel:
                logger.info(f"Using existing channel: #{channel_name}")
                return channel
            else:
                # Channel was deleted, remove from cache
                del self.workflow_channels[workflow_name]
        
        # Search for existing channel by name
        for channel in guild.text_channels:
            if channel.name == channel_name:
                self.workflow_channels[workflow_name] = channel.id
                logger.info(f"Found existing channel: #{channel_name}")
                return channel
        
        # Channel doesn't exist, create it
        logger.info(f"Creating new channel: #{channel_name}")
        
        # Ensure category exists
        category = await self.ensure_category(guild)
        
        try:
            channel = await guild.create_text_channel(
                name=channel_name,
                category=category,
                topic=f"Generated outputs from workflow: {workflow_name}"
            )
            
            self.workflow_channels[workflow_name] = channel.id
            logger.info(f"Created channel: #{channel_name}")
            return channel
            
        except discord.Forbidden:
            logger.error("Bot lacks permission to create channel")
            return None
        except Exception as e:
            logger.error(f"Failed to create channel: {e}")
            return None
    
    async def refresh_workflow_channels(self, guild: discord.Guild):
        """
        Refresh workflow channels based on available workflows in Modal volume.
        
        Args:
            guild: Discord guild
        """
        logger.info("Refreshing workflow channels...")
        
        # Get list of workflows from Modal
        workflows = await modal_manager.list_workflows()
        
        if not workflows:
            logger.warning("No workflows found in Modal volume")
            return
        
        # Create channels for all workflows
        created_count = 0
        for workflow_name in workflows:
            channel = await self.get_or_create_channel(guild, workflow_name)
            if channel:
                created_count += 1
        
        logger.info(f"Refreshed {created_count} workflow channels")
    
    # ========================================================================
    # WORKFLOW OPERATIONS
    # ========================================================================
    
    async def get_workflow_list(self) -> List[str]:
        """
        Get list of available workflows from Modal volume.
        
        Returns:
            List of workflow names
        """
        return await modal_manager.list_workflows()
    
    async def get_workflow_json(self, workflow_name: str) -> Optional[Dict[Any, Any]]:
        """
        Get workflow JSON from Modal volume.
        
        Args:
            workflow_name: Workflow name
        
        Returns:
            Workflow JSON dict or None if failed
        """
        return await modal_manager.get_workflow(workflow_name)
    
    def inject_prompt_into_workflow(
        self,
        workflow: Dict[Any, Any],
        prompt: str
    ) -> Dict[Any, Any]:
        """
        Inject text prompt into workflow JSON.
        
        This is a simplified implementation. The actual logic depends on
        your workflow structure. You may need to customize this for your
        specific workflows.
        
        Args:
            workflow: Workflow JSON dict
            prompt: Text prompt to inject
        
        Returns:
            Modified workflow dict
        """
        # Search for text input nodes in the workflow
        # Common node types that accept text prompts:
        # - "CLIPTextEncode"
        # - "Text"
        # - "String"
        # - "Prompt"
        
        prompt_node_types = [
            "CLIPTextEncode",
            "Text",
            "String", 
            "Prompt",
            "PromptText",
            "TextInput"
        ]
        
        # Iterate through workflow nodes
        if isinstance(workflow, dict):
            for node_id, node_data in workflow.items():
                if isinstance(node_data, dict):
                    # Check if this is a prompt node
                    node_type = node_data.get('class_type', '')
                    
                    if node_type in prompt_node_types:
                        # Inject prompt into the 'inputs' section
                        if 'inputs' in node_data:
                            # Common input field names for prompts
                            prompt_fields = ['text', 'prompt', 'string', 'value']
                            
                            for field in prompt_fields:
                                if field in node_data['inputs']:
                                    logger.info(f"Injecting prompt into node {node_id}, field '{field}'")
                                    node_data['inputs'][field] = prompt
                                    break
        
        return workflow
    
    async def generate_with_workflow(
        self,
        workflow_name: str,
        prompt: str
    ) -> tuple[bool, str, Optional[Dict[Any, Any]]]:
        """
        Generate image using a workflow and prompt.
        
        Args:
            workflow_name: Workflow name
            prompt: Text prompt
        
        Returns:
            (success, message, response_data)
        """
        logger.info(f"Generating with workflow '{workflow_name}' and prompt: {prompt}")
        
        # Get workflow JSON
        workflow = await self.get_workflow_json(workflow_name)
        if not workflow:
            return False, f"Workflow '{workflow_name}' not found", None
        
        # Inject prompt
        workflow = self.inject_prompt_into_workflow(workflow, prompt)
        
        # Send to ComfyUI
        comfyui_url = config.CLOUDFLARE_URLS['comfyui']
        response = await utils.send_comfyui_prompt(comfyui_url, workflow, prompt)
        
        if not response:
            return False, "Failed to send prompt to ComfyUI", None
        
        logger.info(f"Generation started: {response}")
        return True, "Generation started!", response
    
    # ========================================================================
    # OUTPUT POSTING
    # ========================================================================
    
    async def post_output_to_channel(
        self,
        guild: discord.Guild,
        workflow_name: str,
        output_file: Path,
        prompt: str = None,
        generation_time: float = None
    ) -> bool:
        """
        Post generated output to the appropriate workflow channel.
        
        Args:
            guild: Discord guild
            workflow_name: Workflow name
            output_file: Path to output file
            prompt: Original prompt (optional)
            generation_time: Generation time in seconds (optional)
        
        Returns:
            True if successful, False otherwise
        """
        # Get or create channel
        channel = await self.get_or_create_channel(guild, workflow_name)
        if not channel:
            logger.error(f"Failed to get channel for workflow '{workflow_name}'")
            return False
        
        # Check file size
        file_size_mb = output_file.stat().st_size / (1024 * 1024)
        if file_size_mb > config.MAX_DISCORD_FILE_SIZE:
            logger.error(f"File too large: {file_size_mb:.2f}MB (max: {config.MAX_DISCORD_FILE_SIZE}MB)")
            await channel.send(
                f"❌ Output file is too large ({file_size_mb:.2f}MB). "
                f"Use `/get_output {output_file.name}` to download manually."
            )
            return False
        
        # Create embed
        from ui_config import COLORS, ICONS, MESSAGES
        
        embed = discord.Embed(
            title=f"{ICONS['image']} Image Generated",
            color=COLORS['success']
        )
        
        embed.add_field(name="Workflow", value=workflow_name, inline=True)
        
        if prompt:
            # Truncate long prompts
            display_prompt = prompt[:1000] + "..." if len(prompt) > 1000 else prompt
            embed.add_field(name="Prompt", value=display_prompt, inline=False)
        
        if generation_time:
            embed.add_field(name="Generation Time", value=f"{generation_time:.1f}s", inline=True)
        
        # Post to channel
        try:
            file = discord.File(output_file)
            await channel.send(embed=embed, file=file)
            logger.info(f"Posted output to #{channel.name}")
            return True
            
        except discord.Forbidden:
            logger.error(f"No permission to post in #{channel.name}")
            return False
        except Exception as e:
            logger.error(f"Failed to post output: {e}")
            return False
    
    # ========================================================================
    # STATISTICS
    # ========================================================================
    
    def get_workflow_channel_map(self) -> Dict[str, int]:
        """
        Get mapping of workflow names to channel IDs.
        
        Returns:
            Dict mapping workflow_name -> channel_id
        """
        return self.workflow_channels.copy()
    
    async def list_all_outputs(self) -> List[str]:
        """
        List all output files in Modal volume.
        
        Returns:
            List of output filenames
        """
        return await modal_manager.list_outputs()

# ============================================================================
# GLOBAL INSTANCE (will be initialized with bot)
# ============================================================================

workflow_manager = None  # Will be initialized in discord_bot.py

def initialize_workflow_manager(bot: discord.Bot):
    """Initialize the global workflow manager with bot instance."""
    global workflow_manager
    workflow_manager = WorkflowManager(bot)
    logger.info("Workflow manager initialized")
    return workflow_manager

# ============================================================================
# END OF WORKFLOW MANAGER
# ============================================================================
