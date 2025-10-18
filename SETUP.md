# 7-Ply Server Setup Guide

## 🚀 Adding 7-Ply to Your Server

**7-Ply** is a hosted Discord bot service - no installation required!

### Getting Started

1. **Invite the Bot**: [Invite Link Coming Soon]
   
   Required permissions:
   - Send Messages & Use Slash Commands
   - Manage Channels & Manage Roles
   - View Channels & Read Message History

2. **Configure Your Server**: Use `/setup` in any channel:
   ```
   /setup
   ```

3. **Follow Interactive Setup**: The bot will guide you through:
   - ✅ Creating/configuring the rank announcements channel
   - ✅ Setting up proper permissions
   - ✅ Testing the configuration

### Features Available After Setup

#### 🏆 Ranking System
- **15-Ply Progression**: From "1-Ply Newbie" to "15-Ply Mythical"
- **Activity-Based Points**: Earn points for messages, reactions, commands, and community interaction
- **Smart Cooldowns**: Prevents spam while rewarding genuine participation

#### 💬 Commands
- `/rank` - Check your current rank and progress
- `/rank @user` - Check another user's rank
- `/leaderboard` - See top-ranked server members
- `/1up @user` - Give someone a 25-point boost (30min cooldown)
- `/help` - See all available commands based on your permissions

#### 🎯 Point System
- **Chat Messages**: 1 point (1/minute limit)
- **Giving Reactions**: 2 points (1/30sec limit)  
- **Receiving Reactions**: 3 points
- **Using Trick Commands**: 5 points (1/5min limit)
- **Sharing Media**: 20 points (1/10min limit)
- **Daily Bonus**: 10 points (first message each day in EDT)
- **Weekly Bonus**: 25 points (first message each week in EDT)
- **Receiving 1ups**: 25 points
- **Giving 1ups**: 5 points (1/30min limit)

### 🔧 Admin Commands

#### Initial Configuration
```
/setup - Interactive setup wizard (Admin only)
```

#### Channel Management
The setup system automatically:
- Creates a "rank-ups" channel if needed
- Sets proper permissions for the bot
- Configures channel settings for optimal ranking announcements

### 🎪 Skateboard Commands

All the original skateboard-themed fun commands are still available:

- `/trick` - Perform a random skateboard trick
- `/skatefact` - Learn random skateboarding facts
- Plus welcome messages and other community features!

### 🔄 Migrating from Hardcoded Setup

If you were using an older version with hardcoded channel IDs, simply:

1. Run `/setup` to configure channels properly
2. The bot will automatically use the new configuration
3. Old data and ranks are preserved!

### 🆘 Troubleshooting

**Setup command not working?**
- Make sure you have Administrator permissions
- Ensure the bot has "Use Slash Commands" permission
- Try running `/ping` first to test basic functionality

**Rank commands not responding?**
- Run `/setup` to configure the rank channel
- Check that the bot can see and send messages in the configured channel

**Points not updating?**
- Check cooldown limits (most activities have rate limiting)
- Ensure you're in the correct server where setup was completed

### 🎉 Ready to Roll!

**7-Ply** is now ready for any Discord server! The interactive setup makes deployment simple, and the ranking system will keep your community engaged with skateboard-themed progression.

**Need help?** The bot includes helpful error messages and guidance throughout the setup process.