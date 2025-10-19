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
                "suggestions_channel": None,
                "welcome_channel": None,
                "temp_voice_category": None,
                "features": {
                    "ranking_system": True,      # Core feature - always enabled
                    "suggestions_system": False, # Optional
                    "welcome_messages": False,   # Optional
                    "temp_voice": False,         # Optional
                    "reaction_roles": False      # Optional
                },
                "welcome_config": {
                    "custom_message": None,      # Custom welcome message template
                    "use_embed": True,          # Use embed vs plain message
                    "embed_color": "00ff00",    # Hex color for embed
                    "ping_user": True,          # Whether to ping the new user
                    "show_server_info": True    # Show server member count etc
                },
                "setup_completed": False,
                "setup_date": None
            }
        return self.server_configs[guild_id_str]
    
    def get_rank_channel_id(self, guild_id: int) -> Optional[int]:
        """Get the configured rank channel ID for a server"""
        config = self.get_server_config(guild_id)
        return config.get("rank_channel")
    
    def get_suggestions_channel_id(self, guild_id: int) -> Optional[int]:
        """Get the configured suggestions channel ID for a server"""
        config = self.get_server_config(guild_id)
        return config.get("suggestions_channel")
    
    def get_welcome_channel_id(self, guild_id: int) -> Optional[int]:
        """Get the configured welcome channel ID for a server"""
        config = self.get_server_config(guild_id)
        return config.get("welcome_channel")
    
    def get_temp_voice_category_id(self, guild_id: int) -> Optional[int]:
        """Get the configured temp voice category ID for a server"""
        config = self.get_server_config(guild_id)
        return config.get("temp_voice_category")
    
    def is_feature_enabled(self, guild_id: int, feature: str) -> bool:
        """Check if a specific feature is enabled for a server"""
        config = self.get_server_config(guild_id)
        return config.get("features", {}).get(feature, False)
    
    def get_welcome_config(self, guild_id: int) -> dict:
        """Get welcome message configuration for a server"""
        config = self.get_server_config(guild_id)
        return config.get("welcome_config", {
            "custom_message": None,
            "use_embed": True,
            "embed_color": "00ff00", 
            "ping_user": True,
            "show_server_info": True
        })
    
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
            name="🎯 Available Features:",
            value="🏆 **Ranking System** - User progression and points (Always included)\n💡 **Suggestions System** - Community feedback with voting\n👋 **Welcome Messages** - Greet new members\n🔊 **Temp Voice Channels** - User-managed voice rooms\n🎭 **Reaction Roles** - Self-serve skateboard-themed roles",
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
        """Reset server configuration and clear any stuck setup processes"""
        
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message("❌ This command can only be used in a server!", ephemeral=True)
            return
        
        # Check if setup was stuck
        config = self.get_server_config(guild.id)
        was_stuck = config.get("setup_in_progress", False)
        
        # Reset config (this clears everything including setup locks)
        guild_id_str = str(guild.id)
        if guild_id_str in self.server_configs:
            del self.server_configs[guild_id_str]
            self.save_configs()
        
        description = "Server configuration has been reset. Use `/setup` to configure again."
        if was_stuck:
            description += "\n\n✅ **Also cleared a stuck setup process!**"
        
        embed = discord.Embed(
            title="🔄 Configuration Reset",
            description=description,
            color=0xff6600
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name='setup_edit', description='Edit specific bot settings without resetting everything')
    @app_commands.default_permissions(administrator=True)
    async def setup_edit(self, interaction: discord.Interaction):
        """Edit specific settings with interactive dropdowns"""
        
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message("❌ This command can only be used in a server!", ephemeral=True)
            return
        
        config = self.get_server_config(guild.id)
        
        # Check if setup has been completed
        if not config.get("setup_completed"):
            embed = discord.Embed(
                title="❌ Setup Not Complete",
                description="You need to run `/setup` first before you can edit settings!",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Create edit selection embed
        embed = discord.Embed(
            title="🔧 Edit Bot Settings",
            description="Choose what you'd like to modify:",
            color=0x00ff88
        )
        
        # Show current configuration status
        ranking_channel = f"<#{config.get('ranking_channel_id')}>" if config.get('ranking_channel_id') else "Not set"
        welcome_status = "✅ Enabled" if config.get('features', {}).get('welcome_messages') else "❌ Disabled"
        suggestions_status = "✅ Enabled" if config.get('features', {}).get('suggestions') else "❌ Disabled"
        temp_voice_status = "✅ Enabled" if config.get('features', {}).get('temp_voice') else "❌ Disabled"
        reaction_roles_status = "✅ Enabled" if config.get('features', {}).get('reaction_roles') else "❌ Disabled"
        
        embed.add_field(
            name="📊 Current Settings:",
            value=f"🏆 **Ranking Channel**: {ranking_channel}\n💡 **Suggestions**: {suggestions_status}\n👋 **Welcome Messages**: {welcome_status}\n🔊 **Temp Voice**: {temp_voice_status}\n🎭 **Reaction Roles**: {reaction_roles_status}",
            inline=False
        )
        
        embed.add_field(
            name="💡 What can you edit?",
            value="• Change channel assignments\n• Enable/disable features\n• Modify welcome message settings\n• Update any configuration without losing other settings",
            inline=False
        )
        
        # Create edit view with dropdown
        view = SetupEditView(self, guild, config)
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @app_commands.command(name='welcome_config', description='Configure custom welcome messages')
    @app_commands.default_permissions(administrator=True)
    async def welcome_config(self, interaction: discord.Interaction):
        """Configure welcome message settings"""
        
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message("❌ This command can only be used in a server!", ephemeral=True)
            return
        
        # Check if welcome messages are enabled
        if not self.is_feature_enabled(guild.id, "welcome_messages"):
            await interaction.response.send_message("❌ Welcome messages are not enabled! Run `/setup` and enable the welcome feature first.", ephemeral=True)
            return
        
        # Show current configuration and customization options
        welcome_config = self.get_welcome_config(guild.id)
        
        embed = discord.Embed(
            title="👋 Welcome Message Configuration",
            description="Customize how 7-Ply greets new members!",
            color=0x00ff88
        )
        
        current_message = welcome_config.get("custom_message") or "**Default skateboard-themed welcome**"
        embed.add_field(
            name="📝 Current Message Template:",
            value=f"```{current_message}```",
            inline=False
        )
        
        embed.add_field(
            name="🎨 Available Variables:",
            value="`{user}` - Mentions the new user\n`{user_name}` - User's display name\n`{server}` - Server name\n`{member_count}` - Current member count\n`{date}` - Current date",
            inline=False
        )
        
        embed.add_field(
            name="⚙️ Current Settings:",
            value=f"📋 Use Embed: {'✅' if welcome_config.get('use_embed', True) else '❌'}\n🎨 Embed Color: #{welcome_config.get('embed_color', '00ff00')}\n🔔 Ping User: {'✅' if welcome_config.get('ping_user', True) else '❌'}\n📊 Show Server Info: {'✅' if welcome_config.get('show_server_info', True) else '❌'}",
            inline=False
        )
        
        embed.add_field(
            name="🛠️ How to Customize:",
            value="Use `/welcome_set_message` to change the message template\nUse `/welcome_settings` to adjust display options",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name='welcome_set_message', description='Set a custom welcome message template')
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(message="Custom welcome message (use {user}, {server}, {member_count} etc.)")
    async def welcome_set_message(self, interaction: discord.Interaction, *, message: str):
        """Set custom welcome message template"""
        
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message("❌ This command can only be used in a server!", ephemeral=True)
            return
        
        if not self.is_feature_enabled(guild.id, "welcome_messages"):
            await interaction.response.send_message("❌ Welcome messages are not enabled! Run `/setup` first.", ephemeral=True)
            return
        
        # Validate message length
        if len(message) > 1000:
            await interaction.response.send_message("❌ Welcome message must be 1000 characters or less!", ephemeral=True)
            return
        
        # Save custom message
        config = self.get_server_config(guild.id)
        if "welcome_config" not in config:
            config["welcome_config"] = {}
        config["welcome_config"]["custom_message"] = message
        self.save_configs()
        
        # Preview the message
        preview_message = message.format(
            user=interaction.user.mention,
            user_name=interaction.user.display_name,
            server=guild.name,
            member_count=guild.member_count,
            date="Today"
        )
        
        embed = discord.Embed(
            title="✅ Welcome Message Updated!",
            description="Here's how your new welcome message will look:",
            color=0x00ff00
        )
        
        embed.add_field(
            name="📝 New Template:",
            value=f"```{message}```",
            inline=False
        )
        
        embed.add_field(
            name="👀 Preview:",
            value=preview_message,
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name='welcome_settings', description='Adjust welcome message display settings')
    @app_commands.default_permissions(administrator=True)
    async def welcome_settings(self, interaction: discord.Interaction):
        """Configure welcome message display settings"""
        
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message("❌ This command can only be used in a server!", ephemeral=True)
            return
        
        if not self.is_feature_enabled(guild.id, "welcome_messages"):
            await interaction.response.send_message("❌ Welcome messages are not enabled! Run `/setup` first.", ephemeral=True)
            return
        
        # Create interactive view for settings
        view = WelcomeSettingsView(self, guild.id)
        
        embed = discord.Embed(
            title="⚙️ Welcome Message Settings",
            description="Click the buttons below to toggle settings:",
            color=0x00ff88
        )
        
        welcome_config = self.get_welcome_config(guild.id)
        settings_text = f"📋 Use Embed: {'✅' if welcome_config.get('use_embed', True) else '❌'}\n"
        settings_text += f"🔔 Ping User: {'✅' if welcome_config.get('ping_user', True) else '❌'}\n" 
        settings_text += f"📊 Show Server Info: {'✅' if welcome_config.get('show_server_info', True) else '❌'}\n"
        settings_text += f"🎨 Embed Color: #{welcome_config.get('embed_color', '00ff00')}"
        
        embed.add_field(
            name="Current Settings:",
            value=settings_text,
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
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

class FeatureSelectView(discord.ui.View):
    """Feature selection view for setup"""
    
    def __init__(self, setup_cog: SetupSystem, guild: discord.Guild):
        super().__init__(timeout=300)  # 5 minute timeout
        self.setup_cog = setup_cog
        self.guild = guild
        self.selected_features = {"ranking_system": True}  # Always enabled
        self.add_feature_selectors()
    
    def add_feature_selectors(self):
        """Add feature selection buttons"""
        # Suggestions System
        suggestions_button = discord.ui.Button(
            label="� Suggestions System",
            style=discord.ButtonStyle.secondary,
            custom_id="toggle_suggestions"
        )
        suggestions_button.callback = self.toggle_suggestions
        self.add_item(suggestions_button)
        
        # Welcome Messages  
        welcome_button = discord.ui.Button(
            label="👋 Welcome Messages", 
            style=discord.ButtonStyle.secondary,
            custom_id="toggle_welcome"
        )
        welcome_button.callback = self.toggle_welcome
        self.add_item(welcome_button)
        
        # Temp Voice
        voice_button = discord.ui.Button(
            label="🔊 Temp Voice Channels",
            style=discord.ButtonStyle.secondary, 
            custom_id="toggle_voice"
        )
        voice_button.callback = self.toggle_voice
        self.add_item(voice_button)
        
        # Reaction Roles
        reaction_roles_button = discord.ui.Button(
            label="🎭 Reaction Roles",
            style=discord.ButtonStyle.secondary,
            custom_id="toggle_reaction_roles"
        )
        reaction_roles_button.callback = self.toggle_reaction_roles
        self.add_item(reaction_roles_button)
        
        # Proceed button
        proceed_button = discord.ui.Button(
            label="🚀 Proceed with Setup",
            style=discord.ButtonStyle.green,
            custom_id="proceed_setup"
        )
        proceed_button.callback = self.proceed_setup
        self.add_item(proceed_button)
    
    async def toggle_suggestions(self, interaction: discord.Interaction):
        """Toggle suggestions system"""
        if not await self.check_permissions(interaction):
            return
        
        current = self.selected_features.get("suggestions_system", False)
        self.selected_features["suggestions_system"] = not current
        await self.update_display(interaction)
    
    async def toggle_welcome(self, interaction: discord.Interaction):
        """Toggle welcome messages"""
        if not await self.check_permissions(interaction):
            return
        
        current = self.selected_features.get("welcome_messages", False)
        self.selected_features["welcome_messages"] = not current
        await self.update_display(interaction)
    
    async def toggle_voice(self, interaction: discord.Interaction):
        """Toggle temp voice channels"""
        if not await self.check_permissions(interaction):
            return
        
        current = self.selected_features.get("temp_voice", False)
        self.selected_features["temp_voice"] = not current
        await self.update_display(interaction)
    
    async def toggle_reaction_roles(self, interaction: discord.Interaction):
        """Toggle reaction roles"""
        if not await self.check_permissions(interaction):
            return
        
        current = self.selected_features.get("reaction_roles", False)
        self.selected_features["reaction_roles"] = not current
        await self.update_display(interaction)
    
    async def check_permissions(self, interaction: discord.Interaction) -> bool:
        """Check if user has permissions"""
        if not isinstance(interaction.user, discord.Member) or not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ You need Administrator permissions!", ephemeral=True)
            return False
        return True
    
    async def update_display(self, interaction: discord.Interaction):
        """Update the display with current selections"""
        embed = discord.Embed(
            title="🛹 7-Ply Bot Setup - Feature Selection",
            description="Choose which features you want to enable:",
            color=0x00ff88
        )
        
        # Show current selections
        feature_status = "🏆 **Ranking System** ✅ (Always enabled)\n"
        
        if self.selected_features.get("suggestions_system"):
            feature_status += "💡 **Suggestions System** ✅\n"
        else:
            feature_status += "💡 **Suggestions System** ❌\n"
            
        if self.selected_features.get("welcome_messages"):
            feature_status += "👋 **Welcome Messages** ✅\n"
        else:
            feature_status += "👋 **Welcome Messages** ❌\n"
            
        if self.selected_features.get("temp_voice"):
            feature_status += "🔊 **Temp Voice Channels** ✅\n"
        else:
            feature_status += "🔊 **Temp Voice Channels** ❌\n"
            
        if self.selected_features.get("reaction_roles"):
            feature_status += "🎭 **Reaction Roles** ✅"
        else:
            feature_status += "🎭 **Reaction Roles** ❌"
        
        embed.add_field(
            name="📋 Selected Features:",
            value=feature_status,
            inline=False
        )
        
        embed.add_field(
            name="💡 Feature Descriptions:",
            value="• **Suggestions** - Community feedback system with voting\n• **Welcome** - Greet new members with skateboard flair\n• **Temp Voice** - Auto-managed voice channels for sessions",
            inline=False
        )
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def proceed_setup(self, interaction: discord.Interaction):
        """Proceed with setup using selected features"""
        if not await self.check_permissions(interaction):
            return
            
        # Check bot permissions
        bot_member = self.guild.get_member(self.setup_cog.bot.user.id)
        if not bot_member or not bot_member.guild_permissions.manage_channels:
            await interaction.response.send_message("❌ I need 'Manage Channels' permission to complete setup!", ephemeral=True)
            return
        
        await self.run_setup(interaction)
    
    async def run_setup(self, interaction: discord.Interaction):
        """Run the actual setup process with selected features"""
        
        # Check if setup is already in progress
        config = self.setup_cog.get_server_config(self.guild.id)
        if config.get("setup_in_progress", False):
            await interaction.response.edit_message(
                embed=discord.Embed(
                    title="⚠️ Setup In Progress",
                    description="Setup is already running! Please wait for it to complete or try again in a few minutes.",
                    color=0xff6600
                ),
                view=None
            )
            return
        
        # Mark setup as in progress
        config["setup_in_progress"] = True
        self.setup_cog.save_configs()
        
        setup_embed = discord.Embed(
            title="🔧 Running Setup...",
            description="Setting up your server configuration...\n⚠️ **Don't close Discord until this completes!**",
            color=0xffd700
        )
        
        await interaction.response.edit_message(embed=setup_embed, view=None)
        
        try:
            config = self.setup_cog.get_server_config(self.guild.id)
            created_channels = []
            
            # Step 1: Always set up ranking system
            rank_channel = await self.setup_rank_channel()
            created_channels.append(f"🏆 {rank_channel.mention} - Ranking announcements")
            
            # Step 2: Set up optional features
            if self.selected_features.get("suggestions_system"):
                suggestions_channel = await self.setup_suggestions_channel()
                created_channels.append(f"💡 {suggestions_channel.mention} - Community suggestions")
                
            if self.selected_features.get("welcome_messages"):
                welcome_channel = await self.setup_welcome_channel()
                created_channels.append(f"👋 {welcome_channel.mention} - Welcome messages")
                
            if self.selected_features.get("temp_voice"):
                voice_category = await self.setup_temp_voice()
                created_channels.append(f"🔊 {voice_category.name} - Temp voice category")
            
            # Step 3: Save configuration
            config["features"] = self.selected_features.copy()
            config["setup_completed"] = True
            config["setup_date"] = self.setup_cog.get_edt_now().strftime("%Y-%m-%d")
            # Remove setup in progress flag
            config.pop("setup_in_progress", None)
            self.setup_cog.save_configs()
            
            # Step 4: Send success message
            success_embed = discord.Embed(
                title="✅ Setup Complete!",
                description="Your server is now configured for 7-Ply Bot!",
                color=0x00ff00
            )
            
            success_embed.add_field(
                name="📊 Configured Channels/Features:",
                value="\n".join(created_channels),
                inline=False
            )
            
            success_embed.add_field(
                name="🎯 Next Steps:",
                value="• Members can start earning points by chatting\n• Use `/rank` to check progress\n• Use `/help` to see all available commands\n• Try `/trick` or `/skatefact` for skateboard content!",
                inline=False
            )
            
            success_embed.set_footer(text="Setup completed successfully! 🛹")
            
            await interaction.edit_original_response(embed=success_embed)
            
        except Exception as e:
            # Clean up setup in progress flag on error
            config = self.setup_cog.get_server_config(self.guild.id)
            config.pop("setup_in_progress", None)
            self.setup_cog.save_configs()
            
            error_embed = discord.Embed(
                title="❌ Setup Failed",
                description=f"**Error:** {str(e)}\n\n**Common fixes:**\n• Make sure I have Administrator permissions\n• Try running `/setup` again\n• Contact support if this persists",
                color=0xff0000
            )
            await interaction.edit_original_response(embed=error_embed)
            print(f"Setup error: {e}")
    
    async def setup_rank_channel(self) -> discord.TextChannel:
        """Set up the ranking channel"""
        # Look for existing rank channel
        for channel in self.guild.text_channels:
            if channel.name.lower() in ['rank', 'ranks', 'ranking']:
                rank_channel = channel
                break
        else:
            # Create new rank channel
            rank_channel = await self.guild.create_text_channel(
                name='rank-ups',
                topic='🛹 User rankings and progression - powered by 7-Ply Bot',
                reason='7-Ply Bot setup - ranking channel'
            )
        
        # Set up permissions
        await rank_channel.set_permissions(
            self.guild.default_role,
            send_messages=False,
            add_reactions=True,
            read_messages=True
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
        
        # Save channel ID
        config = self.setup_cog.get_server_config(self.guild.id)
        config["rank_channel"] = rank_channel.id
        
        return rank_channel
    
    async def setup_suggestions_channel(self) -> discord.TextChannel:
        """Set up the suggestions channel"""
        # Look for existing suggestions channel
        for channel in self.guild.text_channels:
            if 'suggest' in channel.name.lower():
                suggestions_channel = channel
                break
        else:
            # Create new suggestions channel
            suggestions_channel = await self.guild.create_text_channel(
                name='suggestions',
                topic='💡 Community suggestions and feedback - powered by 7-Ply Bot',
                reason='7-Ply Bot setup - suggestions channel'
            )
        
        # Save channel ID
        config = self.setup_cog.get_server_config(self.guild.id)
        config["suggestions_channel"] = suggestions_channel.id
        
        return suggestions_channel
    
    async def setup_welcome_channel(self) -> discord.TextChannel:
        """Set up welcome channel - uses general or creates one"""
        # Look for general/welcome channel
        welcome_channel = None
        for channel in self.guild.text_channels:
            if channel.name.lower() in ['general', 'welcome', 'lobby', 'main']:
                welcome_channel = channel
                break
        
        if not welcome_channel:
            # Use system channel if available
            welcome_channel = self.guild.system_channel
            
        if not welcome_channel:
            # Create welcome channel as last resort
            welcome_channel = await self.guild.create_text_channel(
                name='welcome',
                topic='👋 Welcome new members - powered by 7-Ply Bot',
                reason='7-Ply Bot setup - welcome channel'
            )
        
        # Save channel ID
        config = self.setup_cog.get_server_config(self.guild.id)
        config["welcome_channel"] = welcome_channel.id
        
        return welcome_channel
    
    async def setup_temp_voice(self) -> discord.CategoryChannel:
        """Set up temporary voice category"""
        # Look for existing voice category
        voice_category = None
        for category in self.guild.categories:
            if 'voice' in category.name.lower() or 'temp' in category.name.lower():
                voice_category = category
                break
        
        if not voice_category:
            # Create new category
            voice_category = await self.guild.create_category(
                name='🔊 Temp Voice',
                reason='7-Ply Bot setup - temporary voice category'
            )
        
        # Save category ID
        config = self.setup_cog.get_server_config(self.guild.id)
        config["temp_voice_category"] = voice_category.id
        
        return voice_category

class WelcomeSettingsView(discord.ui.View):
    """Interactive view for welcome message settings"""
    
    def __init__(self, setup_cog: 'SetupSystem', guild_id: int):
        super().__init__(timeout=300)
        self.setup_cog = setup_cog
        self.guild_id = guild_id
    
    @discord.ui.button(label='📋 Toggle Embed', style=discord.ButtonStyle.secondary)
    async def toggle_embed(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Toggle embed usage"""
        config = self.setup_cog.get_server_config(self.guild_id)
        current = config.get("welcome_config", {}).get("use_embed", True)
        
        if "welcome_config" not in config:
            config["welcome_config"] = {}
        config["welcome_config"]["use_embed"] = not current
        self.setup_cog.save_configs()
        
        await self.update_display(interaction, f"📋 Embed usage: {'Enabled' if not current else 'Disabled'}")
    
    @discord.ui.button(label='🔔 Toggle Ping', style=discord.ButtonStyle.secondary)
    async def toggle_ping(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Toggle user pinging"""
        config = self.setup_cog.get_server_config(self.guild_id)
        current = config.get("welcome_config", {}).get("ping_user", True)
        
        if "welcome_config" not in config:
            config["welcome_config"] = {}
        config["welcome_config"]["ping_user"] = not current
        self.setup_cog.save_configs()
        
        await self.update_display(interaction, f"🔔 User ping: {'Enabled' if not current else 'Disabled'}")
    
    @discord.ui.button(label='📊 Toggle Server Info', style=discord.ButtonStyle.secondary)
    async def toggle_server_info(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Toggle server info display"""
        config = self.setup_cog.get_server_config(self.guild_id)
        current = config.get("welcome_config", {}).get("show_server_info", True)
        
        if "welcome_config" not in config:
            config["welcome_config"] = {}
        config["welcome_config"]["show_server_info"] = not current
        self.setup_cog.save_configs()
        
        await self.update_display(interaction, f"📊 Server info: {'Enabled' if not current else 'Disabled'}")
    
    async def update_display(self, interaction: discord.Interaction, change_message: str):
        """Update the settings display"""
        embed = discord.Embed(
            title="⚙️ Welcome Message Settings",
            description=f"✅ {change_message}\n\nClick buttons below to toggle more settings:",
            color=0x00ff88
        )
        
        welcome_config = self.setup_cog.get_welcome_config(self.guild_id)
        settings_text = f"📋 Use Embed: {'✅' if welcome_config.get('use_embed', True) else '❌'}\n"
        settings_text += f"🔔 Ping User: {'✅' if welcome_config.get('ping_user', True) else '❌'}\n"
        settings_text += f"📊 Show Server Info: {'✅' if welcome_config.get('show_server_info', True) else '❌'}\n"
        settings_text += f"🎨 Embed Color: #{welcome_config.get('embed_color', '00ff00')}"
        
        embed.add_field(
            name="Current Settings:",
            value=settings_text,
            inline=False
        )
        
        await interaction.response.edit_message(embed=embed, view=self)

class SetupView(discord.ui.View):
    """Initial setup view - directs to feature selection"""
    
    def __init__(self, setup_cog: SetupSystem, guild: discord.Guild):
        super().__init__(timeout=300)  # 5 minute timeout
        self.setup_cog = setup_cog
        self.guild = guild
    
    @discord.ui.button(label='🎯 Select Features', style=discord.ButtonStyle.green)
    async def select_features(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Start feature selection"""
        
        # Check permissions
        if not isinstance(interaction.user, discord.Member) or not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ You need Administrator permissions to run setup!", ephemeral=True)
            return
        
        # Switch to feature selection view
        feature_view = FeatureSelectView(self.setup_cog, self.guild)
        
        embed = discord.Embed(
            title="🛹 7-Ply Bot Setup - Feature Selection",
            description="Choose which features you want to enable:",
            color=0x00ff88
        )
        
        embed.add_field(
            name="📋 Available Features:",
            value="🏆 **Ranking System** ✅ (Always enabled)\n💡 **Suggestions System** ❌\n👋 **Welcome Messages** ❌\n🔊 **Temp Voice Channels** ❌",
            inline=False
        )
        
        embed.add_field(
            name="💡 Click buttons to toggle features, then proceed!",
            value="• **Suggestions** - Community feedback system with voting\n• **Welcome** - Greet new members with skateboard flair\n• **Temp Voice** - Auto-managed voice channels for sessions",
            inline=False
        )
        
        await interaction.response.edit_message(embed=embed, view=feature_view)
    
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

class SetupEditView(discord.ui.View):
    """Interactive view for editing specific bot settings"""
    
    def __init__(self, setup_cog: SetupSystem, guild: discord.Guild, config: dict):
        super().__init__(timeout=300)  # 5 minute timeout
        self.setup_cog = setup_cog
        self.guild = guild
        self.config = config
    
    @discord.ui.select(
        placeholder="🔧 Choose what to edit...",
        options=[
            discord.SelectOption(
                label="🏆 Ranking Channel",
                description="Change which channel displays rank updates",
                value="ranking_channel"
            ),
            discord.SelectOption(
                label="💡 Suggestions System",
                description="Enable/disable or change suggestions channel",
                value="suggestions_feature"
            ),
            discord.SelectOption(
                label="👋 Welcome Messages", 
                description="Enable/disable or configure welcome settings",
                value="welcome_feature"
            ),
            discord.SelectOption(
                label="🔊 Temp Voice Channels",
                description="Enable/disable temporary voice channels",
                value="temp_voice_feature"
            ),
            discord.SelectOption(
                label="🎭 Reaction Roles",
                description="Enable/disable reaction role functionality",
                value="reaction_roles_feature"
            )
        ]
    )
    async def edit_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        """Handle selection of what to edit"""
        
        if select.values[0] == "ranking_channel":
            await self.edit_ranking_channel(interaction)
        elif select.values[0] == "suggestions_feature":
            await self.edit_suggestions_feature(interaction)
        elif select.values[0] == "welcome_feature":
            await self.edit_welcome_feature(interaction)
        elif select.values[0] == "temp_voice_feature":
            await self.edit_temp_voice_feature(interaction)
        elif select.values[0] == "reaction_roles_feature":
            await self.edit_reaction_roles_feature(interaction)
    
    async def edit_ranking_channel(self, interaction: discord.Interaction):
        """Edit ranking channel with channel selector"""
        
        # Get all text channels
        text_channels = [ch for ch in self.guild.text_channels if ch.permissions_for(self.guild.me).send_messages]
        
        if not text_channels:
            await interaction.response.send_message(
                "❌ No available text channels found! Make sure the bot has send message permissions.",
                ephemeral=True
            )
            return
        
        # Create channel selection dropdown
        channel_options = []
        for channel in text_channels[:25]:  # Discord limit of 25 options
            current = " (Current)" if self.config.get('ranking_channel_id') == channel.id else ""
            channel_options.append(
                discord.SelectOption(
                    label=f"#{channel.name}{current}",
                    description=f"Set ranking channel to #{channel.name}",
                    value=str(channel.id)
                )
            )
        
        class ChannelSelectView(discord.ui.View):
            def __init__(self, setup_cog, guild):
                super().__init__(timeout=60)
                self.setup_cog = setup_cog
                self.guild = guild
            
            @discord.ui.select(placeholder="🏆 Choose new ranking channel...", options=channel_options)
            async def channel_select(self, interaction: discord.Interaction, select: discord.ui.Select):
                new_channel_id = int(select.values[0])
                new_channel = self.guild.get_channel(new_channel_id)
                
                # Update config
                config = self.setup_cog.get_server_config(self.guild.id)
                config['ranking_channel_id'] = new_channel_id
                self.setup_cog.save_configs()
                
                embed = discord.Embed(
                    title="✅ Ranking Channel Updated!",
                    description=f"Ranking channel changed to {new_channel.mention}",
                    color=0x00ff88
                )
                
                await interaction.response.edit_message(embed=embed, view=None)
        
        embed = discord.Embed(
            title="🏆 Change Ranking Channel",
            description="Select a new channel for ranking displays:",
            color=0x00ff88
        )
        
        channel_view = ChannelSelectView(self.setup_cog, self.guild)
        await interaction.response.edit_message(embed=embed, view=channel_view)
    
    async def edit_suggestions_feature(self, interaction: discord.Interaction):
        """Toggle suggestions feature"""
        
        current_enabled = self.config.get('features', {}).get('suggestions', False)
        
        class SuggestionsToggleView(discord.ui.View):
            def __init__(self, setup_cog, guild):
                super().__init__(timeout=60)
                self.setup_cog = setup_cog
                self.guild = guild
            
            @discord.ui.button(label="✅ Enable Suggestions" if not current_enabled else "❌ Disable Suggestions", 
                             style=discord.ButtonStyle.green if not current_enabled else discord.ButtonStyle.red)
            async def toggle_suggestions(self, interaction: discord.Interaction, button: discord.ui.Button):
                config = self.setup_cog.get_server_config(self.guild.id)
                
                if not config.get('features'):
                    config['features'] = {}
                
                config['features']['suggestions'] = not current_enabled
                self.setup_cog.save_configs()
                
                status = "enabled" if not current_enabled else "disabled"
                embed = discord.Embed(
                    title=f"✅ Suggestions {status.title()}!",
                    description=f"Suggestions system has been {status}.",
                    color=0x00ff88 if not current_enabled else 0xff6600
                )
                
                await interaction.response.edit_message(embed=embed, view=None)
        
        embed = discord.Embed(
            title="💡 Edit Suggestions Feature",
            description=f"Suggestions are currently: **{'Enabled' if current_enabled else 'Disabled'}**",
            color=0x00ff88
        )
        
        toggle_view = SuggestionsToggleView(self.setup_cog, self.guild)
        await interaction.response.edit_message(embed=embed, view=toggle_view)
    
    async def edit_welcome_feature(self, interaction: discord.Interaction):
        """Toggle welcome messages feature"""
        
        current_enabled = self.config.get('features', {}).get('welcome_messages', False)
        
        class WelcomeToggleView(discord.ui.View):
            def __init__(self, setup_cog, guild):
                super().__init__(timeout=60)
                self.setup_cog = setup_cog
                self.guild = guild
            
            @discord.ui.button(label="✅ Enable Welcome Messages" if not current_enabled else "❌ Disable Welcome Messages",
                             style=discord.ButtonStyle.green if not current_enabled else discord.ButtonStyle.red)
            async def toggle_welcome(self, interaction: discord.Interaction, button: discord.ui.Button):
                config = self.setup_cog.get_server_config(self.guild.id)
                
                if not config.get('features'):
                    config['features'] = {}
                
                config['features']['welcome_messages'] = not current_enabled
                self.setup_cog.save_configs()
                
                status = "enabled" if not current_enabled else "disabled"
                embed = discord.Embed(
                    title=f"✅ Welcome Messages {status.title()}!",
                    description=f"Welcome messages have been {status}.",
                    color=0x00ff88 if not current_enabled else 0xff6600
                )
                
                if not current_enabled:
                    embed.add_field(
                        name="💡 Next Steps:",
                        value="Use `/welcome_config` to customize your welcome messages!",
                        inline=False
                    )
                
                await interaction.response.edit_message(embed=embed, view=None)
        
        embed = discord.Embed(
            title="👋 Edit Welcome Messages",
            description=f"Welcome messages are currently: **{'Enabled' if current_enabled else 'Disabled'}**",
            color=0x00ff88
        )
        
        toggle_view = WelcomeToggleView(self.setup_cog, self.guild)
        await interaction.response.edit_message(embed=embed, view=toggle_view)
    
    async def edit_temp_voice_feature(self, interaction: discord.Interaction):
        """Toggle temp voice channels feature"""
        
        current_enabled = self.config.get('features', {}).get('temp_voice', False)
        
        class TempVoiceToggleView(discord.ui.View):
            def __init__(self, setup_cog, guild):
                super().__init__(timeout=60)
                self.setup_cog = setup_cog
                self.guild = guild
            
            @discord.ui.button(label="✅ Enable Temp Voice" if not current_enabled else "❌ Disable Temp Voice",
                             style=discord.ButtonStyle.green if not current_enabled else discord.ButtonStyle.red)
            async def toggle_temp_voice(self, interaction: discord.Interaction, button: discord.ui.Button):
                config = self.setup_cog.get_server_config(self.guild.id)
                
                if not config.get('features'):
                    config['features'] = {}
                
                config['features']['temp_voice'] = not current_enabled
                self.setup_cog.save_configs()
                
                status = "enabled" if not current_enabled else "disabled"
                embed = discord.Embed(
                    title=f"✅ Temp Voice {status.title()}!",
                    description=f"Temporary voice channels have been {status}.",
                    color=0x00ff88 if not current_enabled else 0xff6600
                )
                
                await interaction.response.edit_message(embed=embed, view=None)
        
        embed = discord.Embed(
            title="🔊 Edit Temp Voice Channels",
            description=f"Temp voice channels are currently: **{'Enabled' if current_enabled else 'Disabled'}**",
            color=0x00ff88
        )
        
        toggle_view = TempVoiceToggleView(self.setup_cog, self.guild)
        await interaction.response.edit_message(embed=embed, view=toggle_view)

    async def edit_reaction_roles_feature(self, interaction: discord.Interaction):
        """Toggle reaction roles feature"""
        
        current_enabled = self.config.get('features', {}).get('reaction_roles', False)
        
        class ReactionRolesToggleView(discord.ui.View):
            def __init__(self, setup_cog, guild):
                super().__init__(timeout=60)
                self.setup_cog = setup_cog
                self.guild = guild
            
            @discord.ui.button(label="✅ Enable Reaction Roles" if not current_enabled else "❌ Disable Reaction Roles",
                             style=discord.ButtonStyle.green if not current_enabled else discord.ButtonStyle.red)
            async def toggle_reaction_roles(self, interaction: discord.Interaction, button: discord.ui.Button):
                config = self.setup_cog.get_server_config(self.guild.id)
                
                if not config.get('features'):
                    config['features'] = {}
                
                config['features']['reaction_roles'] = not current_enabled
                self.setup_cog.save_configs()
                
                status = "enabled" if not current_enabled else "disabled"
                embed = discord.Embed(
                    title=f"✅ Reaction Roles {status.title()}!",
                    description=f"Reaction role functionality has been {status}.\n"
                               f"{'Use `/reactionroles` to set up role reactions.' if not current_enabled else ''}",
                    color=0x00ff88 if not current_enabled else 0xff6600
                )
                
                await interaction.response.edit_message(embed=embed, view=None)
        
        embed = discord.Embed(
            title="🎭 Edit Reaction Roles",
            description=f"Reaction roles are currently: **{'Enabled' if current_enabled else 'Disabled'}**\n\n"
                       f"Reaction roles allow users to get skateboard-themed roles by reacting to messages.\n"
                       f"Roles include: Street Skater, Vert Skater, Freestyle, Cruiser, and Longboard.",
            color=0x00ff88
        )
        
        toggle_view = ReactionRolesToggleView(self.setup_cog, self.guild)
        await interaction.response.edit_message(embed=embed, view=toggle_view)

async def setup(bot):
    await bot.add_cog(SetupSystem(bot))