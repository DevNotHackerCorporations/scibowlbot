from discord.ext import commands
from discord.ext.commands import BadArgument
import discord

intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix=".", intents=intents)

async def setup(bot):
	bot.add_command(_gift)

@client.command(name="gift")
async def _gift(message, amount: int, to_user: discord.Member):
	"""
	Be a generous person and gift some points to someone!

	Note that to_user can be a mention or the id of a user
	"""
	if amount < 0:
		embed = discord.Embed(title=f":warning: Error :warning:", description="While processing this request, we ran into an error", color=0xFFFF00)
		embed.set_author(name=message.author.display_name, url="", icon_url=message.author.avatar)
		embed.add_field(name=f'Invalid value', value="There are two people in life, those whose power is to give and those whos weakness is to take, in other words, YOU GREEDY LITTLE--")
		await message.channel.send(embed=embed)
		return
		
	to = str(to_user.id)
	
	embed = discord.Embed(title=f"Some points were just gifted!", description=f"{message.author.display_name} just tried to gift {amount} points.", color=0xFF5733)
	embed.set_author(name=message.author.display_name, url="", icon_url=message.author.avatar)
	embed.set_thumbnail(url=message.author.avatar)

	if not message.guild:
		embed.add_field(name="Error", value="You can't gift points outside of a server.")
		await message.channel.send(embed=embed)
		return
	user = str(message.author.id)
	user_money = int(message.bot.getpoints(user))
	
	to_user = await message.guild.fetch_member(int(to))
	embed.set_thumbnail(url=to_user.avatar)

	if amount > user_money:
		raise BadArgument(f"This goes over your current balance of {user_money}")
	elif to_user.bot:
		raise BadArgument("You can't give points to a bot...")
		await message.channel.send(embed=embed)
		return
	else:
		message.bot.changepoints(user, -1*amount)
		message.bot.changepoints(to, amount)
		embed.add_field(name=f"{message.author.display_name} now has", value=f"{message.bot.getpoints(user)} points. (-{amount})")
		embed.add_field(name=f"{to_user.display_name} now has", value=f"{message.bot.getpoints(to)} points. (+{amount})")
	await message.reply(embed=embed)
	try:
		await to_user.send(f"**{message.author.display_name}** just sent you **{amount}** coins!") 
	except:
		raise BadArgument("This user may have DMs disabled. There is nothing we can do about this. It doesn't matter really.") from None