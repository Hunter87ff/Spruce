"""
A module for managing esports tournaments in a Discord server.
    :author: hunter87
    :copyright: (c) 2022-present hunter87.dev@gmail.com
    :license: GPL-3, see LICENSE for more details.
"""


import discord
import datetime
import asyncio
from asyncio import sleep
from typing import TYPE_CHECKING
from discord.ext import commands
from discord.ui import Button, View
from discord import app_commands
from modules import checker
from ext import constants, checks, Tourney, emoji, color, files

if TYPE_CHECKING:
    from modules.bot import Spruce  # Type checking


def get_front(name:str):
  li = []
  for i in name.split()[0:2]:li.append(i[0])
  return str("".join(li) + "-")


class EsportsCog(commands.Cog):
    """
    ## EsportsCog
    This class contains commands and event listeners for managing esports tournaments.
    """
    ONLY_AUTHOR_BUTTON = "Only Author Can Use This Button"
    MANAGER_PREFIXES = ["Cslot", "Mslot", "Tname", "Cancel"]

    def __init__(self, bot:'Spruce'):
        self.bot:"Spruce" = bot
        self.dbc = bot.db.dbc
        self.TOURNEY_LOG_CHANNEL_NAME = f"{self.bot.user.name.lower()}-tourney-log"
        self._tnotfound = "Tournament Not Found"


    @commands.Cog.listener()
    async def on_guild_role_delete(self, role:discord.Role):
        members = []
        if self.dbc.find_one({"crole":role.id}):
            db = self.dbc.find_one({"crole":role.id})
            cch = discord.utils.get(role.guild.channels,id=db["cch"])
            messages = cch.history(limit=int(db["tslot"])+50)
            members = {m async for msg in messages for m in role.guild.members if m.mention in msg.content}
            newr = await role.guild.create_role(name=role.name, reason="[Recovering] If You Want To Delete This Role use &tourney command")
            self.dbc.update_one({"crole":int(role.id)}, {"$set" : {"crole" :int(newr.id)}})
            
            for i in members:
                await i.add_roles(newr, reason="[Recovering] Previous Confirm Role Was acidentally Deleted.")


    async def get_input(self, ctx:commands.Context, check=None, timeout=30):
        """
        Asynchronously waits for user input in a Discord context.

        This method waits for a message from the user in the specified Discord context and returns the content of the message.

        Parameters
        ----------
        ctx : commands.Context
            The Discord context in which to wait for input.
        check : Callable, optional
            A function that takes a message and returns a boolean indicating whether the message should be accepted.
            If None, defaults to checking if the message is in the same channel and from the same author as the context.
        timeout : int, optional
            The maximum time to wait for input in seconds, defaults to 30.

        Returns
        -------
        str or Coroutine
            The content of the received message if successful.
            If timeout occurs, returns the coroutine from sending a timeout message.

        Raises
        ------
        asyncio.TimeoutError
            If no message matching the check is received before the timeout.
        """
        check = check or (lambda m: m.channel == ctx.channel and m.author == ctx.author)
        try:
            msg:discord.Message = await self.bot.wait_for("message", check=check, timeout=timeout)
            return msg.content
        except asyncio.TimeoutError:
            return await ctx.send("Time Out! Try Again", delete_after=5)
        


    def is_tourney_mod(self, member:discord.Member):
        return any([
            member.guild_permissions.manage_guild,
            member.guild_permissions.administrator,
            discord.utils.get(member.guild.roles, name="tourney-mod") in member.roles,
        ])
    

    async def log(self, guild:discord.Guild, message:str, color:int=color.cyan):
        """
        Logs a message to the tourney log channel.
        
        Parameters
        ----------
        guild : discord.Guild
            The guild where the log channel is located.
        message : str
            The message to log.
        color : int, optional
            The color of the embed, defaults to color.cyan.
        """
        channel = discord.utils.get(guild.text_channels, name=self.TOURNEY_LOG_CHANNEL_NAME)
        if not channel:
            return 
        
        embed = discord.Embed(description=message, color=color)
        embed.set_author(name=guild.me.name, icon_url=guild.me.avatar)
        await channel.send(embed=embed)


    @commands.hybrid_command(name="tourney_log", description="Setup Tourney Log Channel", aliases=["tlog"])
    @commands.guild_only()
    @app_commands.guild_only()
    @checks.tourney_mod()
    @commands.bot_has_guild_permissions(send_messages=True, attach_files=True, manage_channels=True)
    async def setup_tourney_log(self, ctx:commands.Context):
        await ctx.defer(ephemeral=True)

        if not self.is_tourney_mod(ctx.author):
            return await ctx.send("You don't have `tourney-mod` role or `manager_server` permission to use this command.")


        channel = self.bot.helper.get_tourney_log(ctx.guild)

        if not channel:
            channel = await ctx.guild.create_text_channel(
                name=f"{self.bot.user.name}-tourney-log",
            )

        await channel.set_permissions( ctx.guild.default_role, read_messages =False, )
        await channel.set_permissions( ctx.guild.me, 
                                read_messages =True, 
                                send_messages=True, 
                                attach_files=True, 
                                manage_channels=True, 
                                manage_messages=True, 
                                add_reactions=True, 
                                external_emojis=True
        )
        await ctx.send(f"**Tourney Log Channel Set To {channel.mention}**")
        await channel.send(
            embed=discord.Embed(
                title="Tourney Log Channel Created", 
                description=f"**This Channel Will Be Used To Log Tourney Events**\n\n{emoji.tick} | **Created By** : {ctx.author.mention}", 
                color=color.cyan
            )
        )



    @commands.hybrid_command(name="export_event_data", description="Export Tournament Data to CSV file", aliases=["export_toueney"])
    @commands.guild_only()
    @checks.tourney_mod()
    @app_commands.guild_only()
    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.bot_has_guild_permissions(send_messages=True, attach_files=True)
    @app_commands.describe( registration_channel="The channel where the tournament is registered, usually the registration channel." )
    async def export_event_data(self, ctx:commands.Context, registration_channel:discord.TextChannel):
        if ctx.author.bot:return

        try:
            _event = Tourney.findOne(registration_channel.id)
            if not _event:
                return await ctx.send("No event found in this channel")
            
            _teams = "" ## to store the teams data
            _slot = 1 ## to store the slot number

            _confirm_channel = self.bot.get_channel(_event.cch) ##confirm channel to get the teams data

            # if the confirm channel is not found, return an error message
            if not _confirm_channel:
                return await ctx.send("No confirm channel found")
            
            if not _confirm_channel.permissions_for(ctx.guild.me).read_message_history:
                return await ctx.send(f"insufficient permission to read message history in {_confirm_channel.mention}")

            async for message in _confirm_channel.history(limit=_event.reged+50):
                # if the message author is not the bot, skip it
                if any([
                    message.author.id != ctx.me.id, 
                    not message.embeds,
                    not message.content
                ]): 
                    continue

                # if the message doesn't contains a mention, skip it
                _captain = message.mentions[0]

                _team = message.content.replace(_captain.mention, "").replace(" ", "").replace("\n", "")

                # fetches the teammates from embed description, currently it can can't handle the usernames, just the mentions
                _players = message.embeds[0].description.split("\n")[-1].replace("**Players** : ", "").replace(",", " ") if message.embeds else "Added By Moderator"
                if _captain and _team:
                    _teams += f"{_slot},Team {_team.replace('Team ','')},{_captain}, {_players}\n"
                    _slot += 1

            _content = "Event,Slots,Registered,Mentions,Prize\n"
            _content += f"{_event.tname or registration_channel.category.name},{_event.tslot},{_event.reged-1},{_event.mentions},{_event.prize}\n\n"
            _content += "Slot, Team Name, Captain, players\n"
            _content += _teams

            _filename = f"event_data_{_event.rch}"
            fp, cleanup = files.export_to_csv(
                _content,  
                _filename, 
                lambda module, loc, e: self.bot.embed_log(module, loc, e)
            )
            await ctx.send(file=discord.File(fp, filename=fp))
            cleanup()

        except Exception as e:
            await ctx.send(embed=discord.Embed(description="Something Went Wrong!! please try again later! or contact support server `/support`", color=color.red), delete_after=10)
            await self.bot.embed_log("core.tourney.export_event_data", 134, str(e))




    @commands.hybrid_command(description="Create tournament", with_app_command = True, aliases=['ts','setup', 'tsetup'])
    @app_commands.describe(
        total_slot="Total number of slots for the tournament",
        mentions="Number of mentions required for registration",
        slot_per_group="Number of slots per group",
        name="Name of the tournament"
    )
    @commands.bot_has_guild_permissions(manage_channels=True, manage_roles=True, send_messages=True, add_reactions=True, read_message_history=True)
    @commands.guild_only()
    @app_commands.guild_only()
    @commands.cooldown(1, 30, commands.BucketType.user)
    @checks.tourney_mod()
    async def tourney_setup(self, ctx:commands.Context, total_slot:int, mentions:int, slot_per_group:int,  *, name:str):
        if ctx.author.bot:
            return None

        if slot_per_group < 1:
            return await ctx.send("Slot Per Group Should Be 1 or above")
    
        front = self.bot.helper.get_event_prefix(name)
        try:
            ms = await ctx.send(constants.PROCESSING)
            bt = ctx.guild.get_member(self.bot.user.id)
            tmrole = discord.utils.get(ctx.guild.roles, name="tourney-mod")
            if not tmrole:tmrole = await ctx.guild.create_role(name="tourney-mod")
            if tmrole and not ctx.author.guild_permissions.administrator:
                if tmrole not in ctx.author.roles:
                    return await ctx.send(f"You Must Have {tmrole.mention} role to run rhis command")
                

            if int(total_slot) > self.bot.config.MAX_SLOTS_PER_TOURNEY:
                return await ctx.send(f"Total Slot should be below {self.bot.config.MAX_SLOTS_PER_TOURNEY}")

            if int(total_slot) < self.bot.config.MAX_SLOTS_PER_TOURNEY:
                overwrite = ctx.channel.overwrites_for(bt)
                overwrite.update(send_messages=True, manage_messages=True, read_message_history=True, add_reactions=True, manage_channels=True, external_emojis=True, view_channel=True)
                reason= f'Created by {ctx.author.name}'   #reason for auditlog
                category = await ctx.guild.create_category(name, reason=f"{ctx.author.name} created")
                await category.set_permissions(bt, overwrite=overwrite)
                await category.set_permissions(ctx.guild.default_role, send_messages=False, add_reactions=False)
                await sleep(1)  #sleep
                await ctx.guild.create_text_channel(str(front)+"info", category=category, reason=reason)
                await ctx.guild.create_text_channel(str(front)+"updates", category=category,reason=reason)
                await ctx.guild.create_text_channel(str(front)+"schedule", category=category,reason=reason)
                roadmap = await ctx.guild.create_text_channel(str(front)+"roadmap", category=category,reason=reason)
                rdmm = await roadmap.send(constants.PROCESSING)
                await ctx.guild.create_text_channel(str(front)+"point-system", category=category,reason=reason)
                await sleep(1) #sleep
                htrc = await ctx.guild.create_text_channel(str(front)+"how-to-register", category=category, reason=reason)
                r_ch = await ctx.guild.create_text_channel(str(front)+"register-here", category=category, reason=reason)    

                await self.bot.helper.unlock_channel(channel=r_ch) # unlocks the registration channel
                c_ch = await ctx.guild.create_text_channel(str(front)+"confirmed-teams", category=category, reason=reason)  
                await sleep(1)  #sleep
                g_ch = await ctx.guild.create_text_channel(str(front)+"groups", category=category, reason=reason)
                quer = await ctx.guild.create_text_channel(str(front)+"queries", category=category, reason=reason)

                await self.bot.helper.unlock_channel(channel=quer) # unlocks the queries channel
            
                c_role = await ctx.guild.create_role(name=front + "Confirmed", reason=f"Created by {ctx.author}")
                rchm = await r_ch.send(embed=discord.Embed(color=color.cyan, description=f"**{emoji.cup} | REGISTRATION STARTED | {emoji.cup}\n{emoji.tick} | TOTAL SLOT : {total_slot}\n{emoji.tick} | REQUIRED MENTIONS : {mentions}\n{emoji.cross} | FAKE TAGS NOT ALLOWED**"))
                htr = ""
                for i in range(1, mentions+1): htr+=f"\nPLAYER {i}:\nUID: PLAYER ID\nIGN : PLAYER NAME\n"
                htrm = await htrc.send(
                    "**REGISTRATION FORM**", 
                    embed=discord.Embed(
                        color=color.cyan, 
                        description=f"**TEAM NAME : YOUR TEAM NAME\n{htr}\nSUBSTITUTE PLAYER IF EXIST\nMENTION YOUR {mentions} TEAMMATES**"
                    )
                )
                await rdmm.edit(
                    content="https://tenor.com/view/coming-soon-coming-soon-its-coming-shortly-gif-21517225"
                ) if rdmm else None
                await htrm.add_reaction(emoji.tick)
                await rchm.add_reaction(emoji.tick)
                await sleep(1)  #sleep
                tour = {
                    "guild" : int(ctx.guild.id), 
                    "t_name" : str(name), 
                    "prefix" : str(front),
                    "rch" : int(r_ch.id), 
                    "cch" : int(c_ch.id), 
                    "gch" : int(g_ch.id), 
                    "crole" : int(c_role.id), 
                    "tslot" : int(total_slot), 
                    "reged" : 1, 
                    "mentions" : int(mentions), 
                    "status" : "started", 
                    "faketag": "no", 
                    "pub" : "no", 
                    "prize" : "No Data", 
                    "auto_grp":"no", 
                    "spg":slot_per_group, 
                    "cgp":0, 
                    "created_at":datetime.datetime.now()
                }
                tour_count = len(self.dbc.find({"guild" : ctx.guild.id}).to_list())

                if tour_count > 5:
                    return await ctx.send(
                        embed=discord.Embed(
                            description="Tournament Limit Reached!! you can delete previous tournament to create another one. or contact us via support server!!", 
                            color=self.bot.color.red), 
                            delete_after=30
                        )
                inserted = self.dbc.insert_one(tour)
                if not inserted.inserted_id:
                    return await ctx.send(
                        embed=discord.Embed(
                            description="**Failed To Create Tournament**", 
                            color=color.red
                        ), 
                        delete_after=10
                    )
                


                # configures the slot manager for the tournament
                await self.set_manager(ctx, r_ch)

                return await ms.edit(
                    content=None, 
                    embed=discord.Embed(
                        color=color.cyan, 
                        description=f'{emoji.tick} | Successfully Created. Tournament Slot({tour_count+1}/5 used)'
                    ), 
                    delete_after=20) if ms else None
            
        except Exception:return



    @commands.hybrid_command(description="Create a girls lobby")
    @commands.guild_only()
    @checks.tourney_mod()
    @commands.cooldown(1, 30, commands.BucketType.user)
    @app_commands.describe(vc_amount="Number of voice channels to create")
    async def girls_lobby(self, ctx:commands.Context, vc_amount : int):
        await ctx.defer(ephemeral=True)
        if ctx.author.bot:return

        snd = await ctx.send(f"{emoji.loading} | {constants.PROCESSING}")
        cat = await ctx.guild.create_category(name="GIRLS LOBBY")
        crl = await ctx.guild.create_role(name="GIRLS LOBBY", color=0xD02090)
        await cat.set_permissions(ctx.guild.default_role, connect=False, send_messages=False, add_reactions=False)
        overwrite = cat.overwrites_for(crl)
        overwrite.update(send_messages=True, connect=True, speak=True, stream=True, use_voice_activation=True)
        await cat.set_permissions(crl, overwrite=overwrite)
        amt = vc_amount + 1
        for i in range(1, amt):
            await cat.create_voice_channel(name=f"SLOT {i}", user_limit=6)
            await sleep(1)
        if snd:
            await snd.edit(
                content=f"{emoji.tick} | {vc_amount} vc created access role is {crl.mention}"
            )



    @commands.hybrid_command(description="Start a tournament", with_app_command = True)
    @commands.guild_only()
    @checks.tourney_mod()
    @app_commands.describe(
        registration_channel="The channel where the tournament is registered, usually the registration channel."
    )
    async def start_tourney(self, ctx:commands.Context, registration_channel : discord.TextChannel):
        await ctx.defer(ephemeral=True)
        if ctx.author.bot:return
        dbcd = self.dbc.find_one({"rch" : registration_channel.id})
        if not dbcd:
            return await ctx.send(embed=discord.Embed(description="**No Tournament Running In This Channel**", color=color.blurple), delete_after=10)
        self.dbc.update_one({"rch" : registration_channel.id}, {"$set" : {"status" : "started"}})
        await registration_channel.send(embed=discord.Embed(color=color.cyan, description="Registration Started"))
        await ctx.send("Started", delete_after=10)

            

    @commands.hybrid_command(description="Pause a tournament", with_app_command = True, aliases=['pt'])
    @commands.guild_only()
    @checks.tourney_mod()
    @app_commands.describe(
        registration_channel="The channel where the tournament is registered, usually the registration channel."
    )
    async def pause_tourney(self, ctx:commands.Context, registration_channel : discord.TextChannel):
        if ctx.author.bot:return
        await ctx.defer(ephemeral=True)
        dbcd = self.dbc.find_one({"rch" : registration_channel.id})
        if not dbcd:
            return await ctx.send('No Tournament Running In This Channel')
        self.dbc.update_one({"rch" : registration_channel.id}, {"$set" : {"status" : "paused"}})
        await registration_channel.send(embed=discord.Embed(color=self.bot.color.orange, description="Registration Paused"))
        await ctx.send("Paused", delete_after=10)

        

    @commands.hybrid_command(description="Cancel a slot for a team", with_app_command = True)
    @commands.guild_only()
    @checks.tourney_mod()
    @app_commands.describe(
        registration_channel="The channel where the tournament is registered, usually the registration channel.",
        member="The member whose slot you want to cancel",
        reason="The reason for canceling the slot"
    )
    async def cancel_slot(self, ctx:commands.Context, registration_channel : discord.TextChannel, member : discord.Member, reason:str="Not Provided"):
        await ctx.defer(ephemeral=True)
        if ctx.author.bot:return

        dbcd = self.dbc.find_one({"rch" : registration_channel.id})
        if not dbcd:
            return await ctx.send(embed=discord.Embed(description=f"**{self._tnotfound}**", color=color.red), delete_after=10)
        crole = discord.utils.get(ctx.guild.roles, id=int(dbcd["crole"]))
        reged = dbcd["reged"]
        cch = self.bot.get_channel(int(dbcd["cch"]))
        if ctx.channel == cch:
            return await ctx.message.delete()
        if crole not in member.roles:
            return await ctx.send(embed=discord.Embed(title="Player Not Registered `or` Don't have Confirmed Role", color=color.red), delete_after=60)
        
        if crole in member.roles:
            await member.remove_roles(crole)
            self.dbc.update_one({"rch" : registration_channel.id}, {"$set" : {"reged" : reged - 1}})

            async for message in cch.history(limit=123):
                if member.mention in message.content and message.author.id == self.bot.user.id:
                    await message.delete() 
                    await ctx.send(
                        embed=discord.Embed(
                            title=f"{member}'s Slot Canceled with reason of {reason}", 
                            color=color.green
                        )
                    )



    @commands.hybrid_command(description="Add a slot for a team", with_app_command = True)
    @commands.guild_only()
    @checks.tourney_mod()
    @app_commands.describe(
        registration_channel="The channel where the tournament is registered, usually the registration channel.",
        member="The member to add to the slot",
        team_name="The name of the team"
    )
    async def add_slot(self, ctx:commands.Context, registration_channel: discord.TextChannel, member:discord.Member, *, team_name):
        await ctx.defer(ephemeral=True)
        if ctx.author.bot:return

        dbcd:dict[str] = self.dbc.find_one({"rch" : registration_channel.id})
        if not dbcd:
            return await ctx.send(embed=discord.Embed(description=f"**{self._tnotfound}**", color=color.red), delete_after=10)
        
        crole = discord.utils.get(ctx.guild.roles, id=int(dbcd["crole"]))
        if not crole:
            return await ctx.send("Confirm Role Not Found", delete_after=10)
        
        reged = dbcd.get("reged")
        cch = discord.utils.get(ctx.guild.channels, id=int(dbcd["cch"]))

        if not cch:
            return await ctx.send(embed=discord.Embed(description="**Confirm Channel Not Found**", color=color.red), delete_after=10)
    
        if crole in member.roles:
            return await ctx.send("**Already Registered**", delete_after=50)
        
        if crole not in member.roles:
            await member.add_roles(crole)
            self.dbc.update_one({"rch" : registration_channel.id}, {"$set" : {"reged" : reged + 1}})
            emb = discord.Embed(color=0xffff00, description=f"**{reged}) TEAM NAME: {team_name.upper()}**\n**Added By** : {ctx.author.mention} ")
            emb.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon)
            emb.timestamp = datetime.datetime.now()
            await cch.send(f"{team_name} {member.mention}", embed=emb)
            await ctx.send(f"**{reged}){team_name}{member.mention} Added**", delete_after=50)   
        


    @commands.hybrid_command(name="tourneys", description="Get Ongoing Tournaments in Your DM")
    @commands.cooldown(2, 60, commands.BucketType.user)
    @commands.guild_only()
    async def tourneys(self, ctx:commands.Context):
        if ctx.author.bot:return 

        await ctx.defer(ephemeral=True)
        ms = await ctx.send(constants.PROCESSING)
        emb = discord.Embed(title="__ONGOING TOURNAMENTS__", url=self.bot.config.INVITE_URL, color=0x00ff00)
        data  = self.dbc.find({"pub" : "yes"}).to_list()


        def is_eligible(tourney_obj : Tourney) -> bool:
            """
            Check if the tournament is eligible to be displayed.
            A tournament is eligible if it has less than 98% of its slots filled,
            at least 10% of its slots filled, and its status is 'started'.
            """
            return all([ 
                tourney_obj.reged >= 40,
                tourney_obj.status == "started",
                tourney_obj.created_at > datetime.datetime.now() - datetime.timedelta(days=30),
            ])
        
        if len(data) == 0:
            return await ctx.send("No Ongoing Tournaments", delete_after=30)

        for i in data:
            _tourney_obj = Tourney(i)
            rch = self.bot.get_channel(int(_tourney_obj.rch))
            if rch and is_eligible(_tourney_obj):
                if not rch.permissions_for(ctx.guild.me).create_instant_invite:
                    continue
                
                link = await rch.create_invite(max_age=3600, unique=False)
                emb.add_field(
                    name=f'{_tourney_obj.tname.upper()}', 
                    value=f"Prize: {_tourney_obj.prize.upper()}\nServer: {rch.guild.name[0:20]}\n[Register]({link})\n---------------- "
                )

        if len(emb.fields) > 0:
            try:
                await ctx.author.send(embed=emb)
                await ctx.send("Please Check Your DM")
                
            except discord.Forbidden:
                return await ctx.send("Please Enable Your DM to Receive Ongoing Tournaments", delete_after=30)
                
            if ms:
                await ms.edit(content="Please Check Your DM") 
                return


    @commands.hybrid_command(description="Publish a tournament", with_app_command = True, aliases=["pub"])
    @commands.guild_only()
    @commands.cooldown(2, 20, commands.BucketType.user)
    @checks.tourney_mod()
    @app_commands.describe(
        reg_channel="The channel where the tournament is registered",
        prize="The prize for the tournament"
    )
    async def publish(self, ctx:commands.Context, reg_channel: discord.TextChannel, *, prize: str):
        await ctx.defer(ephemeral=True)
        if ctx.author.bot:return

        if len(prize) > 30:
            return await ctx.reply("Only 30 Letters Allowed ")
        try:
            dbcd = self.dbc.find_one({"rch" : reg_channel.id})
            if dbcd["reged"] < dbcd["tslot"]*0.1:
                return await ctx.send("You need To Fill 10% Of Total Slot. To Publish This Tournament")
        except Exception:
            return await ctx.send(self._tnotfound)
        self.dbc.update_one({"rch" : reg_channel.id}, {"$set" : {"pub" : "yes", "prize" : prize}})
        await ctx.send(f"**{reg_channel.category.name} is now public**")



    @commands.hybrid_command(description="Toggle the fake tag filter for a tournament", with_app_command = True)
    @commands.guild_only()
    @checks.tourney_mod()
    @app_commands.describe(registration_channel="The channel where the tournament is registered, usually the registration channel.")
    async def faketag(self, ctx:commands.Context, registration_channel: discord.TextChannel):
        await ctx.defer(ephemeral=True)
        if ctx.author.bot:return
        t_mod = discord.utils.get(ctx.guild.roles, name="tourney-mod")
        if t_mod == None: await ctx.guild.create_role("tourney-mod")
        dbcd:dict[str] = self.dbc.find_one({"rch" : registration_channel.id})
        if not dbcd: 
            return await ctx.send(
                embed=discord.Embed(
                    description="**No Tournament Running In This Channel**", 
                    color=color.red
                ), 
                delete_after=10
            )
        btn = Button(label="Enable", style = discord.ButtonStyle.green)
        btn1 = Button(label="Disable", style = discord.ButtonStyle.green)
        view1 = View()
        view2 = View()
        view1.add_item(btn)
        view2.add_item(btn1)

        if dbcd.get("faketag") == "no":
            await ctx.send("Disable Fake Tag Filter", view=view2)

        if dbcd.get("faketag") == "yes":
            await ctx.send("Enable Fake Tag Filter", view=view1)

        async def enable_duplicate_tag_filter(interaction:discord.Interaction):
            """
            Enable Duplicate Tag Filter Button Interaction
            """
            self.dbc.update_one({"rch" : registration_channel.id, "faketag" : "yes"}, {"$set":{"faketag" : "no"}})
            await interaction.response.send_message("Enabled")

        async def disable_duplicate_tag_filter(interaction:discord.Interaction):
            """
            Disable Duplicate Tag Filter Button Interaction
            """
            self.dbc.update_one({"rch" : registration_channel.id, "faketag" : "no"}, {"$set":{"faketag" : "yes"}})
            await interaction.response.send_message(embed=discord.Embed(description=f"{emoji.tick} | Duplicate Tag Filter Disabled"))


        btn.callback = enable_duplicate_tag_filter
        btn1.callback = disable_duplicate_tag_filter


    @commands.hybrid_command(description="Manage tournament settings", with_app_command = True)
    @commands.guild_only()
    @checks.tourney_mod()
    @app_commands.describe( registration_channel="The channel where the tournament is registered, usually the registration channel."  )
    async def tourney(self, ctx:commands.Context, registration_channel: discord.TextChannel):
        await ctx.defer(ephemeral=True)
        if ctx.author.bot:return

        pub = ""
        rch = registration_channel
        tdb:dict = self.dbc.find_one({"rch": rch.id})   
        tourn = Tourney(tdb) if tdb != None else None
        if tdb == None:
            emb = discord.Embed(
                description=f"{emoji.cross} | Kindly Mention Registration Channel I'm Managing..", 
                color=color.red
            )
            return await ctx.reply(embed=emb, delete_after=30) 
           
        if tdb != None:
            if tdb["pub"] == "no":pub = "Publish"; 
            if tdb["pub"] == "yes":pub = "Unlisted"; 
            bt0 = Button(label="Start/Pause", style=discord.ButtonStyle.green)
            bt1 = Button(label="Fake Tag", style=discord.ButtonStyle.green)
            bt2 = Button(label="Total Slot", style=discord.ButtonStyle.green) 
            bt3 = Button(label="Mentions", style=discord.ButtonStyle.green)
            bt4 = Button(label="Save")
            bt6 = Button(label="Slot Channel")
            bt9 = Button(label="Confirm Role", style=discord.ButtonStyle.secondary)
            bt10 = Button(label="Delete", style=discord.ButtonStyle.danger)
            bt11 = Button(label="Confirm", style=discord.ButtonStyle.danger)
            bt12 = Button(label=pub, style=discord.ButtonStyle.blurple)
            change_group_btn = Button(label="Group Channel", style=discord.ButtonStyle.secondary)
            exportButton = Button(label="Export Data", style=discord.ButtonStyle.blurple)
            
            spgbtn = Button(label="Slots per group")
            buttons = [bt0, bt1, bt2, bt3, spgbtn, bt6, bt9, bt10, bt12, bt4, exportButton, change_group_btn]
            view = View()
            emb = discord.Embed(
                title=rch.category.name, 
                description=f"**Total Slot : {tourn.tslot}\nRegistered : {tourn.reged}\nMentions : {tourn.mentions}\nStatus : {tourn.status}\nPublished : {tourn.pub.upper()}\nPrize : {tourn.prize}\nSlot per group: {tourn.spg}\nFakeTag Allowed : {tourn.faketag.upper()}\nRegistration : <#{tourn.rch}>\nConfirm Channel: <#{tourn.cch}>\nGroup Channel: <#{tourn.gch}>\nConfirm Role : <@&{tourn.crole}>**", 
                color=color.cyan, 
                timestamp=datetime.datetime.now()
            )
            emb.set_footer(
                text=f"Requested By {ctx.author}", 
                icon_url=ctx.author.avatar or ctx.me.avatar
            )
            for button in buttons:
                view.add_item(button)
            msg1 = await ctx.send(embed=emb, view=view)

            async def save_delete(interaction:discord.Interaction):
                if msg1 : await msg1.delete()

            async def delete_tourney_confirm(interaction:discord.Interaction):
                """
                Confirms the deletion of a tournament with a confirmation message and a view containing a button.

                Args:
                    interaction (discord.Interaction): The interaction that triggered the confirmation.

                Returns:
                    None: Sends a confirmation message with a view to the channel where the interaction occurred.

                Note:
                    This function is intended to be used as a callback for a discord interaction.
                    It requires a pre-defined button 'bt11' to be added to the view.
                """
                view = View().add_item(bt11)
                await interaction.response.send_message("**Are You Sure To Delete The Tournament?**", view=view)


            async def delete_t_confirmed(interaction:discord.Interaction):
                """
                Process a confirmed tournament deletion request.

                This asynchronous function updates the message with a processing indicator, 
                removes the tournament from the database based on the registration channel ID,
                saves the deletion action, and finally removes the confirmation message.

                Parameters:
                ----------
                interaction : discord.Interaction
                    The interaction that triggered the deletion confirmation

                Returns:
                -------
                None
                """
                if interaction.message:
                    await interaction.message.edit(
                        content=f"**{emoji.loading} {constants.PROCESSING}**"
                    )
                self.dbc.delete_one({"rch" : registration_channel.id })
                await save_delete(interaction)
                await interaction.message.delete()


            async def publish(interaction:discord.Interaction):
                """
                Publishes or unpublishes a tournament.
                If the tournament is not yet published:
                - Checks if at least 10% of the tournament slots are filled
                - If so, prompts for a prize description (max 15 characters)
                - Updates the tournament to public status with the prize
                - If slots requirement not met, sends an error message
                If the tournament is already published:
                - Updates the tournament to non-public status
                - Sends confirmation message
                Args:
                    interaction (discord.Interaction): The interaction object from the button press
                Returns:
                    None: Responses are sent via Discord messages or interaction responses
                """
                if tourn.pub == "no":
                    if tourn.reged >= tourn.tslot*0.1:
                        ms = await ctx.send("Enter The Prize Under 15 characters")
                        prize = str(await self.get_input(ctx))

                        if len(prize) > 15:
                            return await ms.edit(content="Word Limit Reached. Try Again Under 15 Characters") if ms else None
                        
                        self.dbc.update_one({"rch" : rch.id}, {"$set" : {"pub" : "yes", "prize" : prize}})
                        await ms.delete()
                        await ctx.send("Tournament Is Now Public", delete_after=5)

                    if tourn.reged < tourn.tslot*0.1:
                        return await interaction.response.send_message(
                            "**You Need To Fill 10% Slot To Publish**", 
                            ephemeral=True, 
                            delete_after=10
                        )

                if tdb["pub"] == "yes":
                    self.dbc.update_one({"rch" : rch.id}, {"$set" : {"pub" : "no"}})
                    await interaction.response.send_message("Tournament Unpublished",  delete_after=5)

            async def change_confirm_channel(interaction:discord.Interaction):
                """
                Updates the confirmation channel for a tournament.
                
                This function allows the original command author to change the channel where tournament
                confirmations will be sent. It checks if the user is authorized, validates that the specified
                channel isn't already in use for another tournament, and updates the database accordingly.
                
                Parameters:
                -----------
                interaction : discord.Interaction
                    The interaction object containing information about the button press event
                    
                Returns:
                --------
                None
                    Function sends responses directly to Discord channels
                    
                Side Effects:
                -------------
                - Sends messages to Discord channels
                - Updates tournament database record
                - Modifies embed message to reflect the new confirmation channel
                """
                if interaction.user != ctx.author: 
                    return await ctx.send(self.ONLY_AUTHOR_BUTTON)
                
                await interaction.response.send_message("Mention Confiration Channel")
                cchannel = await checker.channel_input(ctx)
                acch = self.dbc.find_one({"cch" : cchannel.id})

                if cchannel.id == tourn.cch or acch != None:
                    return await ctx.send("A Tournament Already Running In This channel", delete_after=10)
                
                await interaction.delete_original_response()
                if not cchannel:
                    return await ctx.send("Kindly Mention A Channel!!", delete_after=5)
                
                self.dbc.update_one({"rch": rch.id}, {"$set":{"cch": cchannel.id}})
                await ctx.send("Confirm Channel Updated", delete_after=5)
                await interaction.message.edit(
                    embed=discord.Embed(
                        description=interaction.message.embeds[0].description.replace(f"<#{tourn.cch}>", f"<#{cchannel.id}>"), 
                        color=color.cyan)
                ) if interaction.message else None
                tourn.cch = cchannel.id


            async def change_group_channel(group_channel_interaction:discord.Interaction):
                await group_channel_interaction.response.defer(ephemeral=True)
                if group_channel_interaction.user != ctx.author:
                    return await group_channel_interaction.followup.send(self.ONLY_AUTHOR_BUTTON)
                
                await group_channel_interaction.followup.send("Mention Group Channel")
                _text_selection = await checker.channel_input(ctx)

                if not isinstance(_text_selection, discord.TextChannel):
                    return await group_channel_interaction.followup.send("Kindly Mention A Channel!!", ephemeral=True)

                if _text_selection.id == tourn.gch:
                    return await group_channel_interaction.followup.send("This Channel is Already Set as Group Channel",ephemeral=True)

                if  any([not _text_selection.category , _text_selection.category != rch.category]):
                    await _text_selection.move(category=rch.category, sync_permissions=True, end=True)

                    return await group_channel_interaction.followup.send("Group Channel Should Be In The Same Category As Registration Channel", ephemeral=True)

                # edit the message to reflect the new group channel
                await msg1.edit(
                    embed=discord.Embed(
                        description=msg1.embeds[0].description.replace(f"<#{tourn.gch}>", f"<#{_text_selection.id}>"), 
                        color=color.cyan
                    )
                ) if msg1 else None


                tourn.gch = _text_selection.id
                tourn.save()
                await group_channel_interaction.followup.send(f"Group Channel Updated to <#{_text_selection.id}>", ephemeral=True)


            async def ft(interaction:discord.Interaction):
                """
                Fake Tag Button Interaction
                """
                if interaction.user == ctx.author and tdb["faketag"] == "yes":
                    self.dbc.update_one({"rch": rch.id}, {"$set":{"faketag" : "no"}})
                    bt1.disabled = True
                    await interaction.response.edit_message(view=view) if interaction.message else None
                    await ctx.send("Enabled", delete_after=10)


                if interaction.user == ctx.author and tdb["faketag"] == "no":
                    self.dbc.update_one({"rch": rch.id}, {"$set":{"faketag" : "yes"}})
                    bt1.disabled = True
                    await interaction.response.edit_message(view=view) if interaction.message else None
                    await ctx.send("Disabled", delete_after=10)


            async def ttl_slot(interaction:discord.Interaction):
                """
                Updates the total slot count for a tournament.
                
                This function handles the interaction when a user attempts to update the total slot count.
                It verifies the user is the author, prompts for input, validates the input is between 1 and 1100,
                updates the database, and refreshes the displayed information.
                
                Parameters
                ----------
                interaction : discord.Interaction
                    The interaction object containing information about the user's interaction with the bot
                
                Returns
                -------
                None
                    This function doesn't return anything but sends messages to the Discord channel
                    
                Notes
                -----
                - Only the author of the original command can update the total slot
                - Total slots must be between 1 and {self.bot.config.MAX_SLOTS_PER_TOURNEY}
                - Updates are reflected in both the database and the displayed embed
                """


                if interaction.user != ctx.author:
                    return await ctx.send(self.ONLY_AUTHOR_BUTTON)
                tsl = await(checker.get_input(interaction=interaction, title="Total Slot", label=f"Enter Total Slot Between 2 and {self.bot.config.MAX_SLOTS_PER_TOURNEY}"))
                try:
                    if int(tsl) > self.bot.config.MAX_SLOTS_PER_TOURNEY or int(tsl)<1:
                        return await ctx.send(f"Only Number Between 1 and {self.bot.config.MAX_SLOTS_PER_TOURNEY}", delete_after=20)
                    self.dbc.update_one({"rch": rch.id}, {"$set":{"tslot" : int(tsl)}})
                    await ctx.send("Total Slots Updated", delete_after=5)
                    if interaction.message:
                        await interaction.message.edit(
                            embed=discord.Embed(
                                description=interaction.message.embeds[0].description.replace(f"Total Slot : {tourn.tslot}", f"Total Slot : {int(tsl)}"), 
                                color=color.cyan
                            )
                        )
                    tourn.tslot = int(tsl)
                except ValueError:
                    return await ctx.send("Numbers Only", delete_after=10)
    
            async def mnts(interaction:discord.Interaction):
                """
                Updates the number of mentions for a tournament.
                Validates that the interaction is from the original author, then prompts for
                a number of mentions between 1 and 20. Updates the database with the new mention
                count, updates the message embed, and sets the new mentions value on the tournament object.

                Parameters
                ----------
                interaction : discord.Interaction
                    The interaction that triggered this function

                Returns
                -------
                None
                    Sends feedback messages to the channel based on input validation
                    
                Raises
                ------
                ValueError
                    If the input cannot be converted to an integer
                """
                if interaction.user != ctx.author:
                    return await ctx.send(self.ONLY_AUTHOR_BUTTON)
                mns = await checker.get_input(interaction=interaction, title="Mentions", label="Enter Number Between 1 and 20")
                try:
                    if int(mns) > 20: 
                        return await ctx.send("Only Number upto 20", delete_after=5)
                    
                    self.bot.db.dbc.update_one({"rch": rch.id}, {"$set":{"mentions" : int(mns)}})
                    await ctx.send("Mentions Updated", delete_after=5)
                    await interaction.message.edit(
                        embed=discord.Embed(
                            description=interaction.message.embeds[0].description.replace(f"Mentions : {tourn.mentions}", f"Mentions : {int(mns)}"), 
                            color=color.cyan)
                    )  if interaction.message else None
                    tourn.mentions = int(mns)
                except ValueError:
                    return await ctx.send("Numbers Only", delete_after=5)
    

            async def strtps(interaction:discord.Interaction):
                """
                Toggles the tournament status between 'started' and 'paused'.
                This function checks if the user interacting is the author of the context,
                then changes the tournament status in the database and sends appropriate
                notifications.
                Args:
                    interaction (discord.Interaction): The interaction object from Discord.
                Returns:
                    None
                Side effects:
                    - Updates tournament status in database
                    - Sends notification messages to the tournament channel
                    - Disables a button (bt0) in the interaction view
                    - Edits the interaction message if it exists
                    - Sends a temporary confirmation message to the context channel
                """
                if interaction.user == ctx.author:
                    if tdb["status"] == "started":
                        self.dbc.update_one({"rch": rch.id}, {"$set":{"status" : "paused"}})
                        await rch.send("**Tournament Paused**")
                        bt0.disabled = True
                        await interaction.response.edit_message(view=view) if interaction.message else None
                        await ctx.send("Tournament Paused", delete_after=2)

                    if tdb["status"] == "paused":
                        self.dbc.update_one({"rch": rch.id}, {"$set":{"status" : "started"}})
                        await rch.send("**Tournament Statred**")
                        bt0.disabled = True
                        await interaction.response.edit_message(view=view)  if interaction.message else None
                        await ctx.send("Tournament Started", delete_after=2)
    

            async def conro(interaction:discord.Interaction):
                """
                Async callback method for changing/setting the confirmation role of a tournament.
                This method is called when the user interacts with a specific component (likely a button) 
                to change the confirmation role for a tournament. It prompts the user to mention a role,
                validates it, and updates the tournament configuration in the database.
                Parameters:
                    interaction (discord.Interaction): The interaction object representing the user's interaction.

                Notes:
                    - Only the original command author can trigger this action
                    - Checks if the specified role is already being used for another tournament
                    - Updates the database and refreshes the embedded message with the new role
                """
                if interaction.user == ctx.author:
                    await interaction.response.send_message("Mention The Confirm Role")
                    try:
                        con_role = await checker.check_role(ctx)
                        await interaction.delete_original_response()
                        if not con_role:
                            return await ctx.send("Kindly Mention A Role!!", delete_after=5)
                    except Exception:
                        return await ctx.send("Something went wrong!! please try again later!!", delete_after=5)
                    cndb = self.dbc.find_one({"crole" : str(con_role.id)})

                    if cndb == None:
                        self.dbc.update_one({"rch": rch.id}, {"$set":{"crole" : con_role.id}})
                        await ctx.send("Confirm Role Updated", delete_after=5)
                        if interaction.message:
                            await interaction.message.edit(
                                embed=discord.Embed(
                                    description=interaction.message.embeds[0].description.replace(f"<@&{tourn.crole}>", f"<@&{con_role.id}>"), 
                                    color=color.cyan
                                )
                            )
                        tourn.crole = con_role.id
                    if cndb != None:
                        return await ctx.send("I'm Already Managing A Tournament With This Role", delete_after=20)

            async def spg_change(interaction:discord.Interaction):
                """
                Asynchronously handles the change of slots per group (SPG) in a tournament.
                This coroutine allows authorized users to modify the number of slots available per group
                in a tournament setup. It includes input validation and database updates.
                Parameters:
                    interaction (discord.Interaction): The interaction object from the Discord event
                Returns:
                    None
                Raises:
                    Exception: Any error during the execution is caught and reported to the error log channel
                Flow:
                    1. Validates if the user is the original author
                    2. Gets and validates the new SPG value from user input
                    3. Updates the database with new SPG value
                    4. Updates the display message with new SPG value
                    5. Updates the tournament object's SPG attribute
                Requirements:
                    - User must be the original author of the tournament
                    - SPG value must be a positive integer (>= 1)
                """
                if not ctx.author:
                    return await ctx.send(self.ONLY_AUTHOR_BUTTON)
                try:
                    spg = int(await checker.get_input(interaction=interaction, title="Slot Per Group"))
                    if not spg:
                        return await ctx.send(embed=discord.Embed(description="Kindly Mention the number of slot per group!!", color=color.red), delete_after=5)
                    elif spg < 1 or type(spg)!= int: 
                        return await ctx.send(
                            embed=discord.Embed(
                                description="Slot per group must be a number 1 or above..", 
                                color=color.red
                            ), 
                            delete_after=5
                        )
                    self.dbc.update_one({"rch":rch.id},{"$set":{"spg":spg}})
                    await ctx.send(
                        embed=discord.Embed(
                            description=f"{emoji.tick} Updated the current slot per group to : {spg}", 
                            color=color.green
                        ), 
                        delete_after=2
                    )
                    if interaction.message :
                        await interaction.message.edit(
                            embed=discord.Embed(
                                description=interaction.message.embeds[0].description.replace(f"Slot per group: {tourn.spg}", f"Slot per group: {spg}"), 
                                color=color.cyan
                            )
                        )
                    tourn.spg = spg

                except Exception as e :
                    await self.bot.log_channel.send(
                        content=f"<@{self.bot.config.OWNER_ID}>",
                        embed=discord.Embed(
                            title=f"Error | {ctx.command.name}\n `Module : core.tourney | call : tourney.spg_change`", description=f"```{e}```", 
                            color=color.red
                        )
                    )
                    return await ctx.send(
                        embed=discord.Embed(
                            description="Unable to update | Try again!!", 
                            color=color.red
                            ), 
                        delete_after=5
                    )
                
            async def export_event_data_callback(interaction:discord.Interaction):
                """
                Callback handler for exporting event data.

                This asynchronous function handles the button interaction for exporting tournament event data.
                It verifies the user is the original command author and manages the export process.

                Args:
                    interaction (discord.Interaction): The interaction event from the button press

                Returns:
                    None: This function handles the interaction response directly and returns nothing

                Raises:
                    None: Exceptions are handled internally
                """
                if interaction.user != ctx.author:
                    await interaction.response.send_message(self.ONLY_AUTHOR_BUTTON)
                    return
                await interaction.response.defer(ephemeral=True)
                await interaction.edit_original_response(content="Exporting Event Data...")
                await self.export_event_data(ctx, rch)

                


            bt6.callback = change_confirm_channel
            bt4.callback = save_delete
            bt1.callback = ft
            bt2.callback = ttl_slot
            bt3.callback = mnts
            bt0.callback = strtps
            bt9.callback = conro
            bt10.callback = delete_tourney_confirm
            bt11.callback = delete_t_confirmed
            bt12.callback = publish
            spgbtn.callback = spg_change
            change_group_btn.callback = change_group_channel
            exportButton.callback = export_event_data_callback





    @commands.hybrid_command(description="Setup group channels by position (it doesn't gives role to players)", with_app_command = True, aliases=['gsetup'])
    @commands.guild_only()
    @app_commands.guild_only()
    @checks.tourney_mod()
    @commands.cooldown(1, 60, commands.BucketType.guild)
    @app_commands.describe(prefix="Prefix for group channels", start="Starting Group Number", end="Ending Group Number", category="Category for group channels")
    async def group_setup(self, ctx:commands.Context, prefix:str, start:int, end:int, category:discord.CategoryChannel=None):
        await ctx.defer(ephemeral=True)
        if ctx.author.bot:return

        elif start < 1:
            return await ctx.reply("Starting Number Should Not Be Lower Than 1")
        
        elif end < start:
            return await ctx.reply("Ending Number Should Not Be Lower Than Starting Number")
        
        ms = await ctx.send(f"{emoji.loading}| {constants.PROCESSING}")
        if category == None:category = await ctx.guild.create_category(name=f"{prefix} Groups")
        await category.set_permissions(ctx.guild.default_role, view_channel=False)
        for i in range(start, end+1):
            role = await ctx.guild.create_role(name=f"{prefix.upper()} G{i}", color=0x4bd6af)
            channel = await ctx.guild.create_text_channel(name=f"{prefix}-group-{i}", category=category)
            overwrite = ctx.channel.overwrites_for(role)
            overwrite.update(view_channel=True, send_messages=False, add_reactions=False, attach_files=True)
            await channel.set_permissions(role, overwrite=overwrite)
            await self.log(ctx.guild, message=f"Created Group {i} | {role.mention} | {channel.mention}")
            await sleep(2)
            
        if ms :
            await ms.edit(content=f"{emoji.tick} | Successfully Created") if ms else None


    @commands.command(name="change_slot", aliases=["cslot"])
    @commands.guild_only()
    @checks.tourney_mod()
    async def change_slot(self, ctx:commands.Context, *, slot:str):
        await ctx.defer(ephemeral=True)
        if not ctx.message.reference:
            return await ctx.reply(
                embed = discord.Embed(
                    description=f"**{emoji.cross} | Please Run This Command By Replying The Group Message**", 
                    color=color.red), 
                delete_after=30
            )
        msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        if slot not in msg.content:
            return await ctx.send("No Team Found")
        ask = await ctx.send("Enter New Team Name + Mention")
        new_slot = await self.get_input(ctx)
        if not new_slot: 
            await ctx.send("Kindly Mention The New Slot")
        if msg and msg.author.id != self.bot.user.id: 
            return await ctx.send("Got It!\n But I Can't Edit The Message.\nBecause I'm Not The Author Of The Message")
        if msg : await msg.edit(content=msg.content.replace(str(slot), str(new_slot))) if msg else None
        if ask : await ask.delete()
        return await ctx.send(embed=discord.Embed(
            description=f"{emoji.tick} | Successfully Changed", 
            color=color.green
        ), delete_after=10)
    


    @commands.command(enabled=False, aliases=["t_reset"])
    @commands.guild_only()
    @checks.tourney_mod()
    async def tourney_reset(self, ctx:commands.Context, channel: discord.TextChannel):
        if ctx.author.bot:return 
        td = self.dbc.find_one({"rch" : channel.id})
        tmrole = discord.utils.get(ctx.guild.roles, name="tourney-mod")
        if tmrole not in ctx.author.roles:return await ctx.reply("You Don't Have `tourney-mod` role")
        if not td:return await ctx.send("No Registration Running in this channel")
        try:
            cch = discord.utils.get(ctx.guild.channels, id=td["cch"])
            await channel.purge(limit=20000)
            await cch.purge(limit=20000)
            self.dbc.update_one({"rch" : channel.id}, {"$set":{"reged" : 1}})
            await ctx.send("Done")
        except Exception as e:return await ctx.send(f"Error : {e}")


    @commands.hybrid_command(description="Automatically create groups for the tournament", with_app_command = True, aliases=["autogroup"])
    @commands.guild_only()
    @commands.cooldown(1, 30, commands.BucketType.guild)
    @checks.tourney_mod()
    @app_commands.describe(registration_channel="mention the registration channel")
    async def auto_group(self, ctx:commands.Context, registration_channel:discord.TextChannel):
        if ctx.author.bot:
            return
        
        rch = registration_channel
        await ctx.defer(ephemeral=True)

        _event = Tourney.findOne(registration_channel.id)
        if not _event: 
            return await ctx.send(self._tnotfound, delete_after=10)

        # Check if the event is already in progress
        self.dbc.update_one({"rch": registration_channel.id}, {"$set": {"cgp": 0}})
        

        confirm_channel = self.bot.get_channel(_event.cch)
        group_channel = self.bot.get_channel(_event.gch)

        if not confirm_channel:
            return await ctx.send("Confirm Channel Not Found")

        if not group_channel:
            return await ctx.send("Group Channel Not Found")

        slot_per_group = _event.spg # slots per group
        current_group_position = 0 # current group position

        # check permission for confirm channel for bot
        if not confirm_channel.permissions_for(ctx.guild.me).read_message_history:
            return await ctx.send(f"I Don't Have Permission To Read Message History In {confirm_channel.mention}")
        
        teams = []
        # old confirm messages
        async for msg in confirm_channel.history(limit=_event.reged+50, oldest_first=True):
            if msg.author.id == self.bot.user.id and len(msg.embeds) > 0:
                if "TEAM" in msg.embeds[0].description:
                    teams.append(msg)

        if len(teams) < 1:
            return await ctx.send("Minimum Number Of Teams Isn't Reached!!")
        
        category = await ctx.guild.create_category(name=f"{_event.prefix} Groups")
        await category.set_permissions(ctx.guild.default_role, view_channel=False)

        group = int(len(teams)/slot_per_group)

        # Create groups
        if len(teams)/slot_per_group > group:
            group = group+1

        if len(teams)/slot_per_group < 1:
            group = 1

        # private channels for each groups
        for i in range(1, group+1):
            channel = await confirm_channel.guild.create_text_channel(name=f"{_event.prefix}-group-{i}", category=category)
            role = await confirm_channel.guild.create_role(name=f"{_event.prefix.upper()} G{i}", color=0x4bd6af)
            overwrite = channel.overwrites_for(role)
            overwrite.update(view_channel=True, send_messages=False, add_reactions=False, attach_files=True)
            await channel.set_permissions(role, overwrite=overwrite)
            ms = f"**__GROUP__ {i}\n"

            # get the messages for each group
            current_group:list[discord.Message] = teams[current_group_position:current_group_position+slot_per_group]

            for p in current_group:
                ms = ms + f"{current_group.index(p)+1}) {p.content}" + "\n"

            self.dbc.update_one({"rch":rch.id},{"$set":{"cgp":current_group_position + slot_per_group}})

            # increase the starting position for the next group
            current_group_position += slot_per_group
            msg = await group_channel.send(f"{ms}**")

            for m in ctx.guild.members:
                if m.mention in msg.content: 
                    await m.add_roles(role)

            await msg.add_reaction(emoji.tick)
        await ctx.send(f"check this channel {group_channel.mention}")


    @commands.hybrid_command(description="Set the manager for the tournament", with_app_command = True)
    @commands.guild_only()
    @checks.tourney_mod()
    @app_commands.describe(registration_channel="The channel where the tournament is registered")
    async def set_manager(self, ctx:commands.Context, registration_channel:discord.TextChannel):
        if ctx.author.bot:
            return
        view = View()
        channel = registration_channel
        db = self.dbc.find_one({"rch":channel.id})
        if not db:
            return await ctx.send(embed=discord.Embed(description=self._tnotfound, color=color.red), delete_after=10)
        
        rch = self.bot.get_channel(db["rch"])
        mch = await rch.category.create_text_channel(name="manage-slot")
        emb = discord.Embed(
            title=rch.category.name, 
            description=f"{emoji.arow} **Cancel Slot** : To Cancel Your Slot\n{emoji.arow} **My Slot** : To Get Details Of Your Slot\n{emoji.arow} **Team Name** : To Change Your Team Name", 
            color=color.cyan
        )
        buttons = [
            Button(label='Cancel Slot', style=discord.ButtonStyle.red, custom_id="Cslot"),
            Button(label='My Slot', style=discord.ButtonStyle.blurple, custom_id="Mslot"),
            Button(label='Team Name', style=discord.ButtonStyle.green, custom_id="Tname"),
        ]
        
        for i in buttons:
            view.add_item(i)

        await mch.send(embed=emb, view=view)
        await self.bot.helper.lock_channel(channel=mch)
        self.dbc.update_one({"rch":channel.id},{"$set":{"mch":int(mch.id)}})
        await ctx.send(f"{emoji.tick} | {mch.mention} created")


    @app_commands.command(name="team_name" , description="Change your team name in the tournament")
    @app_commands.guild_only()
    @checks.tourney_mod(interaction=True)
    async def team_name(self, interaction:discord.Interaction, registration_channel:discord.TextChannel, player: discord.Member, new_name:str=None):
        await interaction.response.defer(ephemeral=True)
        if interaction.user.bot:
            return
        
        tourney:dict = self.dbc.find_one({"rch":registration_channel.id})
        if not tourney:
            return await interaction.followup.send(embed=discord.Embed(description=self._tnotfound, color=color.red), ephemeral=True)

        rch = self.bot.get_channel(tourney["rch"])
        cch = self.bot.get_channel(tourney["cch"])

        if not rch or not cch:
            return await interaction.followup.send(embed=discord.Embed(description="Registration or Confirm Channel Not Found", color=color.red), ephemeral=True)

        team: discord.Message = None
        async for msg in cch.history(limit=int(tourney.get("reged")+20)):
            if msg.author.id == self.bot.user.id and player.mention in msg.content:
                team = msg
                break

        if not team:
            return await interaction.followup.send(embed=discord.Embed(description="Team Not Found", color=color.red), ephemeral=True)

        if not new_name:
            return await interaction.followup.send(embed=team.embeds[0], ephemeral=True)

        newEmbed = team.embeds[0].copy()
        newEmbed.description = newEmbed.description.replace(team.content.split(" ")[0], new_name)
        await team.edit(content=f"{new_name} {player.mention}", embed=newEmbed)

        await interaction.followup.send(embed=discord.Embed(description="Team Name Updated Successfully", color=color.green), ephemeral=True)


    @commands.hybrid_command(with_app_command = True, description="list of all the ongoing tournaments")
    @commands.guild_only()
    @checks.tourney_mod()
    async def tconfig(self,ctx:commands.Context):
        await ctx.defer()
        _msg :discord.Message
        data = list(self.dbc.find({"guild":ctx.guild.id}))

        if not data or len(data)<1:
            return await ctx.send(embed=discord.Embed(description="**No Ongoing Tournament Found**", color=color.red), delete_after=20)
        
        options = [discord.SelectOption(label=i["t_name"], value=i["rch"]) for i in data]
        view = View()
        embed = discord.Embed(title="Select Tournament", color=color.cyan)
        bt10 = Button(label="Delete Tournament", style=discord.ButtonStyle.danger)
        exportButton = Button(label="Export Data", style=discord.ButtonStyle.blurple)
        bt11 = Button(label="Confirm", style=discord.ButtonStyle.danger)
        cancelButton = Button(label="Cancel", style=discord.ButtonStyle.blurple)
        btmanage = Button(label="Manage",  style=discord.ButtonStyle.green)
        tlist = discord.ui.Select(min_values=1, max_values=1, options=options)
        view.add_item(tlist)
        view.add_item(cancelButton)
        _msg = await ctx.send(embed=embed, view=view)

        async def tourney_details(interaction:discord.Interaction):
            await interaction.response.defer()
            db:Tourney = self.dbc.find_one({"rch":int(tlist.values[0])})
            if not db: 
                await interaction.response.send_message(self._tnotfound, delete_after=10)
                return
            
            db = Tourney(db)
            embed.title=db.tname.upper()
            embed.description=f"**Total Slot : {db.tslot}\nRegistered : {db.reged}\nMentions : {db.mentions}\nStatus : {db.status}\nPublished : {db.pub}\nPrize : {db.prize}\nSlot per group: {db.spg}\nFakeTag Allowed: {db.faketag}\nRegistration : <#{db.rch}>\nConfirm Channel: <#{db.cch}>\nGroup Channel: <#{db.gch}>\nConfirm Role : <@&{db.crole}>**"

            if bt10 not in view.children:
                view.add_item(bt10)

            if btmanage not in view.children:
                view.add_item(btmanage)

            if exportButton not in view.children:
                view.add_item(exportButton)

            await _msg.edit(embed=embed, view=view) if _msg else None
        
        async def delete_tourney_confirm(interaction:discord.Interaction):
            await interaction.response.defer()
            view1 = View().add_item(bt11)
            await interaction.channel.send("**Are You Sure To Delete The Tournament?**", view=view1)

        async def delete_t_confirmed(interaction:discord.Interaction):
            """This function will delete the tournament"""
            await interaction.response.defer()
            await interaction.message.edit(
                content=f"**{emoji.loading} {constants.PROCESSING}**"
            ) if interaction.message else None
            x = self.dbc.delete_one({"rch" : int(tlist.values[0])})
            if x:
                await interaction.message.delete()
                await _msg.delete()
                channel:discord.TextChannel = ctx.guild.get_channel(int(tlist.values[0]))
                if channel: await self.tconfig(ctx)

        async def manage_tournament(interaction:discord.Interaction):
            await interaction.response.defer()
            _msg = await interaction.message.edit(
                    content=f"**{emoji.loading} {constants.PROCESSING}**"
            ) if  interaction.message else None
            await self.tourney(await self.bot.get_context(ctx.message), registration_channel=ctx.guild.get_channel(int(tlist.values[0])))
            if _msg: await _msg.delete()


        async def export_event_data_callback(interaction:discord.Interaction):
            if interaction.user != ctx.author:
                await interaction.response.send_message(self.ONLY_AUTHOR_BUTTON)
                return
            await interaction.response.defer(ephemeral=True)
            await interaction.edit_original_response(content="Exporting Event Data...")
            await self.export_event_data(ctx, ctx.guild.get_channel(int(tlist.values[0])))


        async def cancel_button_callback(interaction:discord.Interaction):
            await interaction.response.defer(ephemeral=True)
            if interaction.message:
                await interaction.message.delete()


        cancelButton.callback = cancel_button_callback
        tlist.callback = tourney_details
        bt10.callback = delete_tourney_confirm
        bt11.callback = delete_t_confirmed
        btmanage.callback = manage_tournament
        exportButton.callback = export_event_data_callback


    # Currently it's a developer only command, and under development
    # With this command you can send a message containing a button to register a team
    # Then the user can submit a regiatration form to register their team
    # but there is a issue with the teammate mention and i'm working on it 
    # @commands.hybrid_command(with_app_command = True)
    @commands.command()
    @commands.guild_only()
    @checks.dev_only()
    @checks.tourney_mod()
    @commands.bot_has_guild_permissions(manage_channels=True, manage_roles=True, manage_permissions=True)
    async def start_reg(self, ctx:commands.Context, registration_channel:discord.TextChannel):
        if ctx.author.bot:
            return
        
        await ctx.defer(ephemeral=True)
        db = self.dbc.find_one({"rch":registration_channel.id})
        if not db:
            return await ctx.send(embed=discord.Embed(description=self._tnotfound, color=color.red), delete_after=10)
        tourObj:Tourney = Tourney(db)
        emb:discord.Embed = discord.Embed(
            color=color.cyan, 
            description=f"**{emoji.cup} | REGISTRATION STARTED | {emoji.cup}\n{emoji.tick} | TOTAL SLOT : {tourObj.tslot}\n{emoji.tick} | REQUIRED MENTIONS : {tourObj.mentions}\n{emoji.cross} | FAKE TAGS NOT ALLOWED**"
        )
        btn:Button = Button(
            label="Register Team", 
            style=discord.ButtonStyle.red, 
            custom_id=f"db_reg_btn_{self.bot.user.id}"
        )
        view:View = View().add_item(btn)
        await registration_channel.send(embed=emb, view=view)



    # This one is under development and currently testing on it!! and im not sure to impliment this or not, due to some mention related issues
    # If you have any idea or suggestion please let me know in the issue section or raise a PR
    async def register(self, interaction:discord.Interaction):
        db = self.dbc.find_one({"rch":interaction.channel.id})
        if not db:
            return await interaction.response.send_message("Tournament is No Longer Available!!", ephemeral=True)
        
        if interaction.data["custom_id"] == f"db_reg_btn_{self.bot.user.id}":
            t:Tourney = Tourney(db)
            crole:discord.Role = interaction.guild.get_role(t.crole)
            cch:discord.TextChannel = self.bot.get_channel(t.cch)

            inp = discord.ui.Modal(title="Registration Form", timeout=30)
            fields = [
                discord.ui.TextInput(label="Enter Team Name", placeholder="Team Name", max_length=20, custom_id="rg_teamname"),
                discord.ui.TextInput(label="Enter Player Names", placeholder="playerX, playerR, player4 (comma as separator)", max_length=200, custom_id="rg_players"),
                ]
            for i in fields:
                inp.add_item(i)
            await interaction.response.send_modal(inp)

            async def register_team(interaction:discord.Interaction):
                teamname:str = inp.children[0].value.upper()
                players:list[str] = inp.children[1].value.split(",")
                emb = discord.Embed(
                    description=f"**{t.reged}) TEAM NAME: {teamname}**\n**Players** : {', '.join(players)} ")
                emb.set_author(name=interaction.guild.name, icon_url=interaction.guild.icon or interaction.guild.me.avatar.url)
                emb.timestamp = interaction.message.created_at
                emb.set_thumbnail(url=interaction.user.display_avatar)
                await cch.send(content=f"{interaction.user.mention} {teamname}", embed=emb)
                await interaction.user.add_roles(crole)
                self.dbc.update_one({"rch":cch.id},{"$inc":{"reged":1}})
                await interaction.response.send_message("Team Registered!!", ephemeral=True)
            inp.on_submit = register_team


    @commands.Cog.listener()
    async def on_interaction(self, interaction:discord.Interaction):
        
        if interaction.user.bot or not interaction.guild:
            return

        if interaction.data.get("custom_id") not in self.MANAGER_PREFIXES:
            return
        
        db:dict = self.bot.db.dbc.find_one({"mch":interaction.channel.id})
        await interaction.response.defer(ephemeral=True)
        if not db:
            _message = "Tournament is No Longer Available!!"
            return await interaction.followup.send( _message,  ephemeral=True )

        view = View()
        crole:discord.Role = interaction.guild.get_role(db["crole"])
        cch:discord.TextChannel = self.bot.get_channel(db["cch"])
        
        if not cch : 
            return await interaction.followup.send(
                f"Confirm Channel Not Found!! {discord.utils.get(interaction.guild.roles, name='tourney-mod')}", 
                ephemeral=True
            )
        
        if not crole:
            await self.log(interaction.guild, message=f"{emoji.cross} | Confirm Role Not Found For <#{db.get('rch')}>!!\nPlease Check The Tournament Configurations",
                    color=self.bot.color.red
                ) #fixed NoneType Error !!
            return await interaction.followup.send("Confirm Role Not Found!! please try again later!! i've notified mods...", ephemeral=True)

        options = []
        async for i in cch.history(limit=db["tslot"]):
            if i.embeds and "TEAM" in i.embeds[0].description and i.author.id == i.guild.me.id:
                if any([interaction.user.id in i.mentions, interaction.user.name in i.embeds[0].description]):
                    st = i.embeds[0].description.find("[")+1
                    en = i.embeds[0].description.find("]")
                    options.append(discord.SelectOption(label=i.embeds[0].description[st:en],  value=i.id))

        if len(options) == 0:
            return await interaction.followup.send("Unable to find your team!! ", ephemeral=True)

        cslotlist = discord.ui.Select(min_values=1, max_values=1, options=options)
        view.add_item(cslotlist)
        cslotlist.callback = None    

        if interaction.data["custom_id"] == "Cslot":
            await interaction.followup.send(view=view, ephemeral=True)

            async def confirm(interact:discord.Interaction):
                await interact.response.defer(ephemeral=True)
                conf = Button(label="Confirm", style=discord.ButtonStyle.red)
                canc = Button(label="Cancel", style=discord.ButtonStyle.green)
                v2 = View()
                for i in [conf]:
                    v2.add_item(i)

                await interact.followup.send(embed=discord.Embed(description="Do You Want To Cancel Your Slot?"), view=v2, ephemeral=True)


                async def cnf(cnfinteract:discord.Interaction):
                    await cnfinteract.response.defer(ephemeral=True)
                    """
                    Asynchronously cancels a slot and removes the associated role from the mentioned member.

                    This function deletes the message containing the slot information and removes the specified role
                    from the guild member mentioned in the message.

                    Parameters:
                        cnfinteract (discord.Interaction): The interaction that triggered the confirmation.

                    Returns:
                        None: Sends an ephemeral message confirming the slot cancellation.
                    """
                    ms = await cch.fetch_message(cslotlist.values[0])

                    # maybe we can optimize it further by parsing the member through his id from the message content
                    for member in ms.mentions:

                        if isinstance(member, discord.Member):
                            # check self permission before removing the role
                            if (not interaction.guild.me.guild_permissions.manage_roles) or  (not interaction.guild.me.guild_permissions.manage_messages):
                                await cnfinteract.followup.send(
                                    "I Don't Have Permission To Remove The Role\nRequired Perms : `manage_roles`, `manage_messages`", 
                                    ephemeral=True
                                )
                                return
                            await member.remove_roles(crole)
                            await ms.delete()
                            self.bot.db.dbc.update_one({"rch":cch.id},{"$inc":{"reged":-1}})

                    await cnfinteract.followup.send("Slot Cancelled!!", ephemeral=True)
                    return
                        
                async def cnc(interact:discord.Interaction):
                    await interact.response.defer(ephemeral=True)
                    """
                    Cancels the current operation and deletes the interaction message.

                    Parameters
                    ----------
                    interact : discord.Interaction
                        The interaction to respond to.

                    Returns
                    -------
                    None
                        This function doesn't return anything, but has the side effect of deleting the message
                        associated with the interaction.
                    """
                    await interact.message.delete()


                conf.callback = cnf
                canc.callback = cnc
            cslotlist.callback = confirm

        if interaction.data["custom_id"] == "Mslot":

            await interaction.followup.send(view=view, ephemeral=True) #fixe unknown interaction error

            async def myteam(m_int:discord.Interaction):
                await m_int.response.defer(ephemeral=True)
                ms = await cch.fetch_message(cslotlist.values[0])
                emb = ms.embeds[0].copy()
                await m_int.followup.send(embed=emb, ephemeral=True)

            cslotlist.callback = myteam

        if interaction.data.get("custom_id") == "Cancel" and interaction.message:
            await interaction.message.delete()

        if interaction.data["custom_id"] == "Tname":
            await interaction.followup.send(view=view, ephemeral=True)

            async def change_teamname(tname_int:discord.Interaction):
                inp = discord.ui.Modal(title="Team Name", timeout=30)
                text = (discord.ui.TextInput(label="Enter Team Name", placeholder="Team Name", max_length=20, custom_id="teamname"))
                inp.add_item(text)
                await tname_int.response.send_modal(inp)

                async def tname(tname_modal_int:discord.Interaction):
                        await tname_modal_int.response.defer(ephemeral=True)
                        nme = inp.children[0].value.upper()
                        ms = await cch.fetch_message(cslotlist.values[0])
                        pem = ms.embeds[0]
                        st = pem.description.find("[")+1
                        en = pem.description.find("]")
                        team = pem.description[st:en]
                        desc = pem.description.replace(team, nme)
                        emb = discord.Embed(color=pem.color, description=desc)
                        emb.set_author(name=tname_modal_int.guild.name, icon_url=tname_modal_int.guild.icon or tname_modal_int.guild.me.avatar.url)
                        emb.set_thumbnail(url=tname_modal_int.user.display_avatar or tname_modal_int.guild.icon or tname_modal_int.guild.me.avatar.url)
                        emb.timestamp = ms.created_at
                        try:
                            await ms.edit(content = f"{nme} {ms.mentions[0].mention}",embed=emb) if ms else None

                        except Exception as e:
                            return await tname_modal_int.followup.send(
                                f'Unable To Change Team Name At This Time!!\nReason : {e}', 
                                ephemeral=True
                            )
                        return await tname_modal_int.followup.send(f'Team Name Changed {team} -> {nme}', ephemeral=True)


                inp.on_submit = tname
            cslotlist.callback = change_teamname


        # Currently Testing on this and not sure to impliment this or not
        elif "custom_id" in interaction.data and interaction.data["custom_id"].startswith("db_reg_btn"):
            await self.register(interaction)


    @commands.Cog.listener()
    async def  on_guild_channel_delete(self, channel:discord.TextChannel):
        tourch = self.dbc.find_one({"rch" : channel.id})
        dlog = self.bot.get_channel(self.bot.config.tourney_delete_log)
        if tourch:
            self.dbc.delete_one({"rch" : channel.id})
            await dlog.send(f"```json\n{tourch}\n```")
