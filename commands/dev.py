# The dev commands
from discord.ext import commands
from discord.ext.commands import BadArgument
import discord

intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix=".", intents=intents)

async def setup(bot):
	await bot.add_cog(Dev(bot))
	
class Dev(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

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
		await ctx.bot.reload_extension(command_name)
		await ctx.channel.send("Reloaded extention")