import discord
import datetime
import asyncio
from asyncio import sleep
from discord.utils import get
from discord.ext import commands
from discord.ui import Button, View
from modules import config, checker
cmd = commands
dbc = config.dbc
gtadbc = config.gtadbc

def get_front(name):
  li = []
  for i in name.split()[0:2]:li.append(i[0])
  return str("".join(li) + "-")

class Esports(commands.Cog):
	
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        members = []
        if dbc.find_one({"crole":role.id}):
            db = dbc.find_one({"crole":role.id})
            cch = discord.utils.get(role.guild.channels,id=db["cch"])
            messages = [message async for message in cch.history(limit=int(db["tslot"])+50)]
            for msg in messages:
                for m in role.guild.members:
                    if m.mention in msg.content:
                        members.append(m)
            newr = await role.guild.create_role(name=role.name, reason="[Recovering] If You Want To Delete This Role use &tourney command")
            dbc.update_one({"crole":int(role.id)}, {"$set" : {"crole" :int(newr.id)}})
            for i in members:
                await i.add_roles(newr, reason="[Recovering] Previous Confirm Role Was acidentally Deleted.")
        del members

    async def get_input(self, ctx, check=None, timeout=30):
        check = check or (lambda m: m.channel == ctx.channel and m.author == ctx.author)
        try:
            msg = await ctx.bot.wait_for("message", check=check, timeout=timeout)
            return msg.content
        except asyncio.TimeoutError:
            return await ctx.send("Time Out! Try Again", delete_after=5)

    async def unlc_ch(self, channel:discord.TextChannel, role:discord.Role=None):
        if role == None:role = channel.guild.default_role
        overwrite = channel.overwrites_for(role)
        overwrite.update(send_messages=True)
        await channel.set_permissions(role, overwrite=overwrite)

    async def lc_ch(self, channel:discord.TextChannel, role:discord.Role=None):
        if role == None:role = channel.guild.default_role
        overwrite = channel.overwrites_for(role)
        overwrite.update(send_messages=False)
        await channel.set_permissions(role, overwrite=overwrite)

    @commands.hybrid_command(with_app_command = True, aliases=['ts','tourneysetup','setup'])
    @commands.bot_has_permissions(manage_channels=True, manage_roles=True)
    @commands.guild_only()
    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.has_permissions(manage_channels=True, manage_roles=True, manage_messages=True, add_reactions=True, read_message_history=True)
    async def tourney_setup(self, ctx, total_slot:int, mentions:int, slot_per_group:int,  *, name:str):
        if ctx.author.bot:return
        if not await config.voted(ctx, bot=self.bot):return await config.vtm(ctx)            
        front = get_front(name)
        try:
            ms = await ctx.send("Processing...")
            bt = ctx.guild.get_member(self.bot.user.id)
            tmrole = discord.utils.get(ctx.guild.roles, name="tourney-mod")
            if not tmrole:tmrole = await ctx.guild.create_role(name="tourney-mod")
            if tmrole:
                if not ctx.author.guild_permissions.administrator:
                    if tmrole not in ctx.author.roles:
                        return await ctx.send(f"You Must Have {tmrole.mention} role to run rhis command")
            if int(total_slot) > 20000:
                return await ctx.send("Total Slot should be below 20000")
            if int(total_slot) < 20000:
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
                rdmm = await roadmap.send("Processing...")
                await ctx.guild.create_text_channel(str(front)+"point-system", category=category,reason=reason)
                await sleep(2) #sleep
                htrc = await ctx.guild.create_text_channel(str(front)+"how-to-register", category=category, reason=reason)
                r_ch = await ctx.guild.create_text_channel(str(front)+"register-here", category=category, reason=reason)    
                await self.unlc_ch(channel=r_ch)
                c_ch = await ctx.guild.create_text_channel(str(front)+"confirmed-teams", category=category, reason=reason)  
                await sleep(1)  #sleep
                g_ch = await ctx.guild.create_text_channel(str(front)+"groups", category=category, reason=reason)
                quer = await ctx.guild.create_text_channel(str(front)+"queries", category=category, reason=reason)
                await self.unlc_ch(channel=quer)
                c_role = await ctx.guild.create_role(name=front + "Confirmed", reason=f"Created by {ctx.author}")
                rchm = await r_ch.send(embed=discord.Embed(color=config.cyan, description=f"**{config.cup} | REGISTRATION STARTED | {config.cup}\n{config.tick} | TOTAL SLOT : {total_slot}\n{config.tick} | REQUIRED MENTIONS : {mentions}\n{config.cross} | FAKE TAGS NOT ALLOWED**"))
                htr = ""
                for i in range(1, mentions+1): htr+=f"\nPLAYER {i}:\nUID: PLAYER ID\nIGN : PLAYER NAME\n"
                htrm = await htrc.send("**REGISTRATION FORM**", embed=discord.Embed(color=config.cyan, description=f"**TEAM NAME : YOUR TEAM NAME\n{htr}\nSUBSTITUTE PLAYER IF EXIST\nMENTION YOUR {mentions} TEAMMATES**"))
                await rdmm.edit(content="https://tenor.com/view/coming-soon-coming-soon-its-coming-shortly-gif-21517225")
                await htrm.add_reaction(config.tick)
                await rchm.add_reaction(config.tick)
                await sleep(1)  #sleep
                tour = {"guild" : int(ctx.guild.id), "t_name" : str(name), "prefix" : str(front),"rch" : int(r_ch.id), "cch" : int(c_ch.id), "gch" : int(g_ch.id), "crole" : int(c_role.id), "tslot" : int(total_slot), "reged" : 1, "mentions" : int(mentions), "status" : "started", "faketag": "no", "pub" : "no", "prize" : "No Data", "auto_grp":"no", "spg":slot_per_group, "cgp":0, "created_at":datetime.datetime.now()}
                tour_count = len(list(dbc.find({"guild" : ctx.guild.id})))
                print(tour_count)
                if tour_count > 5:return await ctx.send(embed=discord.Embed(description="Tournament Limit Reached", color=0xff0000))
                dbc.insert_one(tour)
                await self.set_manager(ctx, r_ch)
                return await ms.edit(content=None, embed=discord.Embed(color=config.cyan, description=f'<:vf:947194381172084767> | Successfully Created({tour_count+1}/5 used)'), delete_after=20)
        except:return

    """

    @cmd.hybrid_command(with_app_command = True)
    @commands.has_role("tourney-mod")
    @commands.guild_only()
    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.has_permissions(manage_channels=True, manage_roles=True)
    @commands.bot_has_permissions(manage_channels=True, manage_roles=True, send_messages=True)
    async def _gsetup(self, ctx, registration_channel:discord.TextChannel):
        if ctx.author.bot:
            return
        rch = registration_channel
        await ctx.defer(ephemeral=True)
        dbc.update_one({"rch":rch.id},{"$set":{"cgp":0}})
        db = dbc.find_one({"rch":rch.id})    
        if db is not None:
            teams = []
            cch = self.bot.get_channel(int(db["cch"]))
            gch = self.bot.get_channel(int(db["gch"]))
            tslot = db["tslot"]
            spg = db["spg"]
            cgp = db["cgp"]    
            messages = [message async for message in cch.history(limit=tslot+100)]
            for msg in messages[::-1]:
                #print(msg.embeds[0])
                if msg.author.id == self.bot.user.id and msg.embeds != None:
                    if "TEAM" in msg.embeds[0].description:
                        teams.append(msg)
                else:
                    pass
            if len(teams) < 1:
                return await ctx.send("Minimum Number Of Teams Is't Reached!!")
            group = int(len(teams)/spg)
            if len(teams)/spg > group:
                group = group+1
            if len(teams)/spg < 1:
                group = 1
            for i in range(1, group+1):
                ms = f"**__GROUP__ {i}\n"
                grp = teams[cgp:cgp+spg]
                for p in grp:
                    ms = ms + f"{grp.index(p)+1}) {p.content}" + "\n"
                grp.clear()
                ncgp = cgp+spg
                dbc.update_one({"rch":rch.id},{"$set":{"cgp":ncgp}})
                cgp = cgp+spg
                msg = await gch.send(f"{ms}**")
                await msg.add_reaction(config.tick)
            await ctx.send(f"check this channel {gch.mention}")
        else:
            return await ctx.send("Tournament Not Found", delete_after=10)
                
        """		


    @cmd.hybrid_command(with_app_command = True, aliases=["girlslobby"])
    @commands.has_role("tourney-mod")
    @commands.guild_only()
    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.has_permissions(manage_channels=True, manage_roles=True)
    @commands.bot_has_permissions(manage_channels=True, manage_roles=True, send_messages=True)
    async def girls_lobby(self, ctx, vc_amount : int):
        await ctx.defer(ephemeral=True)
        if ctx.author.bot:return
        if not await config.voted(ctx, bot=self.bot):
            return await config.vtm(ctx)
        snd = await ctx.send(f"{config.loading} | Processing...")
        cat = await ctx.guild.create_category(name="GIRLS LOBBY")
        crl = await ctx.guild.create_role(name="GIRLS LOBBY", color=0xD02090)
        await cat.set_permissions(ctx.guild.default_role, connect=False, send_messages=False, add_reactions=False)
        overwrite = cat.overwrites_for(crl)
        overwrite.update(send_messages=True, connect=True, speak=True, stream=True, use_voice_activation=True)
        await cat.set_permissions(crl, overwrite=overwrite)
        amt = vc_amount + 1
        for i in range(1, amt):
            await cat.create_voice_channel(name=f"SLOT {i}", user_limit=6)
            await sleep(2)
        await snd.edit(content=f"{config.tick} | {vc_amount} vc created access role is {crl.mention}")



    @cmd.hybrid_command(with_app_command = True)
    @commands.guild_only()
    @commands.has_role("tourney-mod")
    async def start_tourney(self, ctx, registration_channel : discord.TextChannel):
        await ctx.defer(ephemeral=True)
        if ctx.author.bot:
            return
        dbcd = dbc.find_one({"rch" : registration_channel.id})
        if not dbcd:
            return await ctx.send("**No Tournament Running In This Channel**")
        dbc.update_one({"rch" : registration_channel.id}, {"$set" : {"status" : "started"}})
        await registration_channel.send(embed=discord.Embed(color=config.cyan, description="Registration Started"))
        await ctx.send("Started", delete_after=10)

            
    @cmd.hybrid_command(with_app_command = True, aliases=['pt'])
    @commands.guild_only()
    @commands.has_role("tourney-mod")
    async def pause_tourney(self, ctx, registration_channel : discord.TextChannel):
        await ctx.defer(ephemeral=True)
        if ctx.author.bot:
            return
        dbcd = dbc.find_one({"rch" : registration_channel.id})
        if not dbcd:
            return await ctx.send('No Tournament Running In This Channel')
        dbc.update_one({"rch" : registration_channel.id}, {"$set" : {"status" : "paused"}})
        await registration_channel.send(embed=discord.Embed(color=config.orange, description="Registration Paused"))
        await ctx.send("Paused", delete_after=10)

        

    @cmd.hybrid_command(with_app_command = True)
    @commands.guild_only()
    @commands.has_role("tourney-mod")
    async def cancel_slot(self, ctx, registration_channel : discord.TextChannel, member : discord.Member, reason=None):
        await ctx.defer(ephemeral=True)
        if ctx.author.bot:
            return
        if not await config.voted(ctx, bot=self.bot):
            return await config.vtm(ctx)
        if reason == None:
                reason = "Not Provided"
        tmrole = discord.utils.get(ctx.guild.roles, name="tourney-mod")
        if tmrole == None:
            tmrole = await ctx.guild.create_role("tourney-mod")
        if tmrole not in ctx.author.roles:
            return await ctx.send("You don't have `tourney-mod` role")
        if tmrole in ctx.author.roles:
            dbcd = dbc.find_one({"rch" : registration_channel.id})
            crole = discord.utils.get(ctx.guild.roles, id=int(dbcd["crole"]))
            reged = dbcd["reged"]
            tslot = dbcd["reged"] + 10
            cch = discord.utils.get(ctx.guild.channels, id=int(dbcd["cch"]))
            if ctx.channel == cch:
                await ctx.message.delete()
            if crole not in member.roles:
                nrg = discord.Embed(title="Player Not Registered `or` Don't have Confirmed Role", color=0xffff00)
                await ctx.send(embed=nrg, delete_after=60)
            if crole in member.roles:
                await member.remove_roles(crole)
                dbc.update_one({"rch" : registration_channel.id}, {"$set" : {"reged" : reged - 1}})
                messages = [message async for message in cch.history(limit=123)]  
                for message in messages:
                    if member.mention in message.content:
                        if message.author.id == self.bot.user.id:
                            #emb = discord.Embed(color=0xffff00, description=f"**{reged}) {message.content} CANCELLED BY {ctx.author.mention}\nReason : {reason}**")
                            #emb.set_author(name=message.guild.name, icon_url=message.guild.icon)
                            #emb.timestamp = datetime.datetime.utcnow()
                            await message.delete() #.edit(content=None, embed=emb)
                            canemb = discord.Embed(title=f"{member}'s Slot Canceled with reason of {reason}", color=0xffff00)
                            await ctx.send(embed=canemb, delete_after=60)

    #@cmd.hybrid_command(with_app_command = True)
    @cmd.hybrid_command(with_app_command = True)
    @commands.guild_only()
    @commands.has_role("tourney-mod")
    async def add_slot(self, ctx, registration_channel: discord.TextChannel, member:discord.Member, *, team_name):
    #async def add_slot(self, ctx, total_slot:int, mentions:int, slot_per_group:int,  *, name:str):
        await ctx.defer(ephemeral=True)
        if ctx.author.bot:
            return
        if not await config.voted(ctx, bot=self.bot):
            return await config.vtm(ctx)
        tmrole = discord.utils.get(ctx.guild.roles, name="tourney-mod")
        if tmrole == None:
            tmrole = await ctx.guild.create_role("tourney-mod")
        if ctx.author.guild_permissions.manage_channels and tmrole in ctx.author.roles:
            dbcd = dbc.find_one({"rch" : registration_channel.id})
            crole = discord.utils.get(ctx.guild.roles, id=int(dbcd["crole"]))
            reged = dbcd["reged"]
            tslot = dbcd["reged"] + 10
            cch = discord.utils.get(ctx.guild.channels, id=int(dbcd["cch"]))
            if crole in member.roles:
                return await ctx.send("**Already Registered**", delete_after=50)
            if crole not in member.roles:
                await member.add_roles(crole)
                dbc.update_one({"rch" : registration_channel.id}, {"$set" : {"reged" : reged + 1}})
                emb = discord.Embed(color=0xffff00, description=f"**{reged}) TEAM NAME: {team_name.upper()}**\n**Added By** : {ctx.author.mention} ")
                emb.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon)
                emb.timestamp = datetime.datetime.utcnow()
                return await cch.send(f"{team_name} {member.mention}", embed=emb)     
            


    @cmd.hybrid_command(with_app_command = True)
    @commands.cooldown(2, 60, commands.BucketType.user)
    @commands.guild_only()
    async def tourneys(self, ctx):
        if ctx.author.bot:return 
        if not await config.voted(ctx, bot=self.bot):return await config.vtm(ctx)
        await ctx.defer(ephemeral=True)
        ms = await ctx.send("Processing...")
        emb = discord.Embed(title="__ONGOING TOURNAMENTS__", url=config.invite_url, color=0x00ff00)
        data  = dbc.find({"pub" : "yes"})
        for i in data:
            rch = self.bot.get_channel(int(i["rch"]))
            if rch != None and i["reged"] < i["tslot"]*0.98 and i["reged"] >= i["tslot"]*0.1 and i["status"]=="started":
                link = await rch.create_invite(reason=None,max_age=360000,max_uses=0,temporary=False,unique=False,target_type=None,target_user=None,target_application_id=None)
                emb.add_field(name=f'{i["t_name"].upper()}', value=f"Prize: {i['prize'].upper()}\nServer: {rch.guild.name[0:20]}\n[Register]({link})\n---------------- ")
            if not rch:
                pass
        if len(emb.fields) > 0:
            await ctx.author.send(embed=emb)
            await ms.edit(content="Please Check Your DM")
        else:
            await ms.edit(content="Currently Unavailable")
        


    @cmd.hybrid_command(with_app_command = True, aliases=["pub"])
    @commands.bot_has_permissions(create_instant_invite=True)
    @commands.has_permissions(manage_messages=True, manage_channels=True, manage_roles=True)
    @commands.has_role("tourney-mod")
    @commands.cooldown(2, 20, commands.BucketType.user)
    @commands.guild_only()
    async def publish(self, ctx, rch: discord.TextChannel, *, prize: str):
        await ctx.defer(ephemeral=True)
        if ctx.author.bot:
            return
        if not await config.voted(ctx, bot=self.bot):
            return await config.vtm(ctx)
        if len(prize) > 30:
            return await ctx.reply("Only 30 Letters Allowed ")
        try:
            dbcd = dbc.find_one({"rch" : rch.id})
            if dbcd["reged"] < dbcd["tslot"]*0.1:
                return await ctx.send("You need To Fill 10% Of Total Slot. To Publish This Tournament")
        except:
            return await ctx.send("Tournament Not Found")
        dbc.update_one({"rch" : rch.id}, {"$set" : {"pub" : "yes", "prize" : prize}})
        await ctx.send(f"**{rch.category.name} is now public**")



            
    @cmd.hybrid_command(with_app_command = True)
    @commands.guild_only()
    @commands.has_role("tourney-mod")
    async def faketag(self, ctx, registration_channel: discord.TextChannel):
        await ctx.defer(ephemeral=True)
        if ctx.author.bot:
            return
        t_mod = discord.utils.get(ctx.guild.roles, name="tourney-mod")
        if t_mod == None:
            t_mod = await ctx.guild.create_role("tourney-mod")
        if t_mod in ctx.author.roles:
            dbcd = dbc.find_one({"rch" : registration_channel.id})
            btn = Button(label="Enable", style = discord.ButtonStyle.green)
            btn1 = Button(label="Disable", style = discord.ButtonStyle.green)
            view1 = View()
            view2 = View()
            view1.add_item(btn)
            view2.add_item(btn1)
            if dbcd["faketag"] == "no":
                await ctx.send("Disable Fake Tag Filter", view=view2)
            if dbcd["faketag"] == "yes":
                await ctx.send("Enable Fake Tag Filter", view=view1)
            async def enable_ftf(interaction):
                dbc.update_one({"rch" : registration_channel.id, "faketag" : "yes"}, {"$set":{"faketag" : "no"}})
                await interaction.response.send_message("Enabled")
            async def disable_ftf(interaction):
                dbc.update_one({"rch" : registration_channel.id, "faketag" : "no"}, {"$set":{"faketag" : "yes"}})
                await interaction.response.send_message("Disabled")
            btn.callback = enable_ftf
            btn1.callback = disable_ftf


    @cmd.hybrid_command(with_app_command = True)
    @commands.guild_only()
    @commands.has_any_role("tourney-mod")
    @commands.bot_has_permissions(send_messages=True)
    async def tourney(self, ctx, registration_channel: discord.TextChannel):
        await ctx.defer(ephemeral=True)
        if ctx.author.bot:return
        if not await config.voted(ctx, bot=self.bot): return await config.vtm(ctx)
        pub = ""
        pubb = ""
        rch = registration_channel
        tdb = dbc.find_one({"rch": rch.id})   
        if tdb == None:await ctx.send("Kindly Mention Registration Channel I'm Managing..", delete_after=30)    
        if tdb != None:
            if tdb["pub"] == "no":
                pub = "Publish"
                pubb = config.default_cross
            if tdb["pub"] == "yes":
                pub = "Unpublish"
                pubb = config.default_tick
            bt0 = Button(label="Start/Pause", style=discord.ButtonStyle.green)
            bt1 = Button(label="Fake Tag", style=discord.ButtonStyle.green)
            bt2 = Button(label="Total Slot", style=discord.ButtonStyle.green) 
            bt3 = Button(label="Mentions", style=discord.ButtonStyle.green)
            bt4 = Button(label="Save Changes")
            #bt5 = Button(label="Registration Channel")
            bt6 = Button(label="Confirmation Channel")
            bt7 = Button(label="Add Slots")
            bt8 = Button(label="Cancle Slots")
            bt9 = Button(label="Confirm Role")
            bt10 = Button(label="Delete Tournament", style=discord.ButtonStyle.danger)
            bt11 = Button(label="Confirm", style=discord.ButtonStyle.danger)
            bt12 = Button(label=pub, style=discord.ButtonStyle.blurple)
            spgbtn = Button(label="Slot per group")
            buttons = [bt0, bt1, bt2, bt3, bt4, bt6, bt9, bt10, bt12, spgbtn]
            view = View()
            ftf = None
            if tdb["faketag"] == "yes":ftf = "Disabled"
            if tdb["faketag"] == "no":ftf = "Enabled"   
            cch = get(ctx.guild.channels, id=int(tdb["cch"]))
            tcat = rch.category    
            if tcat:tname = tcat.name
            if tcat == None:tname = ctx.guild.name
            crole = get(ctx.guild.roles, id=int(tdb["crole"]))
            emb = discord.Embed(title=tname.upper(), description=f'**Status : {tdb["status"].upper()}\nMentions : {tdb["mentions"]}\nTotal Slot : {tdb["tslot"]}\nRegistered : {tdb["reged"]-1}\nFake Tag Filter : {ftf}\nRegistration Channel : <#{tdb["rch"]}>\nConfirmation Channel : <#{tdb["cch"]}>\nConfirm Role : <@&{tdb["crole"]}>\nPublished : {pubb}\nPrize : {tdb["prize"].upper()}\nSlot Per Group : {tdb["spg"]}\n**', 
                color=0x00ff00)    
            for button in buttons:view.add_item(button)
            msg1 = await ctx.send(embed=emb, view=view)

            async def save_delete(interaction):
                await msg1.delete()

            async def delete_tourney_confirm(interaction):
                view = View().add_item(bt11)
                del_t_con = await interaction.response.send_message("**Are You Sure To Delete The Tournament?**", view=view)

            async def delete_t_confirmed(interaction):
                await interaction.message.edit(content=f"**{config.loading} Processing...**")
                dbc.delete_one({"rch" : registration_channel.id })
                await save_delete(interaction)
                await interaction.message.delete()

            async def r_ch(interaction):
                await interaction.response.send_message("Mention Registration Channel")
                channel = await checker.channel_input(ctx)
                ach = dbc.find_one({"rch" : channel.id})
                if channel.id == tdb["rch"] or ach != None:
                    return await ctx.send("A Tournament Already Running In This channel", delete_after=15)
                else:
                    dbc.update_one({"rch": rch.id}, {"$set":{"rch": channel.id}})
                    await ctx.send("Registration Channel Updated", delete_after=5)

            async def publish(interaction):
                if tdb["pub"] == "no":
                    if tdb["reged"] >= tdb["tslot"]*0.1:
                        await interaction.response.defer(ephemeral=True)
                        ms = await ctx.send("Enter The Prize Under 15 characters")
                        prize = str(await self.get_input(ctx))
                        if len(prize) > 15:await ms.edit("Word Limit Reached. Try Again Under 15 Characters")
                        if len(prize) <= 15:
                            dbc.update_one({"rch" : rch.id}, {"$set" : {"pub" : "yes", "prize" : prize}})
                            await ms.delete()
                            await ctx.send("Tournament Is Now Public", delete_after=5)
                    if tdb["reged"] < tdb["tslot"]*0.1:
                        return await ctx.send("**You Need To Fill 10% Slot To Publish**", ephemeral=True, delete_after=10)
                    
                    
                if tdb["pub"] == "yes":
                    dbc.update_one({"rch" : rch.id}, {"$set" : {"pub" : "no"}})
                    await interaction.response.send_message("Tournament Unpublished",  delete_after=5)

            async def c_ch(interaction):
                if interaction.user == ctx.author:
                    await interaction.response.send_message("Mention Confiration Channel")
                    try:
                        cchannel = await checker.channel_input(ctx)
                        if not cchannel:return await ctx.send("Kindly Mention A Channel `-_-`", delete_after=5)
                    except:return await ctx.send("Kindly Mention A Channel `-_-`", delete_after=5)
                    acch = dbc.find_one({"cch" : cchannel.id})
                    if cchannel.id == tdb["cch"] or acch != None:
                        return await ctx.send("A Tournament Already Running In This channel", delete_after=10)
                    else:
                        dbc.update_one({"rch": rch.id}, {"$set":{"cch": cchannel.id}})
                        await ctx.send("Confirm Channel Updated", delete_after=5)
        
            async def ft(interaction):
                if interaction.user == ctx.author:
                    if tdb["faketag"] == "yes":
                        dbc.update_one({"rch": rch.id}, {"$set":{"faketag" : "no"}})
                        bt1.disabled = True
                        await interaction.response.edit_message(view=view)
                        await ctx.send("Enabled", delete_after=10)

                if tdb["faketag"] == "no":
                    dbc.update_one({"rch": rch.id}, {"$set":{"faketag" : "yes"}})
                    bt1.disabled = True
                    await interaction.response.edit_message(view=view)
                    await ctx.send("Disabled", delete_after=10)

            async def ttl_slot(interaction):
                if interaction.user == ctx.author:
                    await interaction.response.send_message("Enter Number Between 2 and 20000")
                    tsl = await checker.ttl_slots(ctx)
                    
                    try:
                        if int(tsl) > 20000:
                            return await ctx.send("Only Number Between 1 and 20000", delete_after=20)
                        if int(tsl) == 20000 or int(tsl) < 20000:
                            dbc.update_one({"rch": rch.id}, {"$set":{"tslot" : int(tsl)}})
                            await ctx.send("Total Slots Updated", delete_after=5)
        
                    except ValueError:
                        return await ctx.send("Numbers Only", delete_after=20)
        
            async def mnts(interaction):
                if interaction.user == ctx.author:
                    await interaction.response.send_message("Enter Number Between 1 and 20")
                    mns = await checker.ttl_slots(ctx)
                    try:
                        if int(mns) > 20:
                            await ctx.send("Only Number upto 20", delete_after=5)
        
                        if int(mns) == 20 or int(mns) < 20:
                            dbc.update_one({"rch": rch.id}, {"$set":{"mentions" : int(mns)}})
                            await ctx.send("Mentions Updated", delete_after=5)
        
                    except ValueError:
                        return await ctx.send("Numbers Only", delete_after=5)
        

            async def strtps(interaction):
                if interaction.user == ctx.author:
                    if tdb["status"] == "started":
                        dbc.update_one({"rch": rch.id}, {"$set":{"status" : "paused"}})
                        await rch.send("**Tournament Paused**")
                        bt0.disabled = True
                        await interaction.response.edit_message(view=view)
                        await ctx.send("Tournament Paused", delete_after=2)

                    if tdb["status"] == "paused":
                        dbc.update_one({"rch": rch.id}, {"$set":{"status" : "started"}})
                        await rch.send("**Tournament Statred**")
                        bt0.disabled = True
                        await interaction.response.edit_message(view=view)
                        await ctx.send("Tournament Started", delete_after=2)

            async def conro(interaction):
                if interaction.user == ctx.author:
                    await interaction.response.send_message("Mention The Confirm Role")
                    try:
                        con_role = await checker.check_role(ctx)
                        if not con_role:
                            return await ctx.send("Kindly Mention A Role `-_-`", delete_after=5)
                    except:
                        return await ctx.send("Kindly Mention A Role `-_-`", delete_after=5)
                    cndb = dbc.find_one({"crole" : str(con_role.id)})

                    if cndb == None:
                        dbc.update_one({"rch": rch.id}, {"$set":{"crole" : con_role.id}})
                        await ctx.send("Confirm Role Updated", delete_after=5)
                    if cndb != None:
                        return await ctx.send("I'm Already Managing A Tournament With This Role", delete_after=20)

            async def spg_change(interaction):
                if not ctx.author:
                    return await ctx.send("Only author can use these buttons")
                await interaction.response.send_message("Mention the number of slot per group")
                try:
                    spg = await checker.ttl_slots(ctx)
                    if not spg:
                        return await ctx.send("Kindly Mention the number of slot per group `-_-`", delete_after=5)
                except:
                    return await ctx.send("Kindly Mention the number of slot per group `-_-`", delete_after=5)
                dbc.update_one({"rch":rch.id},{"$set":{"spg":spg}})
                await ctx.send(f"Updated the current slot per group to : {spg}", delete_after=2)
                
                
            #bt5.callback = r_ch
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





    @cmd.hybrid_command(with_app_command = True, aliases=['gsetup'])
    @commands.has_role("tourney-mod")
    @commands.guild_only()
    @commands.cooldown(1, 60, commands.BucketType.guild)
    @commands.has_permissions(manage_channels=True, manage_roles=True, manage_permissions=True)
    @commands.bot_has_permissions(send_messages=True, manage_channels=True, manage_roles=True, manage_permissions=True)
    async def group_setup(self, ctx, prefix:str, start:int, end:int, category:discord.CategoryChannel=None):
        await ctx.defer(ephemeral=True)
        if ctx.author.bot:return
        elif not await config.voted(ctx, bot=self.bot): return await config.vtm(ctx)
        elif start < 1:return await ctx.reply("Starting Number Should Not Be Lower Than 1")
        elif end < start:return await ctx.reply("Ending Number Should Not Be Lower Than Starting Number")
        ms = await ctx.send(f"{config.loading}Processing...")
        if category == None:category = await ctx.guild.create_category(name=f"{prefix} Groups")
        await category.set_permissions(ctx.guild.default_role, view_channel=False)
        for i in range(start, end+1):
            role = await ctx.guild.create_role(name=f"{prefix.upper()} G{i}", color=0x4bd6af)
            channel = await ctx.guild.create_text_channel(name=f"{prefix}-group-{i}", category=category)
            overwrite = ctx.channel.overwrites_for(role)
            overwrite.update(view_channel=True, send_messages=False, add_reactions=False, attach_files=True)
            await channel.set_permissions(role, overwrite=overwrite)
            await sleep(2)
        await ms.edit(content=f"{config.vf}Successfully Created")

    @cmd.hybrid_command(with_app_command = True, aliases=["cs"])
    @commands.has_any_role("tourney-mod")
    @commands.guild_only()
    @commands.bot_has_permissions(send_messages=True)
    @commands.has_permissions(manage_messages=True)
    async def change_slot(self, ctx, *, slot:str):
        if not await config.voted(ctx, bot=self.bot):return await config.vtm(ctx)
        await ctx.defer(ephemeral=True)
        if ctx.message.reference:
            msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            if slot in msg.content:
                dta = msg.content
                ask = await ctx.send("Enter New Team Name + Mention")
                new_slot = await self.get_input(ctx)
                if new_slot:
                    dta = dta.replace(str(slot), str(new_slot))
                    if msg.author.id == self.bot.user.id:
                        await msg.edit(content=dta)
                        await ask.delete()
                        return await ctx.send("Group Updated", delete_after=10)
                    if msg.author.id != self.bot.user.id:return await ctx.send("I Got It!\n But I Can't Edit The Message.\nBecause I'm Not The Author Of The Message")
            else:return await ctx.send("No Team Found")
        if not ctx.message.reference:return await ctx.reply("**Please Run This Command By Replying The Group Message**", delete_after=30)


    @cmd.command(enabled=False, aliases=["t_reset"])
    @commands.guild_only()
    @commands.has_role("tourney-mod")
    @commands.has_permissions(manage_channels=True, manage_roles=True, manage_permissions=True)
    @commands.bot_has_permissions(send_messages=True, manage_channels=True, manage_roles=True, manage_permissions=True)
    async def tourney_reset(self, ctx, channel: discord.TextChannel):
        if ctx.author.bot:return 
        if not await config.voted(ctx, bot=self.bot): return await config.vtm(ctx)
        td = dbc.find_one({"rch" : channel.id})
        tmrole = discord.utils.get(ctx.guild.roles, name="tourney-mod")
        if tmrole not in ctx.author.roles:return await ctx.reply("You Don't Have `tourney-mod` role")
        if not td:return await ctx.send("No Registration Running in this channel")
        try:
            cch = discord.utils.get(ctx.guild.channels, id=td["cch"])
            await channel.purge(limit=20000)
            await cch.purge(limit=20000)
            dbc.update_one({"rch" : channel.id}, {"$set":{"reged" : 1}})
            await ctx.send("Done")

        except:
            return

    @cmd.hybrid_command(with_app_command = True, aliases=["autogroup"])
    @commands.guild_only()
    @commands.has_role("tourney-mod")
    @commands.has_permissions(manage_channels=True, manage_roles=True, manage_permissions=True)
    @commands.bot_has_permissions(send_messages=True, manage_channels=True, manage_roles=True, manage_permissions=True)
    async def auto_group(self, ctx, registration_channel:discord.TextChannel):
        if ctx.author.bot:return
        if not await config.voted(ctx, bot=self.bot):return await config.vtm(ctx)
        rch = registration_channel
        await ctx.defer(ephemeral=True)
        dbc.update_one({"rch":rch.id},{"$set":{"cgp":0}})
        db = dbc.find_one({"rch":rch.id})
        if db != None:
            teams = []
            cch = self.bot.get_channel(int(db["cch"]))
            gch = self.bot.get_channel(int(db["gch"]))
            tslot = db["tslot"]
            spg = db["spg"]
            cgp = db["cgp"]
            tprefix =  db["prefix"]
            messages = [message async for message in cch.history(limit=tslot+100)]
            for msg in messages[::-1]:
                if msg.author.id == self.bot.user.id and msg.embeds != None:
                    if "TEAM" in msg.embeds[0].description:teams.append(msg)
                else:pass
            if len(teams) < 1:return await ctx.send("Minimum Number Of Teams Is't Reached!!")
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
                grp = teams[cgp:cgp+spg]
                for p in grp:
                    ms = ms + f"{grp.index(p)+1}) {p.content}" + "\n"
                grp.clear()
                ncgp = cgp+spg
                dbc.update_one({"rch":rch.id},{"$set":{"cgp":ncgp}})
                cgp = cgp+spg
                msg = await gch.send(f"{ms}**")
                for m in ctx.guild.members:
                    if m.mention in msg.content:
                        await m.add_roles(role)
                await msg.add_reaction(config.tick)
            await ctx.send(f"check this channel {gch.mention}")
            await sleep(3)	
        else:
            return await ctx.send("Tournament Not Found", delete_after=10)
                


    @cmd.hybrid_command(with_app_command = True)
    @commands.guild_only()
    @commands.has_role("tourney-mod")
    @commands.has_permissions(manage_channels=True, manage_roles=True, manage_permissions=True)
    @commands.bot_has_permissions(send_messages=True, manage_channels=True, manage_roles=True, manage_permissions=True)
    async def set_manager(self, ctx, registration_channel:discord.TextChannel):
        if ctx.author.bot:return
        view = View()
        channel = registration_channel
        db = dbc.find_one({"rch":channel.id})
        if not db:
            return await ctx.send("Tournament Not Found")
        rch = self.bot.get_channel(db["rch"])
        mch = await rch.category.create_text_channel(name="manage-slot")
        emb = discord.Embed(title=rch.category.name, description=f"{config.arow} **Cancel Slot** : To Cancel Your Slot\n{config.arow} **My Slot** : To Get Details Of Your Slot\n{config.arow} **Team Name** : To Change Your Team Name", color=config.cyan)
        buttons = [Button(label='Cancel Slot', style=discord.ButtonStyle.red, custom_id="Cslot"),
                    Button(label='My Slot', style=discord.ButtonStyle.blurple, custom_id="Mslot"),
                    Button(label='Team Name', style=discord.ButtonStyle.green, custom_id="Tname"),
                    #Button(label='Team Logo', style=discord.ButtonStyle.blurple, custom_id="Tlogo")
                    ]
        
        for i in buttons:view.add_item(i)
        await mch.send(embed=emb, view=view)
        await self.lc_ch(channel=mch)
        dbc.update_one({"rch":channel.id},{"$set":{"mch":int(mch.id)}})
        await ctx.send(f"{config.tick} | {mch.mention} created")

    @cmd.hybrid_command(with_app_command = True)
    @commands.guild_only()
    @commands.has_role("tourney-mod")
    @commands.has_permissions(manage_channels=True, manage_roles=True, manage_permissions=True)
    @commands.bot_has_permissions(send_messages=True, manage_channels=True, manage_roles=True, manage_permissions=True)
    async def tconfig(self,ctx:commands.Context):
        data = config.dbc.find({"guild":ctx.guild.id})
        if not data:return await ctx.send("No Tournament Found")
        await ctx.defer(ephemeral=True)
        options = []
        view = View()
        embed = discord.Embed(title="Select Tournament", color=config.cyan)
        bt10 = Button(label="Delete Tournament", style=discord.ButtonStyle.danger)
        bt11 = Button(label="Confirm", style=discord.ButtonStyle.danger)
        bt12 = Button(label="Cancel", custom_id="Cancel", style=discord.ButtonStyle.blurple)
        for i in data:options.append(discord.SelectOption(label=i["t_name"], value=i["rch"]))
        tlist = discord.ui.Select(min_values=1, max_values=1, options=options)
        view.add_item(tlist)
        view.add_item(bt12)
        msg = await ctx.send(embed=embed, view=view, ephemeral=True)
        async def tourney_details(interaction:discord.Interaction):
            await interaction.response.defer()
            db = dbc.find_one({"rch":int(tlist.values[0])})
            if db:
                embed.title=db["t_name"].upper()
                embed.description=f"**Total Slot : {db['tslot']}\nRegistered : {db['reged']}\nMentions : {db['mentions']}\nStatus : {db['status']}\nFake Tag Filter : {db['faketag']}\nPublished : {db['pub']}\nPrize : {db['prize']}\nRegistration : <#{db['rch']}>\nConfirm Channel: <#{db['cch']}>\nGroup Channel: <#{db['gch']}>\nConfirm Role : <@&{db['crole']}>\n**"
                if bt10 not in view.children:view.add_item(bt10)
                await msg.edit(embed=embed, view=view)
            else:
		return await interaction.response.send_message("Tournament Not Found", delete_after=10)
            
        async def delete_tourney_confirm(interaction):
            view1 = View().add_item(bt11)
            del_t_con = await interaction.response.send_message("**Are You Sure To Delete The Tournament?**", view=view1)

        async def delete_t_confirmed(interaction):
            await interaction.message.edit(content=f"**{config.loading} Processing...**")
            x = dbc.delete_one({"rch" : int(tlist.values[0])})
            if x:
                await interaction.message.delete()
                await msg.delete()
                channel:discord.TextChannel = ctx.guild.get_channel(int(tlist.values[0]))
                if channel: await self.tconfig(ctx)


        tlist.callback = tourney_details
        bt10.callback = delete_tourney_confirm
        bt11.callback = delete_t_confirmed


    @cmd.Cog.listener()
    async def on_interaction(self, interaction:discord.Interaction):
        if interaction.user.bot:return
        if "custom_id" in interaction.data:
            db = dbc.find_one({"mch":interaction.channel.id})
            if db is not None:
                view = View()
                crole = interaction.guild.get_role(db["crole"])
                cch = self.bot.get_channel(db["cch"])
                teams = [message async for message in cch.history(limit=db["tslot"], oldest_first=True)]
                options = []
                for i in teams:
                    if i.embeds and "TEAM" in i.embeds[0].description:
                        if f"<@{interaction.user.id}>" in i.embeds[0].description:
                            #print(i.embeds[0].description.split("\n")[0])
                            st = i.embeds[0].description.find("[")+1
                            en = i.embeds[0].description.find("]")
                            options.append(discord.SelectOption(label=i.embeds[0].description[st:en],  value=i.id))
                if len(options) == 0:
                    return await interaction.response.send_message("You Aren't Registered!!", ephemeral=True)
                cslotlist = discord.ui.Select(min_values=1, max_values=1, options=options)
                view.add_item(cslotlist)
            
            if interaction.data["custom_id"] == "Cslot":
                if not db:
                    return await interaction.response.send_message("Tournament is No Longer Available!!", ephemeral=True)
                await interaction.response.send_message(view=view, ephemeral=True)

                async def confirm(interaction):
                    #await interaction.response.defer()
                    conf = Button(label="Confirm", style=discord.ButtonStyle.red)
                    canc = Button(label="Cancel", style=discord.ButtonStyle.green)
                    v2 = View()
                    for i in [conf]:v2.add_item(i)
                    await interaction.response.send_message(embed=discord.Embed(description="Do You Want To Cancel Your Slot?"), view=v2, ephemeral=True)
                    async def cnf(interaction):
                        #print(self.value)
                        ms = await cch.fetch_message(cslotlist.values[0])
                        for i in interaction.guild.members:
                            if i.mention in ms.content:
                                await i.remove_roles(crole)
                                await ms.delete()
                        return await interaction.response.send_message("Slot Cancelled!!", ephemeral=True)
                            
                    async def cnc(interaction):
                        await interaction.message.delete()
                        
                    conf.callback = cnf
                    canc.callback = cnc
                cslotlist.callback = confirm
            if interaction.data["custom_id"] == "Mslot":
                if not db:
                    return await interaction.response.send_message("Tournament is No Longer Available!!", ephemeral=True)
                await interaction.response.send_message(view=view, ephemeral=True)
                async def myteam(interaction):
                    ms = await cch.fetch_message(cslotlist.values[0])
                    emb = ms.embeds[0].copy()
                    await interaction.response.send_message(embed=emb, ephemeral=True)
                cslotlist.callback = myteam
                        
            if interaction.data["custom_id"] == "Cancel":
                await interaction.message.delete()

            if interaction.data["custom_id"] == "Tname":
                if not db:
                    return await interaction.response.send_message("Tournament is No Longer Available!!", ephemeral=True)
                await interaction.response.send_message(view=view, ephemeral=True)
                async def change_teamname(interaction):
                    inp = discord.ui.Modal(title="Team Name", timeout=30)
                    text = (discord.ui.TextInput(label="Enter Team Name", placeholder="Team Name", max_length=20, custom_id="teamname"))
                    inp.add_item(text)
                    await interaction.response.send_modal(inp)
                    async def tname(interaction):
                            nme = inp.children[0].value.upper()
                            print(nme)
                            ms = await cch.fetch_message(cslotlist.values[0])
                            pem = ms.embeds[0]
                            st = pem.description.find("[")+1
                            en = pem.description.find("]")
                            team = pem.description[st:en]
                            desc = pem.description.replace(team, nme)
                            emb = discord.Embed(color=pem.color, description=desc)
                            emb.set_author(name=interaction.guild.name, icon_url=interaction.guild.icon)
                            emb.set_thumbnail(url=interaction.user.display_avatar)
                            emb.timestamp = ms.created_at
                            try:
                                await ms.edit(content = f"{nme} {interaction.user.mention}",embed=emb)
                            except Exception as e:
                                return await interaction.response.send_message(f'Unable To Change Team Name At This Time!!\nReason : {e}', ephemeral=True)
                            return await interaction.response.send_message(f'Team Name Changed {team} -> {nme}', ephemeral=True)
                    inp.on_submit = tname
                cslotlist.callback = change_teamname
                

async def setup(bot):
    await bot.add_cog(Esports(bot))
