from discord.ext import commands
import discord
import json
client = commands.Bot(command_prefix=".")

def setup(bot):
	bot.add_command(_server_stats)

@client.command(name="serverstats")
async def _server_stats(message):
	"""
	View the statistics for this server!
	"""
	memberlist = set()
	for member in message.guild.members:
		memberlist.add(str(member.id))
	points = json.loads(open("points.json", "r").read()).get("points")
	average = 0
	num_pep = 0
	for k in points:
		if str(k) in memberlist:
			average += points[k]
			num_pep += 1 

	if num_pep == 0:
		num_pep = 1
	average = round(average / num_pep, 2)

		
	# Setting up embed
	embed = discord.Embed(title=f"Server stats of **{message.guild.name}**", color=0xFF5733)
	embed.set_author(name=message.author.display_name, url="", icon_url=message.author.avatar_url)
	embed.set_thumbnail(url=message.guild.icon_url)
	embed.add_field(name=f"Average amount of points", value=f"The average amount of points for {message.guild.name} is {average} points.", inline=False)
	await message.channel.send(embed=embed)
	# end set up