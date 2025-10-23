"""
Utilities Module
================
Helper functions used throughout the bot.
Contains encryption, file operations, HTTP requests, and more.
"""

import os
import json
import asyncio
import subprocess
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
import aiohttp
from cryptography.fernet import Fernet
import config

logger = logging.getLogger(__name__)

# ============================================================================
# ENCRYPTION UTILITIES
# ============================================================================

def get_encryption_key() -> bytes:
    """Get or create encryption key for storing Modal tokens."""
    if config.ENCRYPTION_KEY_FILE.exists():
        return config.ENCRYPTION_KEY_FILE.read_bytes()
    else:
        key = Fernet.generate_key()
        config.ENCRYPTION_KEY_FILE.write_bytes(key)
        logger.info(f"Generated new encryption key: {config.ENCRYPTION_KEY_FILE}")
        return key

def encrypt_data(data: str) -> str:
    """Encrypt sensitive data (like Modal tokens)."""
    key = get_encryption_key()
    f = Fernet(key)
    encrypted = f.encrypt(data.encode())
    return encrypted.decode()

def decrypt_data(encrypted_data: str) -> str:
    """Decrypt sensitive data."""
    key = get_encryption_key()
    f = Fernet(key)
    decrypted = f.decrypt(encrypted_data.encode())
    return decrypted.decode()

# ============================================================================
# FILE OPERATIONS
# ============================================================================

def ensure_directory(path: Path) -> Path:
    """Create directory if it doesn't exist."""
    path.mkdir(parents=True, exist_ok=True)
    return path

def clean_filename(filename: str) -> str:
    """Clean filename for safe file operations."""
    # Remove invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename

def get_file_size_mb(filepath: Path) -> float:
    """Get file size in megabytes."""
    if not filepath.exists():
        return 0.0
    return filepath.stat().st_size / (1024 * 1024)

def is_valid_output_file(filename: str) -> bool:
    """Check if filename has a valid output extension."""
    ext = Path(filename).suffix.lower()
    return ext in config.ALLOWED_OUTPUT_EXTENSIONS

# ============================================================================
# JSON OPERATIONS
# ============================================================================

def read_json_file(filepath: Path) -> Optional[Dict[Any, Any]]:
    """Read and parse JSON file."""
    try:
        if not filepath.exists():
            logger.warning(f"JSON file not found: {filepath}")
            return None
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON file {filepath}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error reading JSON file {filepath}: {e}")
        return None

def write_json_file(filepath: Path, data: Dict[Any, Any]) -> bool:
    """Write data to JSON file."""
    try:
        ensure_directory(filepath.parent)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Error writing JSON file {filepath}: {e}")
        return False

# ============================================================================
# SUBPROCESS UTILITIES (for Modal CLI commands)
# ============================================================================

async def run_command(command: str, timeout: int = 300) -> tuple[int, str, str]:
    """
    Run a shell command asynchronously.
    
    Returns:
        (return_code, stdout, stderr)
    """
    try:
        logger.info(f"Running command: {command}")
        
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            process.kill()
            logger.error(f"Command timed out after {timeout}s: {command}")
            return -1, "", "Command timed out"
        
        return_code = process.returncode
        stdout_str = stdout.decode('utf-8', errors='ignore').strip()
        stderr_str = stderr.decode('utf-8', errors='ignore').strip()
        
        if return_code == 0:
            logger.info(f"Command successful: {command}")
        else:
            logger.error(f"Command failed (code {return_code}): {command}\nStderr: {stderr_str}")
        
        return return_code, stdout_str, stderr_str
        
    except Exception as e:
        logger.error(f"Error running command '{command}': {e}")
        return -1, "", str(e)

def run_command_sync(command: str, timeout: int = 300) -> tuple[int, str, str]:
    """
    Run a shell command synchronously (blocking).
    
    Returns:
        (return_code, stdout, stderr)
    """
    try:
        logger.info(f"Running command (sync): {command}")
        
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if result.returncode == 0:
            logger.info(f"Command successful: {command}")
        else:
            logger.error(f"Command failed (code {result.returncode}): {command}\nStderr: {result.stderr}")
        
        return result.returncode, result.stdout.strip(), result.stderr.strip()
        
    except subprocess.TimeoutExpired:
        logger.error(f"Command timed out after {timeout}s: {command}")
        return -1, "", "Command timed out"
    except Exception as e:
        logger.error(f"Error running command '{command}': {e}")
        return -1, "", str(e)

# ============================================================================
# HTTP REQUEST UTILITIES
# ============================================================================

async def fetch_url(url: str, timeout: int = None) -> Optional[Dict[Any, Any]]:
    """
    Fetch JSON data from URL.
    
    Returns:
        JSON response or None if failed
    """
    if timeout is None:
        timeout = config.REQUEST_TIMEOUT
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=timeout) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.warning(f"HTTP {response.status} from {url}")
                    return None
    except asyncio.TimeoutError:
        logger.error(f"Request timeout for {url}")
        return None
    except Exception as e:
        logger.error(f"Error fetching {url}: {e}")
        return None

async def post_json(url: str, data: Dict[Any, Any], timeout: int = None) -> Optional[Dict[Any, Any]]:
    """
    POST JSON data to URL.
    
    Returns:
        JSON response or None if failed
    """
    if timeout is None:
        timeout = config.REQUEST_TIMEOUT
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data, timeout=timeout) as response:
                if response.status in [200, 201]:
                    return await response.json()
                else:
                    logger.warning(f"HTTP {response.status} from {url}")
                    text = await response.text()
                    logger.debug(f"Response: {text}")
                    return None
    except asyncio.TimeoutError:
        logger.error(f"Request timeout for {url}")
        return None
    except Exception as e:
        logger.error(f"Error posting to {url}: {e}")
        return None

async def check_url_reachable(url: str, timeout: int = 10) -> bool:
    """Check if a URL is reachable."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=timeout) as response:
                return response.status == 200
    except:
        return False

async def wait_for_url(url: str, max_wait: int = 300, check_interval: int = 5) -> bool:
    """
    Wait for a URL to become reachable.
    
    Args:
        url: URL to check
        max_wait: Maximum time to wait in seconds
        check_interval: How often to check in seconds
    
    Returns:
        True if URL became reachable, False if timed out
    """
    logger.info(f"Waiting for {url} to become reachable...")
    elapsed = 0
    
    while elapsed < max_wait:
        if await check_url_reachable(url, timeout=check_interval):
            logger.info(f"{url} is now reachable!")
            return True
        
        await asyncio.sleep(check_interval)
        elapsed += check_interval
        logger.debug(f"Still waiting for {url}... ({elapsed}/{max_wait}s)")
    
    logger.error(f"Timeout waiting for {url} after {max_wait}s")
    return False

# ============================================================================
# COMFYUI SPECIFIC UTILITIES
# ============================================================================

async def check_comfyui_ready(base_url: str) -> bool:
    """Check if ComfyUI is ready by hitting the system_stats endpoint."""
    url = base_url.rstrip('/') + config.COMFYUI_API['system_stats']
    return await check_url_reachable(url)

async def wait_for_comfyui(base_url: str, max_wait: int = None) -> bool:
    """
    Wait for ComfyUI to become ready.
    
    Returns:
        True if ComfyUI is ready, False if timed out
    """
    if max_wait is None:
        max_wait = config.COMFYUI_STARTUP_TIMEOUT
    
    url = base_url.rstrip('/') + config.COMFYUI_API['system_stats']
    return await wait_for_url(url, max_wait, config.COMFYUI_CHECK_INTERVAL)

async def send_comfyui_prompt(base_url: str, workflow: Dict[Any, Any], prompt: str) -> Optional[Dict[Any, Any]]:
    """
    Send a generation prompt to ComfyUI.
    
    Args:
        base_url: ComfyUI base URL
        workflow: Workflow JSON
        prompt: Text prompt to inject
    
    Returns:
        Response JSON or None if failed
    """
    # Inject prompt into workflow (this is simplified - actual implementation
    # would need to find the correct node to inject the prompt into)
    # TODO: Implement proper prompt injection logic
    
    url = base_url.rstrip('/') + config.COMFYUI_API['prompt']
    payload = {
        "prompt": workflow,
        "client_id": "discord_bot"
    }
    
    return await post_json(url, payload)

# ============================================================================
# MODAL VOLUME UTILITIES
# ============================================================================

async def list_modal_volume_files(volume_name: str, path: str) -> List[str]:
    """
    List files in a Modal volume path.
    
    Returns:
        List of filenames
    """
    command = config.get_modal_command(
        'volume_ls',
        volume_name=volume_name,
        path=path
    )
    
    return_code, stdout, stderr = await run_command(command)
    
    if return_code != 0:
        logger.error(f"Failed to list volume files: {stderr}")
        return []
    
    # Parse output (format depends on Modal CLI output)
    files = [line.strip() for line in stdout.split('\n') if line.strip()]
    return files

async def download_from_modal_volume(volume_name: str, remote_path: str, local_path: Path) -> bool:
    """
    Download a file from Modal volume.
    
    Returns:
        True if successful, False otherwise
    """
    ensure_directory(local_path.parent)
    
    command = config.get_modal_command(
        'volume_get',
        volume_name=volume_name,
        remote_path=remote_path,
        local_path=str(local_path)
    )
    
    return_code, stdout, stderr = await run_command(command)
    
    if return_code != 0:
        logger.error(f"Failed to download from volume: {stderr}")
        return False
    
    return local_path.exists()

async def read_balance_from_volume(volume_name: str) -> Optional[float]:
    """
    Read credit balance from balance.json in Modal volume.
    
    Returns:
        Balance amount or None if failed
    """
    # Download balance.json to temp location
    temp_balance_file = config.TEMP_DIR / "balance.json"
    
    success = await download_from_modal_volume(
        volume_name=volume_name,
        remote_path=config.MODAL_PATHS['balance_json'],
        local_path=temp_balance_file
    )
    
    if not success:
        logger.error("Failed to download balance.json")
        return None
    
    # Read balance from JSON
    data = read_json_file(temp_balance_file)
    if not data:
        return None
    
    # Extract balance (adjust key name based on your JSON structure)
    balance = data.get('balance') or data.get('credits') or data.get('amount')
    
    if balance is None:
        logger.error(f"Could not find balance in JSON: {data}")
        return None
    
    try:
        return float(balance)
    except (ValueError, TypeError):
        logger.error(f"Invalid balance value: {balance}")
        return None

# ============================================================================
# STRING FORMATTING UTILITIES
# ============================================================================

def format_time_remaining(seconds: int) -> str:
    """Format seconds into human-readable time."""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes}m"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        if minutes > 0:
            return f"{hours}h {minutes}m"
        return f"{hours}h"

def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate string to maximum length."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

# ============================================================================
# VALIDATION UTILITIES
# ============================================================================

def validate_modal_token(token_id: str, token_secret: str) -> tuple[bool, str]:
    """
    Validate Modal token format.
    
    Returns:
        (is_valid, error_message)
    """
    if not token_id or not token_secret:
        return False, "Token ID and Secret cannot be empty"
    
    if not token_id.startswith('ak-'):
        return False, "Token ID must start with 'ak-'"
    
    if not token_secret.startswith('as-'):
        return False, "Token Secret must start with 'as-'"
    
    if len(token_id) < 10:
        return False, "Token ID is too short"
    
    if len(token_secret) < 10:
        return False, "Token Secret is too short"
    
    return True, ""

def validate_username(username: str) -> tuple[bool, str]:
    """
    Validate username format.
    
    Returns:
        (is_valid, error_message)
    """
    if not username:
        return False, "Username cannot be empty"
    
    if len(username) < 3:
        return False, "Username must be at least 3 characters"
    
    if len(username) > 50:
        return False, "Username must be less than 50 characters"
    
    # Check for valid characters (alphanumeric, underscore, hyphen)
    if not username.replace('_', '').replace('-', '').isalnum():
        return False, "Username can only contain letters, numbers, underscore, and hyphen"
    
    return True, ""

# ============================================================================
# END OF UTILITIES
# ============================================================================
