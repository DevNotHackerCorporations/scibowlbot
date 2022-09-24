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
import json
import pathlib
import typing
from utils.menu import Menu
from utils.func import get_points

intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix=".", intents=intents)


async def setup(bot):
    await bot.add_cog(Currency())


class Currency(commands.Cog):
    """
    Commands that relate to scibowlbot currency (aka. points)
    """

    @commands.guild_only()
    @commands.hybrid_command(name="leaderboard", aliases=["lb"])
    async def _leaderboard(self, ctx, max_people: typing.Optional[int] = 3, global_: typing.Optional[bool] = False):
        """
        View the server leaderboard (and your place in it)

        :param max_people: How many people should we show on the leaderboard? defaults to 3
        :type max_people: int
        :param global_: Should we show the global leaderboard? defaults to no
        :type global_: bool
        """

        standingEmojis = {
            1: ":first_place: ",
            2: ":second_place: ",
            3: ":third_place: ",
        }
        embed = discord.Embed(
            title=f"The points leaderboard for **{ctx.guild.name}**" if not global_ else "Global leaderboard",
            description=f"Top {max_people} people",
            color=0xFF5733)
        embed.set_author(name=ctx.author.display_name,
                         url="",
                         icon_url=ctx.author.avatar)
        embed.set_thumbnail(url=ctx.guild.icon if not global_ else f"https://raw.githubusercontent.com/DevNotHackerCorporations/scibowlbot/main/website/globe.png")
        body = commands.Paginator(prefix="",
                                  suffix=f"\n**What place am I?**\nYou are not among the top {max_people}",
                                  max_size=1024 - 10 - len(embed.title),
                                  linesep="\n")

        points = {x: y for x, y in sorted(get_points(ctx, global_, True).items(), key=lambda x: x[1], reverse=True)}

        for index, (id, points) in enumerate(points.items()):
            if index > max_people - 1:
                break
            if str(ctx.author.id) == str(id):
                body.suffix = f"\n**What place am I?**\nYou occupy place #{index + 1}"

            if not global_:
                name = ctx.guild.get_member(int(id)).display_name
            else:
                name = f"<@{id}>"

            emoji = standingEmojis.get(index + 1, ":medal:")
            body.add_line(emoji + " **" + str(name) + "** (" +
                          str(points) + "pt)")

        view = Menu(ctx, self)

        view.body = body
        view.embed = embed
        await view.goto(0, edit=False)
        view.message = await ctx.send(embed=view.embed, view=view)

    @commands.hybrid_command(name="gift")
    async def _gift(self, message, amount: int, to_user: discord.Member):
        """
        Gift some of your points to someone!

        :param amount: How many coins are you gifting?
        :type amount: int
        :param to_user: Who are you gifting to?
        :type to_user: discord.Member
        """
        if amount < 0:
            raise BadArgument(
                "There are two people in life, those whose power is to give and those whos weakness is to take, "
                "in other words, YOU GREEDY LITTLE--")

        to = str(to_user.id)

        embed = discord.Embed(title=f"Some points were just gifted!",
                              description=f"{message.author.display_name} just tried to gift {amount} points.",
                              color=0xFF5733)
        embed.set_author(name=message.author.display_name, url="", icon_url=message.author.avatar)
        embed.set_thumbnail(url=message.author.avatar)

        if not message.guild:
            embed.add_field(name="Error", value="You can't gift points outside of a server.")
            await message.channel.send(embed=embed)
            return
        user = str(message.author.id)
        user_money = int(message.bot.getpoints(user))

        to_user = await message.guild.fetch_member(int(to))
        embed.set_thumbnail(url=to_user.avatar)

        if amount > user_money:
            raise BadArgument(f"This goes over your current balance of {user_money}")
        elif to_user.bot:
            raise BadArgument("You can't give points to a bot...")
        else:
            message.bot.changepoints(user, -1 * amount)
            message.bot.changepoints(to, amount)
            embed.add_field(name=f"{message.author.display_name} now has",
                            value=f"{message.bot.getpoints(user)} points. (-{amount})")
            embed.add_field(name=f"{to_user.display_name} now has",
                            value=f"{message.bot.getpoints(to)} points. (+{amount})")
        await message.reply(embed=embed)
        try:
            await to_user.send(f"**{message.author.display_name}** just sent you **{amount}** coins!")
        except:
            raise BadArgument(
                "This user may have DMs disabled. There is nothing we can do about this. It doesn't matter really.") from None
