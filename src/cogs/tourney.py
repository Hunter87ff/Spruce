from random import random
import discord
from discord.ext import commands
from asyncio import sleep
import pymongo
from pymongo import MongoClient
import re
import datetime
from modules import config, checker
import os
from discord.utils import get
from discord.ui import Button, View
cmd = commands

maindb = config.maindb 
dbc = maindb["tourneydb"]["tourneydbc"]
tourneydbc=dbc

gtamountdbc = maindb["gtamountdb"]["gtamountdbc"]
gtadbc = gtamountdbc



 






class Esports(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.counter = 0




    @commands.command(aliases=['ts'])
    @commands.cooldown(2, 20, commands.BucketType.user)
    @commands.bot_has_permissions(manage_channels=True, manage_roles=True, manage_messages=True, send_messages=True)
    @commands.has_permissions(manage_channels=True)
    async def tourney_setup(self, ctx, front, total_slot, mentions, *, name):
        tmrole = discord.utils.get(ctx.guild.roles, name="tourney-mod")
        gid = ctx.guild.id%1000000000000
       

        if tmrole == None:
            tmrole = await ctx.guild.create_role(name="tourney-mod")

        if int(total_slot) > 20000:
            return await ctx.send("Total Slot should be below 20000")


        if int(total_slot) < 20000:
            reason= f'Created by {ctx.author.name}'   #reason for auditlog
            category = await ctx.guild.create_category(name, reason=f"{ctx.author.name} created")
            await category.set_permissions(ctx.guild.default_role, send_messages=False)
            await ctx.guild.create_text_channel(str(front)+"info", category=category, reason=reason)
            await ctx.guild.create_text_channel(str(front)+"updates", category=category,reason=reason)
            await ctx.guild.create_text_channel(str(front)+"roadmap", category=category,reason=reason)
            await ctx.guild.create_text_channel(str(front)+"how-to-register", category=category, reason=reason)
            r_ch = await ctx.guild.create_text_channel(str(front)+"register-here", category=category, reason=reason)    #registration Channel
            c_ch = await ctx.guild.create_text_channel(str(front)+"confirmed-teams", category=category, reason=reason)    #confirmation_channel
            await ctx.guild.create_text_channel(str(front)+"groups", category=category, reason=reason)
            await ctx.guild.create_text_channel(str(front)+"queries", category=category, reason=reason)

            role_name = front + "Confirmed"
            c_role = await ctx.guild.create_role(name=role_name, reason=f"Created by {ctx.author}") #role
            await r_ch.set_permissions(c_role, send_messages=False)
            
            tour = {"tid" : int(r_ch.id%1000000000000), 
                    "guild" : gid, "rch" : int(r_ch.id),
                    "cch" : int(c_ch.id),
                    "crole" : int(c_role.id),
                    "tslot" : int(total_slot),
                    "reged" : 1,
                    "mentions" : int(mentions),
                    "slotpg" : 12,
                    "status" : "started",
                    "faketag": "no"}
            
            gtadbcds = gtadbc.find_one({"guild" : gid})
            
            if gtadbcds == None:
                gtadbc.insert_one({"guild" : gid, "gta" : 1})
                await sleep(8)
               
               
             
            gtadbcdf = gtadbc.find_one({"guild" : gid})
            if gtadbcdf["gta"] > 3:
                return await ctx.send("Tournament Limit Reached, You can buy premium to increase limit with more features")

             
            gtadbcd = gtadbc.find_one({"guild" : gid})
            if gtadbcd != None:
                gta = gtadbcd["gta"]
                gtadbc.update_one({"guild" : gid}, {"$set":{"gta" : gta + 1}})

     
            
            dbc.insert_one(tour)
            return await ctx.send('**<:vf:947194381172084767>Successfully Created**',delete_after=5)

    @cmd.command()
    @commands.has_permissions(manage_channels=True, manage_roles=True)
    @commands.bot_has_permissions(manage_channels=True, manage_roles=True, send_messages=True)
    async def girls_lobby(self, ctx, *, Tournament_name):
        snd = await ctx.send("<a:loading:969894982024568856>Processing...")
        cat = await ctx.guild.create_category(name=Tournament_name)
        crl = await ctx.guild.create_role(name=f"Girls Lobby", color=0xD02090)
        await cat.set_permissions(ctx.guild.default_role, connect=False, send_messages=False, add_reactions=False)
        overwrite = cat.overwrites_for(crl)
        overwrite.update(send_messages=True, connect=True, speak=True, stream=True, use_voice_activation=True)
        await cat.set_permissions(crl, overwrite=overwrite)
        for i in range(1, 13):
            await cat.create_voice_channel(name=f"SLOT {i}")
            if len(cat.channels) == 12:
                await ctx.message.delete()
                await snd.delete()
                await ctx.send('**<:vf:947194381172084767>Successfully Created**', delete_after=30)



    @cmd.command()
    async def start_tourney(self, ctx, registration_channel : discord.TextChannel):
        dbcd = dbc.find_one({"tid" : registration_channel.id%1000000000000})
        t_mod = discord.utils.get(ctx.guild.roles, name="tourney-mod")

        if t_mod not in ctx.author.roles:
            return await ctx.send(f"You don't have `tourney-mod` role")

        if t_mod in ctx.author.roles:
            dbc.update_one({"tid" : registration_channel.id%1000000000000}, {"$set" : {"status" : "started"}})
            await registration_channel.send("Registration Started")
            await ctx.send("Started", delete_after=10)

    @cmd.command()
    async def pause_tourney(self, ctx, registration_channel : discord.TextChannel):
        dbcd = dbc.find_one({"tid" : registration_channel.id%1000000000000})
        t_mod = discord.utils.get(ctx.guild.roles, name="tourney-mod")
        
        if t_mod not in ctx.author.roles:
            return await ctx.send(f"You don't have `tourney-mod` role")

        if t_mod in ctx.author.roles:
            dbc.update_one({"tid" : registration_channel.id%1000000000000}, {"$set" : {"status" : "paused"}})
            await registration_channel.send("Registration Paused")
            await ctx.send("Paused", delete_after=10)

            

    @cmd.command()
    async def cancel_slot(self, ctx, registration_channel : discord.TextChannel, member : discord.Member, reason=None):
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
                            emb = discord.Embed(color=0xffff00, description=f"**{reged} SLOT CANCELLED BY {ctx.author.mention}\nReason : {reason}**")
                            emb.set_author(name=message.guild.name, icon_url=message.guild.icon_url)
                            emb.timestamp = datetime.datetime.utcnow()
                            await message.edit(embed=emb)
                            canemb = discord.Embed(title=f"{member.mention}'s Slot Canceled with reason of {reason}", color=0xffff00)
                            await ctx.send(embed=canemb, delete_after=60)

        
            
    @cmd.command()
    async def add_slot(self, ctx, registration_channel: discord.TextChannel, member : discord.Member, *, Team_Name):
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
                emb.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon_url)
                emb.timestamp = datetime.datetime.utcnow()
                return await cch.send(member.mention, embed=emb)     
            
            
            
    @cmd.command()
    async def faketag(self, ctx, registration_channel: discord.TextChannel):
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


    @cmd.command()
    @commands.has_any_role("tourney-mod")
    async def tourney(self, ctx, rch: discord.TextChannel):
        tdb = dbc.find_one({"tid": rch.id%1000000000000})

        if tdb == None:
            await ctx.send("Kindly Mention Registration Channel I'm Managing..", delete_after=30)

        if tdb != None:
            bt0 = Button(label="Start/Pause", style=discord.ButtonStyle.green)
            bt1 = Button(label="Fake Tag", style=discord.ButtonStyle.green)
            bt2 = Button(label="Total Slot", style=discord.ButtonStyle.green) 
            bt3 = Button(label="Mentions", style=discord.ButtonStyle.green)
            bt4 = Button(label="Save Changes")
            bt5 = Button(label="Registration Channel")
            bt6 = Button(label="Confirmation Channel")
            bt7 = Button(label="Add Slots")
            bt8 = Button(label="Cancle Slots")
            bt9 = Button(label="Confirm Role")
            buttons = [bt0, bt1, bt2, bt3, bt5, bt6, bt9, bt4]
            view = View()
            ftf = None
            if tdb["faketag"] == "yes":
                ftf = "Disabled"
            if tdb["faketag"] == "no":
                ftf = "Enabled"

            cch = get(ctx.guild.channels, id=int(tdb["cch"]))
            tcat = cch.category


            if tcat != None:
                tname = tcat.name
            if tcat == None:
                tname = ctx.guild.name
            crole = get(ctx.guild.roles, id=int(tdb["crole"]))
            emb = discord.Embed(title=tname, description=f'Status : {tdb["status"].upper()}\nMentions : {tdb["mentions"]}\nTotal Slot : {tdb["tslot"]}\nRegistered : {tdb["reged"]-1}\nFake Tag Filter : {ftf}\nRegistration Channel : {rch.mention}\nConfirmation Channel : {cch.mention}\nConfirm Role : {crole.mention}', 
                color=0x00ff00)

            for button in buttons:
                view.add_item(button)
            msg1 = await ctx.send(embed=emb, view=view)




            async def save_delete(interaction):
                await msg1.delete()




            async def r_ch(interaction):
                await interaction.response.send_message("Mention Registration Channel")
                channel = await checker.channel_input(ctx)
                ach = dbc.find_one({"tid" : channel.id%1000000000000})

                if channel.id%1000000000000 == tdb["tid"] or ach != None:
                    return await ctx.send("A Tournament Already Running In This channel")

                else:
                    dbc.update_one({"tid": rch.id%1000000000000}, {"$set":{"tid": channel.id%1000000000000}})
                    await ctx.send("Registration Channel Updated")




            async def c_ch(interaction):
                await interaction.response.send_message("Mention Confiration Channel")
                cchannel = await checker.channel_input(ctx)
                acch = dbc.find_one({"cch" : cchannel.id})

                if cchannel.id == cch.id or acch != None:
                    return await ctx.send("A Tournament Already Running In This channel")
                    
                else:
                    dbc.update_one({"tid": rch.id%1000000000000}, {"$set":{"cch": cchannel.id}})
                    await ctx.send("Confirm Channel Updated")




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
                await interaction.response.send_message("Enter Number Between 2 and 20000")
                tsl = await checker.ttl_slots(ctx)
                
                try:
                    if int(tsl) > 20000:
                        return await ctx.send("Only Number Between 1 and 20000")
                    if int(tsl) == 20000 or int(tsl) < 20000:
                        dbc.update_one({"tid": rch.id%1000000000000}, {"$set":{"tslot" : int(tsl)}})
                        await ctx.send("Total Slots Updated")

                except ValueError:
                    return await ctx.send("Numbers Only")




            async def mnts(interaction):
                await interaction.response.send_message("Enter Number Between 1 and 20")
                mns = await checker.ttl_slots(ctx)

                try:
                    if int(mns) > 20:
                        return await ctx.send("Only Number upto 20")

                    if int(mns) == 20 or int(mns) < 20:
                        dbc.update_one({"tid": rch.id%1000000000000}, {"$set":{"mentions" : int(mns)}})
                        await ctx.send("Mentions Updated")

                except ValueError:
                    return await ctx.send("Numbers Only")





            async def strtps(interaction):
                if interaction.user == ctx.author:
                    if tdb["status"] == "started":
                        dbc.update_one({"tid": rch.id%1000000000000}, {"$set":{"status" : "paused"}})
                        await rch.send("**Tournament Paused**")
                        bt0.disabled = True
                        await interaction.response.edit_message(view=view)
                        await ctx.send("Tournament Paused", delete_after=10)

                    if tdb["status"] == "paused":
                        dbc.update_one({"tid": rch.id%1000000000000}, {"$set":{"status" : "started"}})
                        await rch.send("**Tournament Statred**")
                        bt0.disabled = True
                        await interaction.response.edit_message(view=view)
                        await ctx.send("Tournament Started", delete_after=10)




            async def conro(interaction):
                if interaction.user == ctx.author:
                    await interaction.response.send_message("Mention The Confirm Role")
                    con_role = await checker.check_role(ctx)
                    cndb = dbc.find_one({"crole" : str(con_role.id)})

                    if cndb == None:
                        dbc.update_one({"tid": rch.id%1000000000000}, {"$set":{"crole" : con_role.id}})
                    if cndb != None:
                        return await ctx.send("I'm Already Managing A Tournament With This Role", delete_after=20)


            bt5.callback = r_ch
            bt6.callback = c_ch
            bt4.callback = save_delete
            bt1.callback = ft
            bt2.callback = ttl_slot
            bt3.callback = mnts
            bt0.callback = strtps
            bt9.callback = conro
      
            
            
async def setup(bot):
    await bot.add_cog(Esports(bot))
