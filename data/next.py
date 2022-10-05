async def ch_handel(ctx, channel:discord.TextChannel):
	tourch = dbc.find_one({"tid" : channel.id%1000000000000 })

	if tourch != None:
		gtad = gtadbc.find_one({"guild" : channel.guild.id%1000000000000})
		gta = gtad["gta"]
		gtadbc.update_one({"guild" : channel.guild.id%1000000000000}, {"$set" : {"gta" : gta - 1}})
		print("A Tournament Deleted")
		dbc.delete_one({"tid" : channel.id%1000000000000 })
		await ctx.send(f"{channel.category.name} Tournament deleted Successfully")
		print("dbc document deleted")
  



data = {
	"gid" : 37451635462,
	"guild_id" : 83742364723546523,
	"gta" : gta + 1,

	"tourneys" : [{
	"name" : "Vitality Series",
	"reg" : 7481236473216433
	},
	{
	"name" : "Ultimate Battle",
	"reg" : 87346375413461523
	},
	{
	"name" : "Battle Of Warriors",
	"reg" : 8397634856437855
	}]
}

	"gta" : gta + 1,
	""

  gtadbc.update_one({"guild" : gid}, {"$set":{"gta" : gta + 1}})

