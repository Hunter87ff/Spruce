import discord
from discord.ext import commands
from discord import app_commands, Interaction
import typing
from modules import config
mdb = config.maindb
dbc = mdb["tourneydb"]["tourneydbc"]
gtamountdbc = mdb["gtamountdb"]["gtamountdbc"]
gtadbc = gtamountdbc






class Slash(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		#self.tree = app_commands.CommandTree(self)

	async def setup_hook(self):
	    await self.tree.sync(guild=None)
	    

	@app_commands.command()
	@commands.bot_has_permissions(manage_roles=True)
	@commands.has_permissions(manage_roles=True)
	async def lock(self, interaction: Interaction, role:discord.Role=None, channel:typing.Union[discord.TextChannel, discord.VoiceChannel]=None):
		if not role:
			role = interaction.guild.default_role
		if not channel:
			channel = interaction.channel
		overwrite = channel.overwrites_for(role)
		overwrite.update(send_messages=False, add_reactions=False, connect=False, speak=False)
		await channel.set_permissions(role, overwrite=overwrite)
		await interaction.response.send_message(f"Channel {channel.mention} Locked From `{role.name}`")





	@app_commands.command(description="Use This Command To Create A Mention Basis Tournament, ")
	@commands.bot_has_permissions(manage_channels=True, manage_roles=True)
	@commands.has_permissions(manage_channels=True, manage_roles=True, manage_messages=True, add_reactions=True, read_message_history=True)
	async def tourney_setup(self, interaction:Interaction, front:str=None, total_slot:int=None, mentions:int=None, *, name:str=None):
	    if interaction.user.bot:
	        return 
	    if not total_slot:
	    	return await interaction.response.send_message("**Please Enter the Total Slot Of The Tournament**")
	    if not mentions:
	    	return await interaction.response.send_message("**Please Enter Required Mention for The Tournament**")
	    if not name:
	    	return await interaction.response.send_message("**Please Enter the Name Of The Tournament**")
	    if not front:
	    	front=""
	    try:
	        await interaction.response.send_message("**Processing...**")
	        prefix = front
	        bt = interaction.guild.get_member(self.bot.user.id)
	        tmrole = discord.utils.get(interaction.guild.roles, name="tourney-mod")
	        gid = interaction.guild.id%1000000000000
	       

	        if not tmrole:
	            tmrole = await interaction.guild.create_role(name="tourney-mod")

	        if tmrole:
	            if not interaction.user.guild_permissions.administrator:
	                if tmrole not in interaction.user.roles:
	                    return await interaction.response.send_message(f"You Must Have {tmrole.mention} role to run rhis command")

	        if int(total_slot) > 20000:
	            return await interaction.response.send_message("Total Slot should be below 20000")


	        if int(total_slot) < 20000:
	            overwrite = interaction.channel.overwrites_for(bt)
	            overwrite.update(send_messages=True, manage_messages=True, read_message_history=True, add_reactions=True, manage_channels=True, external_emojis=True, view_channel=True)
	            reason= f'Created by {interaction.user.name}'   #reason for auditlog
	            category = await interaction.guild.create_category(name, reason=f"{interaction.user.name} created")
	            await category.set_permissions(bt, overwrite=overwrite)
	            await category.set_permissions(interaction.guild.default_role, send_messages=False, add_reactions=False)
	            await interaction.guild.create_text_channel(str(front)+"info", category=category, reason=reason)
	            await interaction.guild.create_text_channel(str(front)+"updates", category=category,reason=reason)
	            await interaction.guild.create_text_channel(str(front)+"roadmap", category=category,reason=reason)
	            await interaction.guild.create_text_channel(str(front)+"how-to-register", category=category, reason=reason)
	            r_ch = await interaction.guild.create_text_channel(str(front)+"register-here", category=category, reason=reason)    #registration Channel
	            await unlc_ch(channel=r_ch)
	            #await r_ch.set_permissions(interaction.guild.default_role, send_messages=True)
	            c_ch = await interaction.guild.create_text_channel(str(front)+"confirmed-teams", category=category, reason=reason)    #confirmation_channel
	            g_ch = await interaction.guild.create_text_channel(str(front)+"groups", category=category, reason=reason)
	            quer = await interaction.guild.create_text_channel(str(front)+"queries", category=category, reason=reason)
	            await unlc_ch(channel=quer)
	            #await quer.set_permissions(interaction.guild.default_role, send_messages=True)
	            c_role = await interaction.guild.create_role(name=front + "Confirmed", reason=f"Created by {interaction.user}") #role
	            await r_ch.send(embed=discord.Embed(color=0x00ff00, description=f"**REGISTRATION STARTED\nTOTAL SLOT : `{total_slot}`\nMENTION REQUIRED: {mentions}**"))
	            
	            tour = {"tid" : int(r_ch.id%1000000000000), 
	                    "guild" : int(interaction.guild.id),
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
	                    "auto_grp":"yes"
	                    }
	            
	            gtadbcds = gtadbc.find_one({"guild" : gid})
	            if gtadbcds == None:
	                gtadbc.insert_one({"guild" : gid, "gta" : 1})
	                await sleep(2)
	               
	               
	             
	            gtadbcdf = gtadbc.find_one({"guild" : gid})
	            if gtadbcdf["gta"] > 5:
	                return await interaction.response.send_message("Tournament Limit Reached, You can buy premium to increase limit with more features")

	             
	            gtadbcd = gtadbc.find_one({"guild" : gid})
	            if gtadbcd != None:
	                gta = gtadbcd["gta"]
	                gtadbc.update_one({"guild" : gid}, {"$set":{"gta" : gta + 1}})

	     
	            
	            dbc.insert_one(tour)
	            return await interaction.edit_original_response(content='**<:vf:947194381172084767>Successfully Created**')
	    except:
	        return





async def setup(bot):
    await bot.add_cog(Slash(bot))