"""
Admin Commands Cog
Contains administrative slash commands for server management
"""

from discord.ext import commands
from discord import app_commands
import discord
from typing import Optional
import sys
import os
import time

# Import security utilities
from utils.security import SecurityValidator, SecureError

class AdminCommands(commands.Cog):
    """Administrative commands for server management"""
    
    def __init__(self, bot):
        self.bot = bot
        self.command_cooldowns = {}  # Store last use times
        self.user_slowmodes = {}  # Store per-user slowmode settings {guild_id: {user_id: slowmode_seconds}}
        self.user_last_message = {}  # Track last message times {guild_id: {user_id: timestamp}}
    
    def check_cooldown(self, user_id: int, command_name: str, cooldown_seconds: int = 5) -> bool:
        """Check if user is on cooldown for a command"""
        key = f"{user_id}_{command_name}"
        current_time = time.time()
        
        if key in self.command_cooldowns:
            time_since_last = current_time - self.command_cooldowns[key]
            if time_since_last < cooldown_seconds:
                return False
        
        self.command_cooldowns[key] = current_time
        return True

    @app_commands.command(name='say', description='Make the bot say something')
    @app_commands.default_permissions(manage_messages=True)
    async def say(self, interaction: discord.Interaction, channel: Optional[discord.TextChannel] = None, *, message: str):
        """Make the bot say something in a specific channel or current channel"""
        
        # Rate limiting (5 second cooldown)
        if not self.check_cooldown(interaction.user.id, "say", 5):
            await interaction.response.send_message(
                SecureError.rate_limit_error(5),
                ephemeral=True
            )
            return
        
        # Security validation
        has_permission, perm_error = SecurityValidator.validate_moderate_permissions(interaction)
        if not has_permission:
            await interaction.response.send_message(SecureError.permission_error(), ephemeral=True)
            return
        
        # Sanitize input
        sanitized_message, warnings = SecurityValidator.sanitize_message(message, interaction)
        
        # Validate target channel
        target_channel = channel or interaction.channel
        if not isinstance(target_channel, discord.TextChannel):
            await interaction.response.send_message("❌ Can only send messages to text channels.", ephemeral=True)
            return
        
        # Log admin action
        SecurityValidator.log_admin_action(
            interaction, 
            "say_command", 
            f"Channel: {target_channel.name} ({target_channel.id}), Length: {len(sanitized_message)}"
        )
        
        try:
            # Send the sanitized message
            await target_channel.send(sanitized_message)
            
            # Build success response
            success_msg = "✅ Message sent"
            if channel:
                success_msg += f" to {channel.mention}"
            if warnings:
                success_msg += f"\n⚠️ Content modified: {', '.join(warnings)}"
            success_msg += "!"
            
            await interaction.response.send_message(success_msg, ephemeral=True)
                    
        except discord.Forbidden:
            await interaction.response.send_message("❌ I don't have permission to send messages in that channel.", ephemeral=True)
        except discord.HTTPException:
            await interaction.response.send_message(SecureError.invalid_input_error(), ephemeral=True)
        except Exception:
            await interaction.response.send_message(SecureError.generic_error(), ephemeral=True)

    @app_commands.command(name='announce', description='Make a skateboard-themed announcement')
    @app_commands.default_permissions(manage_messages=True)
    async def announce(self, interaction: discord.Interaction, channel: Optional[discord.TextChannel] = None, *, message: str):
        """Make a skateboard-themed announcement"""
        
        # Rate limiting (10 second cooldown for announces)
        if not self.check_cooldown(interaction.user.id, "announce", 10):
            await interaction.response.send_message(
                SecureError.rate_limit_error(10),
                ephemeral=True
            )
            return
        
        # Security validation
        has_permission, perm_error = SecurityValidator.validate_moderate_permissions(interaction)
        if not has_permission:
            await interaction.response.send_message(SecureError.permission_error(), ephemeral=True)
            return
        
        # Sanitize input
        sanitized_message, warnings = SecurityValidator.sanitize_message(message, interaction)
        
        # Validate target channel
        target_channel = channel or interaction.channel
        if not isinstance(target_channel, discord.TextChannel):
            await interaction.response.send_message("❌ Can only send announcements to text channels.", ephemeral=True)
            return
        
        # Log admin action
        SecurityValidator.log_admin_action(
            interaction, 
            "announce_command", 
            f"Channel: {target_channel.name} ({target_channel.id}), Length: {len(sanitized_message)}"
        )
        
        try:
            embed = discord.Embed(
                title="🛹 7-Ply Announcement 🛹",
                description=sanitized_message,
                color=0x00ff00
            )
            embed.set_footer(text="Stay radical! 🤙", icon_url=self.bot.user.display_avatar.url)
            
            await target_channel.send(embed=embed)
            
            # Build success response
            success_msg = "✅ Announcement sent"
            if channel:
                success_msg += f" to {channel.mention}"
            if warnings:
                success_msg += f"\n⚠️ Content modified: {', '.join(warnings)}"
            success_msg += "!"
            
            await interaction.response.send_message(success_msg, ephemeral=True)
                    
        except discord.Forbidden:
            await interaction.response.send_message("❌ I don't have permission to send messages in that channel.", ephemeral=True)
        except discord.HTTPException:
            await interaction.response.send_message(SecureError.invalid_input_error(), ephemeral=True)
        except Exception:
            await interaction.response.send_message(SecureError.generic_error(), ephemeral=True)

    @app_commands.command(name='embed', description='Send a custom embed message')
    @app_commands.default_permissions(manage_messages=True)
    async def embed(self, interaction: discord.Interaction, channel: Optional[discord.TextChannel] = None, title: str = "", *, description: str):
        """Send a custom embed message"""
        
        # Rate limiting (15 second cooldown for embeds)
        if not self.check_cooldown(interaction.user.id, "embed", 15):
            await interaction.response.send_message(
                SecureError.rate_limit_error(15),
                ephemeral=True
            )
            return
        
        # Security validation
        has_permission, perm_error = SecurityValidator.validate_moderate_permissions(interaction)
        if not has_permission:
            await interaction.response.send_message(SecureError.permission_error(), ephemeral=True)
            return
        
        # Sanitize input
        sanitized_title, sanitized_description, warnings = SecurityValidator.sanitize_embed_content(title, description, interaction)
        
        # Validate target channel
        target_channel = channel or interaction.channel
        if not isinstance(target_channel, discord.TextChannel):
            await interaction.response.send_message("❌ Can only send embeds to text channels.", ephemeral=True)
            return
        
        # Log admin action
        SecurityValidator.log_admin_action(
            interaction, 
            "embed_command", 
            f"Channel: {target_channel.name} ({target_channel.id}), Title: {bool(title)}, Description Length: {len(sanitized_description)}"
        )
        
        try:
            embed = discord.Embed(
                title=sanitized_title if sanitized_title else None,
                description=sanitized_description,
                color=0x00ff00
            )
            
            await target_channel.send(embed=embed)
            
            # Build success response
            success_msg = "✅ Embed sent"
            if channel:
                success_msg += f" to {channel.mention}"
            if warnings:
                success_msg += f"\n⚠️ Content modified: {', '.join(warnings)}"
            success_msg += "!"
            
            await interaction.response.send_message(success_msg, ephemeral=True)
                    
        except discord.Forbidden:
            await interaction.response.send_message("❌ I don't have permission to send messages in that channel.", ephemeral=True)
        except discord.HTTPException:
            await interaction.response.send_message(SecureError.invalid_input_error(), ephemeral=True)
        except Exception:
            await interaction.response.send_message(SecureError.generic_error(), ephemeral=True)

    @app_commands.command(name='help', description='Show available commands based on your permissions')
    async def help_slash(self, interaction: discord.Interaction):
        """Show help with commands organized by permission level"""
        user = interaction.user
        is_owner = await self.bot.is_owner(user)
        is_admin = isinstance(user, discord.Member) and user.guild_permissions.administrator
        is_mod = isinstance(user, discord.Member) and user.guild_permissions.manage_messages
        
        embed = discord.Embed(
            title="🛹 7-Ply Bot Commands",
            description="Commands available based on your permissions:",
            color=0x00ff00
        )
        
        # Everyone can use these
        embed.add_field(
            name="🎮 **Member Commands**",
            value=(
                "`/rank [user]` - Check ranking progress\n"
                "`/leaderboard` - View top-ranked members\n"
                "`/1up @user` - Give someone a 25-point boost\n"
                "`/trick` - Perform a random skateboard trick\n"
                "`/skatefact` - Learn skateboarding facts\n"
                "`/ping` - Test bot responsiveness\n"
                "`/help` - Show this help message"
            ),
            inline=False
        )
        
        # Moderator commands (Manage Messages permission)
        if is_mod or is_admin or is_owner:
            embed.add_field(
                name="🛠️ **Moderator Commands** (Manage Messages)",
                value=(
                    "`/say [#channel] <message>` - Make bot send messages\n"
                    "`/announce [#channel] <message>` - Skateboard-themed announcements\n"
                    "`/embed [#channel] [title] <description>` - Custom embed messages"
                ),
                inline=False
            )
        
        # Administrator commands
        if is_admin or is_owner:
            embed.add_field(
                name="🛡️ **Administrator Commands** (Admin Only)",
                value=(
                    "`/setup` - Interactive bot configuration\n"
                    "`!set_rank @user <rank>` - Manually set user ranks (1-15)\n"
                    "`!commands` - Show legacy command help"
                ),
                inline=False
            )
        
        # Bot owner commands
        if is_owner:
            embed.add_field(
                name="👑 **Bot Owner Commands** (Global)",
                value=(
                    "`!sync` - Sync slash commands globally\n"
                    "`!check_commands` - Debug command registration"
                ),
                inline=False
            )
        
        embed.add_field(
            name="📚 **Getting Started**",
            value=(
                "New to the server? Administrators can run `/setup` to configure the ranking system!\n\n"
                "**Earn Points Through:**\n"
                "• Chatting (1pt/min) • Reactions (2-3pts) • Commands (5pts)\n"
                "• Media sharing (20pts) • Community recognition via `/1up`"
            ),
            inline=False
        )
        
        embed.set_footer(text="🛹 Skate hard, rank up! | Use commands to earn points and climb the 15-ply ranking system")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @commands.command(name='commands')
    async def help_legacy(self, ctx):
        """Legacy help command for prefix-based commands"""
        user = ctx.author
        is_owner = await self.bot.is_owner(user)
        is_admin = isinstance(user, discord.Member) and user.guild_permissions.administrator
        is_mod = isinstance(user, discord.Member) and user.guild_permissions.manage_messages
        
        embed = discord.Embed(
            title="🛹 7-Ply Bot Legacy Commands (!)",
            description="Prefix commands available based on your permissions:",
            color=0xff9500
        )
        
        # Everyone can use these  
        embed.add_field(
            name="🎮 **Member Commands**",
            value=(
                "`!commands` - Show this help message\n"
                "*Most commands are now slash commands! Use `/help` for the full list.*"
            ),
            inline=False
        )
        
        # Administrator commands
        if is_admin or is_owner:
            embed.add_field(
                name="🛡️ **Administrator Commands**",
                value=(
                    "`!set_rank @user <rank>` - Manually set user ranks (1-15)\n"
                    "Example: `!set_rank @John 5`"
                ),
                inline=False
            )
        
        # Bot owner commands
        if is_owner:
            embed.add_field(
                name="👑 **Bot Owner Commands** (Global)",
                value=(
                    "`!sync` - Sync slash commands globally\n"
                    "`!check_commands` - Debug command registration"
                ),
                inline=False
            )
        
        embed.add_field(
            name="💡 **Tip**",
            value="Most commands are now **slash commands**! Type `/` and look for 7-Ply commands, or use `/help` for the complete list.",
            inline=False
        )
        
        embed.set_footer(text="🛹 Modern Discord uses slash commands! Try typing '/' to see all available commands")
        
        await ctx.send(embed=embed)

    @app_commands.command(name='slowmode', description='Set personal slowmode for a user')
    @app_commands.default_permissions(manage_messages=True)
    async def user_slowmode(self, interaction: discord.Interaction, user: discord.Member, duration: str):
        """Set personal slowmode for a specific user"""
        
        if not interaction.guild:
            await interaction.response.send_message("❌ This command can only be used in a server!", ephemeral=True)
            return
        
        try:
            # Parse duration
            if duration.lower() in ['off', 'remove', '0']:
                slowmode_seconds = 0
                action = "removed"
            else:
                # Parse duration string (e.g., "30s", "2m", "1h")
                duration = duration.lower().strip()
                if duration.endswith('s'):
                    slowmode_seconds = int(duration[:-1])
                elif duration.endswith('m'):
                    slowmode_seconds = int(duration[:-1]) * 60
                elif duration.endswith('h'):
                    slowmode_seconds = int(duration[:-1]) * 3600
                else:
                    # Assume seconds if no unit
                    slowmode_seconds = int(duration)
                
                # Limit maximum slowmode
                if slowmode_seconds > 21600:  # 6 hours max
                    await interaction.response.send_message(
                        "❌ Maximum slowmode duration is 6 hours!",
                        ephemeral=True
                    )
                    return
                
                action = "set"
            
            guild_id = interaction.guild.id
            
            # Initialize guild data if needed
            if guild_id not in self.user_slowmodes:
                self.user_slowmodes[guild_id] = {}
            
            # Set or remove slowmode
            if slowmode_seconds > 0:
                self.user_slowmodes[guild_id][user.id] = slowmode_seconds
            else:
                self.user_slowmodes[guild_id].pop(user.id, None)
            
            # Create response
            if action == "removed":
                embed = discord.Embed(
                    title="✅ Slowmode Removed",
                    description=f"Personal slowmode removed for {user.mention}",
                    color=0x00ff88
                )
            else:
                # Format duration for display
                if slowmode_seconds < 60:
                    duration_text = f"{slowmode_seconds} seconds"
                elif slowmode_seconds < 3600:
                    duration_text = f"{slowmode_seconds // 60} minutes"
                else:
                    duration_text = f"{slowmode_seconds // 3600} hours"
                
                embed = discord.Embed(
                    title="⏱️ Personal Slowmode Set",
                    description=f"{user.mention} can now only send 1 message every **{duration_text}**",
                    color=0xff6600
                )
                
                embed.add_field(
                    name="💡 How it works:",
                    value="• User can see their message for a few seconds\n• Bot then removes it with an ephemeral warning\n• Other users aren't affected",
                    inline=False
                )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except ValueError:
            await interaction.response.send_message(
                "❌ Invalid duration format! Use: `30s`, `2m`, `1h`, or `off`",
                ephemeral=True
            )
        except Exception as e:
            print(f"Error in slowmode command: {e}")
            await interaction.response.send_message(
                "❌ Something went wrong setting slowmode!",
                ephemeral=True
            )

    @commands.Cog.listener()
    async def on_message(self, message):
        """Monitor messages for per-user slowmode enforcement"""
        
        # Ignore bot messages and DMs
        if message.author.bot or not message.guild:
            return
        
        guild_id = message.guild.id
        user_id = message.author.id
        
        # Check if user has personal slowmode
        if (guild_id in self.user_slowmodes and 
            user_id in self.user_slowmodes[guild_id]):
            
            slowmode_seconds = self.user_slowmodes[guild_id][user_id]
            current_time = time.time()
            
            # Initialize guild tracking if needed
            if guild_id not in self.user_last_message:
                self.user_last_message[guild_id] = {}
            
            # Check if user is on cooldown
            if user_id in self.user_last_message[guild_id]:
                time_since_last = current_time - self.user_last_message[guild_id][user_id]
                
                if time_since_last < slowmode_seconds:
                    # User is on cooldown - show warning and delete message
                    time_left = int(slowmode_seconds - time_since_last)
                    
                    # Send ephemeral-style warning (delete after a few seconds)
                    warning_message = await message.channel.send(
                        f"⏱️ {message.author.mention}, you're on personal slowmode - wait **{time_left}** more seconds before your next message",
                        delete_after=5
                    )
                    
                    # Wait a moment, then delete the original message
                    import asyncio
                    await asyncio.sleep(3)
                    try:
                        await message.delete()
                    except discord.NotFound:
                        pass  # Message already deleted
                    except discord.Forbidden:
                        # Bot doesn't have delete permissions
                        pass
                    
                    return
            
            # Update last message time
            self.user_last_message[guild_id][user_id] = current_time

async def setup(bot):
    await bot.add_cog(AdminCommands(bot))