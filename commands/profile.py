import asyncio
from discord.ext import commands
from discord.ext.commands import BadArgument
import random
import discord
import typing
import re

intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix=".", intents=intents)


async def setup(bot):
    await bot.add_cog(Profile())


class Profile(commands.Cog):
    """
	Commands that relate to your profile
	"""
    @commands.command(name="profile", aliases=["p"])
    async def _profile(self, message, member: typing.Optional[discord.Member]):
        """
		View your server profile!
	
		You can change this with .change_profile
		"""
        if not member:
            member = message.author

        profile = message.bot.getprofile(member.id)

        embed = discord.Embed(
            title=f"{member.display_name}'s profile",
            description=(profile[2] if profile[2] else
                         f"{member.display_name} does not have a bio yet."),
            color=0xFF5733)
        embed.set_author(name=member.display_name,
                         url="",
                         icon_url=member.avatar)
        embed.set_thumbnail(url=member.avatar)
        embed.add_field(
            name=f"{member}'s point count",
            value=
            f"**{str(member.display_name)}** has **{str(message.bot.getpoints(str(member.id)))}** point(s)",
            inline=False)

        if not profile[0]:
            good_at = "∅"
        else:
            good_at = "\n".join(
                list(
                    map(
                        lambda x: message.bot.emoj[x.lower()] + " " + message.
                        bot.apprev[x.upper()][0].lower(), profile[0])))
        if not profile[1]:
            bad_at = "∅"
        else:
            bad_at = "\n".join(
                list(
                    map(
                        lambda x: message.bot.emoj[x.lower()] + " " + message.
                        bot.apprev[x.upper()][0].lower(), profile[1])))

        embed.add_field(name=f"What {member} is is good at",
                        value=good_at,
                        inline=False)
        embed.add_field(name=f"What {member} is is not so good at",
                        value=bad_at,
                        inline=False)
        await message.channel.send(embed=embed)

    @commands.command(name="change_profile", aliases=["cp"])
    async def _c_profile(self, message):
        """
		Changes your server profile
		"""
        obj = ChangeProfile(message)
        await obj.run()

    @commands.command(name="set_bio", aliases=["bio"])
    async def _c_bio(self, ctx, *bio):
        """
		Sets your bio for your profile
		"""
        bio = " ".join(bio)

        if not bio.strip():
            raise BadArgument("You must set your bio to something!")

        if len(bio) > 200:
            raise BadArgument("Bio must be at most 200 characters.")
        ctx.bot.changeprofile(ctx.author.id, bio=bio)
        embed = discord.Embed(title=f":white_check_mark: Success!",
                              description="We successfully set your bio",
                              color=discord.Colour.green())
        embed.set_author(name=ctx.author.display_name,
                         url="",
                         icon_url=ctx.author.avatar)
        await ctx.channel.send(embed=embed)

    @commands.command(name="search")
    async def _c_search(self, ctx):
        """
		Searches for a user
		"""
        obj = SearchView(ctx)
        await obj.run()


class ChangeProfile(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=60.0)
        self.ctx = ctx
        self.add_item(CPGood(self.ctx, self))
        self.add_item(CPBad(self.ctx, self))

    async def run(self):
        profile = self.ctx.bot.getprofile(self.ctx.author.id)
        if not profile[0]:
            good_at = "∅"
        else:
            good_at = "\n".join(
                list(
                    map(
                        lambda x: self.ctx.bot.emoj[x.lower()] + " " + self.ctx
                        .bot.apprev[x.upper()][0].lower(), profile[0])))
        if not profile[1]:
            bad_at = "∅"
        else:
            bad_at = "\n".join(
                list(
                    map(
                        lambda x: self.ctx.bot.emoj[x.lower()] + " " + self.ctx
                        .bot.apprev[x.upper()][0].lower(), profile[1])))

        em = discord.Embed(title="Change your profile", color=0x2ecc71)
        em.set_author(name=str(self.ctx.author),
                      icon_url=self.ctx.author.display_avatar.url)
        em.add_field(name=f"Your current data for 'good at'",
                     value=good_at,
                     inline=False)
        em.add_field(name=f"Your current data for 'not so good at'",
                     value=bad_at,
                     inline=False)
        em.set_footer(text=f"Confused? Learn more with .help change_profile")

        self.message = await self.ctx.send(embed=em, view=self)

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True

        await self.message.edit(view=self)


class CPGood(discord.ui.Select):
    def __init__(self, ctx, view):
        self.ctx = ctx
        self.author = ctx.author.id
        good_at, bad_at, bio = ctx.bot.getprofile(int(self.author))
        if not good_at:
            good_at = []

        options = [
            discord.SelectOption(
                label=ctx.bot.apprev[subject.upper()][0].capitalize(),
                value=subject,
                default=(subject in good_at),
                emoji=ctx.bot.emoj[subject]) for subject in [
                    "phy", "gen", "energy", "eas", "chem", "bio", "astro",
                    "math", "es", "cs"
                ]
        ]

        super().__init__(placeholder='Things you are good at',
                         min_values=1,
                         max_values=10,
                         options=options)

    async def callback(self, interaction):
        if interaction.user.id != self.author:
            return await interaction.response.send_message(
                "Sorry, this select menu is not controlled by you! Your changes have not been saved. Maybe create one by youself with `.change_profile`..?",
                ephemeral=True)
        self.ctx.bot.changeprofile(self.author, good=self.values)
        await interaction.response.defer()


class CPBad(discord.ui.Select):
    def __init__(self, ctx, view):
        self.ctx = ctx
        self.author = ctx.author.id
        good_at, bad_at, bio = ctx.bot.getprofile(int(self.author))
        if not bad_at:
            bad_at = []

        options = [
            discord.SelectOption(
                label=ctx.bot.apprev[subject.upper()][0].capitalize(),
                value=subject,
                default=(subject in bad_at),
                emoji=ctx.bot.emoj[subject]) for subject in [
                    "phy", "gen", "energy", "eas", "chem", "bio", "astro",
                    "math", "es", "cs"
                ]
        ]
        super().__init__(placeholder='Things you are good at',
                         min_values=1,
                         max_values=10,
                         options=options)

    async def callback(self, interaction):
        if interaction.user.id != self.author:
            return await interaction.response.send_message(
                "Sorry, this select menu is not controlled by you! Your changes have not been saved. Maybe create one by youself with `.change_profile`..?",
                ephemeral=True)
        self.ctx.bot.changeprofile(self.author, bad=self.values)
        await interaction.response.defer()


class SearchView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=60.0)
        self.ctx = ctx
        self.add_item(SearchGood(self.ctx))
        self.add_item(SearchBad(self.ctx))


class SearchGood(discord.ui.Select):
    def __init__(self, ctx):
        self.ctx = ctx
        self.author = ctx.author.id

        options = [
            discord.SelectOption(
                
				label=ctx.bot.apprev[subject.upper()][0].capitalize(),
                
				value=subject,
                
				default=False,
                emoji=ctx.bot.emoj[subject]) for subject in [
                    "phy", "gen", "energy", "eas", "chem", "bio", "astro",
                    "math", "es", "cs"
                ]
        ]
        super().__init__(placeholder='Query for good at',
                         min_values=0,
                         max_values=10,
                         options=options)

    async def callback(self, interaction):
        if interaction.user.id != self.author:
            return await interaction.response.send_message(
                "Sorry, this select menu is not controlled by you! Your changes have not been saved. Maybe create one by youself with `.change_profile`..?",
                ephemeral=True)

        await interaction.response.defer()


class SearchBad(discord.ui.Select):
    def __init__(self, ctx):
        self.ctx = ctx
        self.author = ctx.author.id

        options = [
            discord.SelectOption(
                
				label=ctx.bot.apprev[subject.upper()][0].capitalize(),
                
				value=subject,
                
				default=False,
                emoji=ctx.bot.emoj[subject]) for subject in [
                    "phy", "gen", "energy", "eas", "chem", "bio", "astro",
                    "math", "es", "cs"
                ]
        ]
        super().__init__(placeholder='Query for good at',
                         min_values=0,
                         max_values=10,
                         options=options)

    async def callback(self, interaction):
        if interaction.user.id != self.author:
            return await interaction.response.send_message(
                "Sorry, this select menu is not controlled by you! Your changes have not been saved. Maybe create one by youself with `.change_profile`..?",
                ephemeral=True)

        await interaction.response.defer()
