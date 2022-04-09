# The dev commands
from discord.ext import commands
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
			embed = discord.Embed(title=f":warning: Error :warning:", description="While processing this request, we ran into an error", color=0xFFFF00)
			embed.set_author(name=ctx.author.display_name, url="", icon_url=ctx.author.avatar_url)
			embed.add_field(name=f'Unauthorized', value="This command is dev only.")
			await ctx.channel.send(embed=embed)
			return
		ctx.bot.reload_extension(command_name)
		await ctx.channel.send("Reloaded extention")