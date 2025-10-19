# Internal Development Notes

## TODO: Enhanced Help System (Priority: High)

### Feature: Interactive Command Help with Dropdown Menu

**Goal**: Extend the current `/help` command to include detailed help for complex moderator and admin commands using Discord's interactive components.

**Implementation Plan**:
1. Modify existing `/help` command in `cogs/admin.py`
2. Add an optional dropdown select menu for detailed command help
3. Create comprehensive help content for complex commands

**UI Flow**:
```
/help → Shows current overview + "Get detailed help" dropdown
User selects command → Shows detailed usage, examples, troubleshooting
```

**Commands Requiring Detailed Help**:

### Moderator Commands (Manage Messages):
- **`/reactionroles`** - Complex setup with default vs custom options
  - Usage examples for both skateboard themes and custom roles
  - Step-by-step setup process
  - Role management best practices
  
- **`/reactionroles_manage`** - Managing existing reaction role messages
  - How to edit existing messages
  - Deleting reaction role setups
  - Troubleshooting role assignment issues
  
- **`/slowmode`** - Personal user slowmode with duration formatting
  - Duration format examples (30s, 2m, 1h)
  - Use cases and moderation guidelines
  - How to remove slowmodes
  
- **`/embed`** - Custom embed creation
  - Embed formatting options
  - Color codes and field usage
  - Channel targeting examples

### Admin Commands:
- **`/setup`** - Interactive server configuration
  - Feature selection guide
  - Channel creation process
  - Permission setup explanation
  
- **`/welcome_config`** - Welcome message configuration
  - Template variable usage ({user}, {server}, {member_count})
  - Embed vs plain text options
  - Display setting examples

**Technical Implementation**:

1. **Create help content dictionary** in `cogs/admin.py`:
```python
DETAILED_HELP = {
    "reactionroles": {
        "title": "🎭 Reaction Roles - Detailed Help",
        "description": "Create self-assignable roles with emoji reactions",
        "usage": "Detailed usage here...",
        "examples": "Example setups...",
        "troubleshooting": "Common issues..."
    },
    # ... other commands
}
```

2. **Add dropdown select menu** to existing help embed:
```python
class HelpDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Reaction Roles", value="reactionroles", emoji="🎭"),
            discord.SelectOption(label="Slowmode", value="slowmode", emoji="⏱️"),
            # ... other options
        ]
        super().__init__(placeholder="Select a command for detailed help...", options=options)
```

3. **Permission-based dropdown options**: Only show commands the user has permissions to use

4. **Rich help content**: Include usage examples, common scenarios, troubleshooting tips

**Benefits**:
- Reduces support questions
- Better user experience for complex commands
- Keeps main help clean while providing depth
- Familiar Discord UI patterns (dropdowns)

**Files to Modify**:
- `cogs/admin.py` - Main help command and new detailed help system
- Consider separate help content file if it gets large

**Timeline**: 1-2 hours implementation + testing

---

## Notes:
- Keep current `/help` functionality intact
- Make dropdown optional (users can still get overview without it)
- Focus on commands that cause the most confusion
- Consider adding "Tips & Best Practices" sections for each command