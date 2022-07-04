"""
========
= NOTE =
========

This feature is not to be used. Thanks.

"""

from discord.ext import commands
client = commands.Bot(command_prefix=".")

async def setup(bot):
	bot.add_command(_stats)

@client.command(name="serverstats")
async def _stats(message):
	await message.channel.send("Terribly sorry--we (the dev team) are temporarily closing the stats command as it is interfering with the deployment of scibowlbot's website, which is crucial for keeping the bot online 24/7. Thanks for your understanding.")
	"""msgToEdit = await message.channel.send("Generating statistics--please wait.")
	memberlist = set()
	for member in message.guild.members:
		memberlist.add(str(member.id))
	points = json.loads(open("points.json", "r").read())
	values = []
	for k in points:
		if str(k) in memberlist:
			values.append(points.get(k))

	plt.xlabel('Number of points')
	plt.ylabel('Number of users')
	plt.hist(values)
	plt.savefig("tempstats.png")
	await message.channel.send(f"The statistics for **{message.guild.name}**\n", file=discord.File(open("tempstats.png", "rb"), 'stats.png'))
	await msgToEdit.delete()
	os.remove("tempstats.png")		
	plt.clf()"""