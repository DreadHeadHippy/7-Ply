# 🛹 Suggestions System Setup

Your skateboarding bot now has a fully automated suggestions system!

## 🎯 **How It Works**

### **For Members:**
1. **Post in Suggestions Channel** - Just type your suggestion in channel ID `1428418247291830403`
2. **OR Use Command** - Type `!suggest your suggestion here` from any channel
3. **Automatic Processing** - Your message becomes a beautiful embed with:
   - 🛹 Skateboard-themed design
   - ✅/❌ Voting reactions
   - 💬 Discussion thread
   - 🎯 Approve/Deny buttons for staff

### **For Staff:**
- **Approve** - Click the green "✅ Approved" button (requires Manage Messages permission)
- **Deny** - Click the red "❌ Denied" button (requires Manage Messages permission)
- **Review** - Check community votes before making decisions

## ⚙️ **Features**

### **Automatic Processing:**
- ✅ Creates beautiful skateboard-themed embeds
- ✅ Adds voting reactions (✅/❌)
- ✅ Creates discussion threads for each suggestion
- ✅ Adds approve/deny buttons for staff
- ✅ Deletes original message to keep channel clean
- ✅ Shows vote counts when approved/denied

### **Staff Controls:**
- 🎯 **Approve Button** - Marks suggestion as approved (green)
- 🚫 **Deny Button** - Marks suggestion as denied (red)
- 🔒 **Auto-Lock** - Locks discussion thread when decided
- 📊 **Vote Tracking** - Shows final vote counts in decision

### **Discussion Threads:**
- 💬 Auto-created for each suggestion
- 🛹 Skateboard-themed welcome message
- ⏰ 24-hour auto-archive
- 🔒 Locked when suggestion is approved/denied

## 🔧 **Required Bot Permissions**

For the suggestions system to work properly, the bot needs these permissions in the suggestions channel:

### **Essential Permissions:**
- ✅ **Send Messages** - To post suggestion embeds
- ✅ **Manage Messages** - To delete original user messages (keeps channel clean)
- ✅ **Add Reactions** - To add voting reactions (✅/❌)
- ✅ **Create Public Threads** - To create discussion threads
- ✅ **Use External Emojis** - For skateboard-themed emojis
- ✅ **Embed Links** - To create rich embeds

### **How to Set Permissions:**
1. Go to your Discord server settings
2. Navigate to Channels → Suggestions Channel
3. Add the bot role with the permissions listed above
4. Make sure "Manage Messages" is enabled so the bot can delete original messages

## 🔧 **Configuration**

Currently hardcoded in `handlers/suggestions.py`:
```python
SUGGESTIONS_CHANNEL_ID = 1428418247291830403
```

To change the channel, edit this line and restart the bot.

## 🎮 **Usage Examples**

### **Member submits suggestion:**
```
User types: "Add a daily trick challenge feature!"
Bot creates: Beautiful embed with voting and discussion thread
```

### **Staff reviews:**
```
Community votes: 15 ✅, 3 ❌
Staff clicks: "✅ Approved" button
Result: Green embed showing "Approved by StaffName | 15 yays | 3 nays"
```

## 🛠️ **Troubleshooting**

- **"Missing Permissions" error?** 
  - ✅ Make sure the bot has "Manage Messages" permission in the suggestions channel
  - ✅ Check that the bot's role is high enough in the role hierarchy
- **Buttons not working?** Make sure you have "Manage Messages" permission as a user
- **No embed created?** Check if the channel ID matches in the code
- **Commands being processed?** Commands starting with `!` are ignored in suggestions channel
- **Thread not created?** Bot needs "Create Public Threads" permission

## 🎉 **That's It!**

Your skateboard community now has a professional suggestion system that handles everything automatically! 🛹✨