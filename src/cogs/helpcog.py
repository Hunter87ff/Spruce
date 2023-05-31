import discord
from discord.ext import commands
from asyncio import sleep
from discord.ui import Button, View
from modules import config


emd = discord.Embed
cmd = commands
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix=commands.when_mentioned_or("&"), intents=intents, help_command=None)



invbtn = Button(label="Invite", url="https://discord.com/api/oauth2/authorize?client_id=931202912888164474&permissions=8&redirect_uri=https%3A%2F%2Fdiscord.gg%2FvMnhpAyFZm&response_type=code&scope=bot%20identify")
votebtn = Button(label="Vote", url="https://top.gg/bot/931202912888164474/vote")
support_serverbtn = Button(label="Support Server", url="https://discord.gg/vMnhpAyFZm")
hel_p = "• Prefix - `&`\n• Total Commands - `85` | Usable - `80`\n• Type `&help <command | category>` for more info\n\n"
helpemb  = discord.Embed(title=f"Spruce Help Menu", description=f"{hel_p}**__Categories__\n\n<a:music:1017796831272505375> Music\n\n<:mod:999353993035780258> Moderation\n\n<:setting:968374105961300008> Utility\n\n<a:cup:999246631604080711> Esports\n\n<:role:1022568952573984828> Role**", color=0xf0ff0f)
musicemb = discord.Embed(description=f"{hel_p}__**Musics**__\n`play`, `pause`, `resume`, `queue`, `skip`, `loop`, `stop`, `join`, `leave`", color=0xf0ff0f)
modemb   = discord.Embed(description=f"{hel_p}__**Moderation**__\n`clear`, `clear_perms`, `channel_del`, `channel_make`, `create_channel`, `delete_category`, `mute`, `unmute`, `kick`, `ban`, `hide`, `unhide`, `lock`, `unlock`, `hide_category`, `unhide_category`, `lock_category`, `unlock_category`", color=0xf0ff0f)
espemb   = discord.Embed(description=f"{hel_p}__**Esports**__\n`tourney_setup`, `add_slot`, `cancel_slot`, `group_setup`, `change_slot`, `pause_tourney`, `start_tourney`, `tourney`, `faketag`, `girls_lobby`, `publish`, `tourneys`, `auto_group`, `_gsetup`", color=0xf0ff0f)
roleemb  = discord.Embed(description=f"{hel_p}__**Roles**__\n`create_roles`, `port`, `inrole`, `remove_roles`, `del_roles`, `give_roles`, `remove_role_members`, `role_all_bot`, `role_all_human`, `role_all_human`, `role_all_bot`, `hide_roles`, `unhide_roles`", color=0xf0ff0f)
utilemb  = discord.Embed(description=f"{hel_p}__**Utility**__\n`addemoji`, `tts`, `avatar`, `banner`, `botinfo`, `ping`, `embed`, `embed_img`, `member_count`, `nick`, `nitro`, `prefix`, `react`, `server_av`, `serverinfo`, `toss`, `userinfo`, `whoiss`, `uptime`, `vote`, `support`, `invite`", color=0xf0ff0f)
buttons =[invbtn, votebtn, support_serverbtn]


def get_thum(ctx):
    return ctx.guild.get_member(config.bot_id).display_avatar




class Dropdown(discord.ui.Select):
    def __init__(self):

        options = [
            discord.SelectOption(label='Main', description='Select For All Commands'),
            discord.SelectOption(label='Esports', description='Select For Tournament Commands'),
            discord.SelectOption(label='Music', description='Select For Music Commands'),
            discord.SelectOption(label='Moderation', description='Select For Noderation Commands'),
            discord.SelectOption(label='Utility', description='Select For Utility Commands'),
            discord.SelectOption(label='Role', description='Select For Role Commands'),
            #discord.SelectOption(label='Channel', description='Select For Channel Commands'),
            #discord.SelectOption(label='Greet', description='Select For Greeting Commands')
            #discord.SelectOption(label='Automod', description='Select For Automod Commands'),
        ]
        super().__init__(placeholder='Choose Command Category...', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        ctx = interaction
        if self.values[0] == "Music":
            await interaction.response.edit_message(embed=musicemb.set_thumbnail(url=get_thum(ctx)).set_footer(text=f"Requested By {interaction.user}", icon_url=interaction.user.display_avatar))
        if self.values[0] == "Moderation":
            await interaction.response.edit_message(embed=modemb.set_thumbnail(url=get_thum(ctx)).set_footer(text=f"Requested By {interaction.user}", icon_url=interaction.user.display_avatar))
        if self.values[0] == "Esports":
            await interaction.response.edit_message(embed=espemb.set_thumbnail(url=get_thum(ctx)).set_footer(text=f"Requested By {interaction.user}", icon_url=interaction.user.display_avatar))
        if self.values[0] == "Main":
            await interaction.response.edit_message(embed=helpemb.set_thumbnail(url=get_thum(ctx)).set_footer(text=f"Requested By {interaction.user}", icon_url=interaction.user.display_avatar))
        if self.values[0] == "Utility":
            await interaction.response.edit_message(embed=utilemb.set_thumbnail(url=get_thum(ctx)).set_footer(text=f"Requested By {interaction.user}", icon_url=interaction.user.display_avatar))
        if self.values[0] == "Role":
            await interaction.response.edit_message(embed=roleemb.set_thumbnail(url=get_thum(ctx)).set_footer(text=f"Requested By {interaction.user}", icon_url=interaction.user.display_avatar))




class DropdownView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(Dropdown())


class Helper(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @bot.group(invoke_without_command=True,aliases=['commands', 'hel', "h"])
    async def help(self, ctx):
        if ctx.author.bot:
            return

        view = DropdownView()
        for opt in buttons:
            view.add_item(opt)
        msg = await ctx.send(embed=helpemb.set_thumbnail(url=get_thum(ctx)).set_footer(text=f"Requested By {ctx.author}", icon_url=ctx.author.display_avatar), view=view)



    @help.group(invoke_without_command=True)
    async def Music(self, ctx):
        view = View()
        for bt in buttons:
            view.add_item(bt)
        await ctx.send(embed=musicemb.set_thumbnail(url=get_thum(ctx)).set_footer(text=f"Requested By {ctx.author}", icon_url=ctx.author.display_avatar), view=view)



    @help.group(invoke_without_command=True)
    async def Moedration(self, ctx):
        view = View()
        for bt in buttons:
            view.add_item(bt)
        await ctx.send(embed=modemb.set_thumbnail(url=get_thum(ctx)).set_footer(text=f"Requested By {ctx.author}", icon_url=ctx.author.display_avatar), view=view)



    @help.group(invoke_without_command=True)
    async def Esports(self, ctx):
        view = View()
        for bt in buttons:
            view.add_item(bt)
        await ctx.send(embed=espemb.set_thumbnail(url=get_thum(ctx)).set_footer(text=f"Requested By {ctx.author}", icon_url=ctx.author.display_avatar), view=view)


    @help.group(invoke_without_command=True)
    async def Role(self, ctx):
        view = View()
        
        for bt in buttons:
            view.add_item(bt)
        await ctx.send(embed=roleemb.set_thumbnail(url=get_thum(ctx)).set_footer(text=f"Requested By {ctx.author}", icon_url=ctx.author.display_avatar), view=view)



    @help.group(invoke_without_command=True)
    async def Utility(self, ctx):
        view = View()
        for bt in buttons:
            view.add_item(bt)
        await ctx.send(embed=utilemb.set_thumbnail(url=get_thum(ctx)).set_footer(text=f"Requested By {ctx.author}", icon_url=ctx.author.display_avatar), view=view)





#moderation Related

    @help.command()
    async def ban(self, ctx):
        em = discord.Embed(description="Aliases : `Not Available`\nUsage : `ban <member>`\nExample : `&ban @abhi`", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command()
    async def kick(self, ctx):
        em = discord.Embed(description="Aliases : `Not Available`\nUsage : `kick <member>`\nExample : `&kick @abhi`", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command(aliases=["purge"])
    async def clear(self, ctx):
        em = discord.Embed(description="Aliases : `purge`\nUsage : `clear|purge [amount=None]`\nExample : `&clear 10`", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command()
    async def mute(self, ctx):
        em = discord.Embed(description="Aliases : `Not Available`\nUsage : `mute <member> [reason=None]`\nExample : `&mute @abhi spamming`", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command()
    async def unmute(self, ctx):
        em = discord.Embed(description="Aliases : `Not Available`\nUsage : `unmute <member> [reason=None]`\nExample : `&unmute @abhi spamming`", color=0x00ff00)
        await ctx.send(embed=em)


    @help.command()
    async def hide(self, ctx):
        em = discord.Embed(description="Aliases : `Not Available`\nUsage : `hide role(optional) channel(optional)`\nExample : `&hide`\n", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command()
    async def unhide(self, ctx):
        em = discord.Embed(description="Aliases : `Not Available`\nUsage : `unhide [role=None]`\nExample : `&unhide`\n", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command()
    async def lock(self, ctx):
        em = discord.Embed(description="Aliases : `Not Available`\nUsage : `lock [role=None]`\nExample : `&lock`\n", color=0x00ff00)
        await ctx.send(embed=em)


    @help.command()
    async def unlock(self, ctx):
        em = discord.Embed(description="Aliases : `Not Available`\nUsage : `unlock [role=None]`\nExample : `&unlock`\n", color=0x00ff00)
        await ctx.send(embed=em)


#channel Related

    @help.command(aliases=["chd"])
    async def channel_del(self, ctx):
        em = discord.Embed(description="Aliases : `chd`\nUsage : `channel_del [channels...]`\nExample : `&channel_del #general #updates`", color=0x00ff00)
        await ctx.send(embed=em)


    @help.command(aliases=["chm"])
    async def channel_make(self, ctx):
        em = discord.Embed(description="Aliases : `chm`\nUsage : `channel_make [names...]`\nExample : `&channel_make general updates`", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command(aliases=["cch"])
    async def create_channel(self, ctx):
        em = discord.Embed(description="Aliases : `cch`\nUsage : `create_channel <category> [names...]`\nExample : `&create_channel 32745216342163 general memes announcements`", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command(aliases=["dc"])
    async def delete_category(self, ctx):
        em = discord.Embed(description="Aliases : `dc`\nUsage : `delete_category <category>`\nExample : `&dc 7654123645287`\nDescription : `Use This Command To Delete A Hole Category | You Must Have Administrator Permission`", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command(aliases=["hc"])
    async def hide_category(self, ctx):
        em = discord.Embed(description="Aliases : `hc`\nUsage : `hide_category <category> [role=None]`\nExample : `&hc 7654123645287`\nDescription : `Use This Command To Hide A Hole Category`", color=0x00ff00)
        await ctx.send(embed=em)     

    @help.command(aliases=["ulc"])
    async def unlock_category(self, ctx):
        em = discord.Embed(description="Aliases : `ulc`\nUsage : `unlock_category <category> [role=None]`\nExample : `&ulc 7654123645287`\nDescription : `Use This Command To unlock A Hole Category`", color=0x00ff00)
        await ctx.send(embed=em)  

    @help.command(aliases=["lc"])
    async def lock_category(self, ctx):
        em = discord.Embed(description="Aliases : `lc`\nUsage : `lock_category <category> [role=None]`\nExample : `&lc 7654123645287`\nDescription : `Use This Command To lock A Hole Category`", color=0x00ff00)
        await ctx.send(embed=em) 

    @help.command(aliases=["uhc"])
    async def uhide_category(self, ctx):
        em = discord.Embed(description="Aliases : `uhc`\nUsage : `uhc <category_id> [role=None]`\nExample : `&uhc 73462546213542614526`\n", color=0x00ff00)
        await ctx.send(embed=em)





#role Related
    @help.command()
    async def inrole(self, ctx):
        em = discord.Embed(description="Aliases : `Not Available`\nUsage : `inrole`\nExample : `&inrole`", color=0x00ff00)
        await ctx.send(embed=em)


    @help.command()
    async def port(self, ctx):
        em = discord.Embed(description="Aliases : `Not Available`\nUsage : `port <role1> <role2>`\nExample : `&port @ipl-group1 @ipl-group2`", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command(aliases=["croles", "crole"])
    async def create_roles(self, ctx):
        em = discord.Embed(description="Aliases : `croles`\nUsage : `create_roles [Names...]`\nExample : `&create_roles family male female`", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command(aliases=["role", "role_give"])
    async def give_role(self, ctx):
        em = discord.Embed(description="Aliases : `role`\nUsage : `give_role <role> [members...]`\nExample : `&role @Male @hunter`", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command()
    async def give_roles(self, ctx):
        em = discord.Embed(description="Aliases : `role`\nUsage : `give_roles <member> [roles...]`\nExample : `&role @hunter @male @18+`", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command(aliases=["role_remove", "role_re"])
    async def remove_role(self, ctx):
        em = discord.Embed(description="Aliases : `Not Available`\nUsage : `remove_role <role> [memebrs...]`\nExample : `&remove_role @Male @hunter`", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command(aliases=["droles", "drole"])
    async def del_roles(self, ctx):
        em = discord.Embed(description="Aliases : `droles`\nUsage : `del_roles [roles...]`\nExample : `&del_roles @group1 @group2`", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command(aliases=["ra_role"])
    async def remove_role_members(self, ctx):
        em = discord.Embed(description="Aliases : `ra_role`\nUsage : `ra_role <roles>`\nExample : `&ra_role @humans`\nDescription : Use This Command To Remove A Role From Everyone", color=0x00ff00)
        await ctx.send(embed=em)


    @help.command()
    async def role_all_human(self, ctx):
        em = discord.Embed(description="Aliases : `Not Available`\nUsage : `role_all_human`\nExample : `&role_all_human @members`", color=0x00ff00)
        await ctx.send(embed=em)


    @help.command()
    async def role_all_bot(self, ctx):
        em = discord.Embed(description="Aliases : `Not Available`\nUsage : `role_all_bot`\nExample : `&role_all_bot @members`", color=0x00ff00)
        await ctx.send(embed=em)


    @help.command(aliases=["cperms"])
    async def clear_perms(self, ctx):
        em = discord.Embed(description="Aliases : `Not Available`\nUsage : `clear_perms [role=None]`\nExample : `&clear_perms @public`\nDescription : Use this command to remove all permissions from roles", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command(aliases=["hr"])
    async def hide_roles(self, ctx):
        em = discord.Embed(description="Aliases : `hr`\nUsage : `hide_roles`\nExample : `&hide_roles`\nDescription : Use this command to hide all roles in memebr list", color=0x00ff00)
        await ctx.send(embed=em)


    @help.command(aliases=["uhr"])
    async def unhide_roles(self, ctx):
        em = discord.Embed(description="Aliases : `uhr`\nUsage : `unhide_roles [roles..]`\nExample : `&unhide_roles @moderator @Admin`\nDescription : Use this command to roles roles in memebr list", color=0x00ff00)
        await ctx.send(embed=em)



	
#Esports Related
    @help.command(aliases=["cs"])
    async def change_slot(self, ctx):
        em = discord.Embed(description="Aliases : `cs`\nUsage : `change_slot <exact_teame> <mention>`\nExample : `&change_slot HG ESPORTS @hunter `\nDescription: Use This Command By Replying The Group Message! And Use The Exact Slot Detail Otherwise It'll Not Work", color=0x00ff00)
        em.set_image(url="https://media.discordapp.net/attachments/892682901404123137/1057515803823587440/Debut_2022-12-28_09_58_39.png?width=879&height=462")
        await ctx.send(embed=em)

    @help.command(aliases=["pub"])
    async def publish(self, ctx):
        em = discord.Embed(description="Aliases : `Not Available`\nUsage : `publish <registration_channel> <prize>`\nExample : `&publish #register-here  100K INR`", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command()
    async def tourneys(self, ctx):
        em = discord.Embed(description="Aliases : `Not Available`\nUsage : `tourneys`\nExample : `&tourneys`\nDescription: By using this command! you'll get a list of ongoing tournaments to register", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command()
    async def auto_group(self, ctx):
        em = discord.Embed(description="Aliases : `Not Available`\nUsage : `auto_group <registration_channel>`\nExample : `&auto_group <registration_channel> `\nDescription: By using this command it'll create total group system of the tournament\nNote: Make sure no one should send messages in  confirm channel. else it'll not work", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command(aliases=["add"])
    async def add_slot(self, ctx):
        em = discord.Embed(description="Aliases : `Not Available`\nUsage : `add_slot <registration_channel> <member> <Team_Name>`\nExample : `&add_slot #register-here @ayush Team Element`\ndescription : Use This Command To Add Slot To An ongoing Tournament", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command(aliases=["cancel"])
    async def cancel_slot(self, ctx):
        em = discord.Embed(description="Aliases : `Not Available`\nUsage : `cancel_slot <registration_channel> <member> [reason=None]`\nExample : `&cancel_slot #register-here @rahul abusing`\ndescription : Use This Command To Cancel A Slot Of A Tournament", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command(aliases=["ftf", "ft"])
    async def faketag(self, ctx):
        em = discord.Embed(description="Aliases : `Not Available`\nUsage : `faketag <registration_channel>`\nExample : `&faketag #register-here`\ndescription : Use This Command To enable/disable Faketag Filter Of A Tournament", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command(aliases=['gsetup'])
    async def group_setup(self, ctx):
        em = discord.Embed(description="Aliases : `gsetup`\nUsage : `group_setup <prefix> <starting group no> <end group no.> [category=None]`\nExample : `&group_setup ws 1 14`\nNote: Here 1 means group1 and 14 means group14\nIf You Already Have a Category You Can Put The Category Id At Last", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command(aliases=['grls_lobby', "girls_lby"])
    async def girls_lobby(self, ctx):
        em = discord.Embed(description="Aliases : `Not Available`\nUsage : `girls_lobby <vc_amount>`\nExample : `&girls_lobby 12`", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command(aliases=['ts', "tsetup", "setup"])
    async def tourney_setup(self, ctx):
        em = discord.Embed(description="Aliases : `ts`\nUsage : `tourney_setup <total_slot> <mentions> <number_of_slot_per_group> <tournament_name>`\nExample : `&ts 144 4 12 WEEKLY SCRIM`\nNote : You must have @tourney-mod Role to manage the tournament\n\n**[Watch Tutorial](https://youtu.be/R9UmQ_NJD7M)**", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command(aliases=['st_tourney', "tourney_start"])
    async def start_tourney(self, ctx):
        em = discord.Embed(description="Aliases : `Not Available`\nUsage : `start_tourney <registration_channel>`\nExample : `&start_tourney #register-here`\nNote : You Can Also Use channel_id", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command(aliases=['ps_tourney', "tourney_pause"])
    async def pause_tourney(self, ctx):
        em = discord.Embed(description="Aliases : `Not Available`\nUsage : `pause_tourney <registration_channel>`\nExample : `&pause_tourney #register-here`\nNote : You Can Also Use channel_id", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command()
    async def tourney(self, ctx):
        em = discord.Embed(description="Aliases : `Not Available`\nUsage : `tourney <registration_channel>`\nExample : `&tourney #register-here`\nNote : You Can Also Use channel_id", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command()
    async def _gsetup(self, ctx):
        em = discord.Embed(description="Aliases : `Not Available`\nUsage : `_gsetup <registration_channel>`\nExample : `&_gsetup #register-here`\nNote : You Can Also Use channel_id", color=0x00ff00)
        await ctx.send(embed=em)
#Utils Related
    @help.command()
    async def tts(self, ctx):
        em = discord.Embed(description=f"Aliases : `Not Available`\nUsage : `tts <sentense>`\nExample : `&tts hello {ctx.author.name}`", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command(aliases=["steal"])
    async def addemoji(self, ctx):
        em = discord.Embed(description="Aliases : `Not Available`\nUsage : `addemoji <emoji>`\nExample : `&addemoji` <:vf:947194381172084767>", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command(aliases=["av"])
    async def avatar(self, ctx):
        em = discord.Embed(description="Aliases : `av`\nUsage : `avatar|av [user=None]`\nExample : `&av @hunter87`\ndescription : Use This Command To Get Avatar Of User", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command(aliases=["bnr"])
    async def banner(self, ctx):
        em = discord.Embed(description="Aliases : `bnr`\nUsage : `banner|bnr [user=None]`\nExample : `&bnr @hunter87`", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command(aliases=["bi"])
    async def botinfo(self, ctx):
        em = discord.Embed(description="Aliases : `bi`\nUsage : `botinfo`\nDescription : `Use This Command To Get The Details About Me`", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command(aliases=["emb"])
    async def embed(self, ctx):
        em = discord.Embed(description=f"Aliases : `emb`\nUsage : `embed <message>`\nExample : `&emb hello` {ctx.author.mention}", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command(aliases=["em"])
    async def embed_img(self, ctx):
        em = discord.Embed(description=f"Aliases : `em`\nUsage : `embed <image_url> <message>`\nExample : `&emb https://bit.ly/3d39vhz hello` {ctx.author.mention}", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command(aliases=["sav"])
    async def server_av(self, ctx):
        em = discord.Embed(description=f"Aliases : `sav`\nUsage : `server_av [server_id=None]`\nExample : `&sav`", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command(aliases=["mc"])
    async def member_count(self, ctx):
        em = discord.Embed(description=f"Aliases : `mc`\nUsage : `member_count`\nExample : `&mc`", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command()
    async def support(self, ctx):
        em = discord.Embed(description=f"Aliases : `Not Available`\nUsage : `support`\nExample : `&support`", color=0x00ff00)
        await ctx.send(embed=em)


    @help.command()
    async def invite(self, ctx):
        em = discord.Embed(description=f"Aliases : `Not Available`\nUsage : `invite`\nExample : `&invite`", color=0x00ff00)
        await ctx.send(embed=em)

        
    @help.command()
    async def vote(self, ctx):
        em = discord.Embed(description=f"Aliases : `Not Available`\nUsage : `vote`\nExample : `&vote`", color=0x00ff00)
        await ctx.send(embed=em)


    @help.command(aliases=["nick_name"])
    async def nick(self, ctx):
        em = discord.Embed(description=f"Aliases : `Not Available`\nUsage : `nick <member> <new_name>`\nExample : `&nick` {ctx.author.mention} akash friend", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command(aliases=["ui"])
    async def userinfo(self, ctx):
        em = discord.Embed(description=f"Aliases : `ui`\nUsage : `userinfo [member=None]`\nExample : `&ui` {ctx.author.mention}", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command(aliases=["si"])
    async def serverinfo(self, ctx):
        em = discord.Embed(description=f"Aliases : `si`\nUsage : `serverinfo`\nExample : `&si`", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command()
    async def whoiss(self, ctx):
        em = discord.Embed(description=f"Aliases : `Not Available`\nUsage : `whoiss <member>`\nExample : `&whoiss` {ctx.author.mention}", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command()
    async def toss(self, ctx):
        em = discord.Embed(description=f"Aliases : `Not Available`\nUsage : `toss`\nExample : `&toss`", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command()
    async def nitro(self, ctx):
        em = discord.Embed(description=f"Aliases : `Not Available`\nUsage : `nitro`\nExample : `&nitro`", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command()
    async def prefix(self, ctx):
        em = discord.Embed(description=f"Aliases : `Not Available`\nUsage : `prefix`\nExample : `&prefix`", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command()
    async def react(self, ctx):
        em = discord.Embed(description=f"Aliases : `Not Available`\nUsage : `react <message_id> <emoji>`\nExample : `&react 7456213462634` <:vf:947194381172084767>", color=0x00ff00)
        await ctx.send(embed=em)




#Music Related
    @help.command(aliases=["p"])
    async def play(self, ctx):
        em = discord.Embed(description="Aliases : `p`\nUsage : `play <Song_name>`\nExample : `&p Faded`\nNote : You Mus Joined A VoiceChannel", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command()
    async def pause(self, ctx):
        em = discord.Embed(description="Aliases : `Not Available`\nUsage : `pause`\nExample : `&pause`", color=0x00ff00)
        await ctx.send(embed=em)


    @help.command(aliases=["resm"])
    async def resume(self, ctx):
        em = discord.Embed(description="Aliases : `Not Available`\nUsage : `resume`\nExample : `&resume`", color=0x00ff00)
        await ctx.send(embed=em)


    @help.command(aliases=["lup"])
    async def loop(self, ctx):
        em = discord.Embed(description="Aliases : `Not Available`\nUsage : `loop`\nExample : `&loop`\nDescription: Use This Command To Loop The Current Audio!", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command()
    async def join(self, ctx):
        em = discord.Embed(description="Aliases : `Not Available`\nUsage : `join`\nExample : `&join`", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command()
    async def leave(self, ctx):
        em = discord.Embed(description="Aliases : `Not Available`\nUsage : `leave`\nExample : `&leave`", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command()
    async def stop(self, ctx):
        em = discord.Embed(description="Aliases : `Not Available`\nUsage : `stop`\nExample : `&stop`", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command()
    async def skip(self, ctx):
        em = discord.Embed(description="Aliases : `Not Available`\nUsage : `skip`\nExample : `&skip`", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command()
    async def queue(self, ctx):
        em = discord.Embed(description="Aliases : `Not Available`\nUsage : `queue`\nExample : `&queue`", color=0x00ff00)
        await ctx.send(embed=em)



async def setup(bot):
    await bot.add_cog(Helper(bot))