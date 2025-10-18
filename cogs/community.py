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
        target_channel = channel or interaction.channel
        
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
            self.reaction_roles_data[str(message.id)] = {
                "🛹": "Street Skater",
                "🏁": "Vert Skater", 
                "🎯": "Freestyle",
                "🌊": "Cruiser",
                "⚡": "Longboard"
            }
            self.save_reaction_roles()
            
            if channel:
                await interaction.response.send_message(f"✅ Reaction roles message created in {channel.mention}!", ephemeral=True)
            else:
                await interaction.response.send_message("✅ Reaction roles message created!", ephemeral=True)
                
        except discord.Forbidden:
            await interaction.response.send_message("❌ I don't have permission to send messages or add reactions in that channel", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error creating reaction roles: {e}", ephemeral=True)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """Handle reaction role assignment"""
        if payload.user_id == self.bot.user.id:
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