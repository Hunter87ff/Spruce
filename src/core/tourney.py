"""
                    GNU GENERAL PUBLIC LICENSE
                       Version 3, 29 June 2007

 Copyright (C) 2022 hunter87.dev@gmail.com
 Everyone is permitted to copy and distribute verbatim copies
 of this license document, but changing it is not allowed.
 """


import discord
import datetime
import asyncio
from asyncio import sleep
from discord.utils import get
from typing import TYPE_CHECKING
from discord.ext import commands
from discord.ui import Button, View
from modules import config, checker
from modules.bot import Spruce  # Added proper import here

from ext import constants, permissions, Tourney, emoji, color, files





def get_front(name:str):
  li = []
  for i in name.split()[0:2]:li.append(i[0])
  return str("".join(li) + "-")


class Esports(commands.Cog):
    ONLY_AUTHOR_BUTTON = "Only Author Can Use This Button"
    MANAGER_PREFIXES = ["Cslot", "Mslot", "Tname", "Cancel"]

    def __init__(self, bot):
        self.bot:Spruce = bot
        self.dbc = bot.db.dbc
        self._tnotfound = "Tournament Not Found"


    @commands.Cog.listener()
    async def on_guild_role_delete(self, role:discord.Role):
        members = []
        if self.dbc.find_one({"crole":role.id}):
            db = self.dbc.find_one({"crole":role.id})
            cch = discord.utils.get(role.guild.channels,id=db["cch"])
            messages = [message async for message in cch.history(limit=int(db["tslot"])+50)]
            members = {m for msg in messages for m in role.guild.members if m.mention in msg.content}
            newr = await role.guild.create_role(name=role.name, reason="[Recovering] If You Want To Delete This Role use &tourney command")
            self.dbc.update_one({"crole":int(role.id)}, {"$set" : {"crole" :int(newr.id)}})
            for i in members:await i.add_roles(newr, reason="[Recovering] Previous Confirm Role Was acidentally Deleted.")

    async def get_input(self, ctx:commands.Context, check=None, timeout=30):
        check = check or (lambda m: m.channel == ctx.channel and m.author == ctx.author)
        try:
            msg:discord.Message = await ctx.bot.wait_for("message", check=check, timeout=timeout)
            return msg.content
        except asyncio.TimeoutError:
            return await ctx.send("Time Out! Try Again", delete_after=5)

    async def unlc_ch(self, channel:discord.TextChannel, role:discord.Role=None):
        role = role or channel.guild.default_role
        overwrite = channel.overwrites_for(role)
        overwrite.update(send_messages=True)
        await channel.set_permissions(role, overwrite=overwrite)

    async def lc_ch(self, channel:discord.TextChannel, role:discord.Role=None):
        if role == None:role = channel.guild.default_role
        overwrite = channel.overwrites_for(role)
        overwrite.update(send_messages=False)
        await channel.set_permissions(role, overwrite=overwrite)



    @commands.hybrid_command(with_app_command = True, aliases=["export"])
    @commands.guild_only()
    @commands.cooldown(2, 20, commands.BucketType.user)
    @permissions.tourney_mod()
    @commands.bot_has_guild_permissions(send_messages=True, attach_files=True)
    async def export_event_data(self, ctx:commands.Context, registration_channel:discord.TextChannel):
        if ctx.author.bot:return
        await ctx.defer()
        try:
            _event = Tourney.findOne(registration_channel.id)
            if not _event:
                return await ctx.send("No event found in this channel")
            _teams = "" ## to store the teams data
            _slot = 0 ## to store the slot number


            _confirm_channel = self.bot.get_channel(_event.cch) ##confirm channel to get the teams data

            # if the confirm channel is not found, return an error message
            if not _confirm_channel:
                return await ctx.send("No confirm channel found")
            
            async for message in _confirm_channel.history(limit=100):
                # if the message author is not the bot, skip it
                if message.author.id != self.bot.user.id: 
                    continue
                # if the message doesn't contains an embed, skip it
                if not message.embeds:
                    continue
                # if the message doesn't contains a mention, skip it
                _captain = message.mentions[0] if message.mentions else ""

                _team = message.content.replace(_captain.mention, "").replace(" ", "").replace("\n", "")

                # fetches the teammates from embed description, currently it can can't handle the usernames, just the mentions
                _players = message.embeds[0].description.split("\n")[-1].replace("**Players** : ", "") if message.embeds else "Added By Moderator"
                if _captain and _team:
                    _teams += f"{_slot},{_team},{_captain}, {_players}\n"
                    _slot += 1

            _content = "Event,Slots,Registered,Mentions,Prize\n"
            _content += f"{_event.tname or registration_channel.category.name},{_event.tslot},{_event.reged},{_event.mentions},{_event.prize}\n\n"
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
            self.bot.embed_log("core.tourney.export_event_data", 84, e)

    @commands.hybrid_command(description="Create tournament", with_app_command = True, aliases=['ts','tourneysetup','setup', 'tsetup'])
    @commands.bot_has_guild_permissions(manage_channels=True, manage_roles=True, send_messages=True, add_reactions=True, read_message_history=True)
    @commands.guild_only()
    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.has_permissions(manage_channels=True, manage_roles=True, manage_messages=True, add_reactions=True, read_message_history=True)
    async def tourney_setup(self, ctx:commands.Context, total_slot:int, mentions:int, slot_per_group:int,  *, name:str):
        if slot_per_group < 1:
            return await ctx.send("Slot Per Group Should Be 1 or above")
        if ctx.author.bot:return None
        if not await config.voted(ctx, bot=self.bot):
            return await config.vtm(ctx)            
        front = get_front(name)
        try:
            ms = await ctx.send(constants.PROCESSING)
            bt = ctx.guild.get_member(self.bot.user.id)
            tmrole = discord.utils.get(ctx.guild.roles, name="tourney-mod")
            if not tmrole:tmrole = await ctx.guild.create_role(name="tourney-mod")
            if tmrole and not ctx.author.guild_permissions.administrator:
                if tmrole not in ctx.author.roles:
                    return await ctx.send(f"You Must Have {tmrole.mention} role to run rhis command")
            if int(total_slot) > 1100:
                return await ctx.send("Total Slot should be below 1100")
            if int(total_slot) < 1100:
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
                await self.unlc_ch(channel=r_ch)
                c_ch = await ctx.guild.create_text_channel(str(front)+"confirmed-teams", category=category, reason=reason)  
                await sleep(1)  #sleep
                g_ch = await ctx.guild.create_text_channel(str(front)+"groups", category=category, reason=reason)
                quer = await ctx.guild.create_text_channel(str(front)+"queries", category=category, reason=reason)
                await self.unlc_ch(channel=quer)
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
                tour_count = len(list(self.dbc.find({"guild" : ctx.guild.id})))

                if tour_count > 5:
                    return await ctx.send(embed=discord.Embed(description="Tournament Limit Reached!! you can delete previous tournament to create another one. or contact us via support server!!", color=0xff0000), delete_after=30)
                self.dbc.insert_one(tour)
                await self.set_manager(ctx, r_ch)
                return await ms.edit(
                    content=None, 
                    embed=discord.Embed(
                        color=color.cyan, 
                        description=f'{emoji.tick} | Successfully Created. Tournament Slot({tour_count+1}/5 used)'
                    ), 
                    delete_after=20) if ms else None
        except Exception:return



    @commands.hybrid_command(with_app_command = True, aliases=["girlslobby"])
    @commands.has_role("tourney-mod")
    @commands.guild_only()
    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.has_permissions(manage_channels=True, manage_roles=True)
    @commands.bot_has_guild_permissions(manage_channels=True, manage_roles=True, send_messages=True)
    async def girls_lobby(self, ctx:commands.Context, vc_amount : int):
        await ctx.defer(ephemeral=True)
        if ctx.author.bot:return
        if not await config.voted(ctx, bot=self.bot):
            return await config.vtm(ctx)
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



    @commands.hybrid_command(with_app_command = True)
    @commands.guild_only()
    @commands.has_role("tourney-mod")
    @commands.bot_has_guild_permissions(manage_channels=True, send_messages=True)
    async def start_tourney(self, ctx:commands.Context, registration_channel : discord.TextChannel):
        await ctx.defer(ephemeral=True)
        if ctx.author.bot:return
        dbcd = self.dbc.find_one({"rch" : registration_channel.id})
        if not dbcd:
            return await ctx.send(embed=discord.Embed(description="**No Tournament Running In This Channel**", color=color.blurple), delete_after=10)
        self.dbc.update_one({"rch" : registration_channel.id}, {"$set" : {"status" : "started"}})
        await registration_channel.send(embed=discord.Embed(color=color.cyan, description="Registration Started"))
        await ctx.send("Started", delete_after=10)

            

    @commands.hybrid_command(with_app_command = True, aliases=['pt'])
    @commands.guild_only()
    @commands.has_role("tourney-mod")
    async def pause_tourney(self, ctx:commands.Context, registration_channel : discord.TextChannel):
        if ctx.author.bot:return
        await ctx.defer(ephemeral=True)
        dbcd = self.dbc.find_one({"rch" : registration_channel.id})
        if not dbcd:
            return await ctx.send('No Tournament Running In This Channel')
        self.dbc.update_one({"rch" : registration_channel.id}, {"$set" : {"status" : "paused"}})
        await registration_channel.send(embed=discord.Embed(color=config.orange, description="Registration Paused"))
        await ctx.send("Paused", delete_after=10)

        

    @commands.hybrid_command(with_app_command = True)
    @commands.guild_only()
    @commands.has_role("tourney-mod")
    async def cancel_slot(self, ctx:commands.Context, registration_channel : discord.TextChannel, member : discord.Member, reason:str="Not Provided"):
        await ctx.defer(ephemeral=True)
        if ctx.author.bot:return
        if not await config.voted(ctx, bot=self.bot):
            return await config.vtm(ctx)
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
            messages = [message async for message in cch.history(limit=123)]  
            for message in messages:
                if member.mention in message.content and message.author.id == self.bot.user.id:
                    await message.delete() 
                    await ctx.send(embed=discord.Embed(title=f"{member}'s Slot Canceled with reason of {reason}", color=color.green))



    @commands.hybrid_command(with_app_command = True)
    @commands.guild_only()
    @commands.has_role("tourney-mod")
    @commands.bot_has_guild_permissions(send_messages=True, manage_roles=True)
    async def add_slot(self, ctx:commands.Context, registration_channel: discord.TextChannel, member:discord.Member, *, team_name):
        await ctx.defer(ephemeral=True)
        if ctx.author.bot:return
        if not await config.voted(ctx, bot=self.bot):
            return await config.vtm(ctx)
        tmrole = discord.utils.get(ctx.guild.roles, name="tourney-mod")
        if tmrole == None:tmrole = await ctx.guild.create_role("tourney-mod")
        if ctx.author.guild_permissions.manage_channels or tmrole in ctx.author.roles:
            dbcd:dict[str] = self.dbc.find_one({"rch" : registration_channel.id})
            if not dbcd:
                return await ctx.send(embed=discord.Embed(description=f"**{self._tnotfound}**", color=color.red), delete_after=10)
            crole = discord.utils.get(ctx.guild.roles, id=int(dbcd["crole"]))
            if not crole:
                return await ctx.send("Confirm Role Not Found", delete_after=10)
            reged = dbcd.get("reged")
            cch = discord.utils.get(ctx.guild.channels, id=int(dbcd["cch"]))
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
            


    @commands.hybrid_command(with_app_command = True)
    @commands.cooldown(2, 60, commands.BucketType.user)
    @commands.guild_only()
    async def tourneys(self, ctx:commands.Context):
        if ctx.author.bot:return 
        if not await config.voted(ctx, bot=self.bot):return await config.vtm(ctx)
        await ctx.defer(ephemeral=True)
        ms = await ctx.send(constants.PROCESSING)
        emb = discord.Embed(title="__ONGOING TOURNAMENTS__", url=config.invite_url, color=0x00ff00)
        data  = self.dbc.find({"pub" : "yes"})
        for i in data:
            obj = Tourney(i)
            rch = self.bot.get_channel(int(i["rch"]))
            if rch and obj.reged < obj.tslot*0.98 and obj.reged >= obj.tslot*0.1 and obj.status=="started":
                link = await rch.create_invite(reason=None,max_age=360000,max_uses=0,temporary=False,unique=False,target_type=None,target_user=None,target_application_id=None)
                emb.add_field(name=f'{obj.tname.upper()}', value=f"Prize: {obj.prize.upper()}\nServer: {rch.guild.name[0:20]}\n[Register]({link})\n---------------- ")

        if len(emb.fields) > 0:
            await ctx.author.send(embed=emb)
            if ms:
                await ms.edit(content="Please Check Your DM") 
        else: 
            if ms:
                await ms.edit(content="Currently Unavailable")
        


    @commands.hybrid_command(with_app_command = True, aliases=["pub"])
    @commands.bot_has_permissions(create_instant_invite=True)
    @commands.has_guild_permissions(manage_messages=True, manage_channels=True, manage_roles=True)
    @commands.has_role("tourney-mod")
    @commands.cooldown(2, 20, commands.BucketType.user)
    @commands.guild_only()
    async def publish(self, ctx:commands.Context, rch: discord.TextChannel, *, prize: str):
        await ctx.defer(ephemeral=True)
        if ctx.author.bot:return
        if not await config.voted(ctx, bot=self.bot):
            return await config.vtm(ctx)
        if len(prize) > 30:
            return await ctx.reply("Only 30 Letters Allowed ")
        try:
            dbcd = self.dbc.find_one({"rch" : rch.id})
            if dbcd["reged"] < dbcd["tslot"]*0.1:
                return await ctx.send("You need To Fill 10% Of Total Slot. To Publish This Tournament")
        except Exception:
            return await ctx.send(self._tnotfound)
        self.dbc.update_one({"rch" : rch.id}, {"$set" : {"pub" : "yes", "prize" : prize}})
        await ctx.send(f"**{rch.category.name} is now public**")


            
    @commands.hybrid_command(with_app_command = True)
    @commands.guild_only()
    @commands.has_role("tourney-mod")
    @commands.has_guild_permissions(manage_channels=True, manage_roles=True)
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


    @commands.hybrid_command(with_app_command = True)
    @commands.guild_only()
    @commands.has_any_role("tourney-mod")
    @commands.bot_has_guild_permissions(send_messages=True)
    async def tourney(self, ctx:commands.Context, registration_channel: discord.TextChannel):
        await ctx.defer(ephemeral=True)
        if ctx.author.bot:return
        if not await config.voted(ctx, bot=self.bot): 
            return await config.vtm(ctx)
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
            exportButton = Button(label="Export Data", style=discord.ButtonStyle.blurple)
            
            spgbtn = Button(label="Slots per group")
            buttons = [bt0, bt1, bt2, bt3, spgbtn, bt6, bt9, bt10, bt12, bt4, exportButton]
            view = View()
            emb = discord.Embed(
                title=rch.category.name, 
                description=f"**Total Slot : {tourn.tslot}\nRegistered : {tourn.reged}\nMentions : {tourn.mentions}\nStatus : {tourn.status}\nPublished : {tourn.pub.upper()}\nPrize : {tourn.prize}\nSlot per group: {tourn.spg}\nFakeTag Allowed : {tourn.faketag.upper()}\nRegistration : <#{tourn.rch}>\nConfirm Channel: <#{tourn.cch}>\nGroup Channel: <#{tourn.gch}>\nConfirm Role : <@&{tourn.crole}>**", 
                color=color.cyan, 
                timestamp=datetime.datetime.now()
            )
            emb.set_footer(
                text=f"Requested By {ctx.author}", 
                icon_url=ctx.author.avatar.url or ctx.me.avatar.url
            )
            for button in buttons:
                view.add_item(button)
            msg1 = await ctx.send(embed=emb, view=view)

            async def save_delete(interaction:discord.Interaction):
                if msg1 : await msg1.delete()

            async def delete_tourney_confirm(interaction:discord.Interaction):
                view = View().add_item(bt11)
                await interaction.response.send_message("**Are You Sure To Delete The Tournament?**", view=view)

            async def delete_t_confirmed(interaction:discord.Interaction):
                if interaction.message:
                    await interaction.message.edit(
                        content=f"**{emoji.loading} {constants.PROCESSING}**"
                    )
                self.dbc.delete_one({"rch" : registration_channel.id })
                await save_delete(interaction)
                await interaction.message.delete()

            async def publish(interaction:discord.Interaction):
                await interaction.response.defer(ephemeral=True)
                if tourn.pub == "no":
                    if tourn.reged >= tourn.tslot*0.1:
                        ms = await ctx.send("Enter The Prize Under 15 characters")
                        prize = str(await self.get_input(ctx))
                        if len(prize) > 15:
                            return await ms.edit("Word Limit Reached. Try Again Under 15 Characters") if ms else None
                        if len(prize) <= 15:
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

            async def c_ch(interaction:discord.Interaction):
                if interaction.user != ctx.author: return await ctx.send(self.ONLY_AUTHOR_BUTTON)
                await interaction.response.send_message("Mention Confiration Channel")
                cchannel = await checker.channel_input(ctx)
                acch = self.dbc.find_one({"cch" : cchannel.id})
                if cchannel.id == tourn.cch or acch != None:return await ctx.send("A Tournament Already Running In This channel", delete_after=10)
                await interaction.delete_original_response()
                if not cchannel:return await ctx.send("Kindly Mention A Channel!!", delete_after=5)
                self.dbc.update_one({"rch": rch.id}, {"$set":{"cch": cchannel.id}})
                await ctx.send("Confirm Channel Updated", delete_after=5)
                await interaction.message.edit(
                    embed=discord.Embed(
                        description=interaction.message.embeds[0].description.replace(f"<#{tourn.cch}>", f"<#{cchannel.id}>"), 
                        color=color.cyan)
                ) if interaction.message else None
                tourn.cch = cchannel.id


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
                if interaction.user != ctx.author:
                    return await ctx.send(self.ONLY_AUTHOR_BUTTON)
                tsl = await(checker.get_input(interaction=interaction, title="Total Slot", label="Enter Total Slot Between 2 and 1100"))
                try:
                    if int(tsl) > 1100 or int(tsl)<1:
                        return await ctx.send("Only Number Between 1 and 1100", delete_after=20)
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
                    await self.bot.get_channel(config.erl).send(
                        content=f"<@{config.owner_id}>",
                        embed=discord.Embed(
                            title=f"Error | {ctx.command.name}\n `Module : core.tourney | Line : 632`", description=f"```{e}```", 
                            color=color.red
                        )
                    )
                    return await ctx.send(
                        embed=discord.Embed(
                            description=f"{color.reddot} Unable to update | Try again!!", 
                            color=color.red
                            ), 
                        delete_after=5
                    )
                
            async def export_event_data_callback(interaction:discord.Interaction):
                if interaction.user != ctx.author:
                    await interaction.response.send_message(self.ONLY_AUTHOR_BUTTON)
                    return

                await interaction.response.send_message("Exporting Event Data...")
                await self.export_event_data(ctx, rch)
                await interaction.message.delete()
                


            bt6.callback = c_ch
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
            exportButton.callback = export_event_data_callback





    @commands.hybrid_command(with_app_command = True, aliases=['gsetup'])
    @commands.has_role("tourney-mod")
    @commands.guild_only()
    @commands.cooldown(1, 60, commands.BucketType.guild)
    @commands.has_permissions(manage_channels=True, manage_roles=True, manage_permissions=True)
    @commands.bot_has_permissions(send_messages=True, manage_channels=True, manage_roles=True, manage_permissions=True)
    async def group_setup(self, ctx:commands.Context, prefix:str, start:int, end:int, category:discord.CategoryChannel=None):
        await ctx.defer(ephemeral=True)
        if ctx.author.bot:return
        elif not await config.voted(ctx, bot=self.bot): return await config.vtm(ctx)
        elif start < 1:return await ctx.reply("Starting Number Should Not Be Lower Than 1")
        elif end < start:return await ctx.reply("Ending Number Should Not Be Lower Than Starting Number")
        ms = await ctx.send(f"{emoji.loading}| {constants.PROCESSING}")
        if category == None:category = await ctx.guild.create_category(name=f"{prefix} Groups")
        await category.set_permissions(ctx.guild.default_role, view_channel=False)
        for i in range(start, end+1):
            role = await ctx.guild.create_role(name=f"{prefix.upper()} G{i}", color=0x4bd6af)
            channel = await ctx.guild.create_text_channel(name=f"{prefix}-group-{i}", category=category)
            overwrite = ctx.channel.overwrites_for(role)
            overwrite.update(view_channel=True, send_messages=False, add_reactions=False, attach_files=True)
            await channel.set_permissions(role, overwrite=overwrite)
            await sleep(2)
        if ms :
            await ms.edit(content=f"{emoji.tick} | Successfully Created") if ms else None


    @commands.hybrid_command(with_app_command = True, aliases=["cs"])
    @commands.has_any_role("tourney-mod")
    @commands.guild_only()
    @commands.bot_has_guild_permissions(send_messages=True, manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    async def change_slot(self, ctx:commands.Context, *, slot:str):
        if not await config.voted(ctx, bot=self.bot):
            return await config.vtm(ctx)
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
    @commands.has_role("tourney-mod")
    @commands.has_guild_permissions(manage_channels=True, manage_roles=True, manage_permissions=True)
    @commands.bot_has_guild_permissions(send_messages=True, manage_channels=True, manage_roles=True, manage_permissions=True)
    async def tourney_reset(self, ctx:commands.Context, channel: discord.TextChannel):
        if ctx.author.bot:return 
        if not await config.voted(ctx, bot=self.bot): return await config.vtm(ctx)
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


    @commands.hybrid_command(with_app_command = True, aliases=["autogroup"])
    @commands.guild_only()
    @commands.has_role("tourney-mod")
    @commands.has_guild_permissions(manage_channels=True, manage_roles=True, manage_permissions=True)
    @commands.bot_has_guild_permissions(send_messages=True, manage_channels=True, manage_roles=True, manage_permissions=True)
    async def auto_group(self, ctx:commands.Context, registration_channel:discord.TextChannel):
        if ctx.author.bot:return
        if not await config.voted(ctx, bot=self.bot):return await config.vtm(ctx)
        rch = registration_channel
        await ctx.defer(ephemeral=True)
        self.dbc.update_one({"rch":rch.id},{"$set":{"cgp":0}})
        db = self.dbc.find_one({"rch":rch.id})
        if not db: return await ctx.send(self._tnotfound, delete_after=10)
        teams = []
        cch = self.bot.get_channel(int(db["cch"]))
        gch = self.bot.get_channel(int(db["gch"]))
        if not cch:return await ctx.send("Confirm Channel Not Found")
        if not gch:return await ctx.send("Group Channel Not Found")
        tslot = db["tslot"]
        spg = db["spg"]
        cgp = db["cgp"]
        tprefix:str =  db["prefix"]
        messages = [message async for message in cch.history(limit=tslot+100)]
        for msg in messages[::-1]:
            if msg.author.id == self.bot.user.id and msg.embeds:
                if "TEAM" in msg.embeds[0].description:teams.append(msg)

        if len(teams) < 1:return await ctx.send("Minimum Number Of Teams Isn't Reached!!")
        category = await ctx.guild.create_category(name=f"{tprefix} Groups")
        await category.set_permissions(ctx.guild.default_role, view_channel=False)
        group = int(len(teams)/spg)
        if len(teams)/spg > group:group = group+1
        if len(teams)/spg < 1:group = 1
        for i in range(1, group+1):
            channel = await ctx.guild.create_text_channel(name=f"{tprefix}-group-{i}", category=category)
            role = await ctx.guild.create_role(name=f"{tprefix.upper()} G{i}", color=0x4bd6af)
            overwrite = ctx.channel.overwrites_for(role)
            overwrite.update(view_channel=True, send_messages=False, add_reactions=False, attach_files=True)
            await channel.set_permissions(role, overwrite=overwrite)
            ms = f"**__GROUP__ {i}\n"
            grp:list[discord.Message] = teams[cgp:cgp+spg]
            for p in grp:ms = ms + f"{grp.index(p)+1}) {p.content}" + "\n"
            grp.clear()
            ncgp = cgp+spg
            self.dbc.update_one({"rch":rch.id},{"$set":{"cgp":ncgp}})
            cgp = cgp+spg
            msg = await gch.send(f"{ms}**")
            for m in ctx.guild.members:
                if m.mention in msg.content:await m.add_roles(role)
            await msg.add_reaction(emoji.tick)
        await ctx.send(f"check this channel {gch.mention}")
        del messages, teams, group, category, role, channel, overwrite, ms, grp, ncgp, msg, m, cgp


    @commands.hybrid_command(with_app_command = True)
    @commands.guild_only()
    @commands.has_role("tourney-mod")
    @commands.has_permissions(manage_channels=True, manage_roles=True, manage_permissions=True)
    @commands.bot_has_guild_permissions(send_messages=True, manage_channels=True, manage_roles=True, manage_permissions=True)
    async def set_manager(self, ctx:commands.Context, registration_channel:discord.TextChannel):
        if ctx.author.bot:return
        view = View()
        channel = registration_channel
        db = self.dbc.find_one({"rch":channel.id})
        if not db:return await ctx.send(embed=discord.Embed(description=self._tnotfound, color=color.red), delete_after=10)
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
        
        for i in buttons:view.add_item(i)
        await mch.send(embed=emb, view=view)
        await self.lc_ch(channel=mch)
        self.dbc.update_one({"rch":channel.id},{"$set":{"mch":int(mch.id)}})
        await ctx.send(f"{emoji.tick} | {mch.mention} created")


    @commands.hybrid_command(with_app_command = True, description="list of all the ongoing tournaments")
    @commands.guild_only()
    @commands.has_role("tourney-mod")
    @commands.has_permissions(manage_channels=True, manage_roles=True, manage_permissions=True)
    @commands.bot_has_guild_permissions(send_messages=True, manage_channels=True, manage_roles=True, manage_permissions=True)
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
        bt11 = Button(label="Confirm", style=discord.ButtonStyle.danger)
        bt12 = Button(label="Cancel", custom_id="Cancel", style=discord.ButtonStyle.blurple)
        btmanage = Button(label="Manage", custom_id="btmanage", style=discord.ButtonStyle.green)
        tlist = discord.ui.Select(min_values=1, max_values=1, options=options)
        view.add_item(tlist)
        view.add_item(bt12)
        _msg = await ctx.send(embed=embed, view=view)

        async def tourney_details(interaction:discord.Interaction):
            await interaction.response.defer()
            db:Tourney = self.dbc.find_one({"rch":int(tlist.values[0])})
            if not db: 
                await interaction.response.send_message(self._tnotfound, delete_after=10)
                return
            
            db = Tourney(db)
            embed.title=db.tname.upper()
            embed.description=f"**Total Slot : {db.tname}\nRegistered : {db.reged}\nMentions : {db.mentions}\nStatus : {db.status}\nPublished : {db.pub}\nPrize : {db.prize}\nSlot per group: {db.spg}\nFakeTag Allowed: {db.faketag}\nRegistration : <#{db.rch}>\nConfirm Channel: <#{db.cch}>\nGroup Channel: <#{db.gch}>\nConfirm Role : <@&{db.crole}>**"

            if bt10 not in view.children:
                view.add_item(bt10)
            if btmanage not in view.children:
                view.add_item(btmanage)

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


        tlist.callback = tourney_details
        bt10.callback = delete_tourney_confirm
        bt11.callback = delete_t_confirmed
        btmanage.callback = manage_tournament


    # Currently it's a developer only command, and under development
    # With this command you can send a message containing a button to register a team
    # Then the user can submit a regiatration form to register their team
    # but there is a issue with the teammate mention and i'm working on it 
    # @commands.hybrid_command(with_app_command = True)
    @commands.command()
    @commands.guild_only()
    @permissions.dev_only()
    @commands.has_role("tourney-mod")
    @commands.bot_has_guild_permissions(manage_channels=True, manage_roles=True, manage_permissions=True)
    async def start_reg(self, ctx:commands.Context, registration_channel:discord.TextChannel):
        if ctx.author.bot:return
        await ctx.defer(ephemeral=True)
        db = self.dbc.find_one({"rch":registration_channel.id})
        if not db:return await ctx.send(embed=discord.Embed(description=self._tnotfound, color=color.red), delete_after=10)
        tourObj:Tourney = Tourney(db)
        emb:discord.Embed = discord.Embed(color=color.cyan, description=f"**{emoji.cup} | REGISTRATION STARTED | {emoji.cup}\n{emoji.tick} | TOTAL SLOT : {tourObj.tslot}\n{emoji.tick} | REQUIRED MENTIONS : {tourObj.mentions}\n{emoji.cross} | FAKE TAGS NOT ALLOWED**")
        btn:Button = Button(label="Register Team", style=discord.ButtonStyle.red, custom_id=f"db_reg_btn_{self.bot.user.id}")
        view:View = View().add_item(btn)
        await registration_channel.send(embed=emb, view=view)



    # This one is under development and currently testing on it!! and im not sure to impliment this or not, due to some mention related issues
    # If you have any idea or suggestion please let me know in the issue section or raise a PR
    async def register(self, interaction:discord.Interaction):
        db = self.dbc.find_one({"rch":interaction.channel.id})
        if not db:return await interaction.response.send_message("Tournament is No Longer Available!!", ephemeral=True)
        if interaction.data["custom_id"] == f"db_reg_btn_{self.bot.user.id}":
            t:Tourney = Tourney(db)
            crole:discord.Role = interaction.guild.get_role(t.crole)
            cch:discord.TextChannel = self.bot.get_channel(t.cch)

            inp = discord.ui.Modal(title="Registraion Form", timeout=30)
            fields = [
                discord.ui.TextInput(label="Enter Team Name", placeholder="Team Name", max_length=20, custom_id="rg_teamname"),
                discord.ui.TextInput(label="Enter Player Names", placeholder="playerX, playerR, player4 (comma as separator)", max_length=200, custom_id="rg_players"),
                ]
            for i in fields:
                inp.add_item(i)
            await interaction.response.send_modal(inp)

            async def register_team(interaction:discord.Interaction):
                teamname:str = inp.children[0].value.upper()
                players = inp.children[1].value.split(",")
                emb = discord.Embed(color=0xffff00, description=f"**{t.reged}) TEAM NAME: {teamname}**\n**Players** : {players} ")
                emb.timestamp = interaction.message.created_at
                emb.set_thumbnail(url=interaction.user.display_avatar)
                await cch.send(content=f"{interaction.user.mention} {teamname}", embed=emb)
                await interaction.user.add_roles(crole)
                self.dbc.update_one({"rch":cch.id},{"$inc":{"reged":1}})
                await interaction.response.send_message("Team Registered!!", ephemeral=True)
            inp.on_submit = register_team


    @commands.Cog.listener()
    async def on_interaction(self, interaction:discord.Interaction):
        if interaction.user.bot:return
        elif "custom_id" in interaction.data and interaction.data["custom_id"] in self.MANAGER_PREFIXES:
            db = self.dbc.find_one({"mch":interaction.channel.id})
            if not db:
                return await interaction.response.send_message("Tournament is No Longer Available!!", ephemeral=True)
            view = View()
            crole:discord.Role = interaction.guild.get_role(db["crole"])
            cch:discord.TextChannel = self.bot.get_channel(db["cch"])
            if not cch : 
                return await interaction.response.send_message(
                    f"Confirm Channel Not Found!! {discord.utils.get(interaction.guild.roles, name='tourney-mod')}", 
                    ephemeral=True
                )
            if not crole:
                return await interaction.response.send_message("Confirm Role Not Found!!")
            teams = [message async for message in cch.history(limit=db["tslot"])]
            options = []
            for i in teams:
                if i.embeds and "TEAM" in i.embeds[0].description and i.author.id == i.guild.me.id:
                    if f"<@{interaction.user.id}>" in i.embeds[0].description:
                        st = i.embeds[0].description.find("[")+1
                        en = i.embeds[0].description.find("]")
                        options.append(discord.SelectOption(label=i.embeds[0].description[st:en],  value=i.id))
            if len(options) == 0:
                return await interaction.response.send_message("You Aren't Registered!!", ephemeral=True)
            cslotlist = discord.ui.Select(min_values=1, max_values=1, options=options)
            view.add_item(cslotlist)
            cslotlist.callback = None    

            if interaction.data["custom_id"] == "Cslot":
                await interaction.response.send_message(view=view, ephemeral=True)

                async def confirm(interact:discord.Interaction):
                    conf = Button(label="Confirm", style=discord.ButtonStyle.red)
                    canc = Button(label="Cancel", style=discord.ButtonStyle.green)
                    v2 = View()
                    for i in [conf]:v2.add_item(i)
                    await interact.response.send_message(embed=discord.Embed(description="Do You Want To Cancel Your Slot?"), view=v2, ephemeral=True)
                    async def cnf(cnfinteract:discord.Interaction):
                        ms = await cch.fetch_message(cslotlist.values[0])
                        for i in cnfinteract.guild.members:
                            if i.mention in ms.content:
                                await i.remove_roles(crole)
                                await ms.delete()
                        return await cnfinteract.response.send_message("Slot Cancelled!!", ephemeral=True)
                            
                    async def cnc(interact:discord.Interaction):
                        await interact.message.delete()


                    conf.callback = cnf
                    canc.callback = cnc
                cslotlist.callback = confirm

            if interaction.data["custom_id"] == "Mslot":
                await interaction.response.send_message(view=view, ephemeral=True)
                async def myteam(interaction:discord.Interaction):
                    ms = await cch.fetch_message(cslotlist.values[0])
                    emb = ms.embeds[0].copy()
                    await interaction.response.send_message(embed=emb, ephemeral=True)
                cslotlist.callback = myteam
                        
            if interaction.data["custom_id"] == "Cancel":
                if interaction.message:
                    await interaction.message.delete()

            if interaction.data["custom_id"] == "Tname":
                await interaction.response.send_message(view=view, ephemeral=True)
                async def change_teamname(interaction:discord.Interaction):
                    inp = discord.ui.Modal(title="Team Name", timeout=30)
                    text = (discord.ui.TextInput(label="Enter Team Name", placeholder="Team Name", max_length=20, custom_id="teamname"))
                    inp.add_item(text)
                    await interaction.response.send_modal(inp)
                    async def tname(interaction:discord.Interaction):
                            nme = inp.children[0].value.upper()
                            ms = await cch.fetch_message(cslotlist.values[0])
                            pem = ms.embeds[0]
                            st = pem.description.find("[")+1
                            en = pem.description.find("]")
                            team = pem.description[st:en]
                            desc = pem.description.replace(team, nme)
                            emb = discord.Embed(color=pem.color, description=desc)
                            emb.set_author(name=interaction.guild.name, icon_url=interaction.guild.icon or interaction.guild.me.avatar.url)
                            emb.set_thumbnail(url=interaction.user.display_avatar or interaction.guild.icon or interaction.guild.me.avatar.url)
                            emb.timestamp = ms.created_at
                            try:
                                await ms.edit(content = f"{nme} {ms.mentions[0].mention}",embed=emb) if ms else None
                            except Exception as e:return await interaction.response.send_message(f'Unable To Change Team Name At This Time!!\nReason : {e}', ephemeral=True)
                            return await interaction.response.send_message(f'Team Name Changed {team} -> {nme}', ephemeral=True)
                    inp.on_submit = tname
                cslotlist.callback = change_teamname


        # Currently Testing on this and not sure to impliment this or not
        elif "custom_id" in interaction.data and interaction.data["custom_id"].startswith("db_reg_btn"):
            await self.register(interaction)

async def setup(bot:commands.Bot):
    await bot.add_cog(Esports(bot))
