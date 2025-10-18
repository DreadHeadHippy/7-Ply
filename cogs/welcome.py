from discord.ext import commands
import discord
import json
import os
from typing import Optional

class WelcomeHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config_file = "data/welcome_config.json"
        self.welcome_channels = self.load_welcome_config()
    
    def load_welcome_config(self):
        """Load welcome channel configuration from JSON file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading welcome config: {e}")
        return {}
    
    def save_welcome_config(self):
        """Save welcome channel configuration to JSON file"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(self.welcome_channels, f, indent=2)
        except Exception as e:
            print(f"Error saving welcome config: {e}")
    
    def get_welcome_channel(self, guild):
        """Get the configured welcome channel for a guild, or auto-detect one"""
        # Check if we have a configured channel for this guild
        guild_id = str(guild.id)
        if guild_id in self.welcome_channels:
            channel_id = self.welcome_channels[guild_id]
            channel = guild.get_channel(channel_id)
            if channel and channel.permissions_for(guild.me).send_messages:
                return channel
        
        # Auto-detect welcome channel by common names
        welcome_channel_names = ['welcome', 'general', 'lobby', 'main', 'chat', 'introductions']
        for channel in guild.text_channels:
            if any(name in channel.name.lower() for name in welcome_channel_names):
                if channel.permissions_for(guild.me).send_messages:
                    return channel
        
        # Last resort: find any channel the bot can send messages to
        return next((c for c in guild.text_channels if c.permissions_for(guild.me).send_messages), None)

    def get_welcome_config(self, guild_id: int) -> Optional[dict]:
        """Get welcome configuration from setup system"""
        setup_cog = self.bot.get_cog('SetupSystem')
        if setup_cog and setup_cog.is_feature_enabled(guild_id, "welcome_messages"):
            return setup_cog.get_welcome_config(guild_id)
        return None
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Welcome new members with configurable skateboard-themed messages"""
        
        # Check if welcome messages are enabled for this server
        welcome_config = self.get_welcome_config(member.guild.id)
        if not welcome_config:
            return  # Welcome messages not enabled
        
        # Get the setup system's welcome channel
        setup_cog = self.bot.get_cog('SetupSystem')
        if not setup_cog:
            return
        
        welcome_channel_id = setup_cog.get_welcome_channel_id(member.guild.id)
        if not welcome_channel_id:
            welcome_channel = self.get_welcome_channel(member.guild)  # Fallback to auto-detect
        else:
            welcome_channel = member.guild.get_channel(welcome_channel_id)
        
        if not welcome_channel:
            print(f"❌ Could not find welcome channel for {member.display_name} in {member.guild.name}")
            return
        
        # Build the welcome message
        custom_message = welcome_config.get("custom_message")
        if custom_message:
            # Use custom message template
            message_content = custom_message.format(
                user=member.mention if welcome_config.get("ping_user", True) else member.display_name,
                user_name=member.display_name,
                server=member.guild.name,
                member_count=member.guild.member_count,
                date=member.joined_at.strftime("%B %d, %Y") if member.joined_at else "Today"
            )
        else:
            # Use default skateboard-themed message
            ping = member.mention if welcome_config.get("ping_user", True) else member.display_name
            message_content = f"🛹 Welcome to {member.guild.name}, {ping}! Ready to shred with us?\n\nUse `/trick` to get random tricks, `/skatefact` to learn skate history, and start earning your ranks by chatting! Stay radical! 🤙"
        
        # Send as embed or plain message
        if welcome_config.get("use_embed", True):
            embed_color = int(welcome_config.get("embed_color", "00ff00"), 16)
            embed = discord.Embed(
                title=f"🛹 Welcome to {member.guild.name}!",
                description=message_content,
                color=embed_color
            )
            
            if welcome_config.get("show_server_info", True):
                embed.add_field(
                    name="📊 Server Stats",
                    value=f"👥 Members: {member.guild.member_count}\n📅 Joined: {member.joined_at.strftime('%B %d, %Y') if member.joined_at else 'Today'}",
                    inline=True
                )
                
                embed.add_field(
                    name="🎯 Get Started",
                    value="• `/trick` - Random skateboard tricks\n• `/skatefact` - Skate history\n• `/rank` - Check your progress",
                    inline=True
                )
            
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.set_footer(text="Keep pushing and stay radical! 🛹", icon_url=self.bot.user.display_avatar.url)
            
            await welcome_channel.send(embed=embed)
        else:
            # Send as plain message
            await welcome_channel.send(message_content)
        
        print(f"✅ Welcomed {member.display_name} in #{welcome_channel.name} with {'custom' if custom_message else 'default'} message")

    @commands.command(name='set_welcome_channel')
    @commands.has_permissions(manage_guild=True)
    async def set_welcome_channel(self, ctx, channel: Optional[discord.TextChannel] = None):
        """Set the welcome channel for new members (admin only)"""
        target_channel = channel or ctx.channel
        
        # Save the welcome channel for this guild
        guild_id = str(ctx.guild.id)
        self.welcome_channels[guild_id] = target_channel.id
        self.save_welcome_config()
        
        await ctx.send(f"✅ Welcome channel set to {target_channel.mention}!\n"
                      f"🎯 New members will now be welcomed in that channel automatically.")
    
    @commands.command(name='test_welcome')
    @commands.has_permissions(manage_guild=True) 
    async def test_welcome(self, ctx):
        """Test the welcome message (admin only)"""
        welcome_channel = self.get_welcome_channel(ctx.guild)
        
        if welcome_channel:
            # Create test welcome embed
            embed = discord.Embed(
                title="🛹 Welcome Test! 🛹",
                description=f"This is how {ctx.author.mention} would be welcomed!",
                color=0x00ff00
            )
            
            embed.add_field(
                name="🎯 Get Started",
                value="• Use `/trick` to get a random trick to practice\n• Use `/skatefact` to learn cool skate facts\n• Check out our reaction roles to get your skater type!",
                inline=False
            )
            
            embed.add_field(
                name="🤙 Have Fun!", 
                value="Drop a trick, share your setup, and let's keep the stoke alive!",
                inline=False
            )
            
            embed.set_thumbnail(url=ctx.author.display_avatar.url)
            embed.set_footer(text="Stay radical and keep pushing! 🛹 (This is a test)", icon_url=self.bot.user.display_avatar.url)
            
            await welcome_channel.send(embed=embed)
            
            if welcome_channel != ctx.channel:
                await ctx.send(f"✅ Test welcome message sent to {welcome_channel.mention}!")
        else:
            await ctx.send("❌ No welcome channel configured and couldn't auto-detect one. Use `!set_welcome_channel` first.")

async def setup(bot):
    await bot.add_cog(WelcomeHandler(bot))
