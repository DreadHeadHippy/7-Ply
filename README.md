# 7-Ply Discord Bot

A **100% plug-and-play** Discord bot for skateboarding communities! Features a comprehensive ranking system, skateboard commands, and community engagement tools. No hardcoded configuration required - works on any Discord server with a simple setup command.

## ✨ Key Features

### 🏆 **15-Ply Ranking System**
- **Activity-Based Progression**: From "1-Ply Newbie" to "15-Ply Mythical"
- **Smart Point System**: Rewards messages, reactions, media sharing, and community interaction
- **Anti-Spam Protection**: Intelligent cooldowns prevent abuse while encouraging participation
- **Community Recognition**: `/1up` command lets users boost each other's progress

### 🛹 **Skateboard Commands**
- `/trick` — Perform random skateboard tricks with style points
- `/skatefact` — Learn fascinating skateboarding history and facts
- **Themed Interactions**: All commands feature authentic skateboarding culture

### 👥 **Community Features**
- **Interactive Setup**: One `/setup` command configures everything automatically
- **Welcome System**: Greet new members with skateboarding flair
- **Suggestions System**: Community-driven feature requests with voting
- **Temporary Voice Channels**: Auto-managed voice rooms for sessions

### 🔧 **Admin Tools**
- `/setup` — Complete server configuration in minutes
- **Permission Management**: Automatic role and channel setup
- **Data Persistence**: Reliable JSON-based storage
- **Error Handling**: Comprehensive logging and user feedback

## 🚀 **Plug & Play Setup**

### **1. Invite the Bot**
Ensure 7-Ply has these Discord permissions:
- Send Messages & Use Slash Commands
- Manage Channels & Manage Roles  
- View Channels & Read Message History

### **2. Run Setup**
```
/setup
```
The interactive setup wizard will:
- ✅ Create or configure a rank announcements channel
- ✅ Set proper permissions automatically
- ✅ Test configuration and provide feedback
- ✅ Guide you through any issues

### **3. Start Engaging!**
- Members earn points through natural server activity
- Use `/rank` to check progress and `/leaderboard` for community standings
- `/1up @member` lets users recognize each other's contributions

## 📊 **Point System**

| Activity | Points | Cooldown | Description |
|----------|--------|----------|-------------|
| Chat Messages | 1 | 1 minute | Regular conversation |
| Giving Reactions | 2 | 30 seconds | Engaging with content |
| Receiving Reactions | 3 | None | Quality content bonus |
| Trick Commands | 5 | 5 minutes | Using bot features |
| Media Sharing | 20 | 10 minutes | Images/videos |
| **Daily Bonus** | **10** | **Once per day (EDT)** | **First message of the day** |
| **Weekly Bonus** | **25** | **Once per week (EDT)** | **First message of the week** |
| Receiving 1ups | 25 | None | Community recognition |
| Giving 1ups | 5 | 30 minutes | Recognizing others |

## 📁 **Project Structure**

```
📦 7-Ply Discord Bot
├── 📄 bot.py                 # Main bot launcher
├── 📄 requirements.txt       # Python dependencies  
├── 📄 README.md             # Project overview
├── 📄 SETUP.md              # Detailed setup guide
├── 📄 .env                  # Environment config (create this)
├── 📂 cogs/                 # Modular bot features
│   ├── 🏆 ranking.py        # 15-ply ranking system
│   ├── ⚙️ setup.py          # Plug-and-play configuration
│   ├── 🛹 skateboard.py     # Skateboard commands & culture
│   ├── 👥 community.py      # Reaction roles & engagement
│   ├── 💬 suggestions.py    # Community feedback system
│   ├── 🔧 admin.py          # Administrative tools
│   ├── 👋 welcome.py        # New member greetings
│   └── 🔊 tempvoice.py      # Auto-managed voice channels
└── 📂 data/                 # Persistent storage
    ├── � server_configs.json  # Per-server settings
    ├── 📄 user_ranks.json      # Ranking data
    └── 📄 reaction_roles.json  # Role assignments
```

## � **Development Setup**

### **Prerequisites**
- **Python 3.8+** with pip
- **Discord Developer Account**

### **Installation**
```bash
# Clone the repository
git clone <repository-url>
cd "7-Ply"

# Install dependencies
pip install -r requirements.txt
```

### **Discord Bot Configuration**
1. **Create Bot**: [Discord Developer Portal](https://discord.com/developers/applications)
2. **Enable Intents**: Message Content + Server Members
3. **Get Token**: Copy from Bot section
4. **Invite Bot**: Generate invite with required permissions

### **Environment Setup**
Create `.env` file:
```env
DISCORD_TOKEN=your_bot_token_here
SYNC_COMMANDS=false
```

### **Launch**
```bash
# Start the bot
python bot.py

# First-time setup (sync commands globally)
# Set SYNC_COMMANDS=true in .env, restart bot, then set back to false
```

### 5. Run the Bot
```bash
python bot.py
```

## ⚙️ Command Management

### Slash Command Syncing
The bot uses smart command syncing to avoid Discord's rate limits:

- **`SYNC_COMMANDS=false`** (default) - Normal operation
- **`SYNC_COMMANDS=true`** - Sync commands to Discord

**When to sync:**
- First time running the bot
- After modifying slash commands
- After changing command permissions

**Manual sync:**
Use `!sync` (owner only) to manually sync anytime

### Debug Commands
- `!check_commands` - View all registered slash commands
## 🎮 **Usage Guide**

### **For Server Administrators**
1. **Initial Setup**: Run `/setup` after inviting the bot
2. **Monitor Activity**: Use `/leaderboard` to see community engagement
3. **Community Building**: Encourage members to use `/1up` for recognition

### **For Server Members**
1. **Check Progress**: `/rank` shows your current standing and next milestone
2. **Engage Naturally**: Earn points through normal server participation
3. **Support Others**: Use `/1up @member` to recognize contributions
4. **Have Fun**: Try `/trick` and `/skatefact` for skateboarding content

## 📋 **Available Commands**

### **🏆 Ranking System**
- `/rank [user]` - Check rank progress (yours or another member's)
- `/leaderboard` - View top-ranked server members
- `/1up @user` - Give someone a 25-point boost (30min cooldown)

### **🛹 Skateboard Culture**
- `/trick` - Perform a random skateboard trick with style
- `/skatefact` - Learn fascinating skateboarding history and facts

### **🆘 Help & Information**
- `/help` - Show all available commands based on your permissions
- `/ping` - Test bot responsiveness
- `!commands` - Show legacy prefix commands

### **⚙️ Setup & Admin**
- `/setup` - Interactive server configuration (Admin only)
- `!set_rank @user <rank>` - Manually set user ranks 1-15 (Admin only)

### **�️ Moderation Tools** (Manage Messages)
- `/say [#channel] <message>` - Make bot send messages
- `/announce [#channel] <message>` - Skateboard-themed announcements  
- `/embed [#channel] [title] <description>` - Custom embed messages

### **👥 Community Features** 
- **Welcome Messages**: Automatic skateboard-themed greetings
- **Suggestions System**: Community-driven feedback with voting  
- **Temporary Voice**: Auto-managed voice channels
- **Smart Help System**: Commands shown based on your permissions

## 🔍 **Troubleshooting**

### **Common Issues**
- **Setup fails**: Ensure you have Administrator permissions
- **Commands don't respond**: Check bot has "Use Slash Commands" permission
- **Points not updating**: Verify you're within cooldown limits
- **Ranking announcements missing**: Run `/setup` to configure channels

### **Support Resources**
- Check `SETUP.md` for detailed configuration guide
- Use `/ping` to test basic bot functionality
- Verify bot permissions match requirements above

## 🤝 **Contributing**

This bot is designed to be easily customizable:
- **Point Values**: Modify `self.point_values` in `ranking.py`
- **Rank Names**: Update `self.rank_data` for custom progression
- **Cooldowns**: Adjust `self.cooldowns` for different activity limits
- **Commands**: Add new cogs following the existing patterns

## 📄 **License**

Open source skateboarding community bot - feel free to adapt for your server's needs!

---

**🛹 Ready to build your skateboarding community? Get started with `/setup` and watch your server's engagement soar through the 15-ply ranking system!**

## Extending the Bot
- Add more skateboarding commands in `bot.py`.
- PRs and suggestions welcome!
