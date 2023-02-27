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

For any questions, please contact DevNotHackerCorporations by their email at <devnothackercorporations@gmail.com>
"""

import json

from discord.ext import commands
from discord.ext.commands import BadArgument
from discord import app_commands
import discord

intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix=".", intents=intents)


async def setup(bot):
    await bot.add_cog(Utility(bot))


class QuestionView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=300.0)
        self.ctx = ctx

    async def run(self):
        self.message = await self.ctx.send(view=self, ephemeral=True)

    @discord.ui.button(label="Launch Suggestion Modal", style=discord.ButtonStyle.blurple)
    async def btn(self, interaction, button):
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("Sorry, this is not your command!", ephemeral=True)
        else:
            await interaction.response.send_modal(QuestionReq(self.ctx))

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True

        await self.message.edit(view=self)


class QuestionReq(discord.ui.Modal, title='Question Request'):
    category = discord.ui.TextInput(label='Question Category', required=True, placeholder="Physics, Chemistry, "
                                                                                          "Biology, etc.")
    text = discord.ui.TextInput(label='Question', style=discord.TextStyle.paragraph, required=True)
    answer = discord.ui.TextInput(label="Question Answer", style=discord.TextStyle.paragraph, required=True)

    def __init__(self, ctx):
        self.ctx = ctx
        super().__init__()

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Incoming Question Suggestion!", color=discord.Color.blue())
        embed.set_author(name=f"{self.ctx.author.name}#{self.ctx.author.discriminator} (ID: {self.ctx.author.id})",
                         icon_url=self.ctx.author.avatar)
        embed.add_field(name="Category", value=f"`{self.category}`", inline=False)
        embed.add_field(name="Question Statement", value=f"`{self.text}`", inline=False)
        embed.add_field(name="Answer", value=f"`{self.answer}`", inline=False)
        await self.ctx.bot.suggestionLog.send(embed=embed)
        await interaction.response.send_message(f'Your response was recorded.', ephemeral=True)


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="servers")
    async def _dev_servers(self, ctx):
        """
        How many servers is scibowlbot in?
        """
        await ctx.send("I am currently in " + str(len(ctx.bot.guilds)) +
                       " servers!")

    @commands.hybrid_command(name="users")
    async def _dev_users(self, ctx):
        """
        How many users use scibowlbot?
        """
        data = json.loads(open("assets/points.json", "r").read())
        await ctx.send(f"I currently help {len(data['points'])} users get better at science!")

    @commands.hybrid_command(name="clear")
    async def _dev_clear(self, message):
        """
        Remove this channel from the list of channels that already have a question.

        Use this command to override scibowlbot when it incorrectly says that there already is a question in the channel
        """
        if message.channel.id in message.bot.hasQuestion:
            message.bot.hasQuestion.remove(message.channel.id)
        await message.reply("Done!", mention_author=False)

    @commands.is_owner()
    @commands.hybrid_command(name="reload")
    @app_commands.rename(command_name="command-name")
    async def _reload(self, ctx, command_name):
        """
        Refresh a file without restarting the bot.
        This is only to be used by developers.

        :param command_name: The file path
        :type command_name: str
        """
        if ctx.author not in ctx.bot.devs:
            raise BadArgument("Unauthorized. This command is dev only.")
        await ctx.bot.reload_extension(command_name)
        await ctx.send("Reloaded extention")

    @commands.hybrid_command(name="ping")
    async def _ping(self, ctx):
        """
        Check my latency!
        """
        embed = discord.Embed(
            title="Pong",
            color=discord.Colour.green(),
            description=
            f"It took {round(ctx.bot.latency * 1000)}ms to get back here")
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="suggest")
    async def _suggest(self, ctx, *, suggestion):
        """
        Suggest or report a bug to the scibowlbot developers!

        :param suggestion: What's your suggestion/bug?
        :type suggestion: str
        """

        embed = discord.Embed(title="Incoming Suggestion!", color=discord.Color.green(), description=suggestion)
        embed.set_author(name=f"{ctx.author.name}#{ctx.author.discriminator} (ID: {ctx.author.id})",
                         icon_url=ctx.author.avatar)
        embed.add_field(name="Original", value=f"[Jump!]({ctx.message.jump_url})")
        await ctx.bot.suggestionLog.send(embed=embed)
        if ctx.prefix == ".":
            await ctx.message.add_reaction("✅")
        else:
            await ctx.send("Success! Your suggestion was sent!", ephemeral=True)

    @commands.hybrid_command("suggest_question", aliases=["sg"])
    async def _sg(self, ctx):
        """
        Suggest a question that may be considered for publishing
        """
        question = QuestionView(ctx)
        await question.run()
