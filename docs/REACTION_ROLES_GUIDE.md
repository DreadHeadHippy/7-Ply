# 🛹 Reaction Roles Setup Guide

Set up automatic role assignment with skateboard-themed reaction roles!

## ⚙️ **First: Enable Reaction Roles**

Before using reaction roles, an administrator must enable this feature:

1. Run `/setup` to open the bot configuration
2. Click "🎭 Reaction Roles" to enable the feature
3. Or use `/setup_edit` and select "🎭 Reaction Roles" from the dropdown

Once enabled, you can create reaction role messages!

## 🎯 **Quick Setup**

### **Create Reaction Roles Message:**
```
/reactionroles [channel]
```

- `channel` is optional - if not specified, creates in current channel
- Requires **Manage Roles** permission
- **Choose between default skateboard roles or custom roles**

## ⚙️ **Setup Options**

When you run `/reactionroles`, you'll get two options:

### **🛹 Default Skateboard Roles**
Perfect for skateboard communities! Includes:
- 🛹 **Street Skater** - For technical street skating
- 🏁 **Vert Skater** - For bowl and halfpipe riding  
- 🎯 **Freestyle** - For creative flatground tricks
- 🌊 **Cruiser** - For casual cruising and carving
- ⚡ **Longboard** - For distance and downhill riding

### **⚙️ Custom Roles**
Create your own roles with:
- **Custom embed title and description**
- **Up to 3 custom emoji/role pairs**
- **Any emojis you want** (Discord emojis or custom server emojis)
- **Any role names you choose**

**Custom Role Format:** Use `emoji:role name` format (e.g., `🎯:Gamer`)

## ⚙️ **What This Creates**

The bot will post a beautiful embed with your chosen roles and automatically:
- **Add the reaction emojis** to the message
- **Create missing roles** if they don't exist on the server
- **Link reactions to roles** for instant assignment

### **How It Works:**
- **Add Reaction** = Get the role
- **Remove Reaction** = Lose the role
- **Automatic Role Creation** - Bot creates roles if they don't exist
- **Instant Assignment** - No delays or manual intervention needed

## 🛠️ **Managing Existing Messages**

### **Edit or Delete Messages:**
```
/reactionroles_manage
```

This command lets you:
- **📋 List all reaction role messages** in your server
- **✏️ Edit existing messages** - Change roles, emojis, titles, descriptions
- **🗑️ Delete messages** you no longer need
- **📊 View details** of each message

**Perfect for:**
- Updating roles as your community grows
- Fixing typos or changing descriptions
- Removing outdated reaction role messages
- Managing multiple reaction role messages

## 🎮 **Usage Examples**

**Admin enables and sets up default reaction roles:**
```
/setup
→ Click "🎭 Reaction Roles" to enable

/reactionroles #roles
→ Click "🛹 Use Default Skateboard Roles"
✅ Default skateboard reaction roles created in #roles!
```

**Admin sets up custom reaction roles:**
```
/reactionroles #general
→ Click "⚙️ Customize Roles"
→ Fill out the form:
   Title: "🎮 Gaming Roles"
   Role 1: "🎯:Competitive Player"
   Role 2: "🎨:Creative Builder" 
   Role 3: "🎵:Music Lover"
✅ Custom reaction roles created in #general!
```

**Members use it:**
```
User reacts with 🛹 → Gets "Street Skater" role
User reacts with 🎯 → Gets "Competitive Player" role
User removes reaction → Loses the role
```
- **Send Messages** - Post the reaction role embed
- **Add Reactions** - Add the role emojis automatically
- **Manage Roles** - Assign/remove roles from users
- **View Channels** - Access the target channel

### **For You (Admin):**
- **Manage Roles** - Required to use the `/reactionroles` command

## 🛠️ **Troubleshooting**

- **"Missing Permissions" error?** 
  - Ensure bot has **Manage Roles** permission
  - Check that bot's role is higher than the roles it's trying to assign
- **Roles not being assigned?** 
  - Verify bot can see the channel and message
  - Make sure reactions are on the correct message
- **Want multiple reaction role messages?** 
  - Just run `/reactionroles` again in different channels
  - Each message works independently

## ✨ **Pro Tips**

- **Perfect for onboarding** - Put in a welcome channel
- **Multiple setups** - Create different reaction role messages for different purposes
- **Role hierarchy** - Make sure bot's role is above the skateboard roles in server settings
- **Channel organization** - Create a dedicated #roles channel for clean organization

---
One command creates a complete self-serve role system for your skateboard community! 🛹