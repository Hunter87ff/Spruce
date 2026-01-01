"""
                    GNU GENERAL PUBLIC LICENSE
                       Version 3, 29 June 2007

 Copyright (C) 2022-present hunter87.dev@gmail.com
 Everyone is permitted to copy and distribute verbatim copies
 of this license document, but changing it is not allowed.
 """


import discord
from discord.ext import commands
from discord.ui import Button, View
from config import PREFIX, INVITE_URL
from ext import emoji, EmbedBuilder
from typing import TYPE_CHECKING
from core.abstract import Cog


if TYPE_CHECKING:
    from core.bot import Spruce


invbtn = Button(label="Invite", url=INVITE_URL)
votebtn = Button(label="Vote", url="https://top.gg/bot/931202912888164474/vote")
support_serverbtn = Button(label="Support Server", url="https://discord.gg/vMnhpAyFZm")
donate_btn = Button(label="Donate", url="https://discord.gg/x4sUyxttnf")

hel_p = f"• Prefix - `{PREFIX}`\n• Total Commands - `88` | Usable - `79`\n• Type `{PREFIX}help <command | category>` for more info\n\n"
helpemb  = EmbedBuilder(
    
    title="Spruce Help Menu",
    description=f"{hel_p}**__Categories__\n\n{emoji.mod} Moderation\n\n{emoji.setting} Utility\n\n{emoji.cup} Tourney\n\n{emoji.cup} Scrims\n\n{emoji.role} Role\n\n{emoji.music_disk} Music**",
)
musicemb = EmbedBuilder(
    description=f"{hel_p}__**Musics[Disabled]**__\n`play`, `pause`, `resume`, `queue`, `skip`, `loop`, `stop`, `join`, `leave`"
)
modemb   = EmbedBuilder(
    description=f"{hel_p}__**Moderation**__\n`clear`, `clear_perms`, `channel_del`, `channel_make`, `create_channel`, `delete_category`, `mute`, `unmute`, `kick`, `ban`, `hide`, `unhide`, `lock`, `unlock`, `hide_category`, `unhide_category`, `lock_category`, `unlock_category`"
)

espemb   = EmbedBuilder(
    description=f"{hel_p}__**Tourney**__\n`setup`, `add_slot`, `cancel_slot`, `ignore_me`,`change_slot`, `pause`, `start`, `config`, `faketag`, `girls_lobby`, `auto_group`, `tconfig`, `export`, `set log`"
)

scrimemb = EmbedBuilder(
    description=f"{hel_p}__**Scrims**__\n`scrim create`, `scrim start`, `scrim idp`, `scrim audit`, `scrim info`, `scrim cancel_slot`, `scrim delete`, `scrim toggle`, `scrim list`, `scrim reserved_slots`, `scrim set log`, `scrim set idp_channel`, `scrim set fake_tag`, `scrim set idp_role`, `scrim set ping_role`, `scrim set mentions`, `scrim set total_slots`, `scrim set open_time`, `scrim set close_time`, `scrim set time_zone`, `scrim set reg_channel`, `scrim set slot_channel`, `scrim set manager`, `scrim setup group`, `scrim add reserved_slots`, `scrim add slot`, `scrim remove reserved_slots`"
)
roleemb  = EmbedBuilder(
    description=f"{hel_p}__**Roles**__\n`create_roles`, `port`, `inrole`, `remove_roles`, `del_roles`, `give_roles`, `remove_role_members`, `role_all_bot`, `role_all_human`, `hide_roles`, `unhide_roles`"
)
utilemb  = EmbedBuilder(
    description=f"{hel_p}__**Utility**__\n`addemoji`, `tts`, `avatar`, `banner`, `botinfo`, `ping`, `embed`, `embed_img`, `member_count`, `nick`, `nitro`, `prefix`, `react`, `server_av`, `serverinfo`, `toss`, `userinfo`, `whoiss`, `uptime`, `vote`, `support`, `invite`, `setup_ticket`"
)

buttons =[invbtn, votebtn, support_serverbtn, donate_btn]


def get_thum(ctx:commands.Context):
    return ctx.guild.me.display_avatar if ctx.guild.me else ctx.author.display_avatar 

class Dropdown(discord.ui.Select):
    def __init__(self):

        options = [
            discord.SelectOption(label='Main', description='Select For All Commands'),
            discord.SelectOption(label='Tourney', description='Select For Tournament Commands'),
            discord.SelectOption(label='Scrim', description='Select For Scrim Commands'),
            discord.SelectOption(label='Music', description='Select For Music Commands'),
            discord.SelectOption(label='Moderation', description='Select For Moderation Commands'),
            discord.SelectOption(label='Utility', description='Select For Utility Commands'),
            discord.SelectOption(label='Role', description='Select For Role Commands'),
        ]
        super().__init__(placeholder='Choose Command Category...', min_values=1, max_values=1, options=options)

    async def callback(self, ctx: discord.Interaction):
        if self.values[0] == "Music":
            await ctx.response.edit_message(embed=musicemb.set_thumbnail(url=get_thum(ctx)).set_footer(text=f"Requested By {ctx.user}", icon_url=ctx.user.display_avatar))
        if self.values[0] == "Moderation":
            await ctx.response.edit_message(embed=modemb.set_thumbnail(url=get_thum(ctx)).set_footer(text=f"Requested By {ctx.user}", icon_url=ctx.user.display_avatar))
        if self.values[0] == "Tourney":
            await ctx.response.edit_message(embed=espemb.set_thumbnail(url=get_thum(ctx)).set_footer(text=f"Requested By {ctx.user}", icon_url=ctx.user.display_avatar))
        if self.values[0] == "Scrim":
            await ctx.response.edit_message(embed=scrimemb.set_thumbnail(url=get_thum(ctx)).set_footer(text=f"Requested By {ctx.user}", icon_url=ctx.user.display_avatar))
        if self.values[0] == "Main":
            await ctx.response.edit_message(embed=helpemb.set_thumbnail(url=get_thum(ctx)).set_footer(text=f"Requested By {ctx.user}", icon_url=ctx.user.display_avatar))
        if self.values[0] == "Utility":
            await ctx.response.edit_message(embed=utilemb.set_thumbnail(url=get_thum(ctx)).set_footer(text=f"Requested By {ctx.user}", icon_url=ctx.user.display_avatar))
        if self.values[0] == "Role":
            await ctx.response.edit_message(embed=roleemb.set_thumbnail(url=get_thum(ctx)).set_footer(text=f"Requested By {ctx.user}", icon_url=ctx.user.display_avatar))

class DropdownView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(Dropdown())

class HelperCog(Cog):
    def __init__(self, bot:"Spruce"):
        self.bot= bot
        self.bot.remove_command("help")
        self.PREFIX = PREFIX


    @commands.group(invoke_without_command=True,aliases=['commands', 'hel', "h"])
    async def help(self, ctx:commands.Context):
        if ctx.author.bot:return
        view = DropdownView()
        for opt in buttons:view.add_item(opt)
        await ctx.send(embed=helpemb.set_thumbnail(url=get_thum(ctx)).set_footer(text=f"Requested By {ctx.author}", icon_url=ctx.author.display_avatar), view=view)



    @help.group(invoke_without_command=True,aliases=['music'])
    async def Music(self, ctx:commands.Context):
        view = View()
        for bt in buttons:view.add_item(bt)
        await ctx.send(embed=musicemb.set_thumbnail(url=get_thum(ctx)).set_footer(text=f"Requested By {ctx.author}", icon_url=ctx.author.display_avatar), view=view)



    @help.group(invoke_without_command=True,aliases=['mod', "moderation"])
    async def Moedration(self, ctx:commands.Context):
        view = View()
        for bt in buttons:
            view.add_item(bt)
        await ctx.send(embed=modemb.set_thumbnail(url=get_thum(ctx)).set_footer(text=f"Requested By {ctx.author}", icon_url=ctx.author.display_avatar), view=view)



    @help.group(invoke_without_command=True,aliases=["tourney"])
    async def Esports(self, ctx:commands.Context):
        view = View()
        for bt in buttons:
            view.add_item(bt)
        await ctx.send(embed=espemb.set_thumbnail(url=get_thum(ctx)).set_footer(text=f"Requested By {ctx.author}", icon_url=ctx.author.display_avatar), view=view)


    @help.group(invoke_without_command=True,aliases=['scrim'])
    async def Scrim(self, ctx:commands.Context):
        view = View()
        for bt in buttons:
            view.add_item(bt)
        await ctx.send(embed=scrimemb.set_thumbnail(url=get_thum(ctx)).set_footer(text=f"Requested By {ctx.author}", icon_url=ctx.author.display_avatar), view=view)


    @help.group(invoke_without_command=True)
    async def Role(self, ctx:commands.Context):
        view = View()
        
        for bt in buttons:
            view.add_item(bt)
        await ctx.send(embed=roleemb.set_thumbnail(url=get_thum(ctx)).set_footer(text=f"Requested By {ctx.author}", icon_url=ctx.author.display_avatar), view=view)



    @help.group(invoke_without_command=True)
    async def Utility(self, ctx:commands.Context):
        view = View()
        for bt in buttons:
            view.add_item(bt)
        await ctx.send(embed=utilemb.set_thumbnail(url=get_thum(ctx)).set_footer(text=f"Requested By {ctx.author}", icon_url=ctx.author.display_avatar), view=view)




###################
#Moderation Related
###################
    @help.command()
    async def ban(self, ctx:commands.Context):
        em = discord.Embed(description=f"Aliases : `Not Available`\nUsage : `ban <member>`\nExample : `{self.PREFIX}ban @abhi`", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command()
    async def kick(self, ctx:commands.Context):
        em = discord.Embed(description=f"Aliases : `Not Available`\nUsage : `kick <member>`\nExample : `{self.PREFIX}kick @abhi`", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command(aliases=["purge"])
    async def clear(self, ctx:commands.Context):
        em = discord.Embed(description=f"Aliases : `purge`\nUsage : `clear|purge [amount=None]`\nExample : `{self.PREFIX}clear 10`", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command()
    async def mute(self, ctx:commands.Context):
        em = discord.Embed(description=f"Aliases : `Not Available`\nUsage : `mute <member> [reason=None]`\nExample : `{self.PREFIX}mute @abhi spamming`", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command()
    async def unmute(self, ctx:commands.Context):
        em = discord.Embed(description=f"Aliases : `Not Available`\nUsage : `unmute <member> [reason=None]`\nExample : `{self.PREFIX}unmute @abhi spamming`", color=0x00ff00)
        await ctx.send(embed=em)


    @help.command()
    async def hide(self, ctx:commands.Context):
        em = discord.Embed(description=f"Aliases : `Not Available`\nUsage : `hide role(optional) channel(optional)`\nExample : `{self.PREFIX}hide`\n", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command()
    async def unhide(self, ctx:commands.Context):
        em = discord.Embed(description=f"Aliases : `Not Available`\nUsage : `unhide [role=None]`\nExample : `{self.PREFIX}unhide`\n", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command()
    async def lock(self, ctx:commands.Context):
        em = discord.Embed(description=f"Aliases : `Not Available`\nUsage : `lock [role=None]`\nExample : `{self.PREFIX}lock`\n", color=0x00ff00)
        await ctx.send(embed=em)


    @help.command()
    async def unlock(self, ctx:commands.Context):
        em = discord.Embed(description=f"Aliases : `Not Available`\nUsage : `unlock [role=None]`\nExample : `{self.PREFIX}unlock`\n", color=0x00ff00)
        await ctx.send(embed=em)

################
#Channel Related
################
    @help.command(aliases=["chd"])
    async def channel_del(self, ctx:commands.Context):
        em = discord.Embed(description=f"Aliases : `chd`\nUsage : `channel_del [channels...]`\nExample : `{self.PREFIX}channel_del #general #updates`", color=0x00ff00)
        await ctx.send(embed=em)


    @help.command(aliases=["chm"])
    async def channel_make(self, ctx:commands.Context):
        em = discord.Embed(description=f"Aliases : `chm`\nUsage : `channel_make [names...]`\nExample : `{self.PREFIX}channel_make general updates`", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command(aliases=["cch"])
    async def create_channel(self, ctx:commands.Context):
        em = discord.Embed(description=f"Aliases : `cch`\nUsage : `create_channel <category> [names...]`\nExample : `{self.PREFIX}create_channel 32745216342163 general memes announcements`", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command(aliases=["dc"])
    async def delete_category(self, ctx:commands.Context):
        em = discord.Embed(description=f"Aliases : `dc`\nUsage : `delete_category <category>`\nExample : `{self.PREFIX}dc 7654123645287`\nDescription : `Use This Command To Delete A Hole Category | You Must Have Administrator Permission`", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command(aliases=["hc"])
    async def hide_category(self, ctx:commands.Context):
        em = discord.Embed(description=f"Aliases : `hc`\nUsage : `hide_category <category> [role=None]`\nExample : `{self.PREFIX}hc 7654123645287`\nDescription : `Use This Command To Hide A Hole Category`", color=0x00ff00)
        await ctx.send(embed=em)     

    @help.command(aliases=["ulc"])
    async def unlock_category(self, ctx:commands.Context):
        em = discord.Embed(description=f"Aliases : `ulc`\nUsage : `unlock_category <category> [role=None]`\nExample : `{self.PREFIX}ulc 7654123645287`\nDescription : `Use This Command To unlock A Hole Category`", color=0x00ff00)
        await ctx.send(embed=em)  

    @help.command(aliases=["lc"])
    async def lock_category(self, ctx:commands.Context):
        em = discord.Embed(description=f"Aliases : `lc`\nUsage : `lock_category <category> [role=None]`\nExample : `{self.PREFIX}lc 7654123645287`\nDescription : `Use This Command To lock A Hole Category`", color=0x00ff00)
        await ctx.send(embed=em) 

    @help.command(aliases=["uhc"])
    async def uhide_category(self, ctx:commands.Context):
        em = discord.Embed(description=f"Aliases : `uhc`\nUsage : `uhc <category_id> [role=None]`\nExample : `{self.PREFIX}uhc 73462546213542614526`\n", color=0x00ff00)
        await ctx.send(embed=em)




#############
#Role Related
#############
    @help.command()
    async def inrole(self, ctx:commands.Context):
        em = discord.Embed(description=f"Aliases : `Not Available`\nUsage : `inrole`\nExample : `{self.PREFIX}inrole`", color=0x00ff00)
        await ctx.send(embed=em)


    @help.command()
    async def port(self, ctx:commands.Context):
        em = discord.Embed(description=f"Aliases : `Not Available`\nUsage : `port <role1> <role2>`\nExample : `{self.PREFIX}port @ipl-group1 @ipl-group2`", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command(aliases=["croles", "crole"])
    async def create_roles(self, ctx:commands.Context):
        em = discord.Embed(description=f"Aliases : `croles`\nUsage : `create_roles [Names...]`\nExample : `{self.PREFIX}create_roles family male female`", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command(aliases=["role", "role_give"])
    async def give_role(self, ctx:commands.Context):
        em = discord.Embed(description=f"Aliases : `role`\nUsage : `give_role <role> [members...]`\nExample : `{self.PREFIX}role @Male @hunter`", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command()
    async def give_roles(self, ctx:commands.Context):
        em = discord.Embed(description=f"Aliases : `role`\nUsage : `give_roles <member> [roles...]`\nExample : `{self.PREFIX}role @hunter @male @18+`", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command(aliases=["role_remove", "role_re"])
    async def remove_role(self, ctx:commands.Context):
        em = discord.Embed(description=f"Aliases : `Not Available`\nUsage : `remove_role <role> [memebrs...]`\nExample : `{self.PREFIX}remove_role @Male @hunter`", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command(aliases=["droles", "drole"])
    async def del_roles(self, ctx:commands.Context):
        em = discord.Embed(description=f"Aliases : `droles`\nUsage : `del_roles [roles...]`\nExample : `{self.PREFIX}del_roles @group1 @group2`", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command(aliases=["ra_role"])
    async def remove_role_members(self, ctx:commands.Context):
        em = discord.Embed(description=f"Aliases : `ra_role`\nUsage : `ra_role <roles>`\nExample : `{self.PREFIX}ra_role @humans`\nDescription : Use This Command To Remove A Role From Everyone", color=0x00ff00)
        await ctx.send(embed=em)


    @help.command()
    async def role_all_human(self, ctx:commands.Context):
        em = discord.Embed(description=f"Aliases : `Not Available`\nUsage : `role_all_human  <role>`\nExample : `{self.PREFIX}role_all_human @members`\nDescription : This command gives a particular role to all the humans", color=0x00ff00)
        await ctx.send(embed=em)


    @help.command()
    async def role_all_bot(self, ctx:commands.Context):
        em = discord.Embed(description=f"Aliases : `Not Available`\nUsage : `role_all_bot <role>`\nExample : `{self.PREFIX}role_all_bot @members`\nDescription : This command gives a particular role to all the bots", color=0x00ff00)
        await ctx.send(embed=em)


    @help.command(aliases=["cperms"])
    async def clear_perms(self, ctx:commands.Context):
        em = discord.Embed(description=f"Aliases : `Not Available`\nUsage : `clear_perms [role=None]`\nExample : `{self.PREFIX}clear_perms @public`\nDescription : Use this command to remove all permissions from roles\nif no role mentioned it'll remove all permissions from all roles", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command(aliases=["hr"])
    async def hide_roles(self, ctx:commands.Context):
        em = discord.Embed(description=f"Aliases : `hr`\nUsage : `hide_roles`\nExample : `{self.PREFIX}hide_roles`\nDescription : Use this command to hide all roles in memebr list", color=0x00ff00)
        await ctx.send(embed=em)


    @help.command(aliases=["uhr"])
    async def unhide_roles(self, ctx:commands.Context):
        em = discord.Embed(description=f"Aliases : `uhr`\nUsage : `unhide_roles [roles..]`\nExample : `{self.PREFIX}unhide_roles @moderator @Admin`\nDescription : Use this command to roles roles in memebr list", color=0x00ff00)
        await ctx.send(embed=em)



######################	
#Esports Help Commands
######################

    @help.command()
    async def export_event_data(self, ctx:commands.Context):
        em = discord.Embed(description=f"Aliases : `Not Available`\nUsage : `export_event_data <registration_channel>`\nExample : `{self.PREFIX}export_event_data #register-here`\nDescription : Use this command to export event data", color=0x00ff00)
        await ctx.send(embed=em)


    @help.command(aliases=["tc"])
    async def tconfig(self, ctx:commands.Context):
        em = discord.Embed(description=f"Aliases : `tc`\nUsage : `tconfig`\nExample : `{self.PREFIX}tconfig`\nUse this command to see the list of ongoing tournament on the server!!", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command(aliases=["cs"])
    async def change_slot(self, ctx:commands.Context):
        em = discord.Embed(description=f"Aliases : `cs`\nUsage : `change_slot <exact_teame> <mention>`\nExample : `{self.PREFIX}change_slot HG ESPORTS @hunter `\nDescription: Use This Command By Replying The Group Message! And Use The Exact Slot Detail Otherwise It'll Not Work", color=0x00ff00)
        em.set_image(url="https://media.discordapp.net/attachments/892682901404123137/1057515803823587440/Debut_2022-12-28_09_58_39.png?width=879&height=462")
        await ctx.send(embed=em)

    @help.command(aliases=["pub"])
    async def publish(self, ctx:commands.Context):
        em = discord.Embed(description=f"Aliases : `Not Available`\nUsage : `publish <registration_channel> <prize>`\nExample : `{self.PREFIX}publish #register-here  100K INR`", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command()
    async def tourneys(self, ctx:commands.Context):
        em = discord.Embed(description=f"Aliases : `Not Available`\nUsage : `tourneys`\nExample : `{self.PREFIX}tourneys`\nDescription: By using this command! you'll get a list of ongoing tournaments to register", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command(aliases=["autogroup"])
    async def auto_group(self, ctx:commands.Context):
        em = discord.Embed(description=f"Aliases : `Not Available`\nUsage : `auto_group <registration_channel>`\nExample : `{self.PREFIX}auto_group <registration_channel> `\nDescription: By using this command it'll create total group system of the tournament\n\nNote: Make sure no one should send messages in  confirm channel. else it'll not work\nAnd Only use this command if the registration if end or you want to start the tournament\n\n[Watch Tutorial](https://www.youtube.com/watch?v=_ylU69sogAU)", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command(aliases=["add"])
    async def add_slot(self, ctx:commands.Context):
        em = discord.Embed(description=f"Aliases : `Not Available`\nUsage : `add_slot <registration_channel> <member> <Team_Name>`\nExample : `{self.PREFIX}add_slot #register-here @ayush Team Element`\ndescription : Use This Command To Add Slot To An ongoing Tournament", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command(aliases=["cancel"])
    async def cancel_slot(self, ctx:commands.Context):
        em = discord.Embed(description=f"Aliases : `Not Available`\nUsage : `cancel_slot <registration_channel> <member> [reason=None]`\nExample : `{self.PREFIX}cancel_slot #register-here @rahul abusing`\ndescription : Use This Command To Cancel A Slot Of A Tournament", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command(aliases=["ftf", "ft"])
    async def faketag(self, ctx:commands.Context):
        em = discord.Embed(description=f"Aliases : `Not Available`\nUsage : `faketag <registration_channel>`\nExample : `{self.PREFIX}faketag #register-here`\ndescription : Use This Command To enable/disable Faketag Filter Of A Tournament", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command(aliases=['gsetup'])
    async def group_setup(self, ctx:commands.Context):
        em = discord.Embed(description=f"Aliases : `gsetup`\nUsage : `group_setup <prefix> <starting group no> <end group no.> [category=None]`\nExample : `{self.PREFIX}group_setup ws 1 14`\nNote: To create automated groups, run `{self.PREFIX}help auto_group` command\n Here 1 means group1 and 14 means group14\nIf You Already Have a Category You Can Put The Category Id At Last", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command(aliases=['grls_lobby', "girls_lby"])
    async def girls_lobby(self, ctx:commands.Context):
        em = discord.Embed(description=f"Aliases : `Not Available`\nUsage : `girls_lobby <vc_amount>`\nExample : `{self.PREFIX}girls_lobby 12`", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command(aliases=['ts', "tsetup", "setup"])
    async def tourney_setup(self, ctx:commands.Context):
        em = discord.Embed(description=f"Aliases : `ts`\nUsage : `tourney_setup <total_slot> <mentions> <number_of_slot_per_group> <tournament_name>`\nExample : `{self.PREFIX}ts 144 4 12 WEEKLY SCRIM`\nNote : You must have @tourney-mod Role to manage the tournament\n\n**[Watch Tutorial](https://www.youtube.com/watch?v=bVJWdVGHxRc)**", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command()
    async def start_tourney(self, ctx:commands.Context):
        em = discord.Embed(description="Aliases : `Not Available`\nUsage : `start <registration_channel>`\nExample : `/tourney start #register-here`\nNote : You Can Also Use channel_id", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command(aliases=['ps_tourney', "tourney_pause"])
    async def pause_tourney(self, ctx:commands.Context):
        em = discord.Embed(description="Aliases : `Not Available`\nUsage : `pause <registration_channel>`\nExample : `/tourney pause #register-here`\nNote : You Can Also Use channel_id", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command()
    async def config(self, ctx:commands.Context):
        em = discord.Embed(description="Aliases : `Not Available`\nUsage : `config <registration_channel>`", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command()
    async def set_manager(self, ctx:commands.Context):
        em = discord.Embed(description=f"Aliases : `Not Available`\nUsage : `set_manager <registration_channel>`\nExample : `{self.PREFIX}set_manager #register-here`\nNote : You Can Also Use registration channel_id", color=0x00ff00)
        await ctx.send(embed=em)

##############        
#Utils Related
##############

    @help.command()
    async def tts(self, ctx:commands.Context):
        em = discord.Embed(description=f"Aliases : `Not Available`\nUsage : `tts <sentense>`\nExample : `{self.PREFIX}tts hello {ctx.author.name}`", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command(aliases=["steal"])
    async def addemoji(self, ctx:commands.Context):
        em = discord.Embed(description=f"Aliases : `Not Available`\nUsage : `addemoji <emoji>`\nExample : `{self.PREFIX}addemoji` <:vf:947194381172084767>", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command(aliases=["av"])
    async def avatar(self, ctx:commands.Context):
        em = discord.Embed(description=f"Aliases : `av`\nUsage : `avatar|av [user=None]`\nExample : `{self.PREFIX}av @hunter87`\ndescription : Use This Command To Get Avatar Of User", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command(aliases=["bnr"])
    async def banner(self, ctx:commands.Context):
        em = discord.Embed(description=f"Aliases : `bnr`\nUsage : `banner|bnr [user=None]`\nExample : `{self.PREFIX}bnr @hunter87`", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command(aliases=["bi"])
    async def botinfo(self, ctx:commands.Context):
        em = discord.Embed(description="Aliases : `bi`\nUsage : `botinfo`\nDescription : `Use This Command To Get The Details About Me`", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command(aliases=["emb"])
    async def embed(self, ctx:commands.Context):
        em = discord.Embed(description=f"Aliases : `emb`\nUsage : `embed <message>`\nExample : `{self.PREFIX}emb hello` {ctx.author.mention}", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command(aliases=["em"])
    async def embed_img(self, ctx:commands.Context):
        em = discord.Embed(description=f"Aliases : `em`\nUsage : `embed <image_url> <message>`\nExample : `{self.PREFIX}emb https://bit.ly/3d39vhz hello` {ctx.author.mention}", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command(aliases=["sav"])
    async def server_av(self, ctx:commands.Context):
        em = discord.Embed(description=f"Aliases : `sav`\nUsage : `server_av [server_id=None]`\nExample : `{self.PREFIX}sav`", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command(aliases=["mc"])
    async def member_count(self, ctx:commands.Context):
        em = discord.Embed(description=f"Aliases : `mc`\nUsage : `member_count`\nExample : `{self.PREFIX}mc`", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command()
    async def support(self, ctx:commands.Context):
        em = discord.Embed(description=f"Aliases : `Not Available`\nUsage : `support`\nExample : `{self.PREFIX}support`", color=0x00ff00)
        await ctx.send(embed=em)


    @help.command()
    async def invite(self, ctx:commands.Context):
        em = discord.Embed(description=f"Aliases : `Not Available`\nUsage : `invite`\nExample : `{self.PREFIX}invite`", color=0x00ff00)
        await ctx.send(embed=em)

        
    @help.command()
    async def vote(self, ctx:commands.Context):
        em = discord.Embed(description=f"Aliases : `Not Available`\nUsage : `vote`\nExample : `{self.PREFIX}vote`", color=0x00ff00)
        await ctx.send(embed=em)


    @help.command(aliases=["nick_name"])
    async def nick(self, ctx:commands.Context):
        em = discord.Embed(description=f"Aliases : `Not Available`\nUsage : `nick <member> <new_name>`\nExample : `{self.PREFIX}nick` {ctx.author.mention} akash friend", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command(aliases=["ui"])
    async def userinfo(self, ctx:commands.Context):
        em = discord.Embed(description=f"Aliases : `ui`\nUsage : `userinfo [member=None]`\nExample : `{self.PREFIX}ui` {ctx.author.mention}", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command(aliases=["si"])
    async def serverinfo(self, ctx:commands.Context):
        em = discord.Embed(description=f"Aliases : `si`\nUsage : `serverinfo`\nExample : `{self.PREFIX}si`", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command()
    async def whoiss(self, ctx:commands.Context):
        em = discord.Embed(description=f"Aliases : `Not Available`\nUsage : `whoiss <member>`\nExample : `{self.PREFIX}whoiss` {ctx.author.mention}", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command()
    async def toss(self, ctx:commands.Context):
        em = discord.Embed(description=f"Aliases : `Not Available`\nUsage : `toss`\nExample : `{self.PREFIX}toss`", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command()
    async def nitro(self, ctx:commands.Context):
        em = discord.Embed(description=f"Aliases : `Not Available`\nUsage : `nitro`\nExample : `{self.PREFIX}nitro`", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command()
    async def prefix(self, ctx:commands.Context):
        em = discord.Embed(description=f"Aliases : `Not Available`\nUsage : `prefix`\nExample : `{self.PREFIX}prefix`", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command()
    async def react(self, ctx:commands.Context):
        em = discord.Embed(description=f"Aliases : `Not Available`\nUsage : `react <message_id> <emoji>`\nExample : `{self.PREFIX}react 7456213462634` <:vf:947194381172084767>", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command()
    async def translate(self, ctx:commands.Context):
        em = discord.Embed(description="Aliases : `Not Available`\nUsage : `translate fr:<from_lang> to:<to_lang>`\nExample : `/translate ` fr:English` `to:Hindi` `message:one earth one family one future`", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command()
    async def setup_ticket(self, ctx:commands.Context):
        em = discord.Embed(description="Aliases : `Not Available`\nUsage : `setup_ticket`mod_role, button_label, button_emoji, button_color:choose from dropdown, *, message\nExample : `/setup_ticket` `mod_role`: `@tourney-mod` `button_label`: `Claim Reward` `button_emoji`: `<:mobile:1048673949812273252>` `button_color`: `red`", color=0x00ff00)
        await ctx.send(embed=em)


##############
#Music Related
##############
    @help.command(aliases=["p"])
    async def play(self, ctx:commands.Context):
        em = discord.Embed(description=f"Aliases : `p`\nUsage : `play <Song_name>`\nExample : `{self.PREFIX}p Faded`\nNote : You Mus Joined A VoiceChannel", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command()
    async def pause(self, ctx:commands.Context):
        em = discord.Embed(description=f"Aliases : `Not Available`\nUsage : `pause`\nExample : `{self.PREFIX}pause`", color=0x00ff00)
        await ctx.send(embed=em)


    @help.command(aliases=["resm"])
    async def resume(self, ctx:commands.Context):
        em = discord.Embed(description=f"Aliases : `Not Available`\nUsage : `resume`\nExample : `{self.PREFIX}resume`", color=0x00ff00)
        await ctx.send(embed=em)


    @help.command(aliases=["lup"])
    async def loop(self, ctx:commands.Context):
        em = discord.Embed(description=f"Aliases : `Not Available`\nUsage : `loop`\nExample : `{self.PREFIX}loop`\nDescription: Use This Command To Loop The Current Audio!", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command()
    async def join(self, ctx:commands.Context):
        em = discord.Embed(description=f"Aliases : `Not Available`\nUsage : `join`\nExample : `{self.PREFIX}join`", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command()
    async def leave(self, ctx:commands.Context):
        em = discord.Embed(description=f"Aliases : `Not Available`\nUsage : `leave`\nExample : `{self.PREFIX}leave`", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command()
    async def stop(self, ctx:commands.Context):
        em = discord.Embed(description=f"Aliases : `Not Available`\nUsage : `stop`\nExample : `{self.PREFIX}stop`", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command()
    async def skip(self, ctx:commands.Context):
        em = discord.Embed(description=f"Aliases : `Not Available`\nUsage : `skip`\nExample : `{self.PREFIX}skip`", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command()
    async def queue(self, ctx:commands.Context):
        em = discord.Embed(description=f"Aliases : `Not Available`\nUsage : `queue`\nExample : `{self.PREFIX}queue`", color=0x00ff00)
        await ctx.send(embed=em)

    @help.command()
    async def spotify(self, ctx:commands.Context):
        em = discord.Embed(description=f"Aliases : `Not Available`\nUsage : `spotify <playlist_url>`\nExample : `{self.PREFIX}spotify https://open.spotify.com/playlist/3WhVWKNAY2Y9DNU5GVPYE2`", color=0x00ff00)
        await ctx.send(embed=em)