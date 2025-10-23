"""
Account Manager Module
======================
Manages Modal accounts: add, remove, switch, track balances.
Uses SQLite database for encrypted storage.
"""

import sqlite3
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from pathlib import Path
import config
import utils

logger = logging.getLogger(__name__)

# ============================================================================
# DATABASE SCHEMA
# ============================================================================

CREATE_ACCOUNTS_TABLE = """
CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    token_id_encrypted TEXT NOT NULL,
    token_secret_encrypted TEXT NOT NULL,
    balance REAL DEFAULT 80.0,
    status TEXT DEFAULT 'ready',
    is_active INTEGER DEFAULT 0,
    selected_gpu TEXT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""

CREATE_USAGE_LOG_TABLE = """
CREATE TABLE IF NOT EXISTS usage_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    action TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    details TEXT,
    FOREIGN KEY (account_id) REFERENCES accounts (id)
)
"""

# ============================================================================
# ACCOUNT MANAGER CLASS
# ============================================================================

class AccountManager:
    """Manages Modal accounts and their credentials."""
    
    def __init__(self, db_path: Path = None):
        """Initialize account manager with database."""
        if db_path is None:
            db_path = config.DATABASE_FILE
        
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(CREATE_ACCOUNTS_TABLE)
            cursor.execute(CREATE_USAGE_LOG_TABLE)
            conn.commit()
            conn.close()
            logger.info(f"Database initialized: {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn
    
    # ========================================================================
    # ADD / REMOVE ACCOUNTS
    # ========================================================================
    
    def add_account(self, username: str, token_id: str, token_secret: str) -> tuple[bool, str]:
        """
        Add a new Modal account.
        
        Args:
            username: Account username/profile name
            token_id: Modal token ID (starts with 'ak-')
            token_secret: Modal token secret (starts with 'as-')
        
        Returns:
            (success, message)
        """
        # Validate username
        valid, error = utils.validate_username(username)
        if not valid:
            return False, error
        
        # Validate tokens
        valid, error = utils.validate_modal_token(token_id, token_secret)
        if not valid:
            return False, error
        
        # Check account limit
        if self.get_account_count() >= config.MAX_ACCOUNTS:
            return False, f"Maximum account limit reached ({config.MAX_ACCOUNTS} accounts)"
        
        # Check if username already exists
        if self.get_account_by_username(username):
            return False, f"Account '{username}' already exists"
        
        try:
            # Encrypt tokens
            token_id_encrypted = utils.encrypt_data(token_id)
            token_secret_encrypted = utils.encrypt_data(token_secret)
            
            # Insert into database
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO accounts (username, token_id_encrypted, token_secret_encrypted, balance, status)
                VALUES (?, ?, ?, ?, ?)
            """, (username, token_id_encrypted, token_secret_encrypted, config.INITIAL_BALANCE, 'ready'))
            
            account_id = cursor.lastrowid
            
            # Log the action
            self._log_action(account_id, 'account_added', 'New account created')
            
            conn.commit()
            conn.close()
            
            logger.info(f"Account '{username}' added successfully")
            return True, f"Account '{username}' added successfully!"
            
        except Exception as e:
            logger.error(f"Failed to add account '{username}': {e}")
            return False, f"Database error: {str(e)}"
    
    def remove_account(self, username: str) -> tuple[bool, str]:
        """
        Remove a Modal account.
        
        Args:
            username: Account username to remove
        
        Returns:
            (success, message)
        """
        account = self.get_account_by_username(username)
        if not account:
            return False, f"Account '{username}' not found"
        
        # Don't allow removing active account
        if account['is_active']:
            return False, f"Cannot remove active account. Switch to another account first."
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Log before deletion
            self._log_action(account['id'], 'account_removed', 'Account deleted')
            
            # Delete account
            cursor.execute("DELETE FROM accounts WHERE username = ?", (username,))
            conn.commit()
            conn.close()
            
            logger.info(f"Account '{username}' removed successfully")
            return True, f"Account '{username}' removed successfully!"
            
        except Exception as e:
            logger.error(f"Failed to remove account '{username}': {e}")
            return False, f"Database error: {str(e)}"
    
    # ========================================================================
    # GET ACCOUNTS
    # ========================================================================
    
    def get_account_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get account by username."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM accounts WHERE username = ?", (username,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return dict(row)
            return None
            
        except Exception as e:
            logger.error(f"Failed to get account '{username}': {e}")
            return None
    
    def get_account_by_id(self, account_id: int) -> Optional[Dict[str, Any]]:
        """Get account by ID."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM accounts WHERE id = ?", (account_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return dict(row)
            return None
            
        except Exception as e:
            logger.error(f"Failed to get account ID {account_id}: {e}")
            return None
    
    def get_all_accounts(self) -> List[Dict[str, Any]]:
        """Get all accounts."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM accounts ORDER BY created_at ASC")
            rows = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Failed to get all accounts: {e}")
            return []
    
    def get_active_account(self) -> Optional[Dict[str, Any]]:
        """Get the currently active account."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM accounts WHERE is_active = 1 LIMIT 1")
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return dict(row)
            return None
            
        except Exception as e:
            logger.error(f"Failed to get active account: {e}")
            return None
    
    def get_account_count(self) -> int:
        """Get total number of accounts."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM accounts")
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except Exception as e:
            logger.error(f"Failed to get account count: {e}")
            return 0
    
    # ========================================================================
    # DECRYPT CREDENTIALS
    # ========================================================================
    
    def get_decrypted_credentials(self, username: str) -> Optional[Dict[str, str]]:
        """
        Get decrypted credentials for an account.
        
        Returns:
            {'username': str, 'token_id': str, 'token_secret': str} or None
        """
        account = self.get_account_by_username(username)
        if not account:
            return None
        
        try:
            token_id = utils.decrypt_data(account['token_id_encrypted'])
            token_secret = utils.decrypt_data(account['token_secret_encrypted'])
            
            return {
                'username': username,
                'token_id': token_id,
                'token_secret': token_secret
            }
        except Exception as e:
            logger.error(f"Failed to decrypt credentials for '{username}': {e}")
            return None
    
    # ========================================================================
    # UPDATE ACCOUNT DATA
    # ========================================================================
    
    def update_balance(self, username: str, balance: float) -> bool:
        """Update account balance."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE accounts 
                SET balance = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE username = ?
            """, (balance, username))
            conn.commit()
            conn.close()
            
            logger.info(f"Updated balance for '{username}': ${balance:.2f}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update balance for '{username}': {e}")
            return False
    
    def update_status(self, username: str, status: str) -> bool:
        """
        Update account status.
        
        Status can be: 'active', 'ready', 'dead', 'building'
        """
        valid_statuses = ['active', 'ready', 'dead', 'building']
        if status not in valid_statuses:
            logger.error(f"Invalid status: {status}")
            return False
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE accounts 
                SET status = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE username = ?
            """, (status, username))
            conn.commit()
            conn.close()
            
            logger.info(f"Updated status for '{username}': {status}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update status for '{username}': {e}")
            return False
    
    def set_active_account(self, username: str) -> bool:
        """Set an account as active (and deactivate others)."""
        account = self.get_account_by_username(username)
        if not account:
            logger.error(f"Account '{username}' not found")
            return False
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Deactivate all accounts
            cursor.execute("UPDATE accounts SET is_active = 0")
            
            # Activate the specified account
            cursor.execute("""
                UPDATE accounts 
                SET is_active = 1, updated_at = CURRENT_TIMESTAMP 
                WHERE username = ?
            """, (username,))
            
            # Log the action
            self._log_action(account['id'], 'account_activated', 'Set as active account')
            
            conn.commit()
            conn.close()
            
            logger.info(f"Set '{username}' as active account")
            return True
            
        except Exception as e:
            logger.error(f"Failed to set active account '{username}': {e}")
            return False
    
    def update_selected_gpu(self, username: str, gpu: str) -> bool:
        """Update selected GPU for an account."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE accounts 
                SET selected_gpu = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE username = ?
            """, (gpu, username))
            conn.commit()
            conn.close()
            
            logger.info(f"Updated GPU for '{username}': {gpu}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update GPU for '{username}': {e}")
            return False
    
    # ========================================================================
    # ACCOUNT SELECTION LOGIC
    # ========================================================================
    
    def get_next_available_account(self, min_balance: float = None) -> Optional[Dict[str, Any]]:
        """
        Get next available account with sufficient balance.
        
        Args:
            min_balance: Minimum balance required (default: config.MIN_CREDIT_THRESHOLD)
        
        Returns:
            Account dict or None if no available account
        """
        if min_balance is None:
            min_balance = config.MIN_CREDIT_THRESHOLD
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM accounts 
                WHERE is_active = 0 
                AND balance >= ? 
                AND status != 'dead'
                ORDER BY balance DESC
                LIMIT 1
            """, (min_balance,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return dict(row)
            return None
            
        except Exception as e:
            logger.error(f"Failed to get next available account: {e}")
            return None
    
    def has_available_accounts(self, min_balance: float = None) -> bool:
        """Check if there are any available accounts with sufficient balance."""
        return self.get_next_available_account(min_balance) is not None
    
    # ========================================================================
    # USAGE LOGGING
    # ========================================================================
    
    def _log_action(self, account_id: int, action: str, details: str = None):
        """Log an action for an account."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO usage_log (account_id, action, details)
                VALUES (?, ?, ?)
            """, (account_id, action, details))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to log action: {e}")
    
    def get_account_history(self, username: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get action history for an account."""
        account = self.get_account_by_username(username)
        if not account:
            return []
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM usage_log 
                WHERE account_id = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (account['id'], limit))
            rows = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Failed to get history for '{username}': {e}")
            return []
    
    # ========================================================================
    # STATISTICS
    # ========================================================================
    
    def get_total_balance(self) -> float:
        """Get total balance across all accounts."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT SUM(balance) FROM accounts")
            result = cursor.fetchone()[0]
            conn.close()
            return result if result else 0.0
        except Exception as e:
            logger.error(f"Failed to get total balance: {e}")
            return 0.0
    
    def get_accounts_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Get all accounts with a specific status."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM accounts WHERE status = ?", (status,))
            rows = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Failed to get accounts by status '{status}': {e}")
            return []

# ============================================================================
# GLOBAL INSTANCE
# ============================================================================

# Create a global instance for easy access
account_manager = AccountManager()

# ============================================================================
# END OF ACCOUNT MANAGER
# ============================================================================
