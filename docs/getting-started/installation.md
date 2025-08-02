# Installation Guide

Get Spruce Bot up and running on your Discord server in just a few simple steps.

## Step 1: Invite the Bot

Click the button below to invite Spruce Bot to your Discord server:

[:fontawesome-solid-plus: **Invite Spruce Bot**](https://discord.com/api/oauth2/authorize?client_id=931202912888164474&permissions=8&scope=bot%20applications.commands){ .md-button .md-button--primary }

!!! warning "Required Permissions"
    The invite link includes **Administrator** permissions for the easiest setup. You can customize permissions later if needed.

## Step 2: Select Your Server

1. **Choose Server**: Select the Discord server where you want to add Spruce Bot
2. **Confirm Permissions**: Review the permissions being granted
3. **Click "Authorize"**: Complete the invitation process

![Server Selection](../assets/images/server-selection.png)

## Step 3: Verify Installation

Once added, verify that Spruce Bot is working:

```bash
&ping
```

You should see a response showing the bot's latency and status.

## Permission Levels

Spruce Bot works with different permission levels depending on your server's needs:

=== "Administrator (Recommended)"

    **Permissions Included:**
    - All moderation permissions
    - Channel management
    - Role management
    - Message management
    - Voice channel permissions
    
    **Best For:** Full functionality, easiest setup

=== "Custom Permissions"

    **Minimum Required:**
    - Send Messages
    - Embed Links
    - Read Message History
    - Use Slash Commands
    
    **Additional for Features:**
    - Manage Roles (for AutoRole and role commands)
    - Manage Channels (for tournaments and moderation)
    - Kick/Ban Members (for moderation)
    - Manage Messages (for message deletion)

=== "Read-Only"

    **Permissions:**
    - Send Messages
    - Embed Links
    - Read Message History
    
    **Limitations:** Only utility commands will work

## Server Requirements

Before inviting Spruce Bot, ensure your server meets these requirements:

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| **Server Boost Level** | None | Level 1+ |
| **Member Count** | No limit | 10+ members |
| **Channel Count** | 5+ channels | 20+ channels |
| **Role Count** | 5+ roles | 15+ roles |

!!! info "Server Boost Benefits"
    Higher boost levels unlock additional emoji slots, higher quality voice channels, and increased file upload limits for tournament exports.

## Initial Setup Commands

After installation, run these essential commands:

### 1. Check Bot Status
```bash
&botinfo
```

### 2. Sync Slash Commands
```bash
&sync
```

### 3. View Available Commands
```bash
&help
```

### 4. Configure AutoRole (Optional)
```bash
&autorole add human @Members
&autorole add bot @Bots
```

## Troubleshooting Installation

### Bot Not Responding

**Problem:** Bot appears offline or doesn't respond to commands

**Solutions:**
- Check if bot has "Send Messages" permission in the channel
- Ensure bot role is not muted
- Try using slash commands instead: `/help`
- Verify bot is online (green status indicator)

### Permission Errors

**Problem:** "I don't have permission to do that" errors

**Solutions:**
- Move bot's role higher in the role hierarchy
- Grant specific permissions for the feature you're trying to use
- Use `&sync` to refresh slash command permissions

### Slash Commands Not Appearing

**Problem:** Slash commands don't show up when typing `/`

**Solutions:**
- Use `&sync` command (requires Administrator permission)
- Wait 1-2 minutes after syncing
- Restart Discord client
- Check bot has "Use Slash Commands" permission

## Custom Installation

For advanced users who want to customize the bot's permissions:

### Creating Custom Invite Link

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Select Spruce Bot application
3. Navigate to OAuth2 > URL Generator
4. Select scopes: `bot` and `applications.commands`
5. Choose specific permissions needed
6. Copy generated URL

### Recommended Permission Sets

=== "Tournament Organizer"
    ```
    ✅ Manage Channels
    ✅ Manage Roles
    ✅ Send Messages
    ✅ Embed Links
    ✅ Read Message History
    ✅ Use Slash Commands
    ✅ Mention Everyone
    ```

=== "Moderation Focus"
    ```
    ✅ Kick Members
    ✅ Ban Members
    ✅ Manage Messages
    ✅ Manage Channels
    ✅ Manage Roles
    ✅ Send Messages
    ✅ Embed Links
    ✅ Read Message History
    ```

=== "Basic Utility"
    ```
    ✅ Send Messages
    ✅ Embed Links
    ✅ Read Message History
    ✅ Use Slash Commands
    ✅ Add Reactions
    ```

## Post-Installation Steps

After successful installation:

1. **[Configure Permissions →](permissions.md)** - Set up proper role hierarchy
2. **[Quick Setup →](quick-setup.md)** - Configure basic features
3. **[Explore Commands →](../commands/)** - Learn about available commands

## Multiple Server Setup

If you're adding Spruce Bot to multiple servers:

!!! tip "Bulk Setup Tips"
    - Use the same permission template across servers
    - Set up similar role structures for consistency
    - Document your configuration for future reference
    - Consider creating setup scripts for common configurations

## Support

Need help with installation?

- 📚 **[Common Issues](../troubleshooting/common-issues.md)** - Solutions to frequent problems
- 💬 **[Support Server](https://discord.gg/vMnhpAyFZm)** - Get help from our community
- 📧 **Email**: support@nexinlabs.com

---

**Next Step:** [Configure Permissions →](permissions.md)
