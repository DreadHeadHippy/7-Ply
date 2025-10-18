import discord
from discord.ext import commands
from discord import ui, Interaction
import asyncio

# UI View for temp VC controls

# --- Modernized TempVCControlView with all controls ---
class TempVCControlView(ui.View):
    def __init__(self, bot, host_id, vc_id, temp_channels):
        super().__init__(timeout=None)
        self.bot = bot
        self.host_id = host_id
        self.vc_id = vc_id
        self.temp_channels = temp_channels

    # Buttons are added via @ui.button decorators only to avoid duplicate custom_id errors.

    async def interaction_check(self, interaction: Interaction) -> bool:
        if interaction.user.id != self.host_id:
            await interaction.response.send_message("Only the host can use these controls!", ephemeral=True)
            return False
        return True

    @ui.button(label="Lock", style=discord.ButtonStyle.primary, custom_id="lock")
    async def lock_button(self, interaction: Interaction, button: ui.Button):
        vc = interaction.guild.get_channel(self.vc_id)
        if not vc:
            await interaction.response.send_message("VC not found.", ephemeral=True)
            return
        
        # Debug: Check bot permissions
        bot_perms = vc.permissions_for(interaction.guild.me)
        print(f"[TempVoice] Bot permissions in {vc.name}: manage_channels={bot_perms.manage_channels}, manage_roles={bot_perms.manage_roles}")
        
        success_msg = ""
        warning_msg = ""
        
        try:
            # Lock @everyone out
            await vc.set_permissions(vc.guild.default_role, connect=False)
            success_msg = "🔒 Channel locked from @everyone! "
            
            # Try to ensure whitelisted users can still connect
            if self.vc_id in self.temp_channels:
                failed_whitelist = []
                for user_id in self.temp_channels[self.vc_id]["whitelist"]:
                    user = interaction.guild.get_member(user_id)
                    if user:
                        try:
                            await vc.set_permissions(user, connect=True)
                        except discord.Forbidden:
                            failed_whitelist.append(user.display_name)
                
                if failed_whitelist:
                    warning_msg = f"\n⚠️ Could not preserve access for: {', '.join(failed_whitelist)}"
                else:
                    success_msg += "Whitelisted users can still join."
            
            final_msg = success_msg + warning_msg
            await interaction.response.send_message(final_msg, ephemeral=True)
            
        except discord.Forbidden as e:
            print(f"[TempVoice] Forbidden error when locking {vc.name}: {e}")
            await interaction.response.send_message("❌ I don't have permission to lock this channel. Please check my role permissions.", ephemeral=True)
        except Exception as e:
            print(f"[TempVoice] Unexpected error when locking {vc.name}: {e}")
            await interaction.response.send_message(f"❌ Failed to lock channel: {e}", ephemeral=True)

    @ui.button(label="Unlock", style=discord.ButtonStyle.success, custom_id="unlock")
    async def unlock_button(self, interaction: Interaction, button: ui.Button):
        vc = interaction.guild.get_channel(self.vc_id)
        if not vc:
            await interaction.response.send_message("VC not found.", ephemeral=True)
            return
        try:
            # Simply allow @everyone to connect - remove the deny override
            await vc.set_permissions(vc.guild.default_role, connect=True)
            await interaction.response.send_message("🔓 Channel unlocked! Anyone can join.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("❌ I don't have permission to unlock this channel. Please check my role permissions.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to unlock channel: {e}", ephemeral=True)

    @ui.button(label="Kick", style=discord.ButtonStyle.danger, custom_id="kick")
    async def kick_button(self, interaction: Interaction, button: ui.Button):
        vc = interaction.guild.get_channel(self.vc_id)
        if not vc:
            await interaction.response.send_message("VC not found.", ephemeral=True)
            return
        # Show dropdown of current members (except host)
        options = [discord.SelectOption(label=m.display_name, value=str(m.id)) for m in vc.members if m.id != self.host_id]
        if not options:
            await interaction.response.send_message("No one to kick!", ephemeral=True)
            return
        select = ui.Select(placeholder="Select user to kick", options=options)

        async def select_callback(select_interaction: Interaction):
            user_id = int(select.values[0])
            user = interaction.guild.get_member(user_id)
            if user:
                await user.move_to(None)
                await select_interaction.response.send_message(f"👢 {user.display_name} has been kicked!", ephemeral=True)
        select.callback = select_callback
        view = ui.View()
        view.add_item(select)
        await interaction.response.send_message("Select a user to kick:", view=view, ephemeral=True)

    @ui.button(label="Whitelist", style=discord.ButtonStyle.primary, custom_id="whitelist")
    async def whitelist_button(self, interaction: Interaction, button: ui.Button):
        vc = interaction.guild.get_channel(self.vc_id)
        if not vc:
            await interaction.response.send_message("VC not found.", ephemeral=True)
            return
        # Show dropdown of all guild members not already whitelisted
        whitelisted = {uid for uid in self.temp_channels[self.vc_id]["whitelist"]}
        options = [discord.SelectOption(label=m.display_name, value=str(m.id)) for m in vc.guild.members if not m.bot and m.id != self.host_id and m.id not in whitelisted]
        if not options:
            await interaction.response.send_message("No eligible users to whitelist!", ephemeral=True)
            return
        select = ui.Select(placeholder="Select user to whitelist", options=options)

        async def select_callback(select_interaction: Interaction):
            user_id = int(select.values[0])
            user = interaction.guild.get_member(user_id)
            if user:
                try:
                    await vc.set_permissions(user, connect=True)
                    self.temp_channels[self.vc_id]["whitelist"].add(user.id)
                    await select_interaction.response.send_message(f"✅ {user.display_name} has been whitelisted!", ephemeral=True)
                except Exception as e:
                    await select_interaction.response.send_message(f"❌ Failed to whitelist {user.display_name}: {e}", ephemeral=True)
        select.callback = select_callback
        view = ui.View()
        view.add_item(select)
        await interaction.response.send_message("Select a user to whitelist:", view=view, ephemeral=True)

    @ui.button(label="Un-Whitelist", style=discord.ButtonStyle.secondary, custom_id="unwhitelist")
    async def unwhitelist_button(self, interaction: Interaction, button: ui.Button):
        vc = interaction.guild.get_channel(self.vc_id)
        if not vc:
            await interaction.response.send_message("VC not found.", ephemeral=True)
            return
        # Show dropdown of currently whitelisted users (except host)
        whitelisted = [interaction.guild.get_member(uid) for uid in self.temp_channels[self.vc_id]["whitelist"] if uid != self.host_id]
        options = [discord.SelectOption(label=m.display_name, value=str(m.id)) for m in whitelisted if m]
        if not options:
            await interaction.response.send_message("No users to un-whitelist!", ephemeral=True)
            return
        select = ui.Select(placeholder="Select user to remove from whitelist", options=options)

        async def select_callback(select_interaction: Interaction):
            user_id = int(select.values[0])
            user = interaction.guild.get_member(user_id)
            if user:
                try:
                    await vc.set_permissions(user, overwrite=None)
                    self.temp_channels[self.vc_id]["whitelist"].discard(user.id)
                    await select_interaction.response.send_message(f"❌ {user.display_name} has been removed from the whitelist!", ephemeral=True)
                except Exception as e:
                    await select_interaction.response.send_message(f"❌ Failed to remove {user.display_name} from whitelist: {e}", ephemeral=True)
        select.callback = select_callback
        view = ui.View()
        view.add_item(select)
        await interaction.response.send_message("Select a user to remove from whitelist:", view=view, ephemeral=True)

    @ui.button(label="Transfer Ownership", style=discord.ButtonStyle.primary, custom_id="transferhost")
    async def transferhost_button(self, interaction: Interaction, button: ui.Button):
        vc = interaction.guild.get_channel(self.vc_id)
        if not vc:
            await interaction.response.send_message("VC not found.", ephemeral=True)
            return
        # Show dropdown of current members (except host)
        options = [discord.SelectOption(label=m.display_name, value=str(m.id)) for m in vc.members if m.id != self.host_id]
        if not options:
            await interaction.response.send_message("No one to transfer ownership to!", ephemeral=True)
            return
        select = ui.Select(placeholder="Select new owner", options=options)

        async def select_callback(select_interaction: Interaction):
            user_id = int(select.values[0])
            user = interaction.guild.get_member(user_id)
            if user:
                try:
                    self.temp_channels[self.vc_id]["host"] = user.id
                    await vc.set_permissions(user, manage_channels=True, connect=True)
                    await select_interaction.response.send_message(f"👑 Host transferred to {user.display_name}!", ephemeral=True)
                except Exception as e:
                    await select_interaction.response.send_message(f"❌ Failed to transfer ownership to {user.display_name}: {e}", ephemeral=True)
        select.callback = select_callback
        view = ui.View()
        view.add_item(select)
        await interaction.response.send_message("Select a new owner:", view=view, ephemeral=True)

class TempVoice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # temp_channels: {voice_channel_id: {"host": user_id, "whitelist": set, "blacklist": set}}
        self.temp_channels = {}

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        print(f"[TempVoice] on_voice_state_update: member={member}, before={before.channel}, after={after.channel}")
        guild = member.guild
        # User joins a voice channel to create temp VC
        if after.channel:
            print(f"[TempVoice] after.channel.name={after.channel.name} (id={after.channel.id})")
        # Case-insensitive, strip spaces
        trigger_name = "join to create"
        if after.channel and after.channel.name and after.channel.name.strip().lower() == trigger_name:
            # Create temp voice channel WITHOUT overwrites first, then sync and add host perms
            try:
                # Create channel with no initial overwrites so sync_permissions() works properly
                temp_vc = await guild.create_voice_channel(
                    name=f"{member.display_name}'s Session",
                    category=after.channel.category
                )
                print(f"[TempVoice] Created temp VC: {temp_vc.name} (id={temp_vc.id})")
                
                # Manually sync with category permissions (copy category overwrites)
                if after.channel.category:
                    try:
                        category = after.channel.category
                        # Copy all permission overwrites from the category to the temp VC
                        for target, overwrite in category.overwrites.items():
                            await temp_vc.set_permissions(target, overwrite=overwrite)
                        print(f"[TempVoice] Synced permissions with category '{category.name}' ({len(category.overwrites)} overwrites)")
                        
                        # Now add host permissions on top of the synced permissions
                        await temp_vc.set_permissions(member, manage_channels=True, connect=True)
                        print(f"[TempVoice] Added host permissions for {member.display_name}")
                    except discord.Forbidden as perm_error:
                        print(f"[TempVoice] Permission denied syncing with category: {perm_error}")
                        # Fallback: add basic host permissions if sync fails
                        await temp_vc.set_permissions(member, manage_channels=True, connect=True)
                    except Exception as sync_error:
                        print(f"[TempVoice] Could not sync permissions: {sync_error}")
                        # Fallback: add basic host permissions if sync fails
                        await temp_vc.set_permissions(member, manage_channels=True, connect=True)
                else:
                    # No category, just add host permissions
                    await temp_vc.set_permissions(member, manage_channels=True, connect=True)
                    print(f"[TempVoice] No category to sync with, added basic host permissions")
                
                self.temp_channels[temp_vc.id] = {
                    "host": member.id,
                    "whitelist": set([member.id]),
                    "blacklist": set()
                }
                await member.move_to(temp_vc)

                # Find the Discord-generated text channel for this VC (should have same ID as the VC)
                text_channel = guild.get_channel(temp_vc.id)
                if text_channel:
                    embed = discord.Embed(
                        title=f"{member.display_name}'s Session Controls",
                        description=(
                            f"{member.mention} is the host of this session.\n"
                            "Use the dropdowns below to manage your VC."
                        ),
                        color=discord.Color.blue()
                    )
                    view = TempVCControlView(self.bot, member.id, temp_vc.id, self.temp_channels)
                    await text_channel.send(embed=embed, view=view)
                else:
                    print(f"[TempVoice] Could not find text channel with ID {temp_vc.id}")
            except Exception as e:
                print(f"[TempVoice] Error creating temp VC: {e}")
        elif after.channel:
            print(f"[TempVoice] Skipped temp VC creation: after.channel.name='{after.channel.name}' did not match trigger '{trigger_name}'")

        # Clean up empty temp VC
        if before.channel and before.channel.id in self.temp_channels:
            channel = before.channel
            if len(channel.members) == 0:
                try:
                    await channel.delete()
                    print(f"[TempVoice] Deleted empty temp VC: {channel.name}")
                except discord.Forbidden:
                    print(f"[TempVoice] Cannot delete {channel.name} - may be a Discord-managed channel")
                    # For Discord-managed channels, just reset permissions instead
                    try:
                        await channel.set_permissions(channel.guild.default_role, overwrite=None)
                        await channel.edit(name="Temp Voice Channel")  # Reset to generic name
                    except:
                        pass
                except Exception as e:
                    print(f"[TempVoice] Error cleaning up temp VC: {e}")
                finally:
                    # Always remove from tracking
                    del self.temp_channels[channel.id]

async def setup(bot):
    await bot.add_cog(TempVoice(bot))