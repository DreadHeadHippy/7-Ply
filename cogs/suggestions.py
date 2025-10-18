import discord
from discord.ext import commands

# Skateboarding-themed suggestion system
SUGGESTIONS_CHANNEL_ID = 1428418247291830403

class SuggestionView(discord.ui.View):
    def __init__(self, author, thread):
        super().__init__(timeout=None)  # Persistent view
        self.author = author
        self.thread = thread

    @discord.ui.button(style=discord.ButtonStyle.success, label="✅ Approve", custom_id="approve_suggestion")
    async def approve(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Check if user has manage messages permission
        member = interaction.guild.get_member(interaction.user.id) if interaction.guild else None
        if not member or not member.guild_permissions.manage_messages:
            await interaction.response.send_message("❌ You need 'Manage Messages' permission to approve suggestions!", ephemeral=True)
            return

        if not interaction.message or not interaction.message.embeds:
            await interaction.response.send_message("❌ Error: Could not find the suggestion message.", ephemeral=True)
            return

        embed = interaction.message.embeds[0]
        
        # Fetch the message fresh to get accurate reaction counts
        try:
            fresh_message = await interaction.channel.fetch_message(interaction.message.id)
            yays = 0
            nays = 0
            
            if fresh_message.reactions:
                for reaction in fresh_message.reactions:
                    if str(reaction.emoji) == "✅":
                        yays = max(0, reaction.count - 1)  # Subtract 1 for bot's reaction
                    elif str(reaction.emoji) == "❌":
                        nays = max(0, reaction.count - 1)  # Subtract 1 for bot's reaction
        except:
            # Fallback to cached reactions if fetch fails
            yays = 0
            nays = 0
            if interaction.message.reactions:
                for reaction in interaction.message.reactions:
                    if str(reaction.emoji) == "✅":
                        yays = max(0, reaction.count - 1)
                    elif str(reaction.emoji) == "❌":
                        nays = max(0, reaction.count - 1)

        embed.color = discord.Color.green()
        embed.set_author(name=f'Suggested by {self.author}', icon_url=self.author.display_avatar.url)
        embed.set_footer(text=f"🛹 Suggestion Approved by {interaction.user.display_name} | {yays} yays | {nays} nays")
        
        print(f"✅ Suggestion approved with final vote count: {yays} yays, {nays} nays")
        
        await interaction.response.edit_message(embed=embed, view=None)
        await interaction.followup.send(f"🎉 Suggestion by {self.author.mention} has been approved!", ephemeral=True)
        
        if self.thread:
            try:
                await self.thread.edit(locked=True, name=f"✅ APPROVED: {self.author.display_name}'s Suggestion")
            except:
                pass  # Thread might not exist or might not have permissions

    @discord.ui.button(style=discord.ButtonStyle.danger, label="❌ Deny", custom_id="deny_suggestion")
    async def deny(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Check if user has manage messages permission
        member = interaction.guild.get_member(interaction.user.id) if interaction.guild else None
        if not member or not member.guild_permissions.manage_messages:
            await interaction.response.send_message("❌ You need 'Manage Messages' permission to deny suggestions!", ephemeral=True)
            return

        if not interaction.message or not interaction.message.embeds:
            await interaction.response.send_message("❌ Error: Could not find the suggestion message.", ephemeral=True)
            return

        embed = interaction.message.embeds[0]
        
        # Fetch the message fresh to get accurate reaction counts
        try:
            fresh_message = await interaction.channel.fetch_message(interaction.message.id)
            yays = 0
            nays = 0
            
            if fresh_message.reactions:
                for reaction in fresh_message.reactions:
                    if str(reaction.emoji) == "✅":
                        yays = max(0, reaction.count - 1)  # Subtract 1 for bot's reaction
                    elif str(reaction.emoji) == "❌":
                        nays = max(0, reaction.count - 1)  # Subtract 1 for bot's reaction
        except:
            # Fallback to cached reactions if fetch fails
            yays = 0
            nays = 0
            if interaction.message.reactions:
                for reaction in interaction.message.reactions:
                    if str(reaction.emoji) == "✅":
                        yays = max(0, reaction.count - 1)
                    elif str(reaction.emoji) == "❌":
                        nays = max(0, reaction.count - 1)

        embed.color = discord.Color.red()
        embed.set_author(name=f'Suggested by {self.author}', icon_url=self.author.display_avatar.url)
        embed.set_footer(text=f"🚫 Suggestion Denied by {interaction.user.display_name} | {yays} yays | {nays} nays")
        
        await interaction.response.edit_message(embed=embed, view=None)
        await interaction.followup.send(f"🚫 Suggestion by {self.author.mention} has been denied.", ephemeral=True)
        
        if self.thread:
            try:
                await self.thread.edit(locked=True, name=f"❌ DENIED: {self.author.display_name}'s Suggestion")
            except:
                pass  # Thread might not exist or might not have permissions

class SuggestionHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        # Add persistent view for buttons to work after bot restart
        self.bot.add_view(SuggestionView(None, None))

    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignore bot messages
        if message.author.bot:
            return
        
        # Only handle messages in the suggestions channel
        if message.channel.id != SUGGESTIONS_CHANNEL_ID:
            return
        
        # Don't process commands in suggestions channel
        if message.content.startswith('!'):
            return

        try:
            author = message.author
            content = message.content

            # Create skateboarding-themed embed
            embed = discord.Embed(
                color=0x00ff00,  # Skateboard green
                description=content,
                timestamp=message.created_at
            )
            embed.set_author(name=f'🛹 Suggested by {author}', icon_url=author.display_avatar.url)
            embed.set_footer(text="React with ✅ or ❌ to vote! • Waiting for staff decision")

            # Send the embed
            sent_message = await message.channel.send(embed=embed)
            
            # Add voting reactions
            await sent_message.add_reaction("✅")
            await sent_message.add_reaction("❌")

            # Create discussion thread
            thread = await sent_message.create_thread(
                name=f"💬 {author.display_name}'s Suggestion", 
                auto_archive_duration=1440,  # 24 hours
                reason="Discussion thread for skateboarding suggestion"
            )

            # Add approve/deny buttons
            view = SuggestionView(author, thread)
            await sent_message.edit(view=view)

            # Delete original message to keep channel clean
            await message.delete()

            # Send a welcome message in the thread
            welcome_msg = f"🛹 **Discussion for {author.mention}'s suggestion!**\n\n"
            welcome_msg += "Feel free to discuss this suggestion here. Staff will review and make a decision based on community feedback!"
            await thread.send(welcome_msg)

            print(f"✅ Processed suggestion from {author.display_name}: {content[:50]}...")

        except Exception as error:
            print(f"❌ Error processing suggestion: {error}")
            try:
                await message.channel.send(f"❌ Sorry {message.author.mention}, there was an error processing your suggestion. Please try again!")
            except:
                pass

    @commands.command(name='suggest')
    async def suggest_command(self, ctx, *, suggestion):
        """Submit a suggestion using a command (alternative to posting in suggestions channel)"""
        if ctx.channel.id == SUGGESTIONS_CHANNEL_ID:
            await ctx.send("❌ Just post your suggestion directly in this channel! No need to use the command here.", delete_after=5)
            return

        suggestions_channel = self.bot.get_channel(SUGGESTIONS_CHANNEL_ID)
        if not suggestions_channel:
            await ctx.send("❌ Suggestions channel not found!")
            return

        try:
            author = ctx.author

            # Create skateboarding-themed embed
            embed = discord.Embed(
                color=0x00ff00,
                description=suggestion,
                timestamp=ctx.message.created_at
            )
            embed.set_author(name=f'🛹 Suggested by {author}', icon_url=author.display_avatar.url)
            embed.set_footer(text="React with ✅ or ❌ to vote! • Waiting for staff decision")

            # Send to suggestions channel
            sent_message = await suggestions_channel.send(embed=embed)
            
            # Add voting reactions
            await sent_message.add_reaction("✅")
            await sent_message.add_reaction("❌")

            # Create discussion thread
            thread = await sent_message.create_thread(
                name=f"💬 {author.display_name}'s Suggestion", 
                auto_archive_duration=1440,
                reason="Discussion thread for skateboarding suggestion"
            )

            # Add approve/deny buttons
            view = SuggestionView(author, thread)
            await sent_message.edit(view=view)

            # Send confirmation
            await ctx.send(f"✅ Your suggestion has been submitted to {suggestions_channel.mention}!")

            # Welcome message in thread
            welcome_msg = f"🛹 **Discussion for {author.mention}'s suggestion!**\n\n"
            welcome_msg += "Feel free to discuss this suggestion here. Staff will review and make a decision based on community feedback!"
            await thread.send(welcome_msg)

        except Exception as error:
            print(f"❌ Error with suggest command: {error}")
            await ctx.send("❌ There was an error submitting your suggestion. Please try again!")

async def setup(bot):
    await bot.add_cog(SuggestionHandler(bot))