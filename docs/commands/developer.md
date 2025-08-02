# Developer Commands

Administrative and development tools for server management and bot maintenance.

## Quick Reference

| Command | Description | Permission Required |
|---------|-------------|-------------------|
| [`/getprime`](#getprime) | Get premium subscription | Bot Developer |
| [`/load_cog`](#load-cog) | Load a bot cog | Bot Developer |
| [`add_role`](#add-role) | Add role to member in guild | Bot Developer |
| [`add_tester`](#add-tester) | Add user to tester list | Bot Developer |
| [`remove_tester`](#remove-tester) | Remove user from tester list | Bot Developer |
| [`system`](#system) | View system information | Bot Developer |
| [`leaveg`](#leaveg) | Leave guilds with low members | Bot Owner |
| [`get_guild`](#get-guild) | Get invite to a guild | Bot Developer |
| [`get_channel`](#get-channel) | Get channel information | Bot Developer |
| [`get_log`](#get-log) | Download error log file | Bot Developer |

## Overview

Developer commands provide:

- **System Management** - Bot system monitoring and server management
- **User Management** - Tester and developer role management  
- **Premium Services** - Subscription and payment handling
- **Guild Operations** - Server information and management
- **Cog Management** - Loading and managing bot extensions
- **Logging** - Error tracking and system logs
- **Role Management** - Cross-guild role assignment

!!! danger "Security Warning"
    Developer commands have unrestricted access to the bot and server data. These commands should only be used by trusted developers and never shared with unauthorized users.

!!! note "Access Control"
    All developer commands require the user to be in the bot's developer list, defined in the bot configuration. Some commands are restricted to the bot owner only.

## Premium Services

### `/getprime`

Purchase premium subscription plans for enhanced bot features.

<div class="command-syntax">
/getprime plan:&lt;Monthly/Quarterly/HalfYearly/Yearly/Lifetime/Custom&gt;
</div>

**Parameters:**
- `plan` - Subscription plan type

**Available Plans:**

=== "Subscription Plans"
    - **Monthly** - ₹49/month
    - **Quarterly** - ₹139/3 months  
    - **HalfYearly** - ₹229/6 months
    - **Yearly** - ₹429/year
    - **Lifetime** - ₹4,444 one-time

=== "Special Plans"
    - **Custom** - Contact support for custom pricing
    - **Developer** - ₹1 (for bot owner only)

**Examples:**
```bash
/getprime plan:Monthly
/getprime plan:Yearly
/getprime plan:Custom
```

**Features:**
- 🔗 Generates secure payment link
- 💸 Coupon code SP10 available for discount
- 🎯 Custom plans redirect to support server
- ⚡ Automatic session creation for payments

??? example "Payment Process"
    ```
    💳 Premium Subscription
    
    📦 Selected Plan: Yearly (₹429)
    💰 Discount: SP10 (10% off)
    🔗 Payment Link: [Get Prime Button]
    
    ✅ Secure payment gateway
    📧 Automatic confirmation
    🎁 Instant feature activation
    ```

## User Management

### `add_tester`

Add a user to the bot's tester list for beta features.

<div class="command-syntax">
?add_tester &lt;member&gt; [guild]
</div>

**Parameters:**
- `member` - Discord member to add
- `guild` (optional) - Specific guild for testing

**Examples:**
```bash
?add_tester @alice
?add_tester @bob 123456789
```

**Tester Features:**
- 🚀 Access to beta commands
- 🧪 Early feature testing
- 🎭 Special tester role assignment
- 📊 Database tracking
- ✅ Active status management

**Process:**
1. ✅ Validates member isn't already a tester
2. 📝 Creates tester database entry
3. ⚙️ Sets testing level (0.0 default)
4. ➕ Adds to bot's tester list
5. 🎉 Confirms addition

### `remove_tester`

Remove a user from the bot's tester list.

<div class="command-syntax">
?remove_tester &lt;member&gt;
</div>

**Parameters:**
- `member` - Discord member to remove

**Examples:**
```bash
?remove_tester @alice
```

**Effects:**
- ❌ Removes from tester list
- 🗑️ Deletes database entry
- 🚫 Removes beta access
- ✅ Confirms removal

## System Information

### `system`

Display comprehensive system performance metrics.

<div class="command-syntax">
?system
</div>

**System Information Displayed:**

=== "Memory"
    - **Total RAM** - Available memory in GB
    - **RAM Usage** - Current usage in MB and percentage
    - **Memory Status** - Performance indicators

=== "CPU"
    - **CPU Cores** - Physical and logical core count
    - **CPU Usage** - Current utilization percentage
    - **Performance** - Real-time metrics

=== "Storage"
    - **Total Disk** - Available storage in GB
    - **Disk Usage** - Used space in GB and percentage
    - **Storage Status** - Space availability

??? example "System Output"
    ```
    💻 System Information
    
    🧠 Memory:
    • Total RAM: 16.00 GB
    • RAM Usage: 8,234 MB (51.2%)
    
    ⚡ CPU:
    • CPU Cores: P: 8, L: 16
    • CPU Usage: 24.5%
    
    💾 Storage:
    • Total Disk: 512 GB
    • Disk Usage: 256 GB (50%)
    ```

## Guild Management

### `leaveg`

Leave guilds with member count below threshold (Owner only).

<div class="command-syntax">
?leaveg &lt;member_threshold&gt; [guild_id]
</div>

**Parameters:**
- `member_threshold` - Minimum member count
- `guild_id` (optional) - Specific guild to leave

**Examples:**
```bash
?leaveg 100
?leaveg 50 123456789
```

**User Permissions Required:**
- Bot Owner only (`config.OWNER_ID`)

**Functionality:**

=== "Bulk Leave"
    - Scans all guilds bot is in
    - Leaves guilds below member threshold
    - Reports each guild left
    - Shows member count for each

=== "Specific Guild"
    - Leaves specified guild by ID
    - Ignores member threshold
    - Confirms guild name and count

**Safety Features:**
- Owner-only restriction
- Cooldown: 2 uses per 20 seconds
- Guild validation
- Member count reporting

### `get_guild`

Get an invite link to a specific guild.

<div class="command-syntax">
?get_guild &lt;guild&gt;
</div>

**Parameters:**
- `guild` - Discord guild object/ID

**Examples:**
```bash
?get_guild 123456789
```

**Process:**
1. ✅ Validates guild access
2. 📝 Uses first available channel
3. 🔗 Creates temporary invite
4. 📤 Returns invite link

**Invite Settings:**
- ⏰ **Max Age** - 360 seconds (6 minutes)
- 🔢 **Max Uses** - 2 uses
- 👤 **Temporary** - Temporary membership
- 🔄 **Unique** - Not unique (reusable)

**Error Handling:**
- 🔒 Permission check for invite creation
- 🔄 Fallback for inaccessible guilds
- 💬 Clear error messages

### `get_channel`

Get detailed information about a specific channel.

<div class="command-syntax">
?get_channel &lt;channel_id&gt;
</div>

**Parameters:**
- `channel_id` - Channel ID to inspect

**Examples:**
```bash
?get_channel 123456789
```

**Information Displayed:**
- 📝 **Channel Name** - Display name
- 🆔 **Channel ID** - Unique identifier
- 📂 **Channel Type** - Text, voice, category, etc.
- 🏠 **Guild Name** - Server name
- 🆔 **Guild ID** - Server identifier
- 👥 **Member Count** - Server population

**Cooldown:** 2 uses per 20 seconds

## Cog Management

### `/load_cog`

Load a specific bot cog during runtime.

<div class="command-syntax">
/load_cog cog_name:&lt;music/moderation/utility&gt;
</div>

**Parameters:**
- `cog_name` - Cog to load (enum selection)

**Available Cogs:**
- 🎵 **music** - Music playback features
- 🛡️ **moderation** - Moderation commands
- 🔧 **utility** - Utility functions

**Examples:**
```bash
/load_cog cog_name:music
/load_cog cog_name:moderation
```

**Process:**
1. ✅ Validates user permissions
2. 🔄 Attempts to load extension
3. 📊 Reports success or failure
4. 📝 Registers new commands

**Error Handling:**
- 🔒 Permission validation
- ❌ Import error detection
- 📦 Dependency checking
- 💬 Clear error reporting

## Role Management

### `add_role`

Add a role to a member in any guild the bot has access to.

<div class="command-syntax">
?add_role &lt;guild_id&gt; &lt;member_id&gt; &lt;role_id&gt;
</div>

**Parameters:**
- `guild_id` - Target guild ID
- `member_id` - Member to assign role to
- `role_id` - Role to assign

**Examples:**
```bash
?add_role 123456789 987654321 555444333
```

**Validation Checks:**

=== "Guild Validation"
    - ✅ Guild exists and bot has access
    - 👤 Member exists in specified guild
    - 🎭 Role exists in specified guild

=== "Permission Validation"
    - 🚫 Role is not default (@everyone)
    - 🤖 Role is not bot-managed
    - 📈 Role position is below bot's top role
    - ❌ Member doesn't already have role

=== "Safety Features"
    - 📊 Hierarchy respect
    - 🔄 Duplicate prevention
    - 🔒 Permission checking
    - 💬 Clear error messages

## Database Operations

### `dbupdate`

Update configuration values in the database.

<div class="command-syntax">
?dbupdate &lt;key&gt; &lt;value&gt;
</div>

**Parameters:**
- `key` - Configuration key to update
- `value` - New value to set

**Examples:**
```bash
?dbupdate prefix !
?dbupdate feature_enabled true
```

**Safety Features:**
- 🆔 Config ID validation (87)
- ❌ Error handling and reporting
- ✅ Confirmation of updates
- 🔒 Database transaction safety

## Message Management

### `dlm`

Delete a specific message (if bot has permissions).

<div class="command-syntax">
?dlm &lt;message&gt;
</div>

**Parameters:**
- `message` - Message object to delete

**Examples:**
```bash
?dlm [message_link_or_object]
```

**Requirements:**
- 🔒 Bot must have delete permissions
- 👁️ Message must be accessible
- 🏠 Guild-only command

### `cdm`

Clear bot's DM messages with the user.

<div class="command-syntax">
?cdm &lt;amount&gt;
</div>

**Parameters:**
- `amount` - Number of messages to delete

**Examples:**
```bash
?cdm 10
?cdm 50
```

**Features:**
- 💌 DM-only command
- 🤖 Deletes only bot's messages
- ⏱️ Cooldown: 2 uses per 20 seconds
- ✅ Auto-confirmation deletion

### `edm`

Edit a message sent by the bot (Owner only).

<div class="command-syntax">
?edm &lt;message&gt; &lt;content&gt;
</div>

**Parameters:**
- `message` - Message object to edit
- `content` - New message content

**Examples:**
```bash
?edm [message] "Updated content"
```

**Restrictions:**
- 👑 Owner only command
- 🤖 Message must be sent by bot
- ✅ Validates message ownership

### `sdm`

Send a direct message to a user (Owner only).

<div class="command-syntax">
?sdm &lt;member&gt; &lt;message&gt;
</div>

**Parameters:**
- `member` - User to send DM to
- `message` - Message content

**Examples:**
```bash
?sdm @alice "Hello from the bot!"
```

**Features:**
- 👑 Owner-only restriction
- ❌ Error handling for blocked DMs
- ⏱️ Cooldown protection
- ✅ Confirmation of delivery

## Logging and Monitoring

### `get_log`

Download the bot's error log file.

<div class="command-syntax">
?get_log
</div>

**Features:**
- 📥 Downloads error.log file
- ✅ File existence validation
- 📤 Direct file upload to Discord
- ❌ Error handling for missing logs

## Special Administrative Commands

### `owners`

Assign owner role to large guild owners in support server.

<div class="command-syntax">
?owners
</div>

**Process:**
1. 🔍 Scans all guilds bot is in
2. 👑 Identifies guild owners with 1000+ members
3. 🎭 Adds special owner role in support server
4. ✅ Reports completion

**Requirements:**
- 👤 Guild owner must be in support server
- 👥 Guild must have 1000+ members
- 🎭 Support server role management

### `add_dev`

Add or remove a user from the developer list (Owner only).

<div class="command-syntax">
?add_dev &lt;member&gt;
</div>

**Parameters:**
- `member` - Discord member to add/remove

**Examples:**
```bash
?add_dev @alice
```

**Features:**
- 🔄 Toggle functionality (add if not present, remove if present)
- 👑 Owner-only restriction
- 📝 Logging of developer changes
- ✅ Confirmation messages

## Error Handling

Common developer command errors and solutions:

| Error | Cause | Solution |
|-------|-------|----------|
| "You are not allowed" | Not in developer list | Add user to bot config |
| "Guild not found" | Invalid guild ID | Check guild ID and bot access |
| "Permission denied" | Insufficient bot permissions | Grant required permissions |
| "User not found" | Invalid user ID | Verify user exists and is accessible |
| "Role hierarchy" | Role position too high | Ensure bot role is above target role |

## Best Practices

### Development Workflow

=== "Testing"
    - 🧪 Use tester accounts for beta features
    - 📊 Monitor system resources during testing
    - 📝 Check error logs regularly
    - 🔒 Test in controlled environments

=== "Management"
    - 📈 Regular system monitoring
    - 🧹 Guild cleanup for performance
    - 🎭 Role hierarchy maintenance
    - 🔍 Permission auditing

=== "Security"
    - 🔐 Limit developer access
    - 👁️ Monitor command usage
    - 🛡️ Regular security reviews
    - 📋 Audit trail maintenance

## Support

Developer command support:

- 📚 **[Development Guide](../guides/development.md)** - Setup and workflow
- 🔧 **[API Documentation](../api/)** - Technical references  
- 💬 **[Developer Discord](https://discord.gg/vMnhpAyFZm)** - Developer community
- 📧 **Email**: dev@nexinlabs.com

---

**Next:** Return to [Commands Overview →](index.md)
