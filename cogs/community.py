"""
Community Features Cog
Contains reaction roles and suggestions functionality
"""

from discord.ext import commands
from discord import app_commands
import discord
import json
import os
from typing import Optional

class ReactionRoleCustomModal(discord.ui.Modal, title='Custom Reaction Roles'):
    def __init__(self, target_channel, bot):
        super().__init__()
        self.target_channel = target_channel
        self.bot = bot

    embed_title = discord.ui.TextInput(
        label='Embed Title',
        placeholder='Enter the title for your reaction role message...',
        default='🎭 Choose Your Role!',
        max_length=256
    )
    
    embed_description = discord.ui.TextInput(
        label='Embed Description', 
        placeholder='Enter the description...',
        default='React with an emoji to get your role!',
        style=discord.TextStyle.paragraph,
        max_length=1024
    )
    
    role1 = discord.ui.TextInput(
        label='Role 1 (emoji:role name)',
        placeholder='🎯:Gamer',
        max_length=100,
        required=True
    )
    
    role2 = discord.ui.TextInput(
        label='Role 2 (emoji:role name)',
        placeholder='🎨:Artist', 
        max_length=100,
        required=False
    )
    
    role3 = discord.ui.TextInput(
        label='Role 3 (emoji:role name)',
        placeholder='🎵:Musician',
        max_length=100,
        required=False
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            # Parse role inputs
            roles_data = {}
            role_display = []
            emojis = []
            
            for role_input in [self.role1, self.role2, self.role3]:
                if role_input.value.strip():
                    if ':' not in role_input.value:
                        await interaction.response.send_message(
                            "❌ Invalid format! Use `emoji:role name` format (e.g., `🎯:Gamer`)", 
                            ephemeral=True
                        )
                        return
                    
                    emoji, role_name = role_input.value.split(':', 1)
                    emoji = emoji.strip()
                    role_name = role_name.strip()
                    
                    if not emoji or not role_name:
                        await interaction.response.send_message(
                            "❌ Both emoji and role name are required!", 
                            ephemeral=True
                        )
                        return
                    
                    roles_data[emoji] = role_name
                    role_display.append(f"{emoji} {role_name}")
                    emojis.append(emoji)
            
            if not roles_data:
                await interaction.response.send_message(
                    "❌ You must provide at least one role!", 
                    ephemeral=True
                )
                return
            
            # Create embed
            embed = discord.Embed(
                title=self.embed_title.value,
                description=self.embed_description.value,
                color=0x00ff88
            )
            embed.add_field(
                name="Available Roles:",
                value="\n".join(role_display),
                inline=False
            )
            embed.set_footer(text="React to this message to get your role!")
            
            # Send message and add reactions
            message = await self.target_channel.send(embed=embed)
            
            for emoji in emojis:
                try:
                    await message.add_reaction(emoji)
                except discord.HTTPException:
                    # Skip invalid emojis
                    continue
            
            # Store message info
            cog = self.bot.get_cog('CommunityFeatures')
            if cog:
                cog.reaction_roles_data[str(message.id)] = roles_data
                cog.save_reaction_roles()
            
            success_embed = discord.Embed(
                title="✅ Custom Reaction Roles Created!",
                description=f"Your custom reaction roles have been created in {self.target_channel.mention}!",
                color=0x00ff88
            )
            await interaction.response.send_message(embed=success_embed, ephemeral=True)
            
        except Exception as e:
            error_embed = discord.Embed(
                title="❌ Error",
                description=f"Failed to create custom reaction roles: {str(e)}",
                color=0xff6600
            )
            await interaction.response.send_message(embed=error_embed, ephemeral=True)

class ReactionRoleEditModal(discord.ui.Modal, title='Edit Reaction Roles'):
    def __init__(self, msg_data):
        super().__init__()
        self.msg_data = msg_data
        
        # Pre-fill with existing data
        roles_list = list(msg_data['roles_data'].items())
        
        # Extract current title and description from the message embed
        embed = msg_data['message'].embeds[0] if msg_data['message'].embeds else None
        current_title = embed.title if embed else "🎭 Choose Your Role!"
        current_description = embed.description if embed else "React with an emoji to get your role!"
        
        self.embed_title.default = current_title
        self.embed_description.default = current_description
        
        # Pre-fill role fields
        if len(roles_list) > 0:
            emoji, role_name = roles_list[0]
            self.role1.default = f"{emoji}:{role_name}"
        if len(roles_list) > 1:
            emoji, role_name = roles_list[1]
            self.role2.default = f"{emoji}:{role_name}"
        if len(roles_list) > 2:
            emoji, role_name = roles_list[2]
            self.role3.default = f"{emoji}:{role_name}"

    embed_title = discord.ui.TextInput(
        label='Embed Title',
        placeholder='Enter the title for your reaction role message...',
        max_length=256
    )
    
    embed_description = discord.ui.TextInput(
        label='Embed Description', 
        placeholder='Enter the description...',
        style=discord.TextStyle.paragraph,
        max_length=1024
    )
    
    role1 = discord.ui.TextInput(
        label='Role 1 (emoji:role name)',
        placeholder='🎯:Gamer',
        max_length=100,
        required=False
    )
    
    role2 = discord.ui.TextInput(
        label='Role 2 (emoji:role name)',
        placeholder='🎨:Artist', 
        max_length=100,
        required=False
    )
    
    role3 = discord.ui.TextInput(
        label='Role 3 (emoji:role name)',
        placeholder='🎵:Musician',
        max_length=100,
        required=False
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            # Parse role inputs
            roles_data = {}
            role_display = []
            emojis = []
            
            for role_input in [self.role1, self.role2, self.role3]:
                if role_input.value.strip():
                    if ':' not in role_input.value:
                        await interaction.response.send_message(
                            "❌ Invalid format! Use `emoji:role name` format (e.g., `🎯:Gamer`)", 
                            ephemeral=True
                        )
                        return
                    
                    emoji, role_name = role_input.value.split(':', 1)
                    emoji = emoji.strip()
                    role_name = role_name.strip()
                    
                    if not emoji or not role_name:
                        await interaction.response.send_message(
                            "❌ Both emoji and role name are required!", 
                            ephemeral=True
                        )
                        return
                    
                    roles_data[emoji] = role_name
                    role_display.append(f"{emoji} {role_name}")
                    emojis.append(emoji)
            
            if not roles_data:
                await interaction.response.send_message(
                    "❌ You must provide at least one role!", 
                    ephemeral=True
                )
                return
            
            # Update the existing message
            embed = discord.Embed(
                title=self.embed_title.value,
                description=self.embed_description.value,
                color=0x00ff88
            )
            embed.add_field(
                name="Available Roles:",
                value="\n".join(role_display),
                inline=False
            )
            embed.set_footer(text="React to this message to get your role!")
            
            # Edit the existing message
            await self.msg_data['message'].edit(embed=embed)
            
            # Clear old reactions and add new ones
            await self.msg_data['message'].clear_reactions()
            for emoji in emojis:
                try:
                    await self.msg_data['message'].add_reaction(emoji)
                except discord.HTTPException:
                    # Skip invalid emojis
                    continue
            
            # Update stored data
            from discord.ext.commands import Bot
            from typing import cast
            bot = cast(Bot, interaction.client)
            cog = cast('CommunityFeatures', bot.get_cog('CommunityFeatures'))
            if cog:
                cog.reaction_roles_data[self.msg_data['message_id']] = roles_data
                cog.save_reaction_roles()
            
            success_embed = discord.Embed(
                title="✅ Reaction Roles Updated!",
                description=f"The reaction role message in {self.msg_data['channel'].mention} has been updated!",
                color=0x00ff88
            )
            await interaction.response.send_message(embed=success_embed, ephemeral=True)
            
        except Exception as e:
            error_embed = discord.Embed(
                title="❌ Error",
                description=f"Failed to update reaction roles: {str(e)}",
                color=0xff6600
            )
            await interaction.response.send_message(embed=error_embed, ephemeral=True)

class CommunityFeatures(commands.Cog):
    """Community features including reaction roles and suggestions"""
    
    def __init__(self, bot):
        self.bot = bot
        self.data_dir = "data"
        self.reaction_roles_file = os.path.join(self.data_dir, "reaction_roles.json")
        
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Load reaction roles
        self.reaction_roles_data = self.load_reaction_roles()

    def load_reaction_roles(self):
        """Load reaction roles from JSON file"""
        try:
            if os.path.exists(self.reaction_roles_file):
                with open(self.reaction_roles_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading reaction roles: {e}")
        return {}

    def save_reaction_roles(self):
        """Save reaction roles to JSON file"""
        try:
            with open(self.reaction_roles_file, 'w') as f:
                json.dump(self.reaction_roles_data, f, indent=2)
        except Exception as e:
            print(f"Error saving reaction roles: {e}")

    @app_commands.command(name='reactionroles', description='Create a reaction role message')
    @app_commands.default_permissions(manage_roles=True)
    async def reaction_roles(self, interaction: discord.Interaction, channel: Optional[discord.TextChannel] = None):
        """Create a reaction role message in the specified or current channel"""
        
        # Check if reaction roles feature is enabled
        setup_cog = self.bot.get_cog('Setup')
        if setup_cog and interaction.guild:
            config = setup_cog.get_server_config(interaction.guild.id)
            if not config.get('features', {}).get('reaction_roles', False):
                embed = discord.Embed(
                    title="❌ Feature Disabled",
                    description="Reaction roles are currently disabled on this server.\n"
                               "An administrator can enable them using `/setup` command.",
                    color=0xff6600
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
        
        target_channel = channel or interaction.channel
        
        # Ensure we have a text channel
        if not isinstance(target_channel, discord.TextChannel):
            embed = discord.Embed(
                title="❌ Invalid Channel",
                description="Reaction roles can only be created in text channels.",
                color=0xff6600
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Show customization options
        class ReactionRoleSetupView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=300)
            
            @discord.ui.button(label="🛹 Use Default Skateboard Roles", style=discord.ButtonStyle.green)
            async def use_defaults(self, interaction: discord.Interaction, button: discord.ui.Button):
                await self.create_default_roles(interaction)
            
            @discord.ui.button(label="⚙️ Customize Roles", style=discord.ButtonStyle.blurple)
            async def customize_roles(self, interaction: discord.Interaction, button: discord.ui.Button):
                modal = ReactionRoleCustomModal(target_channel, interaction.client)
                await interaction.response.send_modal(modal)
            
            async def create_default_roles(self, interaction: discord.Interaction):
                """Create reaction roles with default skateboard theme"""
                try:
                    embed = discord.Embed(
                        title="🛹 Choose Your Skateboard Style! 🛹",
                        description="React with an emoji to get your skateboard role!",
                        color=0x00ff00
                    )
                    embed.add_field(
                        name="Available Roles:",
                        value="🛹 Street Skater\n🏁 Vert Skater\n🎯 Freestyle\n🌊 Cruiser\n⚡ Longboard",
                        inline=False
                    )
                    embed.set_footer(text="React to this message to get your role!")
                    
                    message = await target_channel.send(embed=embed)
                    
                    # Add reactions
                    emojis = ["🛹", "🏁", "🎯", "🌊", "⚡"]
                    for emoji in emojis:
                        await message.add_reaction(emoji)
                    
                    # Store message info
                    from discord.ext.commands import Bot
                    from typing import cast
                    bot = cast(Bot, interaction.client)
                    cog = cast('CommunityFeatures', bot.get_cog('CommunityFeatures'))
                    if cog:
                        cog.reaction_roles_data[str(message.id)] = {
                            "🛹": "Street Skater",
                            "🏁": "Vert Skater", 
                            "🎯": "Freestyle",
                            "🌊": "Cruiser",
                            "⚡": "Longboard"
                        }
                        cog.save_reaction_roles()
                    
                    success_embed = discord.Embed(
                        title="✅ Reaction Roles Created!",
                        description=f"Default skateboard reaction roles have been created in {target_channel.mention}!",
                        color=0x00ff88
                    )
                    await interaction.response.edit_message(embed=success_embed, view=None)
                    
                except Exception as e:
                    error_embed = discord.Embed(
                        title="❌ Error",
                        description=f"Failed to create reaction roles: {str(e)}",
                        color=0xff6600
                    )
                    await interaction.response.edit_message(embed=error_embed, view=None)

        embed = discord.Embed(
            title="🎭 Reaction Roles Setup",
            description=f"Choose how you want to set up reaction roles in {target_channel.mention}:",
            color=0x00ff88
        )
        embed.add_field(
            name="🛹 Default Skateboard Roles",
            value="Street Skater, Vert Skater, Freestyle, Cruiser, Longboard",
            inline=False
        )
        embed.add_field(
            name="⚙️ Custom Roles",
            value="Create your own roles with custom emojis and names",
            inline=False
        )
        
        view = ReactionRoleSetupView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @app_commands.command(name='reactionroles_manage', description='Manage existing reaction role messages')
    @app_commands.default_permissions(manage_roles=True)
    async def reaction_roles_manage(self, interaction: discord.Interaction):
        """Manage existing reaction role messages in the server"""
        
        # Check if reaction roles feature is enabled
        setup_cog = self.bot.get_cog('Setup')
        if setup_cog and interaction.guild:
            config = setup_cog.get_server_config(interaction.guild.id)
            if not config.get('features', {}).get('reaction_roles', False):
                embed = discord.Embed(
                    title="❌ Feature Disabled",
                    description="Reaction roles are currently disabled on this server.\n"
                               "An administrator can enable them using `/setup` command.",
                    color=0xff6600
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

        if not self.reaction_roles_data:
            embed = discord.Embed(
                title="📝 No Reaction Role Messages",
                description="There are no reaction role messages set up on this server yet.\n"
                           "Use `/reactionroles` to create your first one!",
                color=0x00ff88
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Find messages in this guild
        guild_messages = []
        if interaction.guild:
            for message_id, roles_data in self.reaction_roles_data.items():
                try:
                    # Try to find the message in any channel in this guild
                    message = None
                    for channel in interaction.guild.text_channels:
                        try:
                            message = await channel.fetch_message(int(message_id))
                            break
                        except (discord.NotFound, discord.Forbidden):
                            continue
                    
                    if message:
                        guild_messages.append({
                            'message_id': message_id,
                            'message': message,
                            'roles_data': roles_data,
                            'channel': message.channel
                        })
                except (ValueError, discord.HTTPException):
                    continue

        if not guild_messages:
            embed = discord.Embed(
                title="📝 No Active Reaction Role Messages",
                description="No active reaction role messages found in this server.\n"
                           "They may have been deleted or are in channels I can't access.",
                color=0x00ff88
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Create management interface
        class ReactionRoleManageView(discord.ui.View):
            def __init__(self, messages_data):
                super().__init__(timeout=300)
                self.messages_data = messages_data
                
                # Add dropdown to select message
                options = []
                for i, msg_data in enumerate(messages_data[:25]):  # Discord limit
                    roles_list = list(msg_data['roles_data'].values())[:3]  # Show first 3 roles
                    roles_preview = ", ".join(roles_list)
                    if len(msg_data['roles_data']) > 3:
                        roles_preview += "..."
                    
                    options.append(discord.SelectOption(
                        label=f"#{msg_data['channel'].name}",
                        description=f"Roles: {roles_preview}",
                        value=str(i)
                    ))
                
                if options:
                    self.message_select = MessageSelect(options, self.messages_data)
                    self.add_item(self.message_select)

        class MessageSelect(discord.ui.Select):
            def __init__(self, options, messages_data):
                super().__init__(placeholder="Select a reaction role message to manage...", options=options)
                self.messages_data = messages_data

            async def callback(self, interaction: discord.Interaction):
                selected_index = int(self.values[0])
                selected_message = self.messages_data[selected_index]
                
                # Show management options for selected message
                class MessageManageView(discord.ui.View):
                    def __init__(self, msg_data):
                        super().__init__(timeout=300)
                        self.msg_data = msg_data

                    @discord.ui.button(label="✏️ Edit Message", style=discord.ButtonStyle.blurple)
                    async def edit_message(self, interaction: discord.Interaction, button: discord.ui.Button):
                        # Create pre-filled modal
                        modal = ReactionRoleEditModal(self.msg_data)
                        await interaction.response.send_modal(modal)

                    @discord.ui.button(label="🗑️ Delete Message", style=discord.ButtonStyle.danger)
                    async def delete_message(self, interaction: discord.Interaction, button: discord.ui.Button):
                        try:
                            # Delete the Discord message
                            await self.msg_data['message'].delete()
                            
                            # Remove from data
                            from discord.ext.commands import Bot
                            from typing import cast
                            bot = cast(Bot, interaction.client)
                            cog = cast('CommunityFeatures', bot.get_cog('CommunityFeatures'))
                            if cog:
                                if self.msg_data['message_id'] in cog.reaction_roles_data:
                                    del cog.reaction_roles_data[self.msg_data['message_id']]
                                    cog.save_reaction_roles()
                            
                            success_embed = discord.Embed(
                                title="✅ Message Deleted",
                                description=f"Reaction role message in {self.msg_data['channel'].mention} has been deleted.",
                                color=0x00ff88
                            )
                            await interaction.response.edit_message(embed=success_embed, view=None)
                            
                        except discord.NotFound:
                            error_embed = discord.Embed(
                                title="❌ Message Not Found",
                                description="The message was already deleted.",
                                color=0xff6600
                            )
                            await interaction.response.edit_message(embed=error_embed, view=None)
                        except Exception as e:
                            error_embed = discord.Embed(
                                title="❌ Error",
                                description=f"Failed to delete message: {str(e)}",
                                color=0xff6600
                            )
                            await interaction.response.edit_message(embed=error_embed, view=None)

                    @discord.ui.button(label="📊 View Details", style=discord.ButtonStyle.secondary)
                    async def view_details(self, interaction: discord.Interaction, button: discord.ui.Button):
                        roles_info = []
                        for emoji, role_name in self.msg_data['roles_data'].items():
                            roles_info.append(f"{emoji} → **{role_name}**")
                        
                        embed = discord.Embed(
                            title="📊 Reaction Role Details",
                            description=f"**Channel:** {self.msg_data['channel'].mention}\n"
                                       f"**Message ID:** `{self.msg_data['message_id']}`",
                            color=0x00ff88
                        )
                        embed.add_field(
                            name="Configured Roles:",
                            value="\n".join(roles_info),
                            inline=False
                        )
                        embed.add_field(
                            name="Message Link:",
                            value=f"[Jump to Message]({self.msg_data['message'].jump_url})",
                            inline=False
                        )
                        
                        await interaction.response.edit_message(embed=embed, view=self)

                # Show selected message info and options
                roles_info = []
                for emoji, role_name in selected_message['roles_data'].items():
                    roles_info.append(f"{emoji} **{role_name}**")

                embed = discord.Embed(
                    title="🎭 Manage Reaction Role Message",
                    description=f"**Channel:** {selected_message['channel'].mention}\n"
                               f"**Roles:** {', '.join(roles_info)}",
                    color=0x00ff88
                )
                embed.add_field(
                    name="Available Actions:",
                    value="✏️ **Edit** - Modify roles and message content\n"
                          "🗑️ **Delete** - Remove this reaction role message\n"
                          "📊 **Details** - View full configuration",
                    inline=False
                )

                manage_view = MessageManageView(selected_message)
                await interaction.response.edit_message(embed=embed, view=manage_view)

        # Show list of messages
        embed = discord.Embed(
            title="🎭 Reaction Role Management",
            description=f"Found **{len(guild_messages)}** reaction role message(s) in this server.\n"
                       "Select a message below to manage it.",
            color=0x00ff88
        )
        
        # Add preview of messages
        preview_text = []
        for msg_data in guild_messages[:5]:  # Show first 5
            roles_preview = ", ".join(list(msg_data['roles_data'].values())[:2])
            if len(msg_data['roles_data']) > 2:
                roles_preview += "..."
            preview_text.append(f"• **#{msg_data['channel'].name}**: {roles_preview}")
        
        if preview_text:
            embed.add_field(
                name="Messages Found:",
                value="\n".join(preview_text),
                inline=False
            )

        manage_view = ReactionRoleManageView(guild_messages)
        await interaction.response.send_message(embed=embed, view=manage_view, ephemeral=True)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """Handle reaction role assignment"""
        if payload.user_id == self.bot.user.id:
            return
        
        # Check if reaction roles feature is enabled
        if payload.guild_id:
            setup_cog = self.bot.get_cog('Setup')
            if setup_cog:
                config = setup_cog.get_server_config(payload.guild_id)
                if not config.get('features', {}).get('reaction_roles', False):
                    return
            
        message_id = str(payload.message_id)
        if message_id not in self.reaction_roles_data:
            return
            
        emoji = str(payload.emoji)
        if emoji not in self.reaction_roles_data[message_id]:
            return
            
        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return
            
        member = guild.get_member(payload.user_id)
        if not member:
            return
            
        role_name = self.reaction_roles_data[message_id][emoji]
        role = discord.utils.get(guild.roles, name=role_name)
        
        if not role:
            # Create the role if it doesn't exist
            try:
                role = await guild.create_role(name=role_name, color=0x00ff00)
            except discord.Forbidden:
                print(f"Cannot create role {role_name}: Missing permissions")
                return
            except Exception as e:
                print(f"Error creating role {role_name}: {e}")
                return
        
        try:
            await member.add_roles(role)
            print(f"Added role {role_name} to {member.display_name}")
        except discord.Forbidden:
            print(f"Cannot add role {role_name} to {member.display_name}: Missing permissions")
        except Exception as e:
            print(f"Error adding role {role_name} to {member.display_name}: {e}")

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        """Handle reaction role removal"""
        
        # Check if reaction roles feature is enabled
        if payload.guild_id:
            setup_cog = self.bot.get_cog('Setup')
            if setup_cog:
                config = setup_cog.get_server_config(payload.guild_id)
                if not config.get('features', {}).get('reaction_roles', False):
                    return
        
        message_id = str(payload.message_id)
        if message_id not in self.reaction_roles_data:
            return
            
        emoji = str(payload.emoji)
        if emoji not in self.reaction_roles_data[message_id]:
            return
            
        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return
            
        member = guild.get_member(payload.user_id)
        if not member:
            return
            
        role_name = self.reaction_roles_data[message_id][emoji]
        role = discord.utils.get(guild.roles, name=role_name)
        
        if role and role in member.roles:
            try:
                await member.remove_roles(role)
                print(f"Removed role {role_name} from {member.display_name}")
            except discord.Forbidden:
                print(f"Cannot remove role {role_name} from {member.display_name}: Missing permissions")
            except Exception as e:
                print(f"Error removing role {role_name} from {member.display_name}: {e}")

async def setup(bot):
    await bot.add_cog(CommunityFeatures(bot))