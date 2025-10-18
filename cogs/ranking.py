"""
Ranking System Cog
Tracks user activity and assigns skateboard-themed ranks
"""

import json
import os
import discord
from discord.ext import commands
from discord import app_commands
import datetime
from typing import Dict, Any
import pytz
from utils.security import SecurityValidator, SecureError
from utils.secure_files import get_secure_ranking_handler
from utils.cache import bot_cache

class RankingSystem(commands.Cog):
    """User ranking and progression system"""
    
    def __init__(self, bot):
        self.bot = bot
        self.secure_handler = get_secure_ranking_handler()
        self.user_data = self.load_data()
        
        # EDT timezone
        self.edt = pytz.timezone('America/New_York')
        
        # Rank thresholds (points needed to reach each rank)
        # Designed so max rank (15-ply) takes about a year of active participation
        self.rank_data = {
            1: {"name": "1-Ply Newbie", "points": 0, "emoji": "🛹"},
            2: {"name": "2-Ply Learner", "points": 100, "emoji": "🛹"},
            3: {"name": "3-Ply Cruiser", "points": 250, "emoji": "🛹"},
            4: {"name": "4-Ply Pusher", "points": 450, "emoji": "🛹"},
            5: {"name": "5-Ply Rider", "points": 700, "emoji": "🛹"},
            6: {"name": "6-Ply Skater", "points": 1000, "emoji": "🔥"},
            7: {"name": "7-Ply Shredder", "points": 1400, "emoji": "🔥"},
            8: {"name": "8-Ply Grinder", "points": 1900, "emoji": "🔥"},
            9: {"name": "9-Ply Street", "points": 2500, "emoji": "⚡"},
            10: {"name": "10-Ply Vert", "points": 3200, "emoji": "⚡"},
            11: {"name": "11-Ply Pro", "points": 4000, "emoji": "⚡"},
            12: {"name": "12-Ply Legend", "points": 5000, "emoji": "👑"},
            13: {"name": "13-Ply Master", "points": 6200, "emoji": "👑"},
            14: {"name": "14-Ply Godlike", "points": 7600, "emoji": "👑"},
            15: {"name": "15-Ply Mythical", "points": 9200, "emoji": "💎"}
        }
        
        # Point values for different activities
        self.point_values = {
            "message": 1,           # Regular chat message
            "reaction_given": 2,    # Giving reactions to others
            "reaction_received": 3, # Receiving reactions 
            "trick_command": 5,     # Using skateboard commands
            "daily_streak": 10,     # Daily activity bonus
            "weekly_bonus": 25,     # Weekly activity bonus
            "first_post": 50,       # First post of the day bonus
            "helpful": 15,          # Answering questions/being helpful
            "media_share": 20,      # Sharing images/videos
            "oneup_received": 25,   # Being upvoted by another user
            "oneup_given": 5        # Giving an upvote to another user
        }
        
        # Rate limiting to prevent spam
        self.cooldowns = {
            "message": 60,          # 1 point per minute max
            "reaction_given": 30,   # 2 points per 30 seconds max
            "trick_command": 300,   # 5 points per 5 minutes max
            "media_share": 600,     # 20 points per 10 minutes max
            "oneup_given": 1800     # 1up every 30 minutes max
        }
    
    def get_edt_now(self) -> datetime.datetime:
        """Get current time in EDT"""
        return datetime.datetime.now(self.edt)
    
    def get_rank_channel_id(self, guild_id: int) -> int | None:
        """Get the configured rank channel ID for a server"""
        try:
            setup_cog = self.bot.get_cog('SetupSystem')
            if setup_cog:
                return setup_cog.get_rank_channel_id(guild_id)
        except Exception as e:
            print(f"Error getting rank channel: {e}")
        return None

    def load_data(self) -> Dict[str, Any]:
        """Load user ranking data using secure file handler"""
        try:
            return self.secure_handler.safe_load()
        except Exception as e:
            print(f"Error loading ranking data: {e}")
            return {}

    def save_data(self):
        """Save user ranking data using secure file handler"""
        try:
            self.secure_handler.safe_save(self.user_data)
        except Exception as e:
            print(f"Error saving ranking data: {e}")

    def get_user_data(self, user_id: int) -> Dict[str, Any]:
        """Get or create user data with caching"""
        # Try cache first for 5x faster access
        cached_data = bot_cache.get_user_data(user_id)
        if cached_data is not None:
            return cached_data
        
        # Cache miss - load from file and cache it
        user_id_str = str(user_id)
        if user_id_str not in self.user_data:
            self.user_data[user_id_str] = {
                "points": 0,
                "rank": 1,
                "messages_today": 0,
                "last_message": None,
                "last_daily_bonus": None,
                "last_weekly_bonus": None,
                "join_date": self.get_edt_now().isoformat(),
                "cooldowns": {},
                "total_messages": 0,
                "total_reactions_given": 0,
                "total_reactions_received": 0,
                "media_shares": 0,
                "oneups_given": 0,
                "oneups_received": 0
            }
        
        # Cache the data for next time
        user_data = self.user_data[user_id_str]
        bot_cache.set_user_data(user_id, user_data)
        return user_data

    def can_award_points(self, user_id: int, activity_type: str) -> bool:
        """Check if user can receive points for this activity (rate limiting)"""
        if activity_type not in self.cooldowns:
            return True
            
        user_data = self.get_user_data(user_id)
        cooldown_time = self.cooldowns[activity_type]
        
        if activity_type not in user_data["cooldowns"]:
            return True
            
        last_time = datetime.datetime.fromisoformat(user_data["cooldowns"][activity_type])
        time_diff = self.get_edt_now().replace(tzinfo=None) - last_time.replace(tzinfo=None)
        
        return time_diff.total_seconds() >= cooldown_time

    def award_points(self, user_id: int, activity_type: str, custom_amount: int = 0) -> tuple[int, bool]:
        """Award points to user and check for rank up"""
        if not self.can_award_points(user_id, activity_type):
            return 0, False
            
        user_data = self.get_user_data(user_id)
        points = custom_amount if custom_amount > 0 else self.point_values.get(activity_type, 0)
        
        old_rank = user_data["rank"]
        user_data["points"] += points
        
        # Update cooldown
        if activity_type in self.cooldowns:
            user_data["cooldowns"][activity_type] = self.get_edt_now().isoformat()
        
        # Check for rank up
        new_rank = self.calculate_rank(user_data["points"])
        ranked_up = new_rank > old_rank
        user_data["rank"] = new_rank
        
        # Invalidate cache since user data changed
        bot_cache.invalidate_user(user_id)
        
        self.save_data()
        return points, ranked_up

    def calculate_rank(self, points: int) -> int:
        """Calculate rank based on points"""
        current_rank = 1
        for rank, data in self.rank_data.items():
            if points >= data["points"]:
                current_rank = rank
            else:
                break
        return current_rank

    def get_rank_info(self, rank: int) -> Dict[str, Any]:
        """Get rank information"""
        return self.rank_data.get(rank, self.rank_data[1])

    def get_next_rank_info(self, current_rank: int) -> tuple[Dict[str, Any], int]:
        """Get next rank and points needed"""
        if current_rank >= 15:
            return self.rank_data[15], 0
        
        next_rank = current_rank + 1
        next_rank_info = self.rank_data[next_rank]
        return next_rank_info, next_rank_info["points"]

    @app_commands.command(name='rank', description='Check your current rank and progress')
    async def rank_cmd(self, interaction: discord.Interaction, user: discord.Member | None = None):
        """Display user rank information"""
        
        try:
            target_user = user or interaction.user
            
            # Validate user
            if not isinstance(target_user, (discord.Member, discord.User)):
                await interaction.response.send_message(
                    "❌ Invalid user specified!",
                    ephemeral=True
                )
                return
            
            user_data = self.get_user_data(target_user.id)
            
            current_rank = user_data["rank"]
            points = user_data["points"]
            rank_info = self.get_rank_info(current_rank)
            next_rank_info, next_rank_points = self.get_next_rank_info(current_rank)
        
            # Calculate progress to next rank
            if current_rank < 15:
                current_rank_points = self.rank_data[current_rank]["points"]
                points_needed = next_rank_points - points
                progress_points = points - current_rank_points
                total_points_needed = next_rank_points - current_rank_points
                progress_percentage = (progress_points / total_points_needed) * 100 if total_points_needed > 0 else 100
            else:
                points_needed = 0
                progress_percentage = 100
        
            # Create progress bar
            bar_length = 20
            filled_length = int(bar_length * progress_percentage / 100)
            bar = "█" * filled_length + "░" * (bar_length - filled_length)
            
            embed = discord.Embed(
                title=f"{rank_info['emoji']} {target_user.display_name}'s Rank",
                color=0x00ff88
            )
            
            embed.add_field(
                name="🏆 Current Rank",
                value=f"**{rank_info['name']}** ({current_rank}/15)",
                inline=True
            )
            
            embed.add_field(
                name="💯 Total Points",
                value=f"**{points:,}** points",
                inline=True
            )
            
            if current_rank < 15:
                embed.add_field(
                    name="📈 Next Rank",
                    value=f"{next_rank_info['emoji']} {next_rank_info['name']}",
                    inline=False
                )
                
                embed.add_field(
                    name="🎯 Progress",
                    value=f"`{bar}` {progress_percentage:.1f}%\n**{points_needed:,}** points needed",
                    inline=False
                )
            else:
                embed.add_field(
                    name="🎉 Maximum Rank Achieved!",
                    value="You've reached the highest rank possible!",
                    inline=False
                )
            
            embed.set_thumbnail(url=target_user.display_avatar.url)
            embed.set_footer(text="Keep skating to level up! 🛹")
            
            # Simple behavior: ephemeral outside #rank, normal inside #rank
            rank_channel_id = self.get_rank_channel_id(interaction.guild.id) if interaction.guild else None
            
            if interaction.channel and rank_channel_id and interaction.channel.id == rank_channel_id:
                # Used in #rank channel - respond normally
                await interaction.response.send_message(embed=embed)
            else:
                # Used outside #rank channel or no rank channel configured - respond ephemeral
                await interaction.response.send_message(embed=embed, ephemeral=True)
                
        except Exception as e:
            print(f"Error in rank command: {e}")
            await interaction.response.send_message(
                "❌ Something went wrong checking your rank! Try again in a moment.",
                ephemeral=True
            )

    @app_commands.command(name='leaderboard', description='View the top ranked members')
    async def leaderboard(self, interaction: discord.Interaction):
        """Display server leaderboard"""
        # Sort users by points
        sorted_users = sorted(
            self.user_data.items(),
            key=lambda x: x[1]["points"],
            reverse=True
        )[:10]  # Top 10
        
        embed = discord.Embed(
            title="🏆 7-Ply Leaderboard",
            description="Top ranked skaters in the community",
            color=0xffd700
        )
        
        leaderboard_text = ""
        for i, (user_id_str, data) in enumerate(sorted_users, 1):
            try:
                user = self.bot.get_user(int(user_id_str))
                if user:
                    rank_info = self.get_rank_info(data["rank"])
                    
                    # Medal emojis for top 3
                    if i == 1:
                        medal = "🥇"
                    elif i == 2:
                        medal = "🥈"
                    elif i == 3:
                        medal = "🥉"
                    else:
                        medal = f"**{i}.**"
                    
                    leaderboard_text += f"{medal} {rank_info['emoji']} **{user.display_name}**\n"
                    leaderboard_text += f"    {rank_info['name']} • {data['points']:,} points\n\n"
            except:
                continue
        
        if leaderboard_text:
            embed.description = leaderboard_text
        else:
            embed.description = "No ranked users yet. Start chatting to earn your first rank!"
        
        embed.set_footer(text="Rankings update in real-time • Use /rank to see your progress")
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='ranks', description='View all available ranks and requirements')
    async def ranks(self, interaction: discord.Interaction):
        """Display all available ranks"""
        embed = discord.Embed(
            title="🛹 Skateboard Ply Ranking System",
            description="Progress through 15 ranks by being active in the community!",
            color=0x00ff88
        )
        
        ranks_text = ""
        for rank, info in self.rank_data.items():
            ranks_text += f"{info['emoji']} **{info['name']}** - {info['points']:,} points\n"
        
        embed.add_field(
            name="🏆 All Ranks",
            value=ranks_text,
            inline=False
        )
        
        # Point earning guide
        points_guide = ""
        for activity, points in self.point_values.items():
            activity_name = activity.replace("_", " ").title()
            points_guide += f"• {activity_name}: **{points}** points\n"
        
        embed.add_field(
            name="💯 How to Earn Points",
            value=points_guide,
            inline=False
        )
        
        embed.add_field(
            name="⏱️ Rate Limits",
            value="• Messages: 1 point per minute\n• Reactions: 1 per 30 seconds\n• Commands: 1 per 5 minutes\n• Media: 1 per 10 minutes",
            inline=False
        )
        
        embed.set_footer(text="Stay active and climb the ranks! 🛹")
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='1up', description='Give another user a 1-up! (30 minute cooldown)')
    @app_commands.describe(user="The user you want to give a 1-up to")
    async def oneup(self, interaction: discord.Interaction, user: discord.Member):
        """Give another user bonus points (1-up system)"""
        
        # Can't 1-up yourself
        if user.id == interaction.user.id:
            await interaction.response.send_message("❌ You can't give yourself a 1-up! That's cheating! 🎮", ephemeral=True)
            return
        
        # Can't 1-up bots
        if user.bot:
            await interaction.response.send_message("❌ You can't give bots a 1-up! They don't need the help! 🤖", ephemeral=True)
            return
        
        # Check cooldown for the giver
        if not self.can_award_points(interaction.user.id, "oneup_given"):
            # Get time remaining
            user_data = self.get_user_data(interaction.user.id)
            last_time = datetime.datetime.fromisoformat(user_data["cooldowns"]["oneup_given"])
            time_diff = self.get_edt_now().replace(tzinfo=None) - last_time.replace(tzinfo=None)
            remaining_seconds = 1800 - time_diff.total_seconds()  # 30 minutes
            remaining_minutes = int(remaining_seconds / 60)
            
            await interaction.response.send_message(
                f"⏰ You're on cooldown! You can give another 1-up in **{remaining_minutes}** minutes.",
                ephemeral=True
            )
            return
        
        # Award points to the receiver
        receiver_points, receiver_ranked_up = self.award_points(user.id, "oneup_received")
        receiver_data = self.get_user_data(user.id)
        receiver_data["oneups_received"] += 1
        
        # Award points to the giver
        giver_points, giver_ranked_up = self.award_points(interaction.user.id, "oneup_given")
        giver_data = self.get_user_data(interaction.user.id)
        giver_data["oneups_given"] += 1
        
        # Create success embed
        embed = discord.Embed(
            title="🍄 1-Up Given!",
            description=f"{interaction.user.mention} gave {user.mention} a **1-up**!",
            color=0x00ff00,
            timestamp=self.get_edt_now()
        )
        
        receiver_rank = self.get_rank_info(receiver_data["rank"])
        giver_rank = self.get_rank_info(giver_data["rank"])
        
        embed.add_field(
            name=f"🎯 {user.display_name} Received",
            value=f"**+{receiver_points}** points\n{receiver_rank['emoji']} {receiver_rank['name']}",
            inline=True
        )
        
        embed.add_field(
            name=f"💝 {interaction.user.display_name} Earned",
            value=f"**+{giver_points}** points\n{giver_rank['emoji']} {giver_rank['name']}",
            inline=True
        )
        
        embed.add_field(
            name="📊 1-Up Stats",
            value=f"• {user.display_name}: {receiver_data['oneups_received']} received\n• {interaction.user.display_name}: {giver_data['oneups_given']} given",
            inline=False
        )
        
        embed.set_footer(text="Spread the love! Next 1-up available in 30 minutes")
        
        await interaction.response.send_message(embed=embed)
        
        # Check for rank ups and notify
        if receiver_ranked_up:
            new_rank = receiver_data["rank"]
            rank_info = self.get_rank_info(new_rank)
            
            rankup_embed = discord.Embed(
                title="🎉 Bonus Rank Up!",
                description=f"{user.mention} ranked up from the 1-up! **{rank_info['name']}**!",
                color=0xffd700
            )
            rankup_embed.add_field(
                name="New Rank",
                value=f"{rank_info['emoji']} {rank_info['name']} ({new_rank}/15)",
                inline=True
            )
            
            # Post to configured rank channel
            try:
                guild_id = interaction.guild.id if interaction.guild else None
                rank_channel_id = self.get_rank_channel_id(guild_id) if guild_id else None
                rank_channel = self.bot.get_channel(rank_channel_id) if rank_channel_id else None
                if rank_channel:
                    await rank_channel.send(embed=rankup_embed)
                else:
                    await interaction.followup.send(embed=rankup_embed, wait=False)
            except Exception as e:
                print(f"Error posting 1-up rank up to rank channel: {e}")
                await interaction.followup.send(embed=rankup_embed, wait=False)
        
        if giver_ranked_up:
            new_rank = giver_data["rank"]
            rank_info = self.get_rank_info(new_rank)
            
            rankup_embed = discord.Embed(
                title="🎉 Helper Rank Up!",
                description=f"{interaction.user.mention} ranked up from being helpful! **{rank_info['name']}**!",
                color=0xffd700
            )
            rankup_embed.add_field(
                name="New Rank",
                value=f"{rank_info['emoji']} {rank_info['name']} ({new_rank}/15)",
                inline=True
            )
            
            # Post to configured rank channel
            try:
                guild_id = interaction.guild.id if interaction.guild else None
                rank_channel_id = self.get_rank_channel_id(guild_id) if guild_id else None
                rank_channel = self.bot.get_channel(rank_channel_id) if rank_channel_id else None
                if rank_channel:
                    await rank_channel.send(embed=rankup_embed)
                else:
                    await interaction.followup.send(embed=rankup_embed, wait=False)
            except Exception as e:
                print(f"Error posting helper rank up to rank channel: {e}")
                await interaction.followup.send(embed=rankup_embed, wait=False)

    @commands.Cog.listener()
    async def on_message(self, message):
        """Award points for messages"""
        if message.author.bot:
            return
        
        user_data = self.get_user_data(message.author.id)
        
        # Award message points
        points, ranked_up = self.award_points(message.author.id, "message")
        if points > 0:
            user_data["total_messages"] += 1
        
        # Check for media attachments
        if message.attachments:
            has_media = any(
                attachment.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.mp4', '.mov', '.webm'))
                for attachment in message.attachments
            )
            if has_media:
                media_points, media_ranked_up = self.award_points(message.author.id, "media_share")
                if media_points > 0:
                    user_data["media_shares"] += 1
                    points += media_points
                    if media_ranked_up:
                        ranked_up = True
        
        # Daily bonus for first message of the day (EDT)
        today_edt = self.get_edt_now().date().isoformat()
        if user_data.get("last_daily_bonus") != today_edt:
            daily_points, daily_ranked_up = self.award_points(message.author.id, "daily_streak")
            user_data["last_daily_bonus"] = today_edt
            points += daily_points
            if daily_ranked_up:
                ranked_up = True
        
        # Weekly bonus for first message of the week (EDT)
        current_edt = self.get_edt_now()
        # Get Monday of current week as the week identifier
        week_start = current_edt - datetime.timedelta(days=current_edt.weekday())
        week_id = week_start.date().isoformat()
        
        if user_data.get("last_weekly_bonus") != week_id:
            weekly_points, weekly_ranked_up = self.award_points(message.author.id, "weekly_bonus")
            user_data["last_weekly_bonus"] = week_id
            points += weekly_points
            if weekly_ranked_up:
                ranked_up = True
        
        # Notify on rank up
        if ranked_up:
            new_rank = user_data["rank"]
            rank_info = self.get_rank_info(new_rank)
            
            embed = discord.Embed(
                title="🎉 Rank Up!",
                description=f"{message.author.mention} has reached **{rank_info['name']}**!",
                color=0xffd700
            )
            embed.add_field(
                name="New Rank",
                value=f"{rank_info['emoji']} {rank_info['name']} ({new_rank}/15)",
                inline=True
            )
            embed.add_field(
                name="Total Points",
                value=f"{user_data['points']:,} points",
                inline=True
            )
            
            # Post to configured rank channel
            try:
                guild_id = message.guild.id if message.guild else None
                rank_channel_id = self.get_rank_channel_id(guild_id) if guild_id else None
                rank_channel = self.bot.get_channel(rank_channel_id) if rank_channel_id else None
                if rank_channel:
                    await rank_channel.send(embed=embed)
                else:
                    # Fallback to current channel if rank channel not found
                    await message.channel.send(embed=embed, delete_after=30)
            except Exception as e:
                print(f"Error posting rank up to rank channel: {e}")
                await message.channel.send(embed=embed, delete_after=30)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        """Award points for giving reactions"""
        if user.bot:
            return
        
        # Award points to reaction giver
        points, ranked_up = self.award_points(user.id, "reaction_given")
        if points > 0:
            user_data = self.get_user_data(user.id)
            user_data["total_reactions_given"] += 1
        
        # Award points to reaction receiver (if not self-reaction)
        if reaction.message.author != user and not reaction.message.author.bot:
            recv_points, recv_ranked_up = self.award_points(reaction.message.author.id, "reaction_received")
            if recv_points > 0:
                recv_user_data = self.get_user_data(reaction.message.author.id)
                recv_user_data["total_reactions_received"] += 1

    @commands.command(name='set_rank')
    @commands.has_permissions(administrator=True)
    async def set_rank(self, ctx, user: discord.Member, rank: int):
        """Admin command to manually set a user's rank (1-15)"""
        
        # Validate rank range
        if rank < 1 or rank > 15:
            await ctx.send("❌ Rank must be between 1 and 15!")
            return
        
        # Get user data
        user_data = self.get_user_data(user.id)
        old_rank = user_data["rank"]
        old_rank_info = self.get_rank_info(old_rank)
        
        # Set new rank and points
        new_rank_info = self.get_rank_info(rank)
        user_data["rank"] = rank
        user_data["points"] = new_rank_info["points"]  # Set points to minimum for that rank
        
        self.save_data()
        
        # Create confirmation embed
        embed = discord.Embed(
            title="👑 Rank Manually Set",
            description=f"Admin {ctx.author.mention} set {user.mention}'s rank",
            color=0xff6600,
            timestamp=self.get_edt_now()
        )
        
        embed.add_field(
            name="📉 Previous Rank",
            value=f"{old_rank_info['emoji']} {old_rank_info['name']} ({old_rank}/15)",
            inline=True
        )
        
        embed.add_field(
            name="📈 New Rank",
            value=f"{new_rank_info['emoji']} {new_rank_info['name']} ({rank}/15)",
            inline=True
        )
        
        embed.add_field(
            name="💯 Points Set",
            value=f"{new_rank_info['points']:,} points",
            inline=True
        )
        
        embed.set_footer(text="Manual rank adjustment • Points set to rank minimum")
        
        await ctx.send(embed=embed)
        
        # Log the action
        print(f"Admin {ctx.author} ({ctx.author.id}) set {user} ({user.id}) rank to {rank}")

    @set_rank.error
    async def set_rank_error(self, ctx, error):
        """Handle set_rank command errors"""
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You need administrator permissions to use this command!")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("❌ Usage: `!set_rank @user <rank 1-15>`\nExample: `!set_rank @John 5`")
        else:
            await ctx.send(f"❌ An error occurred: {error}")
            print(f"Set rank error: {error}")

async def setup(bot):
    await bot.add_cog(RankingSystem(bot))