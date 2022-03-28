# The dev commands
from discord.ext import commands
import discord
client = commands.Bot(command_prefix=".")

def setup(bot):
	bot.add_command(_dev_servers)
	bot.add_command(_dev_clear)
	bot.add_command(_reload)
	

@client.command(name="dev_servers")
async def _dev_servers(message):
	"""
	See how many servers scibowlbot is in!
	"""
	await message.channel.send("I am currently in "+str(len(message.bot.guilds))+" servers!")

@client.command(name="dev_clear")
async def _dev_clear(message):
	"""
	Remove this channel from the list of channels that already have a question.

	Use this command to override scibowlbot when he incorrectly says that there already is a question in this channel
	"""
	if message.channel.id in message.bot.hasQuestion:
		message.bot.hasQuestion.remove(message.channel.id)
	await message.reply("Done!", mention_author=False)


@client.command(name="reload")
async def _reload(ctx, command_name):
	if ctx.author not in ctx.bot.devs:
		embed = discord.Embed(title=f":warning: Error :warning:", description="While processing this request, we ran into an error", color=0xFFFF00)
		embed.set_author(name=ctx.author.display_name, url="", icon_url=ctx.author.avatar_url)
		embed.add_field(name=f'Unauthorized', value="This command is dev only.")
		await ctx.channel.send(embed=embed)
		return
	ctx.bot.reload_extension(command_name)
	await ctx.channel.send("Reloaded extention")