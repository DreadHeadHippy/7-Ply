import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
SYNC_COMMANDS = os.getenv('SYNC_COMMANDS', 'false').lower() == 'true'

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.guild_reactions = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f"🛹 7-Ply is online as {bot.user}!")
    
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

# Global error handler for command errors
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.NotOwner):
        await ctx.send("❌ This command is restricted to the bot owner only.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Missing required argument: {error.param}")
    elif isinstance(error, commands.CommandNotFound):
        # Ignore command not found errors (silent)
        pass
    else:
        # Log unexpected errors
        print(f"Unexpected command error: {error}")
        await ctx.send("❌ An unexpected error occurred.")

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

@bot.tree.command(name="ping", description="Test if slash commands work")
async def ping_test(interaction: discord.Interaction):
    """Simple test to verify slash commands are working"""
    await interaction.response.send_message("🛹 Pong! Slash commands are working!", ephemeral=True)

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
