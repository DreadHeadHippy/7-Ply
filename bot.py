from typing import Optional
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import time
from collections import defaultdict
from utils.cache import bot_cache
from utils.security import SecurityValidator

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
SYNC_COMMANDS = os.getenv('SYNC_COMMANDS', 'false').lower() == 'true'

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.guild_reactions = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# Track bot start time for uptime calculation
bot_start_time = None

# Smart rate limiting - prevents individual spam, not bot-wide limits
user_command_usage = defaultdict(list)
suspicious_users = defaultdict(int)  # Track repeated violations

def check_rate_limit(user_id: int, command_name: str = "general", interaction: Optional[discord.Interaction] = None) -> tuple[bool, str]:
    """
    Smart rate limiting that targets individual abusers, not legitimate users
    Admins and moderators bypass rate limits entirely
    Returns: (allowed, reason_if_denied)
    """
    # Bypass rate limits for privileged users (admins/mods)
    if interaction and SecurityValidator.is_privileged_user(interaction):
        return True, ""
    
    current_time = time.time()
    user_commands = user_command_usage[user_id]
    
    # Remove commands older than 1 minute
    user_commands[:] = [cmd_time for cmd_time in user_commands if current_time - cmd_time < 60]
    
    # Aggressive rate limiting only for known spammers
    if suspicious_users[user_id] >= 3:  # 3+ violations = strict limits
        if len(user_commands) >= 10:  # Only 10 commands per minute for spammers
            return False, f"Rate limited (spam prevention): {60 - (current_time - user_commands[0]):.0f}s cooldown"
    
    # Normal users get generous limits
    elif len(user_commands) >= 30:  # 30 commands per minute for normal users
        return False, f"Slow down a bit! Try again in {60 - (current_time - user_commands[0]):.0f} seconds"
    
    # Track rapid-fire commands (potential spam)
    recent_commands = [cmd for cmd in user_commands if current_time - cmd < 10]  # Last 10 seconds
    if len(recent_commands) >= 15:  # 15+ commands in 10 seconds = suspicious
        suspicious_users[user_id] += 1
        return False, "Whoa there! That's too fast. Take a breather 🛹"
    
    # Record this command
    user_commands.append(current_time)
    return True, ""

async def cleanup_rate_limit_data():
    """Clean up old rate limit data to prevent memory bloat"""
    current_time = time.time()
    
    # Clean up user command history older than 5 minutes
    for user_id in list(user_command_usage.keys()):
        user_commands = user_command_usage[user_id]
        user_commands[:] = [cmd_time for cmd_time in user_commands if current_time - cmd_time < 300]
        
        # Remove empty entries
        if not user_commands:
            del user_command_usage[user_id]
    
    # Reset suspicious user counters after 1 hour
    for user_id in list(suspicious_users.keys()):
        if suspicious_users[user_id] > 0:
            suspicious_users[user_id] = max(0, suspicious_users[user_id] - 1)
            if suspicious_users[user_id] == 0:
                del suspicious_users[user_id]

async def validate_server_configurations():
    """Validate server configurations and provide helpful warnings"""
    validation_issues = []
    
    for guild in bot.guilds:
        guild_issues = []
        
        try:
            # Check if bot has essential permissions
            if not bot.user:
                continue
                
            bot_member = guild.get_member(bot.user.id)
            if not bot_member:
                continue
            
            permissions = bot_member.guild_permissions
            
            # Critical permissions check
            critical_perms = {
                'send_messages': 'Cannot send messages',
                'embed_links': 'Cannot send embeds (commands will fail)',
                'manage_messages': 'Cannot delete messages (slowmode won\'t work)',
                'read_message_history': 'Cannot read message history'
            }
            
            missing_critical = []
            for perm, description in critical_perms.items():
                if not getattr(permissions, perm, False):
                    missing_critical.append(f"❌ {description}")
            
            if missing_critical:
                guild_issues.extend(missing_critical)
            
            # Check for recommended permissions
            recommended_perms = {
                'manage_channels': 'Cannot create temporary voice channels',
                'manage_roles': 'Cannot manage user roles',
                'kick_members': 'Cannot use moderation features'
            }
            
            missing_recommended = []
            for perm, description in recommended_perms.items():
                if not getattr(permissions, perm, False):
                    missing_recommended.append(f"⚠️ {description}")
            
            # Only add to issues if there are critical problems
            if missing_critical:
                guild_issues.extend(missing_recommended)
            
            # Check if server has setup data
            server_data_file = f"data/servers/{guild.id}.json"
            import os
            if not os.path.exists(server_data_file):
                guild_issues.append("💡 Server not configured - run /setup to get started")
            else:
                # Validate setup data exists and is readable
                try:
                    import json
                    with open(server_data_file, 'r') as f:
                        data = json.load(f)
                    
                    # Check for essential configuration
                    if not data.get('general_channel'):
                        guild_issues.append("⚠️ No general channel configured")
                    
                    if not data.get('admin_role'):
                        guild_issues.append("💡 No admin role configured")
                        
                except (json.JSONDecodeError, FileNotFoundError):
                    guild_issues.append("❌ Server configuration file is corrupted")
            
            if guild_issues:
                validation_issues.append({
                    'guild_name': guild.name,
                    'guild_id': guild.id,
                    'issues': guild_issues
                })
                
        except Exception as e:
            validation_issues.append({
                'guild_name': guild.name,
                'guild_id': guild.id,
                'issues': [f"❌ Error checking configuration: {str(e)}"]
            })
    
    # Report validation results
    if validation_issues:
        print("\n🔍 Server Configuration Validation Results:")
        print("=" * 50)
        
        for server in validation_issues:
            print(f"\n📍 {server['guild_name']} (ID: {server['guild_id']}):")
            for issue in server['issues']:
                print(f"   {issue}")
        
        print(f"\n💡 Found issues in {len(validation_issues)} server(s). Use /setup in each server to configure properly.")
        print("=" * 50)
    else:
        print("✅ All server configurations look good!")

@bot.event
async def on_ready():
    global bot_start_time
    print(f"🛹 7-Ply is online as {bot.user}!")
    
    # Record start time for uptime tracking
    bot_start_time = time.time()
    
    # Set activity status
    activity = discord.Activity(
        type=discord.ActivityType.watching,
        name="skaters land tricks 🛹"
    )
    await bot.change_presence(activity=activity)
    
    # Start background cleanup task
    # Start background cleanup tasks
    bot.loop.create_task(background_cleanup())
    bot.loop.create_task(hourly_deep_cleanup())
    
    # Validate server configurations
    await validate_server_configurations()
    
    # Show what commands are registered
    commands_list = [cmd.name for cmd in bot.tree.get_commands()]
    print(f"📋 Registered slash commands ({len(commands_list)}): {', '.join(commands_list) if commands_list else 'None'}")
    
    # Only sync slash commands if explicitly requested
    if SYNC_COMMANDS:
        try:
            synced = await bot.tree.sync()
            print(f"✅ Synced {len(synced)} slash commands globally")
            for cmd in synced:
                print(f"   - /{cmd.name}: {getattr(cmd, 'description', 'No description')}")
        except Exception as e:
            print(f"❌ Failed to sync commands: {e}")
    else:
        print("⏭️ Skipping command sync (set SYNC_COMMANDS=true in .env to sync)")
        print("💡 Use !check_commands to see registered commands or !sync to force sync")

async def background_cleanup():
    """Background task to clean up rate limiting data and cache"""
    import asyncio
    while True:
        await asyncio.sleep(300)  # Clean up every 5 minutes
        try:
            # Clean up rate limiting data
            await cleanup_rate_limit_data()
            
            # Clean up expired cache entries
            cleaned_entries = bot_cache.cleanup_expired()
            if cleaned_entries > 0:
                print(f"🧹 Cache cleanup: removed {cleaned_entries} expired entries")
        except Exception as e:
            print(f"Error in cleanup task: {e}")

async def hourly_deep_cleanup():
    """Deep cleanup task that runs every hour for memory optimization"""
    import asyncio
    while True:
        await asyncio.sleep(3600)  # Run every hour
        try:
            # Get stats before cleanup
            stats_before = bot_cache.get_cache_stats()
            
            # Force cleanup of old cache entries (more aggressive)
            bot_cache._cleanup_old_user_data()
            bot_cache._cleanup_old_server_data()
            
            # Clean up admin command cooldowns older than 1 hour
            current_time = time.time()
            try:
                admin_cog = bot.get_cog('AdminCog')
                if admin_cog:
                    cooldowns = getattr(admin_cog, 'command_cooldowns', {})
                    if cooldowns:
                        expired_cooldowns = [
                            key for key, timestamp in cooldowns.items()
                            if current_time - timestamp > 3600  # 1 hour old
                        ]
                        for key in expired_cooldowns:
                            del cooldowns[key]
                        
                        if expired_cooldowns:
                            print(f"🕒 Cleaned {len(expired_cooldowns)} old admin command cooldowns")
            except Exception:
                pass  # Skip if admin cog not found or doesn't have cooldowns
            
            stats_after = bot_cache.get_cache_stats()
            memory_saved = stats_before['memory_estimate_mb'] - stats_after['memory_estimate_mb']
            
            print(f"🧽 Deep cleanup completed: {memory_saved:.2f}MB memory optimized")
            
        except Exception as e:
            print(f"Error in deep cleanup task: {e}")

# Diagnostic commands to help troubleshoot
@bot.command(name='sync')
@commands.is_owner()
async def sync_commands(ctx):
    """Manually sync slash commands (owner only)"""
    try:
        synced = await bot.tree.sync()
        await ctx.send(f"✅ Synced {len(synced)} slash commands")
        for cmd in synced:
            print(f"   - Synced: /{cmd.name}")
    except Exception as e:
        await ctx.send(f"❌ Failed to sync commands: {e}")

# Enhanced global error handlers
@bot.event
async def on_command_error(ctx, error):
    """Handle prefix command errors with security"""
    if isinstance(error, commands.NotOwner):
        await ctx.send("❌ This command is restricted to the bot owner only.")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to use this command.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Missing required argument: `{error.param}`")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Invalid argument provided. Please check your input.")
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"❌ Command is on cooldown. Try again in {error.retry_after:.1f} seconds.")
    elif isinstance(error, commands.CommandNotFound):
        # Silently ignore unknown commands to prevent spam
        pass
    elif isinstance(error, commands.DisabledCommand):
        await ctx.send("❌ This command is currently disabled.")
    else:
        # Log unexpected errors but don't expose details to users
        print(f"Unexpected command error in {ctx.command}: {error}")
        await ctx.send("❌ Something went wrong! Please try again later.")

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
    """Handle slash command errors with security"""
    try:
        if isinstance(error, discord.app_commands.MissingPermissions):
            await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
        elif isinstance(error, discord.app_commands.CommandOnCooldown):
            await interaction.response.send_message(f"❌ Command is on cooldown. Try again in {error.retry_after:.1f} seconds.", ephemeral=True)
        elif isinstance(error, discord.app_commands.BotMissingPermissions):
            await interaction.response.send_message("❌ I don't have the necessary permissions to run this command.", ephemeral=True)
        else:
            # Log the error but provide generic response
            print(f"Slash command error in /{interaction.command.name if interaction.command else 'unknown'}: {error}")
            
            if not interaction.response.is_done():
                await interaction.response.send_message("❌ Something went wrong! Please try again later.", ephemeral=True)
            else:
                await interaction.followup.send("❌ Something went wrong! Please try again later.", ephemeral=True)
    except Exception as e:
        # Ultimate fallback
        print(f"Error in error handler: {e}")
        pass

@bot.command(name='check_commands')
@commands.is_owner()
async def check_commands(ctx):
    """Check what slash commands are registered (owner only)"""
    commands_list = []
    for command in bot.tree.get_commands():
        desc = getattr(command, 'description', 'No description')
        commands_list.append(f"/{command.name} - {desc}")
    
    if commands_list:
        embed = discord.Embed(title="🛹 Registered Slash Commands", color=0x00ff00)
        embed.description = "\n".join(commands_list)
        await ctx.send(embed=embed)
    else:
        await ctx.send("❌ No slash commands registered!")

@bot.command(name='cache_stats')
@commands.is_owner()
async def cache_stats(ctx):
    """Show cache performance statistics (owner only)"""
    stats = bot_cache.get_cache_stats()
    
    embed = discord.Embed(
        title="📊 Cache Performance Stats", 
        color=0x00ff88,
        description="Performance monitoring for Phase 1 caching system"
    )
    
    embed.add_field(
        name="💾 Memory Usage",
        value=f"**{stats['memory_estimate_mb']} MB** estimated",
        inline=True
    )
    
    embed.add_field(
        name="👥 Users Cached",
        value=f"**{stats['users_cached']}** active users",
        inline=True
    )
    
    embed.add_field(
        name="🏠 Servers Cached", 
        value=f"**{stats['servers_cached']}** servers",
        inline=True
    )
    
    embed.add_field(
        name="📦 Static Data",
        value=f"**{stats['static_items']}** items cached",
        inline=True
    )
    
    embed.add_field(
        name="🚀 Performance Gain",
        value="**~5x faster** user lookups\n**Reduced Pi load** significantly",
        inline=False
    )
    
    embed.set_footer(text="Phase 1: In-memory caching • Target: 500 servers on Pi")
    
    await ctx.send(embed=embed)

@bot.tree.command(name="ping", description="Test bot latency and API response time")
async def ping_test(interaction: discord.Interaction):
    """Test bot latency and API response time"""
    import time
    
    # Calculate bot latency (time to process command)
    start_time = time.time()
    await interaction.response.send_message("🛹 Calculating ping...", ephemeral=True)
    bot_latency = round((time.time() - start_time) * 1000)
    
    # Get API latency (WebSocket heartbeat)
    api_latency = round(bot.latency * 1000)
    
    # Update the message with results
    await interaction.edit_original_response(
        content=f"🛹 Pong! Bot latency: **{bot_latency}ms** | API latency: **{api_latency}ms**"
    )

async def setup_bot():
    # Load all cogs from the cogs directory
    await bot.load_extension('cogs.skateboard')
    await bot.load_extension('cogs.admin')
    await bot.load_extension('cogs.community')
    await bot.load_extension('cogs.suggestions')
    await bot.load_extension('cogs.welcome')
    await bot.load_extension('cogs.tempvoice')
    await bot.load_extension('cogs.setup')
    await bot.load_extension('cogs.ranking')

if __name__ == "__main__":
    if not TOKEN or TOKEN.strip() == "" or TOKEN == "your-bot-token-here":
        print("ERROR: DISCORD_TOKEN is not set or is invalid in your .env file.")
    else:
        import asyncio
        asyncio.run(setup_bot())
        bot.run(TOKEN)
