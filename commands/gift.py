from discord.ext import commands
import discord
client = commands.Bot(command_prefix=".")

def setup(bot):
	bot.add_command(_gift)

@client.command(name="gift")
async def _gift(message, amount: int, to_user: discord.Member):
	"""
	Be a generous person and gift some points to someone!

	Note that to_user can be a mention or the id of a user
	"""
	to = str(to_user.id)
	# Setup
	embed = discord.Embed(title=f"Some points were just gifted!", description=f"{message.author.display_name} just tried to gift {amount} points.", color=0xFF5733)
	embed.set_author(name=message.author.display_name, url="", icon_url=message.author.avatar_url)
	embed.set_thumbnail(url=message.author.avatar_url)
	# calculations
	if not message.guild:
		embed.add_field(name="Error", value="You can't gift points outside of a server.")
		await message.channel.send(embed=embed)
		return
	user = str(message.author.id)
	user_money = int(message.bot.getpoints(user))
	
	to_user = await message.guild.fetch_member(int(to))
	embed.set_thumbnail(url=to_user.avatar_url)
	#if amount < 0:
	#	embed.add_field(name="Error", value="It's not like your going to gain money from this...")
	#	return
	if amount > user_money:
		embed.add_field(name="Error", value=f"This goes over your current balance of {user_money}")
	elif to_user.bot:
		embed.add_field(name="Error", value="You can't give points to a bot...")
	else:
		message.bot.changepoints(user, -1*amount)
		message.bot.changepoints(to, amount)
		embed.add_field(name=f"{message.author.display_name} now has", value=f"{message.bot.getpoints(user)} points. (-{amount})")
		embed.add_field(name=f"{to_user.display_name} now has", value=f"{message.bot.getpoints(to)} points. (+{amount})")
	await message.reply(embed=embed)
	try:
		await to_user.send(f"**{message.author.display_name}** just sent you **{amount}** coins!") 
	except:
		embed = discord.Embed(title=f"Notice", description="While processing this request, something interesting happened", color=0x3498DB)
		embed.set_author(name=message.author.display_name, url="", icon_url=message.author.avatar_url)
		embed.add_field(name=f"Message to user \"{to_user.display_name}\" failed", value="This user may have DMs disabled. There is nothing we can do about this. It doesn't matter really.")
		await message.channel.send(embed=embed)