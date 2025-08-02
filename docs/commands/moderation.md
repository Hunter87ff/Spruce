# Moderation Commands

Comprehensive moderation tools for server management and maintaining order in your Discord server.

## Quick Reference

| Command | Description | Permission Required |
|---------|-------------|-------------------|
| [`&lock [role] [channel]`](#lock) | Lock a channel for a specific role | Manage Roles |
| [`&unlock [role] [channel]`](#unlock) | Unlock a channel for a specific role | Manage Roles |
| [`&hide [role] [channel]`](#hide) | Hide a channel from a specific role | Manage Roles |
| [`&unhide [role] [channel]`](#unhide) | Unhide a channel from a specific role | Manage Roles |
| [`&clear [amount] [target]`](#clear) | Delete messages in bulk | Manage Messages |
| [`&kick <member> [reason]`](#kick) | Kick a member from the server | Kick Members |
| [`&ban <member> [reason]`](#ban) | Ban a member from the server | Ban Members |
| [`&unban <user> [reason]`](#unban) | Unban a member from the server | Ban Members |

## Overview

Spruce Bot's moderation system provides:

- **Channel Management** - Lock/unlock and hide/show channels
- **Message Management** - Bulk message deletion and filtering
- **Member Management** - Kick, ban, and unban members
- **Permission Controls** - Advanced permission management
- **Audit Logging** - Track all moderation actions

!!! tip "Best Practices"
    - Always provide clear reasons for moderation actions
    - Use channel locking during discussions that need moderation
    - Test commands in a safe environment first
    - Keep role hierarchy in mind when using moderation commands

## Channel Management

### `&lock`

Lock a channel to prevent members from sending messages.

<div class="command-syntax">
&lock [@role] [#channel]
</div>

**Parameters:**
- `role` (optional) - Role to lock the channel for (default: @everyone)
- `channel` (optional) - Channel to lock (default: current channel)

**Examples:**
```bash
&lock                           # Lock current channel for @everyone
&lock @Members                  # Lock current channel for @Members role
&lock @Members #general         # Lock #general for @Members role
```

**Bot Permissions Required:**
- Manage Roles
- Manage Channels

**User Permissions Required:**
- Manage Roles

??? example "Usage Example"
    **Locking a channel during an announcement:**
    ```bash
    &lock @Members #announcements
    ```
    
    **Bot Response:**
    ```
    🔒 Channel Locked
    #announcements has been locked for @Members
    ```

### `&unlock`

Unlock a previously locked channel.

<div class="command-syntax">
&unlock [@role] [#channel]
</div>

**Parameters:**
- `role` (optional) - Role to unlock the channel for (default: @everyone)
- `channel` (optional) - Channel to unlock (default: current channel)

**Examples:**
```bash
&unlock                         # Unlock current channel for @everyone
&unlock @Members                # Unlock current channel for @Members
&unlock @Members #general       # Unlock #general for @Members
```

### `&hide`

Hide a channel from a specific role's view.

<div class="command-syntax">
&hide [@role] [#channel]
</div>

**Parameters:**
- `role` (optional) - Role to hide the channel from (default: @everyone)
- `channel` (optional) - Channel to hide (default: current channel)

**Examples:**
```bash
&hide @Members                  # Hide current channel from @Members
&hide @Members #staff-only      # Hide #staff-only from @Members
```

### `&unhide`

Make a hidden channel visible to a specific role.

<div class="command-syntax">
&unhide [@role] [#channel]
</div>

**Parameters:**
- `role` (optional) - Role to show the channel to (default: @everyone)
- `channel` (optional) - Channel to unhide (default: current channel)

## Message Management

### `&clear`

Delete messages in bulk from a channel.

<div class="command-syntax">
&clear [amount] [@user]
</div>

**Aliases:** `&purge`

**Parameters:**
- `amount` (optional) - Number of messages to delete (default: 10, max: 50)
- `user` (optional) - Only delete messages from this user

**Examples:**
```bash
&clear                          # Delete 10 messages
&clear 25                       # Delete 25 messages
&clear 20 @spammer              # Delete 20 messages from @spammer
```

**Bot Permissions Required:**
- Manage Messages
- Read Message History

**User Permissions Required:**
- Manage Messages

**Limitations:**
- Maximum 50 messages per command
- Cannot delete messages older than 14 days
- Cannot delete pinned messages

??? example "Bulk Message Cleanup"
    **Cleaning up spam:**
    ```bash
    &clear 30 @spammer
    ```
    
    **Bot Response:**
    ```
    🗑️ Messages Deleted
    Successfully deleted 30 messages from @spammer
    ```

## Member Management

### `&kick`

Kick a member from the server.

<div class="command-syntax">
&kick &lt;@member&gt; [reason]
</div>

**Parameters:**
- `member` - Member to kick from the server
- `reason` (optional) - Reason for the kick

**Examples:**
```bash
&kick @troublemaker             # Kick with no reason
&kick @spammer "Excessive spam" # Kick with reason
```

**Bot Permissions Required:**
- Kick Members

**User Permissions Required:**
- Kick Members

**Safety Features:**
- Cannot kick members with higher roles
- Cannot kick server owner
- Logs action to audit log

### `&ban`

Ban a member from the server.

<div class="command-syntax">
&ban &lt;@member&gt; [reason]
</div>

**Parameters:**
- `member` - Member to ban from the server
- `reason` (optional) - Reason for the ban

**Examples:**
```bash
&ban @rulebreaker               # Ban with no reason
&ban @toxic "Harassment"        # Ban with reason
```

**Bot Permissions Required:**
- Ban Members

**User Permissions Required:**
- Ban Members

**Features:**
- Deletes recent messages from banned user
- Prevents user from rejoining
- Logs action with reason

### `&unban`

Unban a previously banned user.

<div class="command-syntax">
&unban &lt;user&gt; [unban_all] [reason]
</div>

**Parameters:**
- `user` - User ID or username to unban
- `unban_all` (optional) - Set to `True` to unban all users (admin only)
- `reason` (optional) - Reason for the unban

**Examples:**
```bash
&unban 123456789012345678       # Unban by user ID
&unban @username "Appeal accepted" # Unban with reason
&unban all True                 # Unban all banned users
```

!!! warning "Mass Unban"
    Using `unban_all: True` will unban up to 200 users at once. This action cannot be undone!

## Advanced Features

### Batch Operations

Lock multiple channels at once:
```bash
&lock category 123456789012345678 @Members
```

This will lock all channels in the specified category for the given role.

### Permission Management

#### `&clear_perms`

Remove all permissions from roles.

<div class="command-syntax">
&clear_perms [@role]
</div>

**Parameters:**
- `role` (optional) - Specific role to clear permissions for

**Examples:**
```bash
&clear_perms @Muted             # Clear permissions for @Muted role
&clear_perms                    # Clear permissions for all roles below bot
```

**User Permissions Required:**
- Manage Roles

!!! warning "Destructive Action"
    This command removes ALL permissions from the specified role(s). Use with extreme caution!

## Troubleshooting

### Common Issues

=== "Permission Errors"
    **Error:** "Missing permissions" or "Role hierarchy"
    
    **Solutions:**
    - Ensure bot role is above target roles
    - Grant bot the required permissions
    - Check channel-specific permissions

=== "Cannot Delete Messages"
    **Error:** "Cannot delete messages older than 14 days"
    
    **Solution:** Discord API limitation - use smaller batches or manual deletion

=== "Rate Limiting"
    **Error:** Commands becoming slow or timing out
    
    **Solutions:**
    - Wait between bulk operations
    - Use smaller batch sizes
    - Avoid rapid consecutive commands

### Error Messages

| Error | Meaning | Solution |
|-------|---------|----------|
| "Role is higher than mine" | Target role is above bot's role | Move bot role higher in hierarchy |
| "Missing permissions" | Bot lacks required permissions | Grant necessary permissions |
| "Cannot kick/ban user" | Target has higher permissions | Only kick/ban users with lower roles |
| "Message too old" | Message older than 14 days | Cannot bulk delete old messages |

## Best Practices

### Security Guidelines

- ✅ **Always provide reasons** for moderation actions
- ✅ **Use least privilege** - only grant necessary permissions
- ✅ **Test commands** in private channels first
- ✅ **Document actions** for transparency
- ✅ **Review regularly** - check moderation logs

### Workflow Recommendations

1. **Channel Management**
   - Use `&lock` during important announcements
   - `&hide` sensitive channels from general members
   - Unlock channels after discussions

2. **Message Cleanup**
   - Regular cleanup with `&clear` for active channels
   - Target specific users for spam cleanup
   - Use with moderation logs

3. **Member Management**
   - Start with warnings before kicks/bans
   - Always provide clear reasons
   - Consider temporary mutes before permanent bans

## Related Commands

- **[`&autorole`](autorole.md)** - Automatic role assignment
- **[`&role`](roles.md)** - Manual role management  
- **[`&create_roles`](roles.md#create-roles)** - Create new roles
- **[`&serverinfo`](utility.md#serverinfo)** - Server information

## Support

Need help with moderation?

- 📚 **[Troubleshooting Guide](../troubleshooting/)** - Common issues and solutions
- 💬 **[Support Server](https://discord.gg/vMnhpAyFZm)** - Get help from our community
- 📧 **Email**: support@nexinlabs.com

---

**Next:** Learn about [Role Management Commands →](roles.md)
