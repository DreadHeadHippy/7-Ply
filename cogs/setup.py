"""
Setup Commands Cog
Configures the bot for new servers with interactive setup
"""

import json
import os
import discord
from discord.ext import commands
from discord import app_commands
from typing import Dict, Any, Optional
import datetime
import pytz

class SetupSystem(commands.Cog):
    """Server setup and configuration commands"""
    
    def __init__(self, bot):
        self.bot = bot
        self.config_file = "data/server_configs.json"
        self.server_configs = self.load_configs()
        # EDT timezone
        self.edt = pytz.timezone('America/New_York')
    
    def get_edt_now(self) -> datetime.datetime:
        """Get current time in EDT"""
        return datetime.datetime.now(self.edt)
    
    def load_configs(self) -> Dict[str, Any]:
        """Load server configurations from JSON file"""
        if not os.path.exists("data"):
            os.makedirs("data")
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading server configs: {e}")
                return {}
        return {}
    
    def save_configs(self):
        """Save server configurations to JSON file"""
        try:
            if not os.path.exists("data"):
                os.makedirs("data")
            with open(self.config_file, 'w') as f:
                json.dump(self.server_configs, f, indent=2)
        except Exception as e:
            print(f"Error saving server configs: {e}")
    
    def get_server_config(self, guild_id: int) -> Dict[str, Any]:
        """Get or create server configuration"""
        guild_id_str = str(guild_id)
        if guild_id_str not in self.server_configs:
            self.server_configs[guild_id_str] = {
                "rank_channel": None,
                "setup_completed": False,
                "setup_date": None
            }
        return self.server_configs[guild_id_str]
    
    def get_rank_channel_id(self, guild_id: int) -> Optional[int]:
        """Get the configured rank channel ID for a server"""
        config = self.get_server_config(guild_id)
        return config.get("rank_channel")
    
    @app_commands.command(name='setup', description='Configure the bot for your server')
    @app_commands.default_permissions(administrator=True)
    async def setup_bot(self, interaction: discord.Interaction):
        """Interactive setup for the bot"""
        
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message("❌ This command can only be used in a server!", ephemeral=True)
            return
        
        config = self.get_server_config(guild.id)
        
        # Create setup embed
        embed = discord.Embed(
            title="🛹 7-Ply Bot Setup",
            description="Let's configure the bot for your server!",
            color=0x00ff88
        )
        
        embed.add_field(
            name="📋 What This Setup Does:",
            value="• Creates or configures a **#rank** channel for ranking activities\n• Sets up proper permissions\n• Configures the ranking system\n• Enables all skateboard features",
            inline=False
        )
        
        embed.add_field(
            name="🔧 Requirements:",
            value="• You need **Administrator** permissions\n• Bot needs permission to create/manage channels\n• Bot needs permission to send messages and embeds",
            inline=False
        )
        
        # Check if already setup
        if config.get("setup_completed"):
            embed.add_field(
                name="✅ Current Status:",
                value="Setup already completed! Use `/setup reset` to reconfigure.",
                inline=False
            )
            embed.color = 0xffd700
        
        embed.set_footer(text="Click the button below to start setup!")
        
        # Create setup button
        view = SetupView(self, guild)
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @app_commands.command(name='setup_reset', description='Reset bot configuration for this server')
    @app_commands.default_permissions(administrator=True)
    async def setup_reset(self, interaction: discord.Interaction):
        """Reset server configuration"""
        
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message("❌ This command can only be used in a server!", ephemeral=True)
            return
        
        # Reset config
        guild_id_str = str(guild.id)
        if guild_id_str in self.server_configs:
            del self.server_configs[guild_id_str]
            self.save_configs()
        
        embed = discord.Embed(
            title="🔄 Configuration Reset",
            description="Server configuration has been reset. Use `/setup` to configure again.",
            color=0xff6600
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name='setup_status', description='Check current bot configuration')
    async def setup_status(self, interaction: discord.Interaction):
        """Show current setup status"""
        
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message("❌ This command can only be used in a server!", ephemeral=True)
            return
        
        config = self.get_server_config(guild.id)
        
        embed = discord.Embed(
            title="⚙️ Bot Configuration Status",
            color=0x00ff88 if config.get("setup_completed") else 0xff6600
        )
        
        # Setup status
        if config.get("setup_completed"):
            embed.add_field(
                name="✅ Setup Status",
                value="Completed",
                inline=True
            )
            if config.get("setup_date"):
                embed.add_field(
                    name="📅 Setup Date",
                    value=config["setup_date"],
                    inline=True
                )
        else:
            embed.add_field(
                name="❌ Setup Status",
                value="Not completed - use `/setup` to configure",
                inline=True
            )
        
        # Channel configuration
        rank_channel_id = config.get("rank_channel")
        if rank_channel_id:
            rank_channel = guild.get_channel(rank_channel_id)
            if rank_channel:
                embed.add_field(
                    name="📊 Rank Channel",
                    value=rank_channel.mention,
                    inline=True
                )
            else:
                embed.add_field(
                    name="⚠️ Rank Channel",
                    value="Configured but channel no longer exists",
                    inline=True
                )
        else:
            embed.add_field(
                name="❌ Rank Channel",
                value="Not configured",
                inline=True
            )
        
        # Features status
        features_status = "✅ Ranking System\n✅ Skateboard Commands\n✅ Trick Database\n✅ User Progression"
        embed.add_field(
            name="🛹 Available Features",
            value=features_status,
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)

class SetupView(discord.ui.View):
    """Interactive setup view with buttons"""
    
    def __init__(self, setup_cog: SetupSystem, guild: discord.Guild):
        super().__init__(timeout=300)  # 5 minute timeout
        self.setup_cog = setup_cog
        self.guild = guild
    
    @discord.ui.button(label='🚀 Start Setup', style=discord.ButtonStyle.green)
    async def start_setup(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Start the setup process"""
        
        # Check permissions
        # Check if user has administrator permissions
        if not isinstance(interaction.user, discord.Member) or not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ You need Administrator permissions to run setup!", ephemeral=True)
            return
        
        # Check bot permissions
        bot_member = self.guild.get_member(self.setup_cog.bot.user.id)
        if not bot_member or not bot_member.guild_permissions.manage_channels:
            await interaction.response.send_message("❌ I need 'Manage Channels' permission to complete setup!", ephemeral=True)
            return
        
        await self.run_setup(interaction)
    
    async def run_setup(self, interaction: discord.Interaction):
        """Run the actual setup process"""
        
        setup_embed = discord.Embed(
            title="🔧 Running Setup...",
            description="Setting up your server configuration...",
            color=0xffd700
        )
        
        await interaction.response.edit_message(embed=setup_embed, view=None)
        
        try:
            # Step 1: Find or create rank channel
            rank_channel = None
            
            # Look for existing #rank channel
            for channel in self.guild.text_channels:
                if channel.name.lower() in ['rank', 'ranks', 'ranking']:
                    rank_channel = channel
                    break
            
            # Create rank channel if not found
            if not rank_channel:
                rank_channel = await self.guild.create_text_channel(
                    name='rank',
                    topic='🛹 User rankings and progression - powered by 7-Ply Bot',
                    reason='7-Ply Bot setup - ranking channel'
                )
            
            # Step 2: Set up channel permissions
            await rank_channel.set_permissions(
                self.guild.default_role,
                send_messages=False,  # Users can't chat here
                add_reactions=True,   # But can react to rank posts
                read_messages=True    # Can view rankings
            )
            
            bot_member = self.guild.get_member(self.setup_cog.bot.user.id)
            if bot_member:
                await rank_channel.set_permissions(
                    bot_member,
                    send_messages=True,
                    embed_links=True,
                    attach_files=True,
                    read_messages=True
                )
            
            # Step 3: Save configuration
            config = self.setup_cog.get_server_config(self.guild.id)
            config["rank_channel"] = rank_channel.id
            config["setup_completed"] = True
            config["setup_date"] = self.setup_cog.get_edt_now().strftime("%Y-%m-%d")
            
            self.setup_cog.save_configs()
            
            # Step 4: Send welcome message to rank channel
            welcome_embed = discord.Embed(
                title="🛹 Welcome to 7-Ply Rankings!",
                description="This channel will display user rankings and progression.",
                color=0x00ff88
            )
            
            welcome_embed.add_field(
                name="🎯 Available Commands:",
                value="• `/rank` - View your rank and progress\n• `/leaderboard` - See top-ranked users\n• `/1up @user` - Give someone bonus points\n• `/trick` - Get random skateboard tricks",
                inline=False
            )
            
            welcome_embed.add_field(
                name="💯 How to Earn Points:",
                value="• Chat messages: 1 point\n• Give reactions: 2 points\n• Receive reactions: 3 points\n• Use commands: 5 points\n• Share media: 20 points\n• Receive 1-ups: 25 points",
                inline=False
            )
            
            welcome_embed.set_footer(text="Start chatting to begin earning your first rank! 🛹")
            
            await rank_channel.send(embed=welcome_embed)
            
            # Step 5: Update setup message with success
            success_embed = discord.Embed(
                title="✅ Setup Complete!",
                description="Your server is now fully configured for 7-Ply Bot!",
                color=0x00ff00
            )
            
            success_embed.add_field(
                name="📊 Rank Channel",
                value=f"{rank_channel.mention} - All ranking activity will appear here",
                inline=False
            )
            
            success_embed.add_field(
                name="🚀 Next Steps:",
                value="• Users can start chatting to earn ranks\n• Try `/rank` to see your current status\n• Use `/1up @someone` to give bonus points\n• Explore skateboard commands with `/trick`",
                inline=False
            )
            
            success_embed.set_footer(text="Your bot is ready to roll! 🛹")
            
            await interaction.edit_original_response(embed=success_embed)
            
        except Exception as e:
            error_embed = discord.Embed(
                title="❌ Setup Failed",
                description=f"An error occurred during setup: {str(e)}",
                color=0xff0000
            )
            
            error_embed.add_field(
                name="🔧 Troubleshooting:",
                value="• Ensure the bot has 'Manage Channels' permission\n• Make sure you have Administrator permissions\n• Try running `/setup` again",
                inline=False
            )
            
            await interaction.edit_original_response(embed=error_embed)
            print(f"Setup error for guild {self.guild.id}: {e}")

async def setup(bot):
    await bot.add_cog(SetupSystem(bot))