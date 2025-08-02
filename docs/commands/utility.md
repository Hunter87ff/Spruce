# Utility Commands

General purpose utility commands for server enhancement and information display.

## Quick Reference

| Command | Description | Permission Required |
|---------|-------------|-------------------|
| [`&avatar [user]`](#avatar) | Get user's avatar | None |
| [`&banner [user]`](#banner) | Get user's banner | None |
| [`&userinfo [member]`](#userinfo) | Detailed user information | None |
| [`&serverinfo`](#serverinfo) | Detailed server information | None |
| [`&member_count`](#member-count) | Show server member count | None |
| [`&botinfo`](#botinfo) | Bot statistics and information | None |
| [`&ping`](#ping) | Check bot latency | None |
| [`&uptime`](#uptime) | How long the bot has been running | None |
| [`&embed`](#embed) | Create custom embed messages | Manage Messages |
| [`&tts <message>`](#tts) | Convert text to speech | None |
| [`&translate`](#translate) | Translate text between languages | None |

## Overview

Utility commands provide essential tools for:

- **User Information** - Avatars, banners, and profile details
- **Server Information** - Statistics, member counts, and server details
- **Bot Information** - Status, performance, and statistics
- **Communication Tools** - Embeds, translation, and text-to-speech
- **Fun Features** - Coin flips, personality descriptions

!!! info "No Permissions Required"
    Most utility commands can be used by anyone in the server, making them perfect for general community interaction.

## User Information

### `&avatar`

Get a user's avatar in high quality with download links.

<div class="command-syntax">
&avatar [@user]
</div>

**Aliases:** `&av`, `&pfp`

**Parameters:**
- `user` (optional) - User to get avatar for (default: command author)

**Examples:**
```bash
&avatar                                      # Your own avatar
&avatar @alice                               # Alice's avatar
&av @bob                                     # Using alias
```

**Features:**
- 🖼️ **High Resolution** - Shows largest available size
- 🎭 **Animated GIFs** - Supports animated avatars
- 🔗 **Download Links** - JPG, PNG, and GIF formats
- 📱 **Mobile Friendly** - Optimized display for all devices

??? example "Avatar Display"
    **Getting someone's avatar:**
    ```bash
    &avatar @alice
    ```
    
    **Bot Response:**
    ```
    🖼️ Alice's Avatar
    
    [Download as JPG] [Download as PNG] [Download as GIF]
    ```
    *Shows large avatar image with download buttons*

### `&banner`

Get a user's profile banner if they have one.

<div class="command-syntax">
&banner [@user]
</div>

**Aliases:** `&bnr`

**Parameters:**
- `user` (optional) - User to get banner for (default: command author)

**Examples:**
```bash
&banner                                      # Your own banner
&banner @alice                               # Alice's banner
&bnr @bob                                    # Using alias
```

**Features:**
- 🎨 **High Quality** - Full resolution banners
- 🎭 **Animated Support** - GIF banners if available
- 📱 **Fallback Message** - Clear message if no banner exists

### `&userinfo`

Display comprehensive information about a user.

<div class="command-syntax">
&userinfo [@member]
</div>

**Aliases:** `&ui`

**Parameters:**
- `member` (optional) - Member to get information for (default: command author)

**Examples:**
```bash
&userinfo                                    # Your own info
&userinfo @alice                             # Alice's info
&ui @bob                                     # Using alias
```

**Information Displayed:**

=== "Basic Info"
    - Username and discriminator
    - User ID
    - Nickname (if set)
    - Account creation date
    - Server join date

=== "Roles & Status"
    - All roles (up to 15 shown)
    - Highest role and color
    - Online status
    - Custom status (if set)

=== "Additional Details"
    - Bot status (if applicable)
    - Server booster status
    - Avatar and banner links
    - Time since joining

??? example "User Information Display"
    **Getting user details:**
    ```bash
    &userinfo @alice
    ```
    
    **Bot Response:**
    ```
    👤 Alice Information
    
    📛 Username: alice#1234
    🆔 ID: 123456789012345678
    📅 Created: January 1, 2020
    📥 Joined: March 15, 2024
    
    🎭 Roles (5): @VIP @Members @Gamers @Active @Verified
    🎨 Color: #ff6b6b (from @VIP)
    
    💬 Status: Online
    🎮 Activity: Playing Discord
    ```

## Server Information

### `&serverinfo`

Display comprehensive server statistics and information.

<div class="command-syntax">
&serverinfo
</div>

**Aliases:** `&si`

**No parameters required**

**Information Displayed:**

=== "Basic Details"
    - Server name and ID
    - Server owner
    - Creation date
    - Server region
    - Verification level

=== "Member Statistics"
    - Total members
    - Human vs bot count
    - Online member count
    - Member growth trends

=== "Server Features"
    - Boost level and count
    - Channel counts (text, voice, categories)
    - Role count
    - Emoji and sticker counts
    - Server features (if any)

### `&member_count`

Quick display of server member statistics.

<div class="command-syntax">
&member_count
</div>

**Aliases:** `&mc`

**Features:**
- 👥 **Total Members** - All server members
- 🤖 **Bot Count** - Number of bots
- 🧑 **Human Count** - Human members only
- 📊 **Visual Chart** - Member distribution

## Bot Information

### `&botinfo`

Display Spruce Bot statistics and performance information.

<div class="command-syntax">
&botinfo
</div>

**Aliases:** `&bi`, `&stats`, `&about`

**Information Shown:**

=== "Performance"
    - Current latency (ping)
    - Commands executed
    - Memory usage
    - CPU usage
    - Uptime

=== "Statistics"
    - Total servers
    - Total users
    - Commands available
    - Version information

=== "System Info"
    - Python version
    - discord.py version
    - Operating system
    - Hosting information

### `&ping`

Check bot responsiveness and latency.

<div class="command-syntax">
&ping
</div>

**No parameters required**

**Metrics Displayed:**
- 🏓 **Bot Latency** - Command response time
- 💓 **WebSocket Latency** - Discord connection quality
- 📡 **API Latency** - Discord API response time

### `&uptime`

Show how long the bot has been online.

<div class="command-syntax">
&uptime
</div>

**Features:**
- ⏰ **Total Uptime** - Days, hours, minutes, seconds
- 📈 **Uptime Percentage** - Reliability metric
- 🔄 **Last Restart** - When bot was last restarted

## Communication Tools

### `&embed`

Create custom embed messages with advanced formatting.

<div class="command-syntax">
&embed &lt;title&gt; &lt;description&gt; [color] [footer] [thumbnail] [image] [channel]
</div>

**Parameters:**
- `title` - Embed title
- `description` - Main content/description
- `color` (optional) - Embed color (red, blue, green, hex code)
- `footer` (optional) - Footer text
- `thumbnail` (optional) - Small image URL
- `image` (optional) - Large image URL
- `channel` (optional) - Channel to send to

**Examples:**
```bash
&embed "Welcome" "Welcome to our server!" blue
&embed "Rules" "Please read our rules carefully" red "Important Notice"
&embed "Event" "Join our tournament!" green "See you there!" thumbnail_url image_url #events
```

**Bot Permissions Required:**
- Send Messages
- Embed Links

**User Permissions Required:**
- Manage Messages

**Color Options:**
- **Named colors**: red, blue, green, yellow, purple, orange, pink, cyan
- **Hex codes**: #ff6b6b, #4ecdc4, #45b7d1
- **Random**: `random` for random color

### `&embed_img`

Quick embed creation with image.

<div class="command-syntax">
&embed_img &lt;image_url&gt; &lt;message&gt;
</div>

**Aliases:** `&em`

**Parameters:**
- `image_url` - URL of image to embed
- `message` - Text to display with image

**Examples:**
```bash
&embed_img https://example.com/image.png "Check out this cool image!"
&em https://i.imgur.com/example.jpg "Today's meme of the day"
```

### `&tts`

Convert text to speech and send as audio file.

<div class="command-syntax">
&tts &lt;message&gt;
</div>

**Parameters:**
- `message` - Text to convert to speech (max 150 words)

**Examples:**
```bash
&tts Hello everyone, welcome to our server!
&tts "This is a test of the text to speech feature"
```

**Features:**
- 🔒 **Profanity Filter** - Automatically filters inappropriate content
- 🗣️ **Natural Voice** - English with Indian accent
- 📁 **Audio File** - Sends as downloadable MP3
- ⏱️ **Quick Processing** - Fast conversion

**Limitations:**
- Maximum 150 words per message
- English language only
- Rate limited to prevent spam

### `&translate`

Translate text between different languages.

<div class="command-syntax">
&translate &lt;from_lang&gt; &lt;to_lang&gt; &lt;message&gt;
</div>

**Parameters:**
- `from_lang` - Source language (e.g., English, Spanish, French)
- `to_lang` - Target language
- `message` - Text to translate

**Examples:**
```bash
&translate English Spanish "Hello, how are you?"
&translate French English "Bonjour, comment allez-vous?"
&translate Auto German "Automatic language detection"
```

**Features:**
- 🌍 **50+ Languages** - Wide language support
- 🤖 **Auto-Detection** - Use "Auto" for automatic source detection
- 🔄 **Bidirectional** - Translate between any supported languages
- 📝 **Context Preservation** - Maintains meaning and context

**Rate Limits:**
- 2 translations per 50 seconds per user
- Prevents API abuse

## Fun Commands

### `&toss`

Flip a virtual coin.

<div class="command-syntax">
&toss
</div>

**No parameters required**

**Features:**
- 🪙 **Random Result** - True 50/50 chance
- 🎭 **Animated Display** - Coin flip animation
- 📊 **Fair Algorithm** - Cryptographically secure randomness

### `&whoiss`

Get a random personality description for yourself or another user.

<div class="command-syntax">
&whoiss [@user]
</div>

**Parameters:**
- `user` (optional) - User to describe (default: command author)

**Examples:**
```bash
&whoiss                                      # Describe yourself
&whoiss @alice                               # Describe Alice
```

**Features:**
- 🎲 **Random Traits** - Unique descriptions every time
- 😄 **Fun Content** - Entertaining personality traits
- 👥 **Social Feature** - Great for community interaction

## Server Management Utilities

### `&nick`

Change a user's nickname.

<div class="command-syntax">
&nick &lt;@user&gt; &lt;nickname&gt;
</div>

**Parameters:**
- `user` - User to change nickname for
- `nickname` - New nickname (use "reset" to remove)

**Examples:**
```bash
&nick @alice "Alice the Great"               # Set nickname
&nick @bob reset                             # Remove nickname
```

**Bot Permissions Required:**
- Manage Nicknames

**User Permissions Required:**
- Manage Nicknames

### `&addemoji`

Add a custom emoji to the server.

<div class="command-syntax">
&addemoji &lt;emoji&gt;
</div>

**Parameters:**
- `emoji` - Custom emoji from another server or image URL

**Examples:**
```bash
&addemoji :custom_emoji:                     # Add emoji from another server
&addemoji https://example.com/emoji.png      # Add from image URL
```

**Bot Permissions Required:**
- Manage Emojis

**User Permissions Required:**
- Manage Emojis

## Administrative Utilities

### `&prefix`

Show the bot's current prefix.

<div class="command-syntax">
&prefix
</div>

**User Permissions Required:**
- Administrator

### `&sync`

Sync slash commands to the server.

<div class="command-syntax">
&sync
</div>

**User Permissions Required:**
- Administrator

**When to Use:**
- Slash commands not appearing
- After bot updates
- Permission issues with slash commands

### `&invite`

Get bot invite link and related links.

<div class="command-syntax">
&invite
</div>

**No parameters required**

**Provides:**
- 🤖 Bot invite link with proper permissions
- 🆘 Support server link
- 🗳️ Voting links
- 📚 Documentation link

### Support System

#### `&setup_ticket`

Create a ticket support system for your server.

<div class="command-syntax">
&setup_ticket
</div>

**Bot Permissions Required:**
- Manage Channels
- Manage Roles

**User Permissions Required:**
- Manage Channels
- Manage Roles

**What It Creates:**
- 🎫 Ticket category
- 📝 Ticket creation channel with button
- 🎛️ Interactive ticket management
- 🔒 Proper permissions setup

## Performance & Reliability

### Response Times

| Command Type | Expected Response |
|-------------|------------------|
| Simple Info | < 1 second |
| User Data | < 2 seconds |
| Server Stats | < 3 seconds |
| File Generation | < 5 seconds |
| Complex Operations | < 10 seconds |

### Error Handling

All utility commands include comprehensive error handling:

- **Clear error messages** for user mistakes
- **Graceful fallbacks** when data unavailable
- **Rate limit protection** to prevent spam
- **Permission checks** before execution

## Troubleshooting

### Common Issues

=== "Avatar/Banner Not Loading"
    **Issue:** Images not displaying properly
    
    **Solutions:**
    - Check if user has avatar/banner set
    - Verify bot has embed permissions
    - Try again if Discord CDN is slow

=== "Translation Errors"
    **Issue:** Translation command fails
    
    **Solutions:**
    - Check language names (use full names)
    - Verify message isn't too long
    - Wait if rate limited

=== "TTS Not Working"
    **Issue:** Text-to-speech fails
    
    **Solutions:**
    - Keep message under 150 words
    - Avoid special characters
    - Check for profanity filter triggers

## Related Features

- **[AutoRole System](autorole.md)** - Works with user information
- **[Moderation Tools](moderation.md)** - Enhanced with utility data
- **[Role Management](roles.md)** - User info for role decisions

## Support

Need help with utility commands?

- 📚 **[Troubleshooting Guide](../troubleshooting/)** - Common issues and solutions
- 💬 **[Support Server](https://discord.gg/vMnhpAyFZm)** - Get help from our community
- 📧 **Email**: support@nexinlabs.com

---

**Next:** Learn about [Tournament Commands →](tournaments.md)
