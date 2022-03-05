import typing
from discord.ext import commands
import discord
import re
client = commands.Bot(command_prefix=".")

def setup(bot):
	bot.add_command(_profile)

@client.command(name="profile")
async def _profile(message, member: typing.Optional[discord.Member]):
	"""
	View your server profile!

	You can change this with .change_profile
	"""
	if not member:
		member = message.author

	embed = discord.Embed(title=f"{member.display_name}'s profile", description="What they are good at, their points, etc.", color=0xFF5733)
	embed.set_author(name=member.display_name, url="", icon_url=member.avatar_url)
	embed.set_thumbnail(url=member.avatar_url)
	embed.add_field(name=f"{member}'s point count", value=f"**{str(member.display_name)}** has **{str(message.bot.getpoints(str(member.id)))}** point(s)", inline=False)
	good_at = ", ".join(list(map(lambda x: message.bot.apprev[x.upper()][0].lower(), message.bot.getprofile(member.id)[0])))
	if not good_at:
		good_at = "*Nothing*"
	bad_at = ", ".join(list(map(lambda x: message.bot.apprev[x.upper()][0].lower(), message.bot.getprofile(member.id)[1])))
	if not bad_at:
		bad_at = "*Nothing*"
	embed.add_field(name=f"What {member} is is good at", value=f"{str(member.display_name)} is good at {good_at}", inline=False)
	embed.add_field(name=f"What {member} is is not so good at", value=f"{str(member.display_name)} is not so good at {bad_at}", inline=False)
	await message.channel.send(embed=embed)