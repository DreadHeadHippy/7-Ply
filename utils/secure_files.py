"""
Secure file operations for 7-Ply Discord Bot
Provides safe JSON file handling with validation, locking, and backups
"""

import json
import os
import time
import shutil
import tempfile
import hashlib
import logging
from typing import Dict, Any, Optional
from contextlib import contextmanager

# Configure file security logging
file_logger = logging.getLogger('7ply_file_security')

class SecureFileHandler:
    """Secure JSON file operations with validation and atomic writes"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.backup_dir = os.path.join(os.path.dirname(file_path), "backups")
        self.lock_file = f"{file_path}.lock"
        
        # Ensure directories exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)
    
    @contextmanager
    def file_lock(self):
        """Context manager for file locking"""
        lock_fd = None
        try:
            # Create lock file
            lock_fd = os.open(self.lock_file, os.O_CREAT | os.O_EXCL | os.O_RDWR)
            
            # Write process info to lock file
            lock_info = f"PID:{os.getpid()},TIME:{int(time.time())}\n"
            os.write(lock_fd, lock_info.encode())
            
            yield
            
        except OSError as e:
            if e.errno == 17:  # File exists (another process has lock)
                # Check if lock is stale (older than 30 seconds)
                try:
                    stat = os.stat(self.lock_file)
                    if time.time() - stat.st_mtime > 30:
                        os.unlink(self.lock_file)
                        raise Exception("Stale lock removed, please retry")
                    else:
                        raise Exception("File is locked by another process")
                except FileNotFoundError:
                    raise Exception("Lock file disappeared, please retry")
            else:
                raise Exception(f"Failed to acquire file lock: {e}")
        finally:
            # Clean up lock
            if lock_fd is not None:
                os.close(lock_fd)
                try:
                    os.unlink(self.lock_file)
                except FileNotFoundError:
                    pass  # Lock already removed
    
    def validate_json_data(self, data: Any) -> tuple[bool, str]:
        """
        Validate JSON data for security issues
        Returns: (is_valid, error_message)
        """
        if not isinstance(data, dict):
            return False, "Root must be a dictionary"
        
        # Check total size
        try:
            json_str = json.dumps(data)
            if len(json_str) > 10 * 1024 * 1024:  # 10MB limit
                return False, "Data too large (>10MB)"
        except Exception:
            return False, "Data not JSON serializable"
        
        # Check for suspicious keys/values
        def check_dict_recursive(obj, depth=0):
            if depth > 50:  # Prevent deeply nested objects
                return False, "Data too deeply nested"
            
            if isinstance(obj, dict):
                if len(obj) > 10000:  # Prevent too many keys
                    return False, "Too many keys in dictionary"
                
                for key, value in obj.items():
                    # Check key security
                    if not isinstance(key, str):
                        return False, f"Non-string key found: {type(key)}"
                    if len(key) > 1000:
                        return False, "Key too long"
                    
                    # Recursively check values
                    valid, msg = check_dict_recursive(value, depth + 1)
                    if not valid:
                        return False, msg
            
            elif isinstance(obj, list):
                if len(obj) > 10000:  # Prevent huge lists
                    return False, "List too large"
                
                for item in obj:
                    valid, msg = check_dict_recursive(item, depth + 1)
                    if not valid:
                        return False, msg
            
            elif isinstance(obj, str):
                if len(obj) > 100000:  # 100KB string limit
                    return False, "String value too long"
            
            return True, ""
        
        return check_dict_recursive(data)
    
    def create_backup(self) -> Optional[str]:
        """Create a timestamped backup of the current file"""
        if not os.path.exists(self.file_path):
            return None
        
        try:
            timestamp = int(time.time())
            backup_name = f"{os.path.basename(self.file_path)}.{timestamp}.bak"
            backup_path = os.path.join(self.backup_dir, backup_name)
            
            shutil.copy2(self.file_path, backup_path)
            file_logger.info(f"Created backup: {backup_path}")
            
            # Clean old backups (keep only last 10)
            self.cleanup_old_backups()
            
            return backup_path
        except Exception as e:
            file_logger.error(f"Failed to create backup: {e}")
            return None
    
    def cleanup_old_backups(self):
        """Keep only the 10 most recent backups"""
        try:
            base_name = os.path.basename(self.file_path)
            backups = []
            
            for filename in os.listdir(self.backup_dir):
                if filename.startswith(base_name) and filename.endswith('.bak'):
                    backup_path = os.path.join(self.backup_dir, filename)
                    timestamp = os.path.getctime(backup_path)
                    backups.append((timestamp, backup_path))
            
            # Sort by timestamp (newest first) and remove old ones
            backups.sort(reverse=True)
            for _, old_backup in backups[10:]:
                os.unlink(old_backup)
                file_logger.info(f"Removed old backup: {old_backup}")
        
        except Exception as e:
            file_logger.error(f"Failed to cleanup backups: {e}")
    
    def safe_load(self) -> Dict[str, Any]:
        """Safely load JSON data with validation and error handling"""
        with self.file_lock():
            try:
                if not os.path.exists(self.file_path):
                    file_logger.info(f"File not found, creating empty: {self.file_path}")
                    return {}
                
                # Check file size
                file_size = os.path.getsize(self.file_path)
                if file_size > 50 * 1024 * 1024:  # 50MB limit
                    file_logger.error(f"File too large: {file_size} bytes")
                    raise Exception("File too large for security")
                
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Validate loaded data
                valid, error = self.validate_json_data(data)
                if not valid:
                    file_logger.error(f"Data validation failed: {error}")
                    raise Exception(f"Data validation failed: {error}")
                
                return data
                
            except json.JSONDecodeError as e:
                file_logger.error(f"JSON decode error in {self.file_path}: {e}")
                # Try to restore from backup
                return self.restore_from_backup()
            
            except Exception as e:
                file_logger.error(f"Failed to load {self.file_path}: {e}")
                return {}
    
    def safe_save(self, data: Dict[str, Any]) -> bool:
        """Safely save JSON data with atomic writes and validation"""
        with self.file_lock():
            try:
                # Validate data before saving
                valid, error = self.validate_json_data(data)
                if not valid:
                    file_logger.error(f"Cannot save invalid data: {error}")
                    return False
                
                # Create backup before modifying
                self.create_backup()
                
                # Atomic write using temporary file
                temp_fd, temp_path = tempfile.mkstemp(
                    dir=os.path.dirname(self.file_path),
                    prefix=f".{os.path.basename(self.file_path)}.tmp"
                )
                
                try:
                    with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                        f.flush()
                        os.fsync(f.fileno())  # Force write to disk
                    
                    # Atomic move
                    if os.name == 'nt':  # Windows
                        if os.path.exists(self.file_path):
                            os.unlink(self.file_path)
                    os.rename(temp_path, self.file_path)
                    
                    file_logger.info(f"Successfully saved {self.file_path}")
                    return True
                    
                except Exception as e:
                    # Clean up temp file on error
                    try:
                        os.unlink(temp_path)
                    except:
                        pass
                    raise e
                    
            except Exception as e:
                file_logger.error(f"Failed to save {self.file_path}: {e}")
                return False
    
    def restore_from_backup(self) -> Dict[str, Any]:
        """Restore data from the most recent valid backup"""
        try:
            base_name = os.path.basename(self.file_path)
            backups = []
            
            for filename in os.listdir(self.backup_dir):
                if filename.startswith(base_name) and filename.endswith('.bak'):
                    backup_path = os.path.join(self.backup_dir, filename)
                    timestamp = os.path.getctime(backup_path)
                    backups.append((timestamp, backup_path))
            
            # Try backups from newest to oldest
            backups.sort(reverse=True)
            for _, backup_path in backups:
                try:
                    with open(backup_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Validate backup data
                    valid, error = self.validate_json_data(data)
                    if valid:
                        file_logger.info(f"Restored from backup: {backup_path}")
                        return data
                    else:
                        file_logger.warning(f"Invalid backup data: {backup_path} - {error}")
                        
                except Exception as e:
                    file_logger.warning(f"Failed to load backup {backup_path}: {e}")
            
            file_logger.error("No valid backups found")
            return {}
            
        except Exception as e:
            file_logger.error(f"Failed to restore from backup: {e}")
            return {}

# Secure file handlers for bot data
def get_secure_ranking_handler() -> SecureFileHandler:
    """Get secure handler for user ranking data"""
    return SecureFileHandler("data/user_ranks.json")

def get_secure_config_handler() -> SecureFileHandler:
    """Get secure handler for server configuration data"""
    return SecureFileHandler("data/server_configs.json")