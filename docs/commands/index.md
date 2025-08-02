# Commands Overview

Spruce Bot offers over 90 commands across multiple categories. This section provides comprehensive documentation for all available commands.

## Command Categories

<div class="grid cards" markdown>

-   :robot: **[AutoRole Commands](autorole.md)**
    
    ---
    
    Automatic role assignment for new members
    
    - Add/remove auto roles
    - Configure for humans and bots
    - List and reset configurations

-   :shield: **[Moderation Commands](moderation.md)**
    
    ---
    
    Server management and moderation tools
    
    - Channel locking/unlocking
    - Message management
    - Member kick/ban
    - Permission controls

-   :crown: **[Role Management](roles.md)**
    
    ---
    
    Advanced role assignment and management
    
    - Bulk role operations
    - Role creation/deletion
    - Member role management

-   :wrench: **[Utility Commands](utility.md)**
    
    ---
    
    General purpose tools and information
    
    - User/server information
    - Embed creation
    - Translation and TTS

-   :trophy: **[Tournament Commands](tournaments.md)**
    
    ---
    
    Complete esports tournament management
    
    - Tournament setup
    - Registration management
    - Group creation

-   :crossed_swords: **[Scrim Commands](scrims.md)**
    
    ---
    
    Practice match organization
    
    - Scrim configuration
    - Time-based registration
    - Slot management

-   :computer: **[Developer Commands](developer.md)**
    
    ---
    
    Bot administration and debugging
    
    - System information
    - Database management
    - Debug tools

</div>

## Quick Reference

### Essential Commands

| Command | Description | Permission Required |
|---------|-------------|-------------------|
| `&help` | Show interactive help menu | None |
| `&ping` | Check bot latency | None |
| `&sync` | Sync slash commands | Administrator |
| `&botinfo` | Bot statistics | None |
| `&serverinfo` | Server information | None |

### Most Used Commands

| Command | Category | Description |
|---------|----------|-------------|
| `&autorole add human @role` | AutoRole | Add auto role for humans |
| `&lock` | Moderation | Lock current channel |
| `&clear 10` | Moderation | Delete 10 messages |
| `&role @role @user` | Roles | Give role to user |
| `/tourney setup` | Tournaments | Create tournament |

## Command Syntax

All commands follow these syntax conventions:

### Prefix Commands
```bash
&command [required] <optional> [choice1|choice2]
```

### Slash Commands
```bash
/command required_parameter:value optional_parameter:value
```

### Parameter Types

| Type | Description | Example |
|------|-------------|---------|
| `@user` | User mention | `@john#1234` |
| `@role` | Role mention | `@Members` |
| `#channel` | Channel mention | `#general` |
| `<text>` | Text input | `"Hello World"` |
| `<number>` | Numeric input | `10`, `100` |
| `<true\|false>` | Boolean choice | `true`, `false` |

## Permission Levels

Commands are organized by required permission levels:

=== "No Permissions"
    Commands that anyone can use:
    
    - `&help`, `&ping`, `&userinfo`
    - `&avatar`, `&serverinfo`, `&botinfo`
    - `&translate`, `&toss`

=== "Manage Messages"
    Basic moderation commands:
    
    - `&clear`, `&embed`
    - `&tts`

=== "Manage Roles"
    Role and permission management:
    
    - `&autorole`, `&role`, `&lock`
    - `&hide`, `&give_role`

=== "Manage Channels"
    Channel management:
    
    - `&channel_make`, `&channel_del`
    - `&create_channel`, `/tourney setup`

=== "Kick Members"
    Member moderation:
    
    - `&kick`

=== "Ban Members"
    Advanced moderation:
    
    - `&ban`, `&unban`

=== "Administrator"
    Full server management:
    
    - `&sync`, `&delete_category`
    - `&remove_members`

## Command Features

### Interactive Elements

Many commands include interactive elements:

- **Buttons**: Confirm actions, reverse operations
- **Dropdowns**: Select from multiple options
- **Modals**: Input detailed information
- **Reactions**: Navigate through pages

### Bulk Operations

Several commands support bulk operations:

- `&create_roles name1 name2 name3`
- `&del_roles @role1 @role2 @role3`
- `&give_role @role @user1 @user2 @user3`
- `&channel_make channel1 channel2 channel3`

### Safety Features

Important commands include safety measures:

- **Confirmation dialogs** for destructive actions
- **Role hierarchy checks** to prevent privilege escalation
- **Rate limiting** to prevent spam
- **Undo buttons** for reversible operations

## Command Status

| Status | Description | Example |
|--------|-------------|---------|
| :material-check: **Active** | Fully functional | Most commands |
| :material-wrench: **Maintenance** | Temporarily disabled | Music commands |
| :material-test-tube: **Beta** | Testing phase | New features |
| :material-alert: **Deprecated** | Being phased out | Old command aliases |

## Error Handling

When commands fail, Spruce Bot provides clear error messages:

### Common Error Types

=== "Permission Errors"
    ```
    ❌ Missing Permissions
    I need "Manage Roles" permission to use this command.
    ```

=== "Invalid Input"
    ```
    ❌ Invalid Role
    The role "@NonexistentRole" was not found.
    ```

=== "Rate Limiting"
    ```
    ⏱️ Rate Limited
    Please wait 30 seconds before using this command again.
    ```

=== "Bot Limitations"
    ```
    🚫 Role Hierarchy
    I cannot manage roles higher than my own.
    ```

## Getting Help

### Built-in Help System

Use the interactive help system for detailed information:

```bash
&help                    # Show main help menu
&help <command>          # Get specific command help
&help <category>         # Show category commands
```

### Command Documentation

Each command page includes:

- **Description** - What the command does
- **Usage** - Syntax and parameters
- **Examples** - Real-world usage scenarios
- **Permissions** - Required user and bot permissions
- **Troubleshooting** - Common issues and solutions

### External Resources

- **[Support Server](https://discord.gg/vMnhpAyFZm)** - Live community help
- **[GitHub Issues](https://github.com/NexinLabs/Spruce/issues)** - Bug reports
- **[Feature Requests](https://github.com/NexinLabs/Spruce/discussions)** - Suggest improvements

---

**Next Steps:**
- Explore specific [command categories](#command-categories)
- Check the [troubleshooting guide](../troubleshooting/) for common issues
- Join our [support community](https://discord.gg/vMnhpAyFZm) for help
