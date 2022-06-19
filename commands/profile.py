import asyncio
from discord_components import Select, SelectOption
from discord.ext import commands
from discord.ext.commands import BadArgument
import random
import discord
import typing
import re
client = commands.Bot(command_prefix=".")

def setup(bot):
	bot.add_cog(Profile())

class Profile(commands.Cog):
	"""
	Commands that relate to your profile
	"""
	@commands.command(name="profile")
	async def _profile(self, message, member: typing.Optional[discord.Member]):
		"""
		View your server profile!
	
		You can change this with .change_profile
		"""
		if not member:
			member = message.author
	
		profile = message.bot.getprofile(member.id)
	
		embed = discord.Embed(title=f"{member.display_name}'s profile", description=(profile[2] if profile[2] else f"{member.display_name} does not have a bio yet."), color=0xFF5733)
		embed.set_author(name=member.display_name, url="", icon_url=member.avatar_url)
		embed.set_thumbnail(url=member.avatar_url)
		embed.add_field(name=f"{member}'s point count", value=f"**{str(member.display_name)}** has **{str(message.bot.getpoints(str(member.id)))}** point(s)", inline=False)
		if not profile[0]:
			good_at = "Ø"
		else:
			good_at = "\n".join(list(map(lambda x: message.bot.emoj[x.lower()] + " " + message.bot.apprev[x.upper()][0].lower(), profile[0])))
		if not profile[1]:
			bad_at = "Ø"
		else:
			bad_at = "\n".join(list(map(lambda x: message.bot.emoj[x.lower()] + " " + message.bot.apprev[x.upper()][0].lower(), profile[1])))

		embed.add_field(name=f"What {member} is is good at", value=good_at, inline=False)
		embed.add_field(name=f"What {member} is is not so good at", value=bad_at, inline=False)
		await message.channel.send(embed=embed)
		
	@commands.command(name="change_profile")
	async def _c_profile(self, message):
		"""
		Changes your server profile
		"""
		good_at, bad_at, bio = message.bot.getprofile(int(message.author.id))
		select_id = str(message.channel.id)+str(message.author.id)+str(random.randint(1, 100))
		orig_msg = await message.channel.send(f"**{str(message.author.display_name)}**, change your profile here!", components = [
			Select(
				placeholder="The subjects you are good at!",
				max_values=10, 
				id = select_id + "1",
				options=[
					SelectOption(label="Physics", value="phy", default=("phy" in good_at), emoji="\N{Red Apple}"),
					SelectOption(label="General Science", value="gen", default=("gen" in good_at), emoji="\N{Test Tube}"),
					SelectOption(label="Energy", value="energy", default=("energy" in good_at), emoji="\N{High Voltage Sign}"),
					SelectOption(label="Earth and Space", value="eas", default=("eas" in good_at), emoji="\N{Night with Stars}"),
					SelectOption(label="Chemistry", value="chem", default=("chem" in good_at), emoji="\N{Atom Symbol}"),
					SelectOption(label="Biology", value="bio", default=("bio" in good_at), emoji="\N{DNA Double Helix}"),
					SelectOption(label="Astronomy", value="astro", default=("astro" in good_at), emoji="\N{Ringed Planet}"),
					SelectOption(label="Math", value="math", default=("math" in good_at), emoji="\N{Input Symbol for Numbers}"),
					SelectOption(label="Earth Science", value="es", default=("es" in good_at), emoji="\N{Earth Globe Americas}"),
					SelectOption(label="Computer Science", value="cs",default=("cs" in good_at), emoji="\N{Personal Computer}")
				]
			),
			Select(
				placeholder="The subjects you are bad at",
				max_values=10, 
				id = select_id + "2",
				options=[
					SelectOption(label="Physics", value="phy", default=("phy" in bad_at), emoji="\N{Red Apple}"),
					SelectOption(label="General Science", value="gen", default=("gen" in bad_at), emoji="\N{Test Tube}"),
					SelectOption(label="Energy", value="energy", default=("energy" in bad_at), emoji="\N{High Voltage Sign}"),
					SelectOption(label="Earth and Space", value="eas", default=("eas" in bad_at), emoji="\N{Night with Stars}"),
					SelectOption(label="Chemistry", value="chem", default=("chem" in bad_at), emoji="\N{Atom Symbol}"),
					SelectOption(label="Biology", value="bio", default=("bio" in bad_at), emoji="\N{DNA Double Helix}"),
					SelectOption(label="Astronomy", value="astro", default=("astro" in bad_at), emoji="\N{Ringed Planet}"),
					SelectOption(label="Math", value="math", default=("math" in bad_at), emoji="\N{Input Symbol for Numbers}"),
					SelectOption(label="Earth Science", value="es", default=("es" in bad_at), emoji="\N{Earth Globe Americas}"),
					SelectOption(label="Computer Science", value="cs",default=("cs" in bad_at), emoji="\N{Personal Computer}")
				]
			),
		])
		select_author = int(message.author.id)
		def profile_check(interaction):
			if interaction.custom_id[:-1] == select_id and select_author == int(interaction.author.id):
				return True
			asyncio.create_task(interaction.send("This isn't your profile"))
			return False
	
		while True:
			try:
				select_op = await message.bot.wait_for("select_option", timeout=15, check=profile_check)
			except asyncio.TimeoutError:
				await orig_msg.edit(content=f"**{str(message.author.display_name)}**, change your profile here!", components = [
					Select(
						placeholder="The subjects you are good at!",
						max_values=10, 
						disabled=True,
						id = "niu1",
						options=[
							SelectOption(label="Physics", value="phy", default=("phy" in good_at), emoji="\N{Red Apple}"),
							SelectOption(label="General Science", value="gen", default=("" in good_at), emoji="\N{Test Tube}"),
							SelectOption(label="Energy", value="energy", default=("energy" in good_at), emoji="\N{High Voltage Sign}"),
							SelectOption(label="Earth and Space", value="eas", default=("eas" in good_at), emoji="\N{Night with Stars}"),
							SelectOption(label="Chemistry", value="chem", default=("chem" in good_at), emoji="\N{Atom Symbol}"),
							SelectOption(label="Biology", value="bio", default=("bio" in good_at), emoji="\N{DNA Double Helix}"),
							SelectOption(label="Astronomy", value="astro", default=("astro" in good_at), emoji="\N{Ringed Planet}"),
							SelectOption(label="Math", value="math", default=("math" in good_at), emoji="\N{Input Symbol for Numbers}"),
							SelectOption(label="Earth Science", value="es", default=("es" in good_at), emoji="\N{Earth Globe Americas}"),
							SelectOption(label="Computer Science", value="cs",default=("cs" in good_at), emoji="\N{Personal Computer}")
						]
					),
					Select(
						placeholder="The subjects you are bad at",
						max_values=10, 
						id = "niu2",
						disabled=True,
						options=[
							SelectOption(label="Physics", value="phy", default=("phy" in bad_at), emoji="\N{Red Apple}"),
							SelectOption(label="General Science", value="gen", default=("" in bad_at), emoji="\N{Test Tube}"),
							SelectOption(label="Energy", value="energy", default=("energy" in bad_at), emoji="\N{High Voltage Sign}"),
							SelectOption(label="Earth and Space", value="eas", default=("eas" in bad_at), emoji="\N{Night with Stars}"),
							SelectOption(label="Chemistry", value="chem", default=("chem" in bad_at), emoji="\N{Atom Symbol}"),
							SelectOption(label="Biology", value="bio", default=("bio" in bad_at), emoji="\N{DNA Double Helix}"),
							SelectOption(label="Astronomy", value="astro", default=("astro" in bad_at), emoji="\N{Ringed Planet}"),
							SelectOption(label="Math", value="math", default=("math" in bad_at), emoji="\N{Input Symbol for Numbers}"),
							SelectOption(label="Earth Science", value="es", default=("es" in bad_at), emoji="\N{Earth Globe Americas}"),
							SelectOption(label="Computer Science", value="cs",default=("cs" in bad_at), emoji="\N{Personal Computer}")
						]
					),
				])
				break
			inter_number = select_op.custom_id[-1]
			if inter_number == "1":
				message.bot.changeprofile(select_author, good=select_op.values)
			if inter_number == "2":
				message.bot.changeprofile(select_author, bad=select_op.values)
			await select_op.send("Updated your profile")
	
	
	@commands.command(name="set_bio")
	async def _c_bio(self, ctx, * bio):
		"""
		Sets your bio for your profile
		"""
		bio = " ".join(bio)
	
		if len(bio) > 200:
			raise BadArgument("Bio must be at most 200 characters.")
		ctx.bot.changeprofile(ctx.author.id, bio=bio)
		embed = discord.Embed(title=f":white_check_mark: Success!",
						description="We successfully set your bio",
						color=discord.Colour.green())
		embed.set_author(name=ctx.author.display_name, url="", icon_url=ctx.author.avatar_url)
		await ctx.channel.send(embed=embed)