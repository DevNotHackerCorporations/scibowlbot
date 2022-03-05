# The dev commands
from discord.ext import commands
client = commands.Bot(command_prefix=".")

def setup(bot):
	bot.add_command(_dev_servers)
	bot.add_command(_dev_clear)

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