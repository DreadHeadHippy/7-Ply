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

# Import security utilities
from utils.security import SecurityValidator, SecureError

class AdminCommands(commands.Cog):
    """Administrative commands for server management"""
    
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='say', description='Make the bot say something')
    @app_commands.default_permissions(manage_messages=True)
    async def say(self, interaction: discord.Interaction, channel: Optional[discord.TextChannel] = None, *, message: str):
        """Make the bot say something in a specific channel or current channel"""
        
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

async def setup(bot):
    await bot.add_cog(AdminCommands(bot))