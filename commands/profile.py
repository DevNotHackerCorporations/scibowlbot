"""
The GNU General Public License v3.0 (GNU GPLv3)

scibowlbot, a Discord Bot that helps simulate a Science Bowl round.
Copyright (C) 2021-Present DevNotHackerCorporations

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

For any questions, please contant DevNotHackerCorporations by their email at <devnothackercorporations@gmail.com>
"""

from discord.ext import commands
from discord.ext.commands import BadArgument
import discord
import typing
import json
import typing

intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix=".", intents=intents)


async def setup(bot):
    await bot.add_cog(Profile())


def profile_embed(ctx, member: discord.Member, bypassPrivate=False):
    profile = ctx.bot.getprofile(member.id)
    private = ctx.bot.getvisibility(member.id)

    if private and not bypassPrivate:
        embed = discord.Embed(
            title=f"{member.display_name}'s profile",
            description="This user is private. Therefore you may not see their data.",
            color=0xFF5733)
        embed.set_author(name=member.display_name,
                         url="",
                         icon_url=member.avatar)
        embed.set_thumbnail(url=member.avatar)
        return embed

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
        f"**{str(member.display_name)}** has **{str(ctx.bot.getpoints(str(member.id)))}** point(s)",
        inline=False)

    if not profile[0]:
        good_at = "∅"
    else:
        good_at = "\n".join(
            list(
                map(
                    lambda x: ctx.bot.emoj[x.lower()] + " " + ctx.
                    bot.apprev[x.upper()][0].lower(), profile[0])))
    if not profile[1]:
        bad_at = "∅"
    else:
        bad_at = "\n".join(
            list(
                map(
                    lambda x: ctx.bot.emoj[x.lower()] + " " + ctx.
                    bot.apprev[x.upper()][0].lower(), profile[1])))

    embed.add_field(name=f"What {member} is good at",
                    value=good_at,
                    inline=False)
    embed.add_field(name=f"What {member} is not so good at",
                    value=bad_at,
                    inline=False)

    MyAchiev = ctx.bot.Achievements(str(member.id)).desc
    achiev = ""
    for node in MyAchiev:
        if node['earned']:
            achiev += f"{node['emoji']} {node['name']} - {node['description']}\n"
    if not achiev:
        achiev = "None"

    embed.add_field(name="Earned Achievements", value=achiev, inline=False)

    if private and bypassPrivate:
        embed.set_footer(text="This user is private.")

    return embed


class Profile(commands.Cog):
    """
    Commands that relate to your profile
    """

    @commands.hybrid_command(name="profile", aliases=["p"])
    async def _profile(self, message, member: typing.Optional[discord.Member]):
        """
        View your server profile!

        You can change this with .change_profile and .set_bio

        :param member: Whose profile do you want to view? defaults to [your own profile]
        :type member: int
        """
        if not member:
            member = message.author

        await message.send(embed=profile_embed(message, member, message.author.id == member.id))

    @commands.hybrid_command(name="change_profile", aliases=["cp"])
    async def _c_profile(self, message):
        """
        DISCONTINUED - Use /settings instead
        """
        await message.send("This command has been discontinued. Please use /settings instead.", ephemeral=True)

    @commands.hybrid_command(name="set_bio", aliases=["bio"])
    async def _c_bio(self, ctx):
        """
        DISCONTINUED - Use /settings instead
        """
        await ctx.send("This command has been discontinued. Please use /settings instead.", ephemeral=True)

    @commands.hybrid_command(name="search")
    async def _c_search(self, ctx):
        """
        Searches for users

        Basically, users that are good at something and/or bad at something.
        """
        obj = SearchView(ctx)
        await obj.run()

    @commands.hybrid_command(name="settings", aliases=["s"])
    async def _c_settings(self, ctx):
        """
        Changes your settings
        """
        obj = SettingsMainView(ctx)
        await obj.run()


class ChangeProfile(discord.ui.View):
    def __init__(self, ctx, parent):
        super().__init__(timeout=60.0)
        self.ctx = ctx
        self.parent = parent
        self.message = self.parent.message
        self.add_item(CPGood(self.ctx, self))
        self.add_item(CPBad(self.ctx, self))

    @discord.ui.button(label="Back", style=discord.ButtonStyle.green, row=2)
    async def back(self, interaction, button):
        self.parent.cur = self.parent
        await interaction.response.edit_message(view=self.parent)

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True

        await self.message.edit(view=self)
        await self.parent.on_timeout()


class CPGood(discord.ui.Select):
    def __init__(self, ctx, view):
        self.ctx = ctx
        self.author = ctx.author.id
        self.parent = view
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
        self.parent.parent.cur = ChangeProfile(self.ctx, self.parent.parent)
        await self.parent.parent.refresh(interaction)


class CPBad(discord.ui.Select):
    def __init__(self, ctx, view):
        self.ctx = ctx
        self.author = ctx.author.id
        self.parent = view
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
        self.parent.parent.cur = ChangeProfile(self.ctx, self.parent.parent)
        await self.parent.parent.refresh(interaction)


class SearchView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=60.0)
        self.ctx = ctx
        self.data = [[], []]  # Good, Bad
        self.matches = []
        self.pag = 8
        self.add_item(SearchGood(self.ctx))
        self.add_item(SearchBad(self.ctx))
        self.add_item(SearchPagLeft(self.ctx))
        self.add_item(SearchButton(self.ctx))
        self.add_item(SearchReset(self.ctx))
        self.add_item(SearchPagRight(self.ctx))

    async def run(self):
        em = discord.Embed(title=f"Search Results",
                           description="0 Results were Found",
                           color=discord.Colour.blurple())
        em.set_author(name=self.ctx.author.display_name,
                      url="",
                      icon_url=self.ctx.author.avatar)
        self.message = await self.ctx.send(embed=em, view=self)

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True

        await self.message.edit(view=self)


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

        self.view.data[0] = self.values
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
        super().__init__(placeholder='Query for bad at',
                         min_values=0,
                         max_values=10,
                         options=options)

    async def callback(self, interaction):
        if interaction.user.id != self.author:
            return await interaction.response.send_message(
                "Sorry, this select menu is not controlled by you! Your changes have not been saved. Maybe create one by youself with `.change_profile`..?",
                ephemeral=True)

        self.view.data[1] = self.values
        await interaction.response.defer()


class SearchButton(discord.ui.Button):
    def __init__(self, ctx):
        self.ctx = ctx
        self.author = ctx.author.id
        super().__init__(style=discord.ButtonStyle.green, label="Search")

    async def callback(self, interaction):
        if interaction.user.id != self.author:
            return await interaction.response.send_message(
                "Sorry, this button menu is not controlled by you! Your changes have not been saved. Maybe create one by youself with `.change_profile`..?",
                ephemeral=True)

        good_at, bad_at = map(set, self.view.data)
        memberlist = {str(member.id) for member in self.ctx.guild.members}

        with open("assets/points.json") as raw_data:
            raw_data = json.loads(raw_data.read())
            profiles = raw_data["profile"]
            matches = []

            for id, profile in profiles.items():
                good, bad, bio = map(lambda x: x if x else [], profile)
                bio = bio if bio else "None"

                if id in memberlist and len(
                        set(good).intersection(good_at)
                ) == len(good_at) and len(
                    set(bad).intersection(bad_at)) == len(bad_at):  # Match
                    matches.append([
                        self.ctx.bot.get_user(int(id)), bio,
                        self.ctx.bot.getpoints(id), id
                    ])

        matches.sort(key=lambda x: x[2], reverse=True)
        self.view.matches = matches
        s_or_not = "s" if len(matches) - 1 else ""

        em = discord.Embed(
            title=f"Search Results",
            description=f"{len(matches)} result{s_or_not} found. (Results 1-8)",
            color=discord.Colour.blurple())
        em.set_author(name=self.ctx.author.display_name,
                      url="",
                      icon_url=self.ctx.author.avatar)

        for match in matches[self.view.pag - 8:self.view.pag]:
            em.add_field(name=f"{match[0].name}#{match[0].discriminator}",
                         value=f"Points: {match[2]}\nBio: {match[1]}",
                         inline=False)

        await interaction.response.edit_message(embed=em, view=self.view)


class SearchReset(discord.ui.Button):
    def __init__(self, ctx):
        self.ctx = ctx
        self.author = ctx.author.id
        super().__init__(style=discord.ButtonStyle.red, label="Reset", row=2)

    async def callback(self, interaction):
        if interaction.user.id != self.author:
            return await interaction.response.send_message(
                "Sorry, this button menu is not controlled by you! Your changes have not been saved. Maybe create one by youself with `.search`..?",
                ephemeral=True)

        await interaction.response.edit_message()


class SearchPagLeft(discord.ui.Button):
    def __init__(self, ctx):
        self.ctx = ctx
        self.author = ctx.author.id
        super().__init__(style=discord.ButtonStyle.gray, emoji="⬅️", row=2)

    async def callback(self, interaction):
        if interaction.user.id != self.author:
            return await interaction.response.send_message(
                "Sorry, this button menu is not controlled by you! Your changes have not been saved. Maybe create one by youself with `.search`..?",
                ephemeral=True)

        if self.view.pag > 8:
            self.view.pag -= 8

            s_or_not = "s" if len(self.view.matches) - 1 else ""

            em = discord.Embed(
                title=f"Search Results",
                description=
                f"{len(self.view.matches)} result{s_or_not} found. {self.view.pag - 7}-{self.view.pag}",
                color=discord.Colour.blurple())
            em.set_author(name=self.ctx.author.display_name,
                          url="",
                          icon_url=self.ctx.author.avatar)

            for match in self.view.matches[self.view.pag - 8:self.view.pag]:
                em.add_field(name=f"{match[0].name}#{match[0].discriminator}",
                             value=f"Points: {match[2]}\nBio: {match[1]}",
                             inline=False)

            await interaction.response.edit_message(embed=em, view=self.view)
        else:
            await interaction.response.defer()


class SearchPagRight(discord.ui.Button):
    def __init__(self, ctx):
        self.ctx = ctx
        self.author = ctx.author.id
        super().__init__(style=discord.ButtonStyle.gray, emoji="➡️", row=2)

    async def callback(self, interaction):
        if interaction.user.id != self.author:
            return await interaction.response.send_message(
                "Sorry, this button menu is not controlled by you! Your changes have not been saved. Maybe create one by youself with `.search`..?",
                ephemeral=True)
        if self.view.pag < len(self.view.matches):
            self.view.pag += 8

            s_or_not = "s" if len(self.view.matches) - 1 else ""

            em = discord.Embed(
                title=f"Search Results",
                description=
                f"{len(self.view.matches)} result{s_or_not} found. (Results {self.view.pag - 7}-{self.view.pag})",
                color=discord.Colour.blurple())
            em.set_author(name=self.ctx.author.display_name,
                          url="",
                          icon_url=self.ctx.author.avatar)

            for match in self.view.matches[self.view.pag - 8:self.view.pag]:
                em.add_field(name=f"{match[0].name}#{match[0].discriminator}",
                             value=f"Points: {match[2]}\nBio: {match[1]}",
                             inline=False)

            await interaction.response.edit_message(embed=em, view=self.view)
        else:
            await interaction.response.defer()


class SettingsMainView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=600.0)
        self.ctx = ctx
        self.message = None
        self.cur = self

    async def run(self):
        self.message = await self.ctx.send(embed=profile_embed(self.ctx, self.ctx.author, bypassPrivate=True), view=self)

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True

        await self.message.edit(view=self)
        self.stop()

    async def refresh(self, interaction: discord.Interaction):
        await interaction.response.edit_message(embed=profile_embed(self.ctx, self.ctx.author, bypassPrivate=True), view=self.cur)

    @discord.ui.button(label="Change Skills", style=discord.ButtonStyle.blurple)
    async def change_skills(self, interaction: discord.Interaction, button):
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("This is not your command.", ephemeral=True)
        self.cur = ChangeProfile(self.ctx, self)
        await interaction.response.edit_message(view=self.cur)

    @discord.ui.button(label="Set Biography", style=discord.ButtonStyle.blurple)
    async def set_bio(self, interaction: discord.Interaction, button):
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("This is not your command.", ephemeral=True)
        await interaction.response.send_modal(SetBio(self))

    @discord.ui.button(label="Change Visibility", style=discord.ButtonStyle.blurple)
    async def change_vis(self, interaction: discord.Interaction, button):
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("This is not your command.", ephemeral=True)
        self.ctx.bot.changevisibility(self.ctx.author.id)
        await self.refresh(interaction)


class SetBio(discord.ui.Modal, title="Set Biography"):
    answer = discord.ui.TextInput(label='Your biography',
                               style=discord.TextStyle.short,
                               max_length=200,
                               placeholder="Quick! Your answer")

    def __init__(self, view):
        super().__init__(timeout=600.0)
        self.view = view

    async def on_submit(self, interaction: discord.Interaction):
        self.view.ctx.bot.changeprofile(self.view.ctx.author.id, bio=self.answer.value)
        self.view.cur = self.view
        await self.view.refresh(interaction)

    async def on_timeout(self):
        await self.view.on_timeout(True)
        self.stop()
