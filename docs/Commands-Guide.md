# Spruce Bot Commands Guide

[![Discord](https://img.shields.io/badge/Discord-Bot-blue)](https://discord.gg/vMnhpAyFZm)
[![Commands](https://img.shields.io/badge/90+-Commands-violet)](#)
[![Version](https://img.shields.io/badge/Version-2.1.0-green)](#)

Welcome to the comprehensive guide for Spruce Bot commands! This documentation covers all available commands, their usage, permissions, and troubleshooting tips.

## Table of Contents

1. [Getting Started](#getting-started)
2. [AutoRole Commands](#autorole-commands)
3. [Moderation Commands](#moderation-commands)
4. [Role Management Commands](#role-management-commands)
5. [Utility Commands](#utility-commands)
6. [Tournament Commands](#tournament-commands)
7. [Scrim Commands](#scrim-commands)
8. [Music Commands (Deprecated)](#music-commands-deprecated)
9. [Developer Commands](#developer-commands)
10. [Troubleshooting](#troubleshooting)

## Getting Started

### Bot Prefix
- **Default Prefix**: `&`
- **Slash Commands**: All major commands support slash commands (recommended)

### Required Permissions
Make sure Spruce has the following basic permissions:
- Send Messages
- Embed Links
- Read Message History
- Use Slash Commands

### Getting Help
- Use `&help` for the interactive help menu
- Use `&help <command>` for specific command help
- Join our [Support Server](https://discord.gg/vMnhpAyFZm) for assistance

---

## AutoRole Commands

AutoRole system automatically assigns roles to new members when they join your server.

### `/autorole add human`
**Description**: Add an auto role for human members  
**Usage**: `/autorole add human <role>`  
**Example**: `/autorole add human @Members`  
**Permissions**: Manage Roles  
**Bot Permissions**: Manage Roles  

**Troubleshooting**:
- ❌ "Role is higher than mine" → Move bot's role above the target role
- ❌ "Role not accessible" → Check if role is managed by another bot or is @everyone

### `/autorole add bot`
**Description**: Add an auto role for bot members  
**Usage**: `/autorole add bot <role>`  
**Example**: `/autorole add bot @Bots`  
**Permissions**: Manage Roles  
**Bot Permissions**: Manage Roles  

### `&autorole list`
**Description**: List all configured auto roles  
**Usage**: `&autorole list`  
**Permissions**: Manage Roles  

**Example Output**:
```
Human Members: @Members
Bot Members: @Bots
All Members: not-set
```

### `&autorole reset`
**Description**: Reset all auto role configurations  
**Usage**: `&autorole reset`  
**Permissions**: Manage Roles  

**⚠️ Warning**: This will remove all auto role settings and cannot be undone.

---

## Moderation Commands

Comprehensive moderation tools for server management.

### Channel Locking/Unlocking

#### `&lock [role] [channel]`
**Description**: Lock a channel for a specific role  
**Usage**: `&lock [@role] [#channel]`  
**Examples**: 
- `&lock` (locks current channel for @everyone)
- `&lock @Members #general`
**Permissions**: Manage Roles  
**Bot Permissions**: Manage Roles  

#### `&unlock [role] [channel]`
**Description**: Unlock a channel for a specific role  
**Usage**: `&unlock [@role] [#channel]`  
**Permissions**: Manage Roles  

#### `&lock category <category> [role]`
**Description**: Lock an entire category  
**Usage**: `&lock category <category_id> [@role]`  
**Example**: `&lock category 123456789012345678 @Members`  
**Permissions**: Manage Roles  

**Troubleshooting**:
- ❌ Rate limited → Wait and try again with fewer channels
- ❌ Missing permissions → Ensure bot has Manage Roles permission

### Channel Visibility

#### `&hide [role] [channel]`
**Description**: Hide a channel from a specific role  
**Usage**: `&hide [@role] [#channel]`  
**Permissions**: Manage Roles  

#### `&unhide [role] [channel]`
**Description**: Unhide a channel from a specific role  
**Usage**: `&unhide [@role] [#channel]`  
**Permissions**: Manage Roles  

#### `&hide category <category> [role]`
**Description**: Hide an entire category  
**Usage**: `&hide category <category_id> [@role]`  
**Permissions**: Manage Roles  

### Message Management

#### `&clear [amount] [target]`
**Aliases**: `&purge`  
**Description**: Delete messages in bulk  
**Usage**: `&clear [amount] [@user]`  
**Examples**:
- `&clear 10` (deletes 10 messages)
- `&clear 20 @user` (deletes 20 messages from specific user)
**Permissions**: Manage Messages  
**Bot Permissions**: Manage Messages  

**Limits**:
- Maximum: 50 messages per command
- Messages older than 14 days cannot be bulk deleted

### Member Management

#### `&kick <member> [reason]`
**Description**: Kick a member from the server  
**Usage**: `&kick @member [reason]`  
**Example**: `&kick @troublemaker Spamming`  
**Permissions**: Kick Members  
**Bot Permissions**: Kick Members  

#### `&ban <member> [reason]`
**Description**: Ban a member from the server  
**Usage**: `&ban @member [reason]`  
**Example**: `&ban @rulebreaker Breaking rules repeatedly`  
**Permissions**: Ban Members  
**Bot Permissions**: Ban Members  

#### `/unban <user> [unban_all] [reason]`
**Description**: Unban a member or all banned members  
**Usage**: `/unban user:@user unban_all:False reason:unbanned`  
**Options**:
- `unban_all: True` - Unbans up to 200 users at once
**Permissions**: Ban Members  
**Bot Permissions**: Ban Members  

**⚠️ Warning**: Unbanning all users processes 200 members max and may take time.

### Channel Management

#### `&channel_make <names...>`
**Aliases**: `&chm`  
**Description**: Create multiple text channels  
**Usage**: `&channel_make <name1> <name2> <name3>`  
**Example**: `&channel_make general announcements rules`  
**Permissions**: Manage Channels  
**Bot Permissions**: Manage Channels  

#### `&channel_del <channels...>`
**Aliases**: `&chd`  
**Description**: Delete multiple channels  
**Usage**: `&channel_del #channel1 #channel2`  
**Permissions**: Manage Channels  
**Bot Permissions**: Manage Channels  

#### `&create_channel <category> <names...>`
**Aliases**: `&cch`  
**Description**: Create channels in a specific category  
**Usage**: `&create_channel <category_id> <name1> <name2>`  
**Example**: `&create_channel 123456789 general memes`  
**Permissions**: Manage Channels  

#### `&delete_category <category>`
**Aliases**: `&dc`  
**Description**: Delete an entire category and all its channels  
**Usage**: `&delete_category <category_id>`  
**Permissions**: Administrator  
**Bot Permissions**: Manage Channels  

**⚠️ Warning**: This action is irreversible and deletes ALL channels in the category.

### Permission Management

#### `&clear_perms [role]`
**Description**: Remove all permissions from roles  
**Usage**: `&clear_perms [@role]`  
**Examples**:
- `&clear_perms @role` (clears specific role)
- `&clear_perms` (clears all roles below bot)
**Permissions**: Manage Roles  

---

## Role Management Commands

Advanced role management and assignment tools.

### Role Creation & Deletion

#### `&create_roles <names...>`
**Aliases**: `&croles`  
**Description**: Create multiple roles at once  
**Usage**: `&create_roles <name1> <name2> <name3>`  
**Example**: `&create_roles VIP Premium Supporter`  
**Permissions**: Manage Roles  
**Bot Permissions**: Manage Roles  

#### `&del_roles <roles...>`
**Aliases**: `&droles`  
**Description**: Delete multiple roles  
**Usage**: `&del_roles @role1 @role2`  
**Permissions**: Manage Roles  

### Role Assignment

#### `&give_role <role> <members...>`
**Aliases**: `&role`  
**Description**: Give a role to multiple members  
**Usage**: `&give_role @role @user1 @user2`  
**Example**: `&give_role @VIP @alice @bob`  
**Permissions**: Manage Roles  

**Features**:
- ⏪ Includes "Reverse Role" button to undo the action
- 🛡️ Prevents giving admin roles to multiple users
- 📝 Works with message replies

#### `&remove_role <role> <members...>`
**Description**: Remove a role from multiple members  
**Usage**: `&remove_role @role @user1 @user2`  
**Permissions**: Manage Roles  

#### `&role_all_human <role>`
**Description**: Give a role to all human members  
**Usage**: `&role_all_human @Members`  
**Permissions**: Manage Roles  

**Safety Features**:
- 🚫 Prevents assigning admin roles
- ⏱️ Includes rate limiting to avoid API limits

#### `&role_all_bot <role>`
**Description**: Give a role to all bot members  
**Usage**: `&role_all_bot @Bots`  
**Permissions**: Manage Roles  

### Role Utilities

#### `/inrole <role>`
**Description**: List all members with a specific role  
**Usage**: `/inrole role:@Members`  
**Permissions**: Manage Roles  

**Output**: 
- Embed list for small roles
- Text file for large roles (>2000 characters)

#### `&port <role1> <role2>`
**Description**: Copy all members from role1 to role2  
**Usage**: `&port @Source @Destination`  
**Example**: `&port @TempMembers @Members`  
**Permissions**: Manage Roles  

**Use Case**: Useful for transferring members between roles during server restructuring.

#### `/remove_members <role> [reason]`
**Description**: Remove a role from ALL its members  
**Usage**: `/remove_members role:@role reason:cleanup`  
**Permissions**: Administrator  

**⚠️ Warning**: This affects ALL members with the role.

### Role Display

#### `&hide_roles`
**Description**: Hide all roles from member list  
**Usage**: `&hide_roles`  
**Permissions**: Manage Roles  

#### `&unhide_roles <roles...>`
**Aliases**: `&hoist`  
**Description**: Show specific roles in member list  
**Usage**: `&unhide_roles @Moderator @Admin`  
**Permissions**: Manage Roles  

---

## Utility Commands

General purpose utility commands for server enhancement.

### User Information

#### `&avatar [user]`
**Aliases**: `&av`, `&pfp`  
**Description**: Get user's avatar  
**Usage**: `&avatar [@user]`  
**Example**: `&avatar @alice`  

**Features**:
- 🖼️ Shows animated GIFs if available
- 🔗 Provides JPG/PNG/GIF download links

#### `&banner [user]`
**Aliases**: `&bnr`  
**Description**: Get user's banner  
**Usage**: `&banner [@user]`  

#### `&userinfo [member]`
**Aliases**: `&ui`  
**Description**: Detailed user information  
**Usage**: `&userinfo [@member]`  

**Information Shown**:
- User ID, nickname, color
- Account creation and join dates
- Roles (up to 15 shown)
- Status and bot status
- Banner if available

### Server Information

#### `&serverinfo`
**Aliases**: `&si`  
**Description**: Detailed server information  
**Usage**: `&serverinfo`  

**Information Shown**:
- Server name, ID, owner
- Member count, verification level
- Channel counts by type
- Boost level, emojis, stickers
- Server roles and description

#### `&server_av [server_id]`
**Aliases**: `&sav`  
**Description**: Get server's icon  
**Usage**: `&server_av`  

#### `&member_count`
**Aliases**: `&mc`  
**Description**: Show server member count  
**Usage**: `&member_count`  

### Bot Information

#### `&botinfo`
**Aliases**: `&bi`, `&stats`, `&about`  
**Description**: Bot statistics and information  
**Usage**: `&botinfo`  

**Information Shown**:
- Server count and user count
- Bot latency
- Memory usage
- System information

#### `&ping`
**Description**: Check bot latency  
**Usage**: `&ping`  

#### `&uptime`
**Description**: How long the bot has been running  
**Usage**: `&uptime`  

### Message Tools

#### `/embed`
**Description**: Create custom embed messages  
**Usage**: `/embed title:Title description:Description color:teal`  
**Options**:
- `title` - Embed title
- `description` - Main content
- `color` - Embed color
- `footer` - Footer text
- `thumbnail` - Thumbnail image URL
- `image` - Main image URL
- `channel` - Channel to send to

#### `&embed_img <image_url> <message>`
**Aliases**: `&em`  
**Description**: Create embed with image  
**Usage**: `&embed_img https://image.url Your message here`  
**Permissions**: Manage Messages  

### Communication

#### `&tts <message>`
**Description**: Convert text to speech  
**Usage**: `&tts Hello everyone!`  
**Limits**: 150 words maximum  

**Features**:
- 🔒 Automatic profanity filtering
- 🗣️ English language with Indian accent
- 📁 Sends as audio file

#### `/translate`
**Description**: Translate text between languages  
**Usage**: `/translate from_lang:English to_lang:Spanish message:Hello World`  
**Rate Limit**: 2 uses per 50 seconds  

### Fun Commands

#### `&toss`
**Description**: Flip a coin  
**Usage**: `&toss`  

#### `&whoiss [user]`
**Description**: Random personality description  
**Usage**: `&whoiss [@user]`  

### Emoji Management

#### `&addemoji <emoji>`
**Description**: Add custom emoji to server  
**Usage**: `&addemoji :custom_emoji:`  
**Permissions**: Manage Emojis  
**Bot Permissions**: Manage Emojis  

### Utility Functions

#### `/nick <user> <nickname>`
**Description**: Change user's nickname  
**Usage**: `/nick user:@alice nickname:NewName`  
**Permissions**: Manage Nicknames  

#### `&prefix`
**Description**: Show bot's prefix  
**Usage**: `&prefix`  
**Permissions**: Administrator  

#### `&sync`
**Description**: Sync slash commands to server  
**Usage**: `&sync`  
**Permissions**: Administrator  

**Use When**:
- Slash commands not appearing
- After bot updates
- Command permissions issues

### Ticket System

#### `&setup_ticket`
**Description**: Create ticket support system  
**Usage**: Use slash command for full options  
**Permissions**: Manage Channels, Manage Roles  

**What It Creates**:
- 🎫 Ticket category
- 📝 Ticket creation channel
- 🎛️ Interactive ticket buttons
- 🔒 Proper permissions setup

**Features**:
- Automatic ticket channel creation
- Staff role configuration
- Close ticket functionality

### Links & Support

#### `&invite`
**Description**: Get bot invite link  
**Usage**: `&invite`  

#### `&vote`
**Description**: Vote for the bot  
**Usage**: `&vote`  

#### `&support`
**Description**: Join support server  
**Usage**: `&support`  

---

## Tournament Commands

Comprehensive esports tournament management system.

### Tournament Setup

#### `/tourney setup <slots> <mentions> <slot_per_group> <tournament_name>`
**Aliases**: `/tourney ts`  
**Description**: Create a new tournament  
**Usage**: `/tourney setup slots:144 mentions:4 slot_per_group:12 tournament_name:Weekly Tournament`  
**Permissions**: Manage Channels (or @tourney-mod role)  

**Parameters**:
- `slots` - Total number of teams
- `mentions` - How many members to mention per team
- `slot_per_group` - Teams per group
- `tournament_name` - Display name for tournament

**What Gets Created**:
- 📝 Registration channel
- ✅ Confirmation channel  
- 📊 Tournament management roles
- 🎮 Tournament configuration

#### `/tourney config <registration_channel>`
**Description**: View tournament configuration  
**Usage**: `/tourney config channel:#register-here`  

### Registration Management

#### `/tourney start <registration_channel>`
**Description**: Start tournament registration  
**Usage**: `/tourney start channel:#register-here`  
**Permissions**: @tourney-mod  

#### `/tourney pause <registration_channel>`
**Description**: Pause tournament registration  
**Usage**: `/tourney pause channel:#register-here`  
**Permissions**: @tourney-mod  

#### `/tourney add_slot <channel> <member> <team_name>`
**Description**: Manually add a team slot  
**Usage**: `/tourney add_slot channel:#register member:@captain team_name:Team Alpha`  
**Permissions**: @tourney-mod  

#### `/tourney cancel_slot <channel> <member> [reason]`
**Description**: Cancel a team's registration  
**Usage**: `/tourney cancel_slot channel:#register member:@captain reason:Rule violation`  
**Permissions**: @tourney-mod  

#### `/tourney change_slot <exact_team_name> <new_member>`
**Description**: Change team captain (use by replying to group message)  
**Usage**: Reply to group message with `/tourney change_slot team_name:TEAM ALPHA new_member:@newcaptain`  
**Permissions**: @tourney-mod  

**Important**: Must reply to the exact group message and use exact team name.

### Tournament Organization

#### `/tourney auto_group <registration_channel>`
**Description**: Automatically create tournament groups  
**Usage**: `/tourney auto_group channel:#register-here`  
**Permissions**: @tourney-mod  

**Requirements**:
- Registration must be closed
- Confirmation channel should be clean (no extra messages)
- Sufficient registered teams

**What It Does**:
- 📊 Creates group channels
- 👥 Assigns teams to groups
- 🏷️ Sets up group roles
- 📱 Sends group information

#### `/tourney publish <channel> <prize>`
**Description**: Publish tournament announcement  
**Usage**: `/tourney publish channel:#register-here prize:$1000 USD`  
**Permissions**: @tourney-mod  

### Tournament Features

#### `/tourney faketag <registration_channel>`
**Description**: Toggle fake tag detection  
**Usage**: `/tourney faketag channel:#register-here`  
**Permissions**: @tourney-mod  

**Purpose**: Prevents users from registering with fake/non-existent team tags.

#### `/tourney girls_lobby <vc_amount>`
**Description**: Create voice channels for female participants  
**Usage**: `/tourney girls_lobby vc_amount:12`  
**Permissions**: @tourney-mod  

#### `/tourney export <registration_channel>`
**Description**: Export tournament data  
**Usage**: `/tourney export channel:#register-here`  
**Permissions**: @tourney-mod  

**Output**: CSV file with all registered teams and member information.

### Tournament Utilities

#### `/tourney tourneys`
**Description**: List all active tournaments  
**Usage**: `/tourney tourneys`  

#### `/tourney tconfig`
**Aliases**: `/tourney tc`  
**Description**: View all tournament configurations  
**Usage**: `/tourney tconfig`  

### Tournament Logging

#### `/tourney set log <channel>`
**Description**: Set tournament log channel  
**Usage**: `/tourney set log channel:#tournament-logs`  
**Permissions**: Administrator  

**Logged Events**:
- Team registrations
- Slot cancellations
- Tournament state changes
- Group assignments

---

## Scrim Commands

Advanced scrim (practice match) management system.

### Scrim Creation & Management

#### `/scrim create`
**Description**: Create a new scrim configuration  
**Usage**: `/scrim create`  
**Permissions**: Manage Channels (or @scrim-mod role)  

**Interactive Setup**: The bot will guide you through:
- Registration channel selection
- Total slots configuration
- Time zone settings
- Role configurations

#### `/scrim delete <registration_channel>`
**Description**: Delete a scrim configuration  
**Usage**: `/scrim delete channel:#scrim-register`  
**Permissions**: @scrim-mod  

**⚠️ Warning**: This permanently deletes the scrim configuration.

#### `/scrim toggle <registration_channel>`
**Description**: Enable/disable a scrim  
**Usage**: `/scrim toggle channel:#scrim-register`  
**Permissions**: @scrim-mod  

### Scrim Configuration

#### `/scrim set total_slots <channel> <slots>`
**Description**: Set total available slots  
**Usage**: `/scrim set total_slots channel:#scrim slots:20`  
**Permissions**: @scrim-mod  

#### `/scrim set open_time <channel> <time>`
**Description**: Set registration opening time  
**Usage**: `/scrim set open_time channel:#scrim time:10:00 AM`  
**Permissions**: @scrim-mod  

#### `/scrim set close_time <channel> <time>`
**Description**: Set registration closing time  
**Usage**: `/scrim set close_time channel:#scrim time:4:00 PM`  
**Permissions**: @scrim-mod  

#### `/scrim set time_zone <channel> <timezone>`
**Description**: Set scrim timezone  
**Usage**: `/scrim set time_zone channel:#scrim timezone:Asia/Kolkata`  
**Permissions**: @scrim-mod  

**Supported Timezones**:
- Asia/Kolkata (IST)
- America/New_York (EST)
- Europe/London (GMT)
- And more...

### Channel Configuration

#### `/scrim set reg_channel <old_channel> <new_channel>`
**Description**: Change registration channel  
**Usage**: `/scrim set reg_channel old_channel:#old-register new_channel:#new-register`  
**Permissions**: @scrim-mod  

#### `/scrim set slot_channel <scrim_channel> <slot_channel>`
**Description**: Set slot display channel  
**Usage**: `/scrim set slot_channel scrim_channel:#register slot_channel:#slots`  
**Permissions**: @scrim-mod  

#### `/scrim set idp_channel <scrim_channel> <idp_channel>`
**Description**: Set ID proof submission channel  
**Usage**: `/scrim set idp_channel scrim_channel:#register idp_channel:#id-proof`  
**Permissions**: @scrim-mod  

### Role Configuration

#### `/scrim set ping_role <channel> <role>`
**Description**: Set role to ping for announcements  
**Usage**: `/scrim set ping_role channel:#scrim role:@Scrim-Updates`  
**Permissions**: @scrim-mod  

#### `/scrim set idp_role <channel> <role>`
**Description**: Set role given after ID proof verification  
**Usage**: `/scrim set idp_role channel:#scrim role:@Verified`  
**Permissions**: @scrim-mod  

#### `/scrim set manager <channel> <role>`
**Description**: Set scrim manager role  
**Usage**: `/scrim set manager channel:#scrim role:@Scrim-Manager`  
**Permissions**: @scrim-mod  

### Scrim Operations

#### `/scrim start <registration_channel>`
**Description**: Start scrim registration  
**Usage**: `/scrim start channel:#scrim-register`  
**Permissions**: @scrim-mod  

#### `/scrim info <registration_channel>`
**Description**: View scrim information  
**Usage**: `/scrim info channel:#scrim-register`  

#### `/scrim list`
**Description**: List all configured scrims  
**Usage**: `/scrim list`  

### Slot Management

#### `/scrim add slot <channel> <member> <team_name>`
**Description**: Manually add a scrim slot  
**Usage**: `/scrim add slot channel:#scrim member:@captain team_name:Alpha Squad`  
**Permissions**: @scrim-mod  

#### `/scrim cancel_slot <channel> <member> [reason]`
**Description**: Cancel a team's scrim slot  
**Usage**: `/scrim cancel_slot channel:#scrim member:@captain reason:No show`  
**Permissions**: @scrim-mod  

#### `/scrim reserved_slots <channel>`
**Description**: View reserved slots  
**Usage**: `/scrim reserved_slots channel:#scrim`  

#### `/scrim add reserved_slots <channel> <slots>`
**Description**: Add reserved slots  
**Usage**: `/scrim add reserved_slots channel:#scrim slots:5`  
**Permissions**: @scrim-mod  

#### `/scrim remove reserved_slots <channel> <slots>`
**Description**: Remove reserved slots  
**Usage**: `/scrim remove reserved_slots channel:#scrim slots:2`  
**Permissions**: @scrim-mod  

### Scrim Features

#### `/scrim audit <channel>`
**Description**: Audit scrim registrations  
**Usage**: `/scrim audit channel:#scrim-register`  
**Permissions**: @scrim-mod  

**What It Checks**:
- Duplicate registrations
- Invalid team formats
- Role requirements
- Channel permissions

#### `/scrim idp <channel> <member>`
**Description**: Process ID proof submission  
**Usage**: `/scrim idp channel:#scrim member:@player`  
**Permissions**: @scrim-mod  

#### `/scrim setup group <channel> <slots_per_group>`
**Description**: Setup scrim groups  
**Usage**: `/scrim setup group channel:#scrim slots_per_group:4`  
**Permissions**: @scrim-mod  

### Scrim Settings

#### `/scrim set mentions <channel> <count>`
**Description**: Set how many members to mention per team  
**Usage**: `/scrim set mentions channel:#scrim count:4`  
**Permissions**: @scrim-mod  

#### `/scrim set fake_tag <channel> <enabled>`
**Description**: Toggle fake tag detection  
**Usage**: `/scrim set fake_tag channel:#scrim enabled:True`  
**Permissions**: @scrim-mod  

### Scrim Logging

#### `/scrim set log <channel>`
**Description**: Set scrim log channel  
**Usage**: `/scrim set log channel:#scrim-logs`  
**Permissions**: Administrator  

**Logged Events**:
- Registration openings/closings
- Team registrations
- Slot cancellations
- ID proof submissions

---

## Music Commands (Deprecated)

**⚠️ Notice**: Music functionality is currently disabled due to maintenance.

The following commands were available but are temporarily unavailable:

### Playback Controls
- `&play <song>` - Play a song
- `&pause` - Pause playback
- `&resume` - Resume playback
- `&stop` - Stop playback
- `&skip` - Skip current song

### Queue Management
- `&queue` - View song queue
- `&loop` - Toggle loop mode

### Voice Channel
- `&join` - Join voice channel
- `&leave` - Leave voice channel

### Audio Effects
- `&volume <1-200>` - Set volume
- `&pitch <0.5-2.0>` - Adjust pitch
- `&speed <0.5-2.0>` - Adjust speed
- `&nightcore` - Enable nightcore mode

### Streaming
- `&spotify <playlist_url>` - Play Spotify playlist

**Troubleshooting (When Available)**:
- Ensure bot has Connect and Speak permissions
- Join a voice channel before using commands
- Check if voice channel isn't full or restricted

---

## Developer Commands

**🔒 Access**: These commands are restricted to bot developers and administrators.

### System Information

#### `&system`
**Description**: View system resource usage  
**Usage**: `&system`  
**Access**: Developers only  

**Information Shown**:
- CPU usage and core count
- RAM usage and total
- Disk usage and space
- System performance metrics

### Guild Management

#### `&leaveg <member_count> [guild_id]`
**Description**: Leave servers with fewer members  
**Usage**: `&leaveg 50` (leaves servers with <50 members)  
**Access**: Bot owner only  

#### `&get_guild <guild_id>`
**Description**: Get invite link for a server  
**Usage**: `&get_guild 123456789012345678`  
**Access**: Developers only  

#### `&get_channel <channel_id>`
**Description**: Get information about a channel  
**Usage**: `&get_channel 123456789012345678`  
**Access**: Developers only  

### Database Management

#### `&dbupdate <key> <value>`
**Aliases**: `&dbu`  
**Description**: Update database configuration  
**Usage**: `&dbupdate feature_enabled true`  
**Access**: Developers only  

### Message Management

#### `&dlm <message>`
**Description**: Delete a specific message  
**Usage**: `&dlm <message_link>`  
**Access**: Developers only  

#### `&edm <message> <new_content>`
**Description**: Edit a bot message  
**Usage**: `&edm <message_link> New content here`  
**Access**: Bot owner only  

#### `&sdm <user> <message>`
**Description**: Send direct message to user  
**Usage**: `&sdm @user Important announcement`  
**Access**: Bot owner only  

#### `&cdm <amount>`
**Description**: Clear bot's DM messages  
**Usage**: `&cdm 10`  
**Access**: Developers only (DM only)  

### User Management

#### `&add_tester <member> [guild]`
**Description**: Add user to tester list  
**Usage**: `&add_tester @user`  
**Access**: Developers only  

#### `&remove_tester <member>`
**Description**: Remove user from tester list  
**Usage**: `&remove_tester @user`  
**Access**: Developers only  

#### `&add_dev <member>`
**Description**: Add/remove developer access  
**Usage**: `&add_dev @user`  
**Access**: Bot owner only  

### Premium System

#### `/getprime <plan>`
**Description**: Generate premium subscription link  
**Usage**: `/getprime plan:Monthly`  
**Access**: Developers only  

**Plans Available**:
- Monthly ($49)
- Quarterly ($139)
- Half-Yearly ($229)
- Yearly ($429)
- Lifetime ($4444)
- Custom (contact support)

### Cog Management

#### `/load_cog <cog_name>`
**Description**: Load a bot extension  
**Usage**: `/load_cog cog_name:music`  
**Access**: Developers only  

**Available Cogs**:
- music
- moderation
- utility

#### `/add_role <guild_id> <member_id> <role_id>`
**Description**: Add role to member in any server  
**Usage**: `/add_role guild_id:123 member_id:456 role_id:789`  
**Access**: Developers only  

### Logging

#### `&get_log`
**Description**: Download error log file  
**Usage**: `&get_log`  
**Access**: Developers only  

#### `&owners`
**Description**: Give owner role to large server owners  
**Usage**: `&owners`  
**Access**: Developers only  

---

## Troubleshooting

### Common Issues

#### Bot Not Responding
**Symptoms**: Commands don't work, no response from bot  
**Solutions**:
1. ✅ Check bot is online (green status)
2. ✅ Verify bot has "Send Messages" permission
3. ✅ Try using slash commands instead of prefix
4. ✅ Check if bot is muted or restricted
5. ✅ Use `&sync` to refresh slash commands

#### Permission Errors
**Symptoms**: "Missing permissions" or "I don't have permission"  
**Solutions**:
1. ✅ Check bot role position (must be above managed roles)
2. ✅ Verify specific permission requirements
3. ✅ Ensure bot has permission in the specific channel
4. ✅ Check role hierarchy for user permissions

#### Slash Commands Not Showing
**Symptoms**: Slash commands don't appear in autocomplete  
**Solutions**:
1. ✅ Use `&sync` command (requires Administrator)
2. ✅ Wait 1-2 minutes after syncing
3. ✅ Restart Discord client
4. ✅ Check bot has "Use Slash Commands" permission

#### Role Management Issues
**Error**: "Role is higher than mine"  
**Solution**: Move bot's role above the target role in server settings

**Error**: "Role not accessible"  
**Solutions**:
- Check if role is managed by another bot
- Verify role isn't @everyone
- Ensure role exists and wasn't deleted

#### Rate Limiting
**Symptoms**: Commands work slowly or timeout  
**Solutions**:
1. ✅ Reduce bulk operations (use smaller batches)
2. ✅ Wait between commands
3. ✅ Avoid rapid consecutive commands
4. ✅ Check server boost status (affects limits)

### AutoRole Issues

**Problem**: AutoRole not working for new members  
**Checklist**:
- [ ] AutoRole is configured (`&autorole list`)
- [ ] Bot has "Manage Roles" permission
- [ ] Bot role is above target role
- [ ] Role isn't higher than bot's position
- [ ] Role isn't managed by another bot

### Tournament/Scrim Issues

**Problem**: Tournament setup fails  
**Solutions**:
1. ✅ Ensure you have @tourney-mod role or Manage Channels
2. ✅ Check bot has Manage Channels permission
3. ✅ Verify sufficient server boost for channel limits
4. ✅ Make sure tournament name is appropriate length

**Problem**: Registration not working  
**Solutions**:
- Check registration channel permissions
- Verify tournament is started (`/tourney start`)
- Ensure proper team format is being used
- Check if fake tag detection is causing issues

**Problem**: Auto group creation fails  
**Solutions**:
- Registration must be closed first
- Confirm channel must be clean (no extra messages)
- Ensure sufficient registered teams
- Check bot permissions for channel creation

### Music Issues (When Available)

**Problem**: Music commands not working  
**Note**: Music is currently disabled for maintenance

**Common Solutions**:
- Join voice channel before using commands
- Check bot has Connect/Speak permissions
- Verify voice channel isn't full
- Use YouTube links instead of other sources

### Support Resources

#### Getting Help
1. **Documentation**: Read this guide thoroughly
2. **Support Server**: [Join here](https://discord.gg/vMnhpAyFZm)
3. **Help Command**: Use `&help <command>` for specific help
4. **Community**: Ask other users in support server

#### Reporting Bugs
When reporting issues, include:
- 📋 Exact command used
- ❌ Error message received
- 🏗️ Server settings/permissions
- 📱 Steps to reproduce
- 🖼️ Screenshots if helpful

#### Feature Requests
- 💡 Use support server's suggestion channel
- 📝 Explain use case and benefits
- 🗳️ Vote on existing suggestions
- 💎 Consider premium features

### Best Practices

#### Server Setup
1. 🔧 Set bot role high in hierarchy
2. 🛡️ Give necessary permissions only
3. 📝 Create dedicated channels for logs
4. 👥 Train moderators on commands
5. 📋 Read documentation before setup

#### Permission Management
- Use principle of least privilege
- Regularly audit bot permissions
- Keep role hierarchy organized
- Test commands in controlled environment

#### Performance Optimization
- Avoid unnecessary bulk operations
- Use appropriate cooldowns
- Monitor server resources
- Regular maintenance and cleanup

---

## Additional Resources

### Links
- 🤖 [Bot Invite](https://discord.com/api/oauth2/authorize?client_id=931202912888164474&permissions=8&scope=bot%20applications.commands)
- 🆘 [Support Server](https://discord.gg/vMnhpAyFZm)
- 🗳️ [Vote on Top.gg](https://top.gg/bot/931202912888164474/vote)
- 📚 [GitHub Repository](https://github.com/Hunter87ff/Spruce)

### Quick Reference

#### Essential Commands
```
&help                    # Interactive help menu
&ping                    # Check bot status
&sync                    # Sync slash commands
&botinfo                 # Bot statistics
&serverinfo              # Server information
```

#### Moderation Quick Start
```
&lock                    # Lock current channel
&clear 10                # Delete 10 messages
&kick @user reason       # Kick member
&ban @user reason        # Ban member
```

#### Role Management Quick Start
```
&create_roles Name1 Name2    # Create roles
&role @Role @User           # Give role
&role_all_human @Role       # Role to all humans
&autorole add human @Role   # Setup autorole
```

#### Tournament Quick Start
```
/tourney setup slots:144 mentions:4 slot_per_group:12 tournament_name:Weekly
/tourney start channel:#register
/tourney auto_group channel:#register
```

---

*Last Updated: December 2024*  
*Bot Version: 2.1.0*  
*Documentation Version: 1.0*

For the most up-to-date information and support, please join our [Discord support server](https://discord.gg/vMnhpAyFZm).