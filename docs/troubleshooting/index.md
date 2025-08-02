# Troubleshooting Guide

Having issues with Spruce Bot? This comprehensive troubleshooting guide covers the most common problems and their solutions.

## Quick Diagnostics

Start with these basic checks:

<div class="quick-ref" markdown>

### :material-flash: **Quick Fixes**

1. **Check bot status** - Is Spruce online? (Green indicator)
2. **Verify permissions** - Does bot have required permissions?
3. **Test basic command** - Try `&ping` to confirm functionality
4. **Check role hierarchy** - Is bot role positioned correctly?

</div>

## Common Issues

### :robot: Bot Not Responding

**Symptoms:** Commands don't work, no response from bot

=== "Immediate Checks"
    - [ ] Bot shows online (green status)
    - [ ] Bot has "Send Messages" permission
    - [ ] Channel isn't muted for bot
    - [ ] Try slash commands: `/help`

=== "Advanced Solutions"
    - Use `&sync` to refresh slash commands
    - Check if bot is rate limited
    - Verify bot isn't banned/restricted
    - Restart Discord client

=== "Verification Steps"
    ```bash
    &ping                 # Check if bot responds
    /help                 # Try slash command version
    &botinfo              # Check bot status
    ```

**If still not working:** Join [support server](https://discord.gg/vMnhpAyFZm) for assistance.

### :lock: Permission Errors

**Error Messages:**
- "Missing permissions"
- "I don't have permission"
- "Role is higher than mine"

=== "Role Hierarchy Issues"
    **Problem:** "Role is higher than mine"
    
    **Solution:**
    1. Go to Server Settings → Roles
    2. Drag bot's role above target role
    3. Save changes
    4. Try command again

=== "Missing Permissions"
    **Problem:** Bot lacks specific permissions
    
    **Check Required Permissions:**
    
    | Feature | Required Permission |
    |---------|-------------------|
    | AutoRole | Manage Roles |
    | Moderation | Manage Messages, Kick/Ban Members |
    | Channels | Manage Channels |
    | Tournaments | Manage Channels, Manage Roles |

=== "Channel-Specific Permissions"
    **Problem:** Bot can't access specific channels
    
    **Solution:**
    1. Right-click channel → Edit Channel
    2. Go to Permissions tab
    3. Add bot role with required permissions
    4. Save changes

### :material-slash-forward: Slash Commands Issues

**Symptoms:** Slash commands don't appear in autocomplete

=== "Sync Commands"
    **Primary Solution:**
    ```bash
    &sync
    ```
    *Requires Administrator permission*

=== "Wait and Retry"
    - Wait 1-2 minutes after syncing
    - Restart Discord client
    - Try typing the full command

=== "Permission Check"
    Ensure bot has:
    - "Use Slash Commands" permission
    - "Send Messages" permission
    - Proper role hierarchy

### :arrows_counterclockwise: AutoRole Not Working

**Problem:** New members not receiving roles automatically

=== "Configuration Check"
    ```bash
    &autorole list        # Verify configuration
    ```
    
    **Expected Output:**
    ```
    Human Members: @Members
    Bot Members: @Bots
    ```

=== "Permission Verification"
    - [ ] Bot has "Manage Roles" permission
    - [ ] Bot role is above target roles
    - [ ] Target roles exist and aren't deleted
    - [ ] Roles aren't managed by other bots

=== "Testing AutoRole"
    1. Have a friend leave and rejoin
    2. Create a test alt account
    3. Monitor role assignment
    4. Check for error messages in logs

### :warning: Command Errors

=== "Rate Limiting"
    **Error:** "Rate limited" or "Try again later"
    
    **Solutions:**
    - Wait specified time period
    - Reduce bulk operations
    - Avoid rapid command usage
    - Use smaller batches for bulk actions

=== "Invalid Arguments"
    **Error:** "Invalid role/user/channel"
    
    **Common Causes:**
    - Typos in mentions
    - Deleted roles/users/channels
    - Incorrect ID format
    - Missing @ symbol for mentions

=== "Timeout Errors"
    **Error:** Command takes too long
    
    **Solutions:**
    - Break large operations into smaller chunks
    - Wait for current operation to complete
    - Check server boost level (affects limits)
    - Report persistent timeouts

## Feature-Specific Issues

### :trophy: Tournament Problems

=== "Setup Failures"
    **Problem:** Tournament setup command fails
    
    **Checklist:**
    - [ ] Have @tourney-mod role or Manage Channels
    - [ ] Server has enough channel slots
    - [ ] Bot has Manage Channels permission
    - [ ] Tournament name is appropriate length

=== "Registration Issues"
    **Problem:** Users can't register for tournaments
    
    **Solutions:**
    - Check if registration is open (`/tourney info`)
    - Verify proper team format
    - Ensure registration channel permissions
    - Check if fake tag detection is enabled

### :crossed_swords: Scrim Issues

=== "Time Zone Problems"
    **Problem:** Wrong registration times
    
    **Solution:**
    ```bash
    /scrim set time_zone channel:#scrim timezone:Your/Timezone
    ```
    
    **Common Timezones:**
    - `Asia/Kolkata` (IST)
    - `America/New_York` (EST)
    - `Europe/London` (GMT)

=== "Slot Management"
    **Problem:** Slot counting errors
    
    **Verification:**
    ```bash
    /scrim info channel:#scrim-register
    /scrim reserved_slots channel:#scrim
    ```

## Performance Issues

### :material-speedometer: Slow Response Times

**Causes and Solutions:**

=== "Server Overload"
    **Symptoms:** All commands slow
    
    **Solutions:**
    - Check server boost level
    - Reduce concurrent operations
    - Monitor during peak hours
    - Consider premium features

=== "Network Issues"
    **Symptoms:** Intermittent slowness
    
    **Check:**
    - Your internet connection
    - Discord server status
    - Bot hosting status

### :material-memory: Memory/Resource Issues

**Symptoms:** Bot becomes unresponsive or crashes

**Solutions:**
- Report to [support server](https://discord.gg/vMnhpAyFZm)
- Provide server size and usage details
- Note what commands were being used

## Error Code Reference

| Code | Description | Solution |
|------|-------------|----------|
| `50013` | Missing Permissions | Grant required permissions |
| `50001` | Missing Access | Add bot to channel/server |
| `50035` | Invalid Form Body | Check command syntax |
| `50007` | Cannot send messages to user | User has DMs disabled |
| `10011` | Unknown Role | Role was deleted |
| `10003` | Unknown Channel | Channel was deleted |
| `10013` | Unknown User | User left server or doesn't exist |

## Diagnostic Commands

Use these commands to gather information for support:

```bash
&botinfo              # Bot statistics and status
&serverinfo           # Server information
&ping                 # Latency and response time
&help <command>       # Specific command help
```

## Getting Help

### Self-Service Resources

1. **[Common Issues](common-issues.md)** - Most frequent problems
2. **[Permission Guide](permissions.md)** - Permission-related issues
3. **[Performance Guide](performance.md)** - Speed and reliability issues

### Community Support

- **[Discord Support Server](https://discord.gg/vMnhpAyFZm)** - Live community help
- **[GitHub Issues](https://github.com/NexinLabs/Spruce/issues)** - Bug reports
- **[Discussions](https://github.com/NexinLabs/Spruce/discussions)** - General questions

### When Reporting Issues

Include this information:

!!! note "Report Template"
    ```
    **Issue Description:** Brief description of the problem
    
    **Steps to Reproduce:**
    1. Step one
    2. Step two
    3. Step three
    
    **Expected Behavior:** What should happen
    
    **Actual Behavior:** What actually happened
    
    **Error Messages:** Exact error text (if any)
    
    **Server Info:**
    - Member count: ~X members
    - Boost level: Level X
    - Bot permissions: Administrator/Custom
    
    **Additional Context:** Any other relevant information
    ```

### Emergency Contact

For critical issues affecting many users:

- **Priority Support**: Available for premium users
- **Email**: support@nexinlabs.com
- **Discord**: Direct message @support in support server

---

**Related Guides:**
- [Permission Setup Guide](../getting-started/permissions.md)
- [Command Reference](../commands/)
- [Feature Guides](../guides/)
