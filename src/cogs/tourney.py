from random import random
import discord
from discord.ext import commands
from asyncio import sleep
import pymongo
from pymongo import MongoClient
import re
import datetime
from modules import config
import os
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
            
            if crole in member.roles:
                await member.remove_roles(crole)
                dbc.update_one({"tid" : registration_channel.id%1000000000000}, {"$set" : {"reged" : reged - 1}})
                messages = await cch.history(limit=tslot).flatten()
                if ctx.channel == cch:
                    await ctx.message.delete()

                for message in messages:
                    if member.mention in message.content:
                        if message.author.id == 931202912888164474:
                            emb = discord.Embed(color=0xffff00, description=f"**{reged} SLOT CANCELLED BY {ctx.author.mention}\nReason : {reason}**")
                            emb.set_author(name=message.guild.name, icon_url=message.guild.icon_url)
                            emb.timestamp = datetime.datetime.utcnow()
                            await message.edit(embed=emb)
                            await ctx.send(f"{member.mention}'s Slot Canceled with reason of {reason}")

        
            
    @cmd.command()
    async def add_slot(self, ctx, registration_channel: discord.TextChannel, member : discord.Member, *, Team_Name):
        tmrole = discord.utils.get(ctx.guild.roles, name="tourney-mod")

        if tmrole == None:
            tmrole = await ctx.guild.create_role("tourney-mod")

        if tmrole not in ctx.author.roles:
            return await ctx.send("You don't have `tourney-mod` role")

        if ctx.author.guild_permissions.manage_channels and tmrole in ctx.author.roles:
            dbcd = dbc.find_one({"tid" : registration_channel.id%1000000000000})
            crole = discord.utils.get(ctx.guild.roles, id=int(dbcd["crole"]))
            reged = dbcd["reged"]
            tslot = dbcd["reged"] + 10
            cch = discord.utils.get(ctx.guild.channels, id=int(dbcd["cch"]))
            if crole in member.roles:
                return await ctx.send("**Already Registered**", delete_after=5)

            if crole not in member.roles:
                await member.add_roles(crole)
                dbc.update_one({"tid" : registration_channel.id%1000000000000}, {"$set" : {"reged" : reged + 1}})
                emb = discord.Embed(color=0xffff00, description=f"**{reged}) TEAM NAME: {Team_Name.upper()}**\n**Added By** : {ctx.author.mention} ")
                emb.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon_url)
                emb.timestamp = datetime.datetime.utcnow()
                return await cch.send(member.mention, embed=emb)     
            
            
            
            
            
            
            
def setup(bot):
    bot.add_cog(Esports(bot))
