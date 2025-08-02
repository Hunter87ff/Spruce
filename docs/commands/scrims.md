# Scrim Commands

Professional scrim management system with scheduling, slot tracking, and automation.

## Quick Reference

| Command | Description | Permission Required |
|---------|-------------|-------------------|
| [`/scrim create`](#scrim-create) | Set up a new scrim | Manage Channels or @scrim-mod |
| [`/scrim start`](#scrim-start) | Open scrim registration | @scrim-mod |
| [`/scrim pause`](#scrim-pause) | Pause registration | @scrim-mod |
| [`/scrim info`](#scrim-info) | View scrim details | None |
| [`/scrim add team`](#scrim-add-team) | Manually add team | @scrim-mod |
| [`/scrim remove team`](#scrim-remove-team) | Remove team | @scrim-mod |
| [`/scrim timeslot`](#scrim-timeslot) | Set match time | @scrim-mod |
| [`/scrim maps`](#scrim-maps) | Configure map pool | @scrim-mod |

## Overview

Spruce Bot's scrim system provides:

- **Automated Scheduling** - Time slot management with timezone support
- **Team Registration** - Streamlined team signup process
- **Map Pool Management** - Random map selection and bans
- **Slot Tracking** - Real-time availability monitoring
- **Role Integration** - Automatic role assignment for participants
- **Export Features** - CSV data export for external tools
- **Multi-Format Support** - Solo, duo, squad scrims

!!! tip "Scrim Workflow"
    1. **Create** scrim with `/scrim create`
    2. **Set time slots** with `/scrim timeslot`
    3. **Configure maps** (optional)
    4. **Open registration** with `/scrim start`
    5. **Monitor** and manage teams
    6. **Export** data for match coordination

## Scrim Setup

### `/scrim create`

Create a complete scrim infrastructure with channels and configuration.

<div class="command-syntax">
/scrim create total_slots:&lt;number&gt; team_name:&lt;name&gt; mentions:&lt;count&gt; [timezone]
</div>

**Parameters:**
- `total_slots` - Number of teams/players (2-100)
- `team_name` - Scrim identifier (max 30 chars)
- `mentions` - Players to mention per team (0-10)
- `timezone` (optional) - Timezone for scheduling (default: UTC)

**Examples:**
```bash
/scrim create total_slots:32 team_name:"Daily Scrims" mentions:4 timezone:IST
/scrim create total_slots:50 team_name:"Evening Practice" mentions:2
```

**Bot Permissions Required:**
- Manage Channels
- Manage Roles
- Send Messages

**User Permissions Required:**
- Manage Channels (or @scrim-mod role)

**What Gets Created:**

=== "Channels"
    - 📋 **Info** - Scrim information and rules
    - 📝 **How-to-register** - Registration format
    - ✅ **Register-here** - Team registration
    - 👥 **Confirmed-teams** - Confirmed participants
    - 🕐 **Slot-timings** - Time schedule
    - ❓ **Queries** - Questions and support

=== "Roles & Features"
    - 🎯 **Scrim Role** - For confirmed participants
    - 🔒 **Controlled Access** - Managed permissions
    - ⏰ **Time Management** - Built-in scheduling
    - 📊 **Statistics** - Performance tracking

??? example "Scrim Setup Process"
    **Creating a 32-slot scrim:**
    ```bash
    /scrim create total_slots:32 team_name:"BGMI Practice" mentions:4 timezone:IST
    ```
    
    **Bot creates:**
    ```
    📁 BGMI Practice Category
    ├── 📋 bgmi-info
    ├── 📝 bgmi-how-to-register
    ├── ✅ bgmi-register-here
    ├── 👥 bgmi-confirmed-teams
    ├── 🕐 bgmi-slot-timings
    └── ❓ bgmi-queries
    
    🎭 @bgmi-scrim role created
    ```

**Supported Timezones:**
- **IST** - Indian Standard Time
- **UTC** - Coordinated Universal Time
- **EST** - Eastern Standard Time
- **PST** - Pacific Standard Time
- **GMT** - Greenwich Mean Time
- **CET** - Central European Time

## Registration Management

### `/scrim start`

Open scrim registration for teams.

<div class="command-syntax">
/scrim start channel:&lt;registration_channel&gt;
</div>

**Parameters:**
- `channel` - The registration channel from scrim setup

**Examples:**
```bash
/scrim start channel:#bgmi-register-here
```

**Effects:**
- ✅ Opens registration for @everyone
- 📢 Sends registration announcement
- 🔄 Activates auto-confirmation system
- 📝 Enables team processing

**Registration Process:**
1. Teams post in registration format
2. Bot validates format and mentions
3. Automatic confirmation if valid
4. Role assignment for confirmed teams
5. Real-time slot counting

### `/scrim pause`

Pause scrim registration temporarily.

<div class="command-syntax">
/scrim pause channel:&lt;registration_channel&gt;
</div>

**Parameters:**
- `channel` - Registration channel to pause

**Examples:**
```bash
/scrim pause channel:#bgmi-register-here
```

**Effects:**
- ⏸️ Locks registration channel
- 📢 Notifies about pause
- 🔄 Maintains current registrations
- 📝 Prevents new signups

### `/scrim info`

Display comprehensive scrim information.

<div class="command-syntax">
/scrim info channel:&lt;registration_channel&gt;
</div>

**Parameters:**
- `channel` - Registration channel

**Information Displayed:**

=== "Scrim Details"
    - Scrim name and status
    - Total and available slots
    - Mentions per team
    - Timezone setting

=== "Schedule"
    - Configured time slots
    - Next match time
    - Timezone information
    - Countdown timers

=== "Statistics"
    - Registered teams
    - Fill rate percentage
    - Average registration time
    - Peak activity periods

## Team Management

### `/scrim add team`

Manually add a team to the scrim.

<div class="command-syntax">
/scrim add team channel:&lt;reg_channel&gt; captain:&lt;member&gt; team_name:&lt;name&gt;
</div>

**Parameters:**
- `channel` - Registration channel
- `captain` - Team captain
- `team_name` - Team identifier

**Examples:**
```bash
/scrim add team channel:#register captain:@alice team_name:"Alpha Squad"
/scrim add team channel:#register captain:@bob team_name:"Pro Team"
```

**Process:**
1. Validates team and captain
2. Checks slot availability
3. Creates confirmation entry
4. Assigns scrim role
5. Updates slot count

### `/scrim remove team`

Remove a team from the scrim.

<div class="command-syntax">
/scrim remove team channel:&lt;reg_channel&gt; captain:&lt;member&gt; [reason]
</div>

**Parameters:**
- `channel` - Registration channel
- `captain` - Team captain to remove
- `reason` (optional) - Removal reason

**Examples:**
```bash
/scrim remove team channel:#register captain:@alice reason:"No-show"
/scrim remove team channel:#register captain:@bob
```

**Effects:**
- Removes team from scrim
- Frees slot for others
- Removes scrim role
- Logs removal reason
- Notifies team captain

## Time Management

### `/scrim timeslot`

Configure match time slots for the scrim.

<div class="command-syntax">
/scrim timeslot channel:&lt;reg_channel&gt; time:&lt;HH:MM&gt; [date]
</div>

**Parameters:**
- `channel` - Registration channel
- `time` - Match time in 24-hour format
- `date` (optional) - Specific date (YYYY-MM-DD)

**Examples:**
```bash
/scrim timeslot channel:#register time:19:30
/scrim timeslot channel:#register time:15:00 date:2024-01-15
```

**Features:**

=== "Time Display"
    - **Local Time** - Shows in server timezone
    - **UTC Time** - Universal reference
    - **Countdown** - Time until match
    - **Recurring** - Daily schedule support

=== "Notifications"
    - **30 minutes** before match
    - **15 minutes** before match
    - **5 minutes** before match
    - **Match start** notification

??? example "Time Slot Configuration"
    **Setting daily 7:30 PM scrims:**
    ```bash
    /scrim timeslot channel:#bgmi-register time:19:30
    ```
    
    **Result in slot-timings channel:**
    ```
    🕐 Match Schedule
    
    📅 Today: 7:30 PM IST (2:00 PM UTC)
    📅 Tomorrow: 7:30 PM IST (2:00 PM UTC)
    
    ⏰ Next match in: 2 hours 15 minutes
    
    🔔 Reminders:
    • 30 minutes before
    • 15 minutes before  
    • 5 minutes before
    ```

**Multiple Time Slots:**
```bash
# Morning slot
/scrim timeslot channel:#register time:10:00

# Evening slot  
/scrim timeslot channel:#register time:19:30
```

## Map Management

### `/scrim maps`

Configure map pool for random selection.

<div class="command-syntax">
/scrim maps channel:&lt;reg_channel&gt; action:&lt;add/remove/list&gt; [map_name]
</div>

**Parameters:**
- `channel` - Registration channel
- `action` - add, remove, or list
- `map_name` - Map to add/remove

**Examples:**
```bash
/scrim maps channel:#register action:add map_name:Erangel
/scrim maps channel:#register action:remove map_name:Miramar
/scrim maps channel:#register action:list
```

**Map Pool Features:**

=== "Random Selection"
    - **Weighted Random** - Based on popularity
    - **No Repeats** - Prevents consecutive same maps
    - **Ban System** - Team map bans (if enabled)
    - **Override** - Manual map selection

=== "Supported Games"
    - **BGMI/PUBG** - All classic maps
    - **Free Fire** - Popular maps
    - **COD Mobile** - BR and MP maps
    - **Custom** - Add any map name

??? example "Map Pool Setup"
    **BGMI map pool:**
    ```bash
    /scrim maps channel:#register action:add map_name:Erangel
    /scrim maps channel:#register action:add map_name:Miramar
    /scrim maps channel:#register action:add map_name:Sanhok
    /scrim maps channel:#register action:add map_name:Vikendi
    ```
    
    **Random selection result:**
    ```
    🗺️ Next Match Map: Erangel
    
    📊 Map Pool:
    ✅ Erangel (30% chance)
    ✅ Miramar (25% chance)
    ✅ Sanhok (25% chance)
    ✅ Vikendi (20% chance)
    ```

### Map Selection Commands

#### `/scrim select_map`

Manually select next match map.

<div class="command-syntax">
/scrim select_map channel:&lt;reg_channel&gt; map_name:&lt;name&gt;
</div>

#### `/scrim random_map`

Generate random map from pool.

<div class="command-syntax">
/scrim random_map channel:&lt;reg_channel&gt;
</div>

## Advanced Features

### Recurring Scrims

#### `/scrim schedule`

Set up daily recurring scrims.

<div class="command-syntax">
/scrim schedule channel:&lt;reg_channel&gt; daily_time:&lt;HH:MM&gt; auto_start:&lt;true/false&gt;
</div>

**Parameters:**
- `channel` - Registration channel
- `daily_time` - Daily scrim time
- `auto_start` - Automatically open registration

**Features:**
- **Daily Reset** - Clears previous day registrations
- **Auto Start** - Opens registration automatically
- **Timezone Aware** - Consistent time across days
- **Weekend Skip** - Optional weekend exclusion

### Team Formats

#### Solo Scrims
```bash
/scrim create total_slots:100 team_name:"Solo Practice" mentions:0
```

#### Duo Scrims
```bash
/scrim create total_slots:50 team_name:"Duo Scrims" mentions:1
```

#### Squad Scrims
```bash
/scrim create total_slots:25 team_name:"Squad Practice" mentions:3
```

### Registration Formats

The bot automatically adapts registration format based on mentions setting:

=== "Solo (mentions:0)"
    ```
    IGN: PlayerName
    ID: 123456789
    ```

=== "Duo (mentions:1)"
    ```
    Team: TeamName
    Captain: @player1
    Teammate: @player2
    ```

=== "Squad (mentions:3)"
    ```
    Team: TeamName
    Captain: @player1
    Teammates: @player2 @player3 @player4
    ```

## Data Management

### `/scrim export`

Export scrim data for external use.

<div class="command-syntax">
/scrim export channel:&lt;registration_channel&gt; format:&lt;csv/json&gt;
</div>

**Parameters:**
- `channel` - Registration channel
- `format` - Export format (csv or json)

**Exported Data:**
- Team names and captains
- Player lists with mentions
- Registration timestamps
- Time slot assignments
- Contact information

**Use Cases:**
- Match coordination
- Streaming overlays
- Statistics tracking
- Prize distribution

### `/scrim stats`

View detailed scrim statistics.

<div class="command-syntax">
/scrim stats channel:&lt;registration_channel&gt; period:&lt;daily/weekly/monthly&gt;
</div>

**Statistics Include:**
- Participation rates
- Popular time slots
- Team performance
- Registration patterns

## Automation Features

### Auto-Confirmation

Teams are automatically confirmed when:
- ✅ Correct registration format
- ✅ Proper mention count
- ✅ Available slots
- ✅ No duplicate entries

### Smart Notifications

=== "Registration Alerts"
    - Slot milestones (25%, 50%, 75%, 90% full)
    - Registration opened/paused
    - Team confirmations
    - Slot availability warnings

=== "Match Reminders"
    - Countdown notifications
    - Map announcements
    - Last-minute updates
    - Post-match feedback

### Role Management

- **Auto Role Assignment** - Confirmed teams get scrim role
- **Permission Control** - Access to specific channels
- **Role Cleanup** - Automatic removal after scrim
- **Hierarchy Respect** - Maintains server role order

## Troubleshooting

### Common Issues

=== "Setup Problems"
    **Problem:** Scrim creation fails
    
    **Solutions:**
    - Check channel/category limits
    - Verify bot permissions
    - Ensure unique scrim names
    - Check server capacity

=== "Registration Issues"
    **Problem:** Teams can't register
    
    **Solutions:**
    - Verify registration is open
    - Check format in how-to-register
    - Confirm mention requirements
    - Check available slots

=== "Time Zone Problems"
    **Problem:** Wrong time display
    
    **Solutions:**
    - Set correct timezone in setup
    - Use 24-hour format for times
    - Check daylight saving rules
    - Verify server location

### Error Messages

| Error | Meaning | Solution |
|-------|---------|----------|
| "Scrim is full" | No available slots | Increase slots or remove teams |
| "Invalid time format" | Wrong time syntax | Use HH:MM format (24-hour) |
| "Registration closed" | Scrim not active | Use `/scrim start` |
| "Already registered" | Duplicate registration | Check existing confirmations |
| "Invalid timezone" | Unsupported timezone | Use supported timezone codes |

## Best Practices

### Scrim Management

=== "Setup Phase"
    - **Choose appropriate slots** for expected participation
    - **Set clear time slots** with timezone
    - **Configure map pool** if needed
    - **Prepare rules** and guidelines

=== "Operation Phase"
    - **Monitor registration** regularly
    - **Respond to queries** quickly
    - **Manage time slots** effectively
    - **Export data** before matches

=== "Post-Scrim"
    - **Collect feedback** from participants
    - **Review statistics** for improvements
    - **Clean up** old registrations
    - **Plan** next scrims

### Performance Optimization

- **Limit concurrent scrims** to 2-3 per server
- **Use appropriate slot sizes** for server activity
- **Monitor role assignments** for performance
- **Regular cleanup** of old data

## Integration Features

### Discord Features

- **Voice Channel** integration for team coordination
- **Forum Channels** for match discussions
- **Event Scheduling** for calendar integration
- **Bot Status** showing active scrims

### External Tools

- **Streaming Overlays** - Real-time participant data
- **Tournament Brackets** - Export for bracket creation
- **Statistics Platforms** - Performance tracking
- **Mobile Apps** - Registration notifications

## Support

Need help with scrims?

- 📚 **[Scrim Setup Guide](../guides/scrim-setup.md)** - Detailed setup process
- 🛠️ **[Troubleshooting](../troubleshooting/)** - Common problems and solutions
- 💬 **[Support Server](https://discord.gg/vMnhpAyFZm)** - Community assistance
- 📧 **Email**: support@nexinlabs.com

---

**Next:** Learn about [Developer Commands →](developer.md)
