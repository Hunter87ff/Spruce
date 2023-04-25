from random import random
import discord
from discord.ext import commands
from asyncio import sleep
import pymongo
from pymongo import MongoClient
import re
import datetime
import os
from discord.utils import get
from discord.ui import Button, View
cmd = commands
from modules import config, checker

maindb = config.maindb
dbc = maindb["tourneydb"]["tourneydbc"]
tourneydbc=dbc

gtamountdbc = maindb["gtamountdb"]["gtamountdbc"]
gtadbc = gtamountdbc


async def get_input(ctx, check=None, timeout=30):
    check = check or (lambda m: m.channel == ctx.channel and m.author == ctx.author)
    try:
        msg = await ctx.bot.wait_for("message", check=check, timeout=timeout)

    except asyncio.TimeoutError:
        return await ctx.send("Time Out! Try Again")


    else:
        return msg.content

async def lc_ch(channel:discord.TextChannel, role:discord.Role=None):
    if role == None:
        role = channel.guild.default_role
    overwrite = channel.overwrites_for(role)
    overwrite.update(send_messages=False)
    await channel.set_permissions(role, overwrite=overwrite)


async def unlc_ch(channel:discord.TextChannel, role:discord.Role=None):
    if role == None:
        role = channel.guild.default_role
    overwrite = channel.overwrites_for(role)
    overwrite.update(send_messages=True)
    await channel.set_permissions(role, overwrite=overwrite)





class Esports(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.counter = 0



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
            newr = await role.guild.create_role(name=role.name, reason="[Recovering] If You Want To Delete This Ro use &tourney command")
            dbc.update_one({"crole":int(role.id)}, {"$set" : {"crole" :int(newr.id)}})
            for i in members:
                await i.add_roles(newr, reason="[Recovering] Previous Confirm Role Was acidentally Deleted.")








    @commands.hybrid_command(with_app_command = True, aliases=['ts','tourneysetup','setup'])
    @commands.bot_has_permissions(manage_channels=True, manage_roles=True)
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True, manage_roles=True, manage_messages=True, add_reactions=True, read_message_history=True)
    async def tourney_setup(self, ctx, front:str, total_slot:int, mentions:int, *, name:str):
        if ctx.author.bot:
            return
        try:
            ms = await ctx.send("Processing...")
            prefix = front
            bt = ctx.guild.get_member(self.bot.user.id)
            tmrole = discord.utils.get(ctx.guild.roles, name="tourney-mod")
            gid = ctx.guild.id%1000000000000
           

            if not tmrole:
                tmrole = await ctx.guild.create_role(name="tourney-mod")

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
                await ctx.guild.create_text_channel(str(front)+"info", category=category, reason=reason)
                await ctx.guild.create_text_channel(str(front)+"updates", category=category,reason=reason)
                await ctx.guild.create_text_channel(str(front)+"roadmap", category=category,reason=reason)
                await ctx.guild.create_text_channel(str(front)+"how-to-register", category=category, reason=reason)
                r_ch = await ctx.guild.create_text_channel(str(front)+"register-here", category=category, reason=reason)    #registration Channel
                await unlc_ch(channel=r_ch)
                #await r_ch.set_permissions(ctx.guild.default_role, send_messages=True)
                c_ch = await ctx.guild.create_text_channel(str(front)+"confirmed-teams", category=category, reason=reason)    #confirmation_channel
                g_ch = await ctx.guild.create_text_channel(str(front)+"groups", category=category, reason=reason)
                quer = await ctx.guild.create_text_channel(str(front)+"queries", category=category, reason=reason)
                await unlc_ch(channel=quer)
                #await quer.set_permissions(ctx.guild.default_role, send_messages=True)
                c_role = await ctx.guild.create_role(name=front + "Confirmed", reason=f"Created by {ctx.author}") #role
                await r_ch.send(embed=discord.Embed(color=0x00ff00, description=f"**REGISTRATION STARTED\nTOTAL SLOT : `{total_slot}`\nMENTION REQUIRED: {mentions}**"))
                
                tour = {"tid" : int(r_ch.id%1000000000000), 
                        "guild" : int(ctx.guild.id),
                        "t_name" : str(name), 
                        "prefix" : str(prefix),
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
                        "auto_grp":"yes",
                        "spg":12
                        }
                
                gtadbcds = gtadbc.find_one({"guild" : gid})

                if gtadbcds == None:
                    gtadbc.insert_one({"guild" : gid, "gta" : 1})
                    await sleep(8)
                   
                   
                 
                gtadbcdf = gtadbc.find_one({"guild" : gid})
                if gtadbcdf["gta"] > 5:
                    return await ctx.send("Tournament Limit Reached, You can buy premium to increase limit with more features")

                 
                gtadbcd = gtadbc.find_one({"guild" : gid})
                if gtadbcd != None:
                    gta = gtadbcd["gta"]
                    gtadbc.update_one({"guild" : gid}, {"$set":{"gta" : gta + 1}})

         
                
                dbc.insert_one(tour)
                return await ms.edit(content='**<:vf:947194381172084767>Successfully Created**',delete_after=5)
        except:
            return


    @cmd.hybrid_command(with_app_command = True, aliases=["girlslobby"])
    @commands.has_role("tourney-mod")
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True, manage_roles=True)
    @commands.bot_has_permissions(manage_channels=True, manage_roles=True, send_messages=True)
    async def girls_lobby(self, ctx, vc_amount : int):
        await ctx.defer(ephemeral=True)
        if ctx.author.bot:
            return
        male_rs = ["male", "boys", "boy", "men", "MALE", "BOY", "BOYS"]
        female_rs = ["female", "girls", "girl", "women", "FEMALE", "GIRL", "GIRLS", "WOMEN"]
        snd = await ctx.send("<a:loading:969894982024568856>Processing...")
        cat = await ctx.guild.create_category(name="GIRLS LOBBY")
        crl = await ctx.guild.create_role(name=f"GIRLS LOBBY", color=0xD02090)
        await cat.set_permissions(ctx.guild.default_role, connect=False, send_messages=False, add_reactions=False)
        overwrite = cat.overwrites_for(crl)
        overwrite.update(send_messages=True, connect=True, speak=True, stream=True, use_voice_activation=True)
        await cat.set_permissions(crl, overwrite=overwrite)
        amt = vc_amount + 1
        for i in range(1, amt):
            await cat.create_voice_channel(name=f"SLOT {i}", user_limit=6)
            if len(cat.channels) == vc_amount:
                await ctx.message.delete()
                await snd.delete()
                for author_role in ctx.author.roles:

                    if author_role.name in male_rs:
                        msg = f"**{ctx.author.mention} Sir,\nI've Created All Essential Things.\nA little request to you to give the {crl.mention} role to the players. You can use `role <role> [players...]` command, it can help you!\nThanks :heart:**"

                    if author_role.name in female_rs:
                        msg = f"**{ctx.author.mention} Mam,\nI've Created All Essential Things.\nA little request to you to give the {crl.mention} role to the players. You can use `role <role> [players...]` command, it can help you!\nThanks :heart:**"

                    else:
                        msg = f"**{ctx.author.mention}\nI've Created All Essential Things.\nA little request to you to give the {crl.mention} role to the players. You can use `role <role> [players...]` command, it can help you!\nThanks :heart:**"


                await ctx.send(msg)



    @cmd.hybrid_command(with_app_command = True)
    @commands.guild_only()
    @commands.has_role("tourney-mod")
    async def start_tourney(self, ctx, registration_channel : discord.TextChannel):
        await ctx.defer(ephemeral=True)
        if ctx.author.bot:
            return
        dbcd = dbc.find_one({"tid" : registration_channel.id%1000000000000})
        t_mod = discord.utils.get(ctx.guild.roles, name="tourney-mod")

        if t_mod not in ctx.author.roles:
            return await ctx.send(f"You don't have `tourney-mod` role")

        if t_mod in ctx.author.roles:
            dbc.update_one({"tid" : registration_channel.id%1000000000000}, {"$set" : {"status" : "started"}})
            await registration_channel.send("Registration Started")
            await ctx.send("Started", delete_after=10)

            
    @cmd.hybrid_command(with_app_command = True, aliases=['pt'])
    @commands.guild_only()
    @commands.has_role("tourney-mod")
    async def pause_tourney(self, ctx, registration_channel : discord.TextChannel):
        await ctx.defer(ephemeral=True)
        if ctx.author.bot:
            return
        dbcd = dbc.find_one({"tid" : registration_channel.id%1000000000000})
        t_mod = discord.utils.get(ctx.guild.roles, name="tourney-mod")
        
        if t_mod not in ctx.author.roles:
            return await ctx.send(f"You don't have `tourney-mod` role")

        if t_mod in ctx.author.roles:
            dbc.update_one({"tid" : registration_channel.id%1000000000000}, {"$set" : {"status" : "paused"}})
            await registration_channel.send("Registration Paused")
            await ctx.send("Paused", delete_after=10)

            

    @cmd.hybrid_command(with_app_command = True)
    @commands.guild_only()
    @commands.has_role("tourney-mod")
    async def cancel_slot(self, ctx, registration_channel : discord.TextChannel, member : discord.Member, reason=None):
        await ctx.defer(ephemeral=True)
        if ctx.author.bot:
            return
        if reason == None:
                reason = "Not Provided"
       
        tmrole = discord.utils.get(ctx.guild.roles, name="tourney-mod")
        
        if tmrole == None:
            tmrole = await ctx.guild.create_role("tourney-mod")
        
        if tmrole not in ctx.author.roles:
            return await ctx.send("You don't have `tourney-mod` role")
        
        if tmrole in ctx.author.roles:
            dbcd = dbc.find_one({"tid" : registration_channel.id%1000000000000})
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
                dbc.update_one({"tid" : registration_channel.id%1000000000000}, {"$set" : {"reged" : reged - 1}})
                messages = [message async for message in cch.history(limit=123)]   #messages = await cch.history(limit=tslot).flatten()


                for message in messages:
                    if member.mention in message.content:
                        if message.author.id == 931202912888164474:
                            emb = discord.Embed(color=0xffff00, description=f"**{reged}) {message.content} CANCELLED BY {ctx.author.mention}\nReason : {reason}**")
                            emb.set_author(name=message.guild.name, icon_url=message.guild.icon)
                            emb.timestamp = datetime.datetime.utcnow()
                            await message.edit(content=None, embed=emb)
                            canemb = discord.Embed(title=f"{member}'s Slot Canceled with reason of {reason}", color=0xffff00)
                            await ctx.send(embed=canemb, delete_after=60)

        
            
    #@cmd.hybrid_command(with_app_command = True)
    @cmd.command()
    @commands.guild_only()
    @commands.has_role("tourney-mod")
    async def add_slot(self, ctx, registration_channel: discord.TextChannel, member : discord.Member, *, Team_Name:str):
        #await ctx.defer(ephemeral=True)
        if ctx.author.bot:
            return
        tmrole = discord.utils.get(ctx.guild.roles, name="tourney-mod")

        if tmrole == None:
            tmrole = await ctx.guild.create_role("tourney-mod")

        if tmrole not in ctx.author.roles:
            return await ctx.send("You don't have `tourney-mod` role", delete_after=10)

        if ctx.author.guild_permissions.manage_channels and tmrole in ctx.author.roles:
            dbcd = dbc.find_one({"tid" : registration_channel.id%1000000000000})
            crole = discord.utils.get(ctx.guild.roles, id=int(dbcd["crole"]))
            reged = dbcd["reged"]
            tslot = dbcd["reged"] + 10
            cch = discord.utils.get(ctx.guild.channels, id=int(dbcd["cch"]))
            if crole in member.roles:
                return await ctx.send("**Already Registered**", delete_after=50)

            if crole not in member.roles:
                await member.add_roles(crole)
                dbc.update_one({"tid" : registration_channel.id%1000000000000}, {"$set" : {"reged" : reged + 1}})
                emb = discord.Embed(color=0xffff00, description=f"**{reged}) TEAM NAME: {Team_Name.upper()}**\n**Added By** : {ctx.author.mention} ")
                emb.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon)
                emb.timestamp = datetime.datetime.utcnow()
                return await cch.send(f"{Team_Name} {member.mention}", embed=emb)     
            
            
            
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

        if t_mod not in ctx.author.roles:
            return await ctx.reply(f"Tou Don't have `tourney-mod` role")

        if t_mod in ctx.author.roles:

            dbcd = dbc.find_one({"tid": registration_channel.id%1000000000000})


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
                dbc.update_one({"tid": registration_channel.id%1000000000000, "faketag" : "yes"}, {"$set":{"faketag" : "no"}})
                await interaction.response.send_message("Enabled")

            async def disable_ftf(interaction):
                dbc.update_one({"tid": registration_channel.id%1000000000000, "faketag" : "no"}, {"$set":{"faketag" : "yes"}})
                await interaction.response.send_message("Disabled")

            btn.callback = enable_ftf
            btn1.callback = disable_ftf


    @cmd.hybrid_command(with_app_command = True)
    @commands.guild_only()
    @commands.has_any_role("tourney-mod")
    @commands.bot_has_permissions(send_messages=True)
    async def tourney(self, ctx, registration_channel: discord.TextChannel):
        await ctx.defer(ephemeral=True)
        if ctx.author.bot:
            return
        rch = registration_channel
        tdb = dbc.find_one({"tid": rch.id%1000000000000})

        if tdb == None:
            await ctx.send("Kindly Mention Registration Channel I'm Managing..", delete_after=30)

        if tdb != None:
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

            buttons = [bt0, bt1, bt2, bt3, bt4, bt6, bt9, bt10]
            view = View()
            ftf = None
            if tdb["faketag"] == "yes":
                ftf = "Disabled"
            if tdb["faketag"] == "no":
                ftf = "Enabled"

            cch = get(ctx.guild.channels, id=int(tdb["cch"]))
            tcat = rch.category

            if tcat != None:
                tname = tcat.name
            if tcat == None:
                tname = ctx.guild.name
            crole = get(ctx.guild.roles, id=int(tdb["crole"]))
            emb = discord.Embed(title=tname, description=f'Status : {tdb["status"].upper()}\nMentions : {tdb["mentions"]}\nTotal Slot : {tdb["tslot"]}\nRegistered : {tdb["reged"]-1}\nFake Tag Filter : {ftf}\nRegistration Channel : <#{tdb["rch"]}>\nConfirmation Channel : <#{tdb["cch"]}>\nConfirm Role : <@&{tdb["crole"]}>', 
                color=0x00ff00)

            for button in buttons:
                view.add_item(button)
            msg1 = await ctx.send(embed=emb, view=view)




            async def save_delete(interaction):
                await msg1.delete()


            async def delete_tourney_confirm(interaction):
                view = View().add_item(bt11)
                del_t_con = await interaction.response.send_message("**Are You Sure To Delete The Tournament?**", view=view)


            async def delete_t_confirmed(interaction):
                await interaction.message.edit(content=f"**{config.loading} Processing...**")
                gtad = gtadbc.find_one({"guild" : registration_channel.guild.id%1000000000000})
                gta = gtad["gta"]
                gtadbc.update_one({"guild" : registration_channel.guild.id%1000000000000}, {"$set" : {"gta" : gta - 1}})
                print("A Tournament Deleted")
                dbc.delete_one({"tid" : registration_channel.id%1000000000000 })
                await save_delete(interaction)
                await interaction.message.delete()




            async def r_ch(interaction):
                await interaction.response.send_message("Mention Registration Channel", ephemeral=True)
                channel = await checker.channel_input(ctx)
                ach = dbc.find_one({"tid" : channel.id%1000000000000})

                if channel.id%1000000000000 == tdb["tid"] or ach != None:
                    return await ctx.send("A Tournament Already Running In This channel", delete_after=15)

                else:
                    dbc.update_one({"tid": rch.id%1000000000000}, {"$set":{"tid": channel.id%1000000000000}})
                    await ctx.send("Registration Channel Updated", delete_after=5)




            async def c_ch(interaction):
                await interaction.response.send_message("Mention Confiration Channel", ephemeral=True)
                cchannel = await checker.channel_input(ctx)
                acch = dbc.find_one({"cch" : cchannel.id})

                if cchannel.id == cch.id or acch != None:
                    return await ctx.send("A Tournament Already Running In This channel", delete_after=15)
                    
                else:
                    dbc.update_one({"tid": rch.id%1000000000000}, {"$set":{"cch": cchannel.id}})
                    await ctx.send("Confirm Channel Updated", delete_after=5)




            async def ft(interaction):
                if tdb["faketag"] == "yes":
                    dbc.update_one({"tid": rch.id%1000000000000}, {"$set":{"faketag" : "no"}})
                    bt1.disabled = True
                    await interaction.response.edit_message(view=view)
                    await ctx.send("Enabled", delete_after=10)

                if tdb["faketag"] == "no":
                    dbc.update_one({"tid": rch.id%1000000000000}, {"$set":{"faketag" : "yes"}})
                    bt1.disabled = True
                    await interaction.response.edit_message(view=view)
                    await ctx.send("Disabled", delete_after=10)




            async def ttl_slot(interaction):
                await interaction.response.send_message("Enter Number Between 2 and 20000", ephemeral=True)
                tsl = await checker.ttl_slots(ctx)
                
                try:
                    if int(tsl) > 20000:
                        return await ctx.send("Only Number Between 1 and 20000", delete_after=20)
                    if int(tsl) == 20000 or int(tsl) < 20000:
                        dbc.update_one({"tid": rch.id%1000000000000}, {"$set":{"tslot" : int(tsl)}})
                        await ctx.send("Total Slots Updated", delete_after=5)

                except ValueError:
                    return await ctx.send("Numbers Only", delete_after=20)




            async def mnts(interaction):
                await interaction.response.send_message("Enter Number Between 1 and 20", ephemeral=True)
                mns = await checker.ttl_slots(ctx)

                try:
                    if int(mns) > 20:
                        return await ctx.send("Only Number upto 20", delete_after=15)

                    if int(mns) == 20 or int(mns) < 20:
                        dbc.update_one({"tid": rch.id%1000000000000}, {"$set":{"mentions" : int(mns)}})
                        await ctx.send("Mentions Updated")

                except ValueError:
                    return await ctx.send("Numbers Only", delete_after=15)





            async def strtps(interaction):
                if interaction.user == ctx.author:
                    if tdb["status"] == "started":
                        dbc.update_one({"tid": rch.id%1000000000000}, {"$set":{"status" : "paused"}})
                        await rch.send("**Tournament Paused**")
                        bt0.disabled = True
                        await interaction.response.edit_message(view=view)
                        await ctx.send("Tournament Paused", delete_after=5)

                    if tdb["status"] == "paused":
                        dbc.update_one({"tid": rch.id%1000000000000}, {"$set":{"status" : "started"}})
                        await rch.send("**Tournament Statred**")
                        bt0.disabled = True
                        await interaction.response.edit_message(view=view)
                        await ctx.send("Tournament Started", delete_after=5)




            async def conro(interaction):
                if interaction.user == ctx.author:
                    await interaction.response.send_message("Mention The Confirm Role", ephemeral=True)
                    con_role = await checker.check_role(ctx)
                    cndb = dbc.find_one({"crole" : str(con_role.id)})

                    if cndb == None:
                        dbc.update_one({"tid": rch.id%1000000000000}, {"$set":{"crole" : con_role.id}})
                        await ctx.send("Confirm Role Updated", delete_after=5)
                    if cndb != None:
                        return await ctx.send("I'm Already Managing A Tournament With This Role", delete_after=20)


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





    @cmd.hybrid_command(with_app_command = True, aliases=['gsetup'])
    @commands.has_role("tourney-mod")
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True, manage_roles=True, manage_permissions=True)
    @commands.bot_has_permissions(send_messages=True, manage_channels=True, manage_roles=True, manage_permissions=True)
    async def group_setup(self, ctx, prefix:str, start:int, end:int, category:discord.CategoryChannel=None):
        await ctx.defer(ephemeral=True)
        if ctx.author.bot:
            return
        if start < 1:
            return await ctx.reply("Starting Number Should Not Be Lower Than 1")

        if end < start:
            return await ctx.reply("Ending Number Should Not Be Lower Than Starting Number")
        ms = await ctx.send(f"{config.loading}Processing...")
        
        if category == None:
            category = await ctx.guild.create_category(name=f"{prefix} Groups")

        await category.set_permissions(ctx.guild.default_role, view_channel=False)

        for i in range(start, end+1):
            role = await ctx.guild.create_role(name=f"{prefix.upper()} G{i}", color=0x4bd6af)
            channel = await ctx.guild.create_text_channel(name=f"{prefix}-group-{i}", category=category)

            overwrite = ctx.channel.overwrites_for(role)
            overwrite.update(view_channel=True, send_messages=False, add_reactions=False, attach_files=True)
            await channel.set_permissions(role, overwrite=overwrite)
        await ms.edit(content=f"{config.vf}Successfully Created")






    @cmd.hybrid_command(with_app_command = True, aliases=["cs"])
    @commands.has_any_role("tourney-mod")
    @commands.guild_only()
    @commands.bot_has_permissions(send_messages=True)
    @commands.has_permissions(manage_messages=True)
    async def change_slot(self, ctx, *, slot:str):
        await ctx.defer(ephemeral=True)
        if ctx.message.reference:
            msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            if slot in msg.content:
                dta = msg.content
                ask = await ctx.send("Enter New Team Name + Mention")
                new_slot = await get_input(ctx)
                if new_slot:
                    dta = dta.replace(str(slot), str(new_slot))
                    if msg.author.id == self.bot.user.id:
                        await msg.edit(content=dta)
                        await ask.delete()
                        return await ctx.send("Group Updated", delete_after=10)
                    if msg.author.id != self.bot.user.id:
                        return await ctx.send("I Got It!\n But I Can't Edit The Message.\nBecause I'm Not The Author Of The Message")

            else:
                return await ctx.send("No Team Found")

        if not ctx.message.reference:
            return await ctx.reply("**Please Run This Command By Replying The Group Message**", delete_after=30)




    @cmd.command(enabled=False, aliases=["t_reset"])
    @commands.guild_only()
    @commands.has_role("tourney-mod")
    @commands.has_permissions(manage_channels=True, manage_roles=True, manage_permissions=True)
    @commands.bot_has_permissions(send_messages=True, manage_channels=True, manage_roles=True, manage_permissions=True)
    async def tourney_reset(self, ctx, channel: discord.TextChannel):
        if ctx.author.bot:
            return 

        td = dbc.find_one({"rch" : channel.id})
        tmrole = discord.utils.get(ctx.guild.roles, name="tourney-mod")


        if tmrole not in ctx.author.roles:
            return await ctx.reply("You Don't Have `tourney-mod` role")

        if not td:
            return await ctx.send("No Registration Running in this channel")


        try:
            cch = discord.utils.get(ctx.guild.channels, id=td["cch"])
            await channel.purge(limit=20000)
            await cch.purge(limit=20000)
            dbc.update_one({"rch" : channel.id}, {"$set":{"reged" : 1}})
            await ctx.send("Done")

        except:
            return






    @cmd.hybrid_command(with_app_command = True)
    @commands.guild_only()
    @commands.has_role("tourney-mod")
    @commands.has_permissions(manage_channels=True, manage_roles=True, manage_permissions=True)
    @commands.bot_has_permissions(send_messages=True, manage_channels=True, manage_roles=True, manage_permissions=True)
    async def auto_group(self, ctx, reg: discord.TextChannel):
        await ctx.defer(ephemeral=True)
        if ctx.author.bot:
            return
        try:
            td = dbc.find_one({"rch":int(reg.id)})
        except:
            return await ctx.send("No Tournament Found")


        if td["auto_grp"] == "yes":
            dbc.update_one({"rch":reg.id},{"$set":{"auto_grp":"no"}})
            await ctx.send("Auto Group Disabled")
            


        if td["auto_grp"] == "no":
            dbc.update_one({"rch":reg.id},{"$set":{"auto_grp":"yes"}})
            await ctx.send("Auto Group Enabled")
            






            
async def setup(bot):
    await bot.add_cog(Esports(bot))
