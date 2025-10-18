"""
Security utilities for 7-Ply Discord Bot
Provides input validation, sanitization, and security checks
"""

import re
import discord
from typing import Optional, Tuple, List, Dict
import time
from collections import defaultdict, deque

# Import configured loggers
from .logging_config import security_logger

class SecurityValidator:
    """Security validation and sanitization utilities"""
    
    # Maximum lengths for various inputs
    MAX_MESSAGE_LENGTH = 1900  # Discord limit is 2000, leave buffer
    MAX_EMBED_TITLE_LENGTH = 256
    MAX_EMBED_DESCRIPTION_LENGTH = 4096
    MAX_CHANNEL_NAME_LENGTH = 100
    
    # Dangerous patterns to detect/block
    DANGEROUS_PATTERNS = [
        r'@everyone',
        r'@here', 
        r'<@&\d+>',  # Role mentions
        r'https?://discord\.gg/[a-zA-Z0-9]+',  # Discord invites
        r'https?://discord\.com/invite/[a-zA-Z0-9]+',  # Discord invites
    ]
    
    # Allowed characters for various inputs
    SAFE_MESSAGE_PATTERN = re.compile(r'^[\w\s\-_.,!?@#$%^&*()+=\[\]{}|\\:";\'<>/?`~]*$')
    SAFE_CHANNEL_NAME_PATTERN = re.compile(r'^[a-z0-9\-_]+$')
    
    @classmethod
    def is_privileged_user(cls, interaction: discord.Interaction) -> bool:
        """Check if user has admin or mod permissions"""
        if not interaction.guild or not isinstance(interaction.user, discord.Member):
            return False
        
        member = interaction.user
        return (member.guild_permissions.administrator or 
                member.guild_permissions.manage_messages)
    
    @classmethod
    def sanitize_message(cls, message: str, interaction: Optional[discord.Interaction] = None) -> Tuple[str, List[str]]:
        """
        Sanitize user message input for /say, /announce commands
        Admins/mods can use @everyone/@here, regular users cannot
        Returns: (sanitized_message, list_of_warnings)
        """
        warnings = []
        original_message = message
        is_privileged = interaction and cls.is_privileged_user(interaction)
        
        # Length check
        if len(message) > cls.MAX_MESSAGE_LENGTH:
            message = message[:cls.MAX_MESSAGE_LENGTH]
            warnings.append(f"Message truncated to {cls.MAX_MESSAGE_LENGTH} characters")
        
        # Remove null bytes and control characters
        message = ''.join(char for char in message if ord(char) >= 32 or char in '\n\r\t')
        
        # Check for dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, message, re.IGNORECASE):
                # Allow @everyone/@here for privileged users, block for others
                if ('@everyone' in pattern or '@here' in pattern) and is_privileged:
                    continue  # Allow it
                elif '@everyone' in pattern or '@here' in pattern:
                    message = re.sub(pattern, '[everyone]', message, flags=re.IGNORECASE)
                    warnings.append("Mass mentions replaced with [everyone] (admins/mods can use mass mentions)")
                elif 'discord.gg' in pattern or 'discord.com/invite' in pattern:
                    message = re.sub(pattern, '[invite-removed]', message, flags=re.IGNORECASE)
                    warnings.append("Discord invites removed")
        
        # Log security events
        if warnings:
            user_info = f"user {interaction.user.id}" if interaction else "unknown user"
            security_logger.warning(f"Message sanitized: {len(warnings)} issues found in message from {user_info}")
        
        return message, warnings
    
    @classmethod
    def sanitize_embed_content(cls, title: Optional[str], description: str, interaction: Optional[discord.Interaction] = None) -> Tuple[Optional[str], str, List[str]]:
        """
        Sanitize embed content for /embed command
        Returns: (sanitized_title, sanitized_description, warnings)
        """
        warnings = []
        
        # Sanitize title
        if title:
            if len(title) > cls.MAX_EMBED_TITLE_LENGTH:
                title = title[:cls.MAX_EMBED_TITLE_LENGTH]
                warnings.append("Title truncated")
            title, title_warnings = cls.sanitize_message(title, interaction)
            warnings.extend(title_warnings)
        
        # Sanitize description
        if len(description) > cls.MAX_EMBED_DESCRIPTION_LENGTH:
            description = description[:cls.MAX_EMBED_DESCRIPTION_LENGTH]
            warnings.append("Description truncated")
        
        description, desc_warnings = cls.sanitize_message(description, interaction)
        warnings.extend(desc_warnings)
        
        return title, description, warnings
    
    @classmethod
    def validate_channel_name(cls, name: str) -> Tuple[bool, str]:
        """
        Validate channel name for safety
        Returns: (is_valid, error_message)
        """
        if not name:
            return False, "Channel name cannot be empty"
        
        if len(name) > cls.MAX_CHANNEL_NAME_LENGTH:
            return False, f"Channel name too long (max {cls.MAX_CHANNEL_NAME_LENGTH})"
        
        if not cls.SAFE_CHANNEL_NAME_PATTERN.match(name):
            return False, "Channel name contains invalid characters (use lowercase letters, numbers, hyphens, underscores)"
        
        return True, ""
    
    @classmethod
    def validate_guild_context(cls, interaction: discord.Interaction) -> Tuple[bool, str]:
        """
        Validate that command is being used in proper guild context
        Returns: (is_valid, error_message)
        """
        if not interaction.guild:
            return False, "This command can only be used in a server"
        
        if not isinstance(interaction.user, discord.Member):
            return False, "User context invalid"
        
        return True, ""
    
    @classmethod
    def validate_admin_permissions(cls, interaction: discord.Interaction) -> Tuple[bool, str]:
        """
        Validate administrator permissions with security checks
        Returns: (has_permission, error_message)
        """
        # Check for suspicious activity first (keep this - it's useful)
        if security_monitor.is_user_suspicious(interaction.user.id):
            return False, SecureError.suspicious_activity_error()
        
        # First validate guild context
        valid_context, context_error = cls.validate_guild_context(interaction)
        if not valid_context:
            security_monitor.record_failed_attempt(interaction.user.id)
            return False, context_error
        
        # Check administrator permission - user is guaranteed to be Member after guild context check
        member = interaction.user
        if not isinstance(member, discord.Member) or not member.guild_permissions.administrator:
            guild_id = interaction.guild.id if interaction.guild else "Unknown"
            security_logger.warning(f"Non-admin user {interaction.user.id} attempted admin command in guild {guild_id}")
            security_monitor.record_failed_attempt(interaction.user.id)
            return False, "Administrator permissions required"
        
        return True, ""
    
    @classmethod 
    def validate_moderate_permissions(cls, interaction: discord.Interaction) -> Tuple[bool, str]:
        """
        Validate manage messages permissions with security checks
        Returns: (has_permission, error_message)
        """
        # Check for suspicious activity first (keep this - it's useful)
        if security_monitor.is_user_suspicious(interaction.user.id):
            return False, SecureError.suspicious_activity_error()
        
        # First validate guild context  
        valid_context, context_error = cls.validate_guild_context(interaction)
        if not valid_context:
            security_monitor.record_failed_attempt(interaction.user.id)
            return False, context_error
            
        # Check manage messages permission - user is guaranteed to be Member after guild context check
        member = interaction.user
        if not isinstance(member, discord.Member) or not member.guild_permissions.manage_messages:
            guild_id = interaction.guild.id if interaction.guild else "Unknown"
            security_logger.warning(f"User {interaction.user.id} without manage_messages attempted moderation command in guild {guild_id}")
            security_monitor.record_failed_attempt(interaction.user.id)
            return False, "Manage Messages permission required"
            
        return True, ""
    
    @classmethod
    def log_admin_action(cls, interaction: discord.Interaction, action: str, details: str = ""):
        """Log administrative actions for audit trail"""
        security_logger.info(
            f"Admin action: {action} | "
            f"User: {interaction.user.id} ({interaction.user}) | "
            f"Guild: {interaction.guild.id if interaction.guild else 'DM'} | "
            f"Details: {details}"
        )

class RateLimiter:
    """Rate limiting for regular users (admins/mods bypass this)"""
    
    def __init__(self):
        self.user_limits: Dict[str, Dict[int, deque]] = defaultdict(lambda: defaultdict(deque))
    
    def check_rate_limit(self, user_id: int, command_type: str, max_uses: int, window_seconds: int) -> Tuple[bool, int]:
        """Check if user is within rate limits. Returns (allowed, seconds_to_wait)"""
        now = time.time()
        user_history = self.user_limits[command_type][user_id]
        
        # Remove old entries outside the window
        while user_history and user_history[0] < now - window_seconds:
            user_history.popleft()
        
        # Check if under limit
        if len(user_history) < max_uses:
            user_history.append(now)
            return True, 0
        
        # Calculate wait time until oldest entry expires
        wait_time = int(user_history[0] + window_seconds - now) + 1
        return False, wait_time

class SecurityMonitor:
    """Monitor security events and suspicious behavior"""
    
    def __init__(self):
        # Track failed attempts per user (keep this - it's actually useful)
        self.failed_attempts: Dict[int, deque] = defaultdict(deque)
        
    def record_failed_attempt(self, user_id: int):
        """Record a failed permission/validation attempt"""
        now = time.time()
        user_failures = self.failed_attempts[user_id]
        
        # Remove failures older than 1 hour
        while user_failures and user_failures[0] < now - 3600:
            user_failures.popleft()
        
        user_failures.append(now)
        
        # Log if too many failures (potential attack)
        if len(user_failures) > 10:
            security_logger.warning(f"User {user_id} has {len(user_failures)} failed attempts in last hour - potential attack")
    
    def is_user_suspicious(self, user_id: int) -> bool:
        """Check if user has too many recent failed attempts"""
        now = time.time()
        user_failures = self.failed_attempts[user_id]
        
        # Count recent failures (last 10 minutes)
        recent_failures = sum(1 for attempt in user_failures if attempt > now - 600)
        return recent_failures > 5

# Global security instances
rate_limiter = RateLimiter()
security_monitor = SecurityMonitor()

class SecureError:
    """Secure error handling that doesn't leak information"""
    
    @staticmethod
    def generic_error() -> str:
        """Generic error message that doesn't reveal internal details"""
        return "❌ An error occurred while processing your request. Please try again later."
    
    @staticmethod
    def permission_error() -> str:
        """Generic permission denied message"""
        return "❌ You don't have permission to use this command."
    
    @staticmethod
    def guild_only_error() -> str:
        """Error for commands that require guild context"""
        return "❌ This command can only be used in a server."
    
    @staticmethod
    def invalid_input_error() -> str:
        """Error for invalid input without revealing what was invalid"""
        return "❌ Invalid input provided. Please check your command and try again."
    
    @staticmethod
    def rate_limit_error(seconds: int) -> str:
        """Rate limit error without revealing specific limits"""
        if seconds > 60:
            minutes = seconds // 60
            return f"❌ Please wait {minutes} minute{'s' if minutes != 1 else ''} before using this command again."
        else:
            return f"❌ Please wait {seconds} second{'s' if seconds != 1 else ''} before using this command again."
    
    @staticmethod
    def suspicious_activity_error() -> str:
        """Error for users with too many failed attempts"""
        return "❌ Too many failed attempts. Please wait before trying again."