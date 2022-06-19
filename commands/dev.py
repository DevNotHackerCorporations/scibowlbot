# The dev commands
from discord.ext import commands
from discord.ext.commands import BadArgument
import discord
client = commands.Bot(command_prefix=".")

def setup(bot):
	bot.add_cog(Dev(bot))
	
class Dev(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	"""
	@commands.group(invoke_without_command=True)
	async def dev_base(self, ctx):
		await ctx.channel.send("This is a placeholder for something I will add later!")
	"""
		
	@commands.command(name="servers")
	async def _dev_servers(self, message):
		"""
		See how many servers scibowlbot is in!
		"""
		await message.channel.send("I am currently in "+str(len(message.bot.guilds))+" servers!")
	
	@commands.command(name="clear")
	async def _dev_clear(self, message):
		"""
		Remove this channel from the list of channels that already have a question.
	
		Use this command to override scibowlbot when he incorrectly says that there already is a question in this channel
		"""
		if message.channel.id in message.bot.hasQuestion:
			message.bot.hasQuestion.remove(message.channel.id)
		await message.reply("Done!", mention_author=False)
	
	
	@commands.command(name="reload")
	async def _reload(self, ctx, command_name):
		"""
		DEV ONLY
		"""
		if ctx.author not in ctx.bot.devs:
			raise BadArgument("Unauthorized. This command is dev only.")
		ctx.bot.reload_extension(command_name)
		await ctx.channel.send("Reloaded extention")