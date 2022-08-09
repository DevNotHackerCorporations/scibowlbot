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

    @commands.hybrid_command(name="servers")
    async def _dev_servers(self, ctx):
        """
        How many servers is scibowlbot in?
        """
        await ctx.send("I am currently in " + str(len(ctx.bot.guilds)) +
                       " servers!")

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
    async def _reload(self, ctx, command_name):
        """
        Refresh a file without restarting the bot. (Dev only)
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
