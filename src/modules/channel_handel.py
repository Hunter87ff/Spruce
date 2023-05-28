from modules import config




maindb = config.maindb
db = maindb["tourneydb"]
dbc = maindb["tourneydb"]["tourneydbc"]
gtadbc =  maindb["gtamountdb"]["gtamountdbc"]







async def ch_handel(channel, bot):
	tourch = dbc.find_one({"rch" : channel.id})
	dlog = bot.get_channel(config.tdlog)
	if tourch != None:
		gtad = gtadbc.find_one({"guild" : channel.guild.id%1000000000000})
		gta = gtad["gta"]
		gtadbc.update_one({"guild" : channel.guild.id%1000000000000}, {"$set" : {"gta" : gta - 1}})
		await dlog.send(f"```\n{tourch}\n```")
		dbc.delete_one({"tid" : channel.id%1000000000000 })
		
