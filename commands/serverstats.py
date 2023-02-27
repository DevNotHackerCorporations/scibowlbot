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
import math
import discord
import json
import typing
from utils.func import get_points

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats as scistats

intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix=".", intents=intents)


async def setup(bot):
    bot.add_command(stats)


def standard_deviation_approx(arr):
    top = 0
    average = sum(arr) / len(arr)
    for val in arr:
        top += (val - average) ** 2
    top = int(top // len(arr))
    return math.isqrt(top)


@commands.guild_only()
@commands.hybrid_group(fallback="stats", invoke_without_command=True, pass_context=True, aliases=["ss"])
async def stats(ctx):
    """
    View the statistics for this server!

    Statistics include:
        - Average points in server
        - Standard Deviation of points in server
    """
    people = get_points(ctx)

    average = round(sum(people) / len(people), 2)

    embed = discord.Embed(title=f"Server stats of **{ctx.guild.name}**",
                          color=0xFF5733)
    embed.set_author(name=ctx.author.display_name,
                     url="",
                     icon_url=ctx.author.avatar)
    embed.set_thumbnail(url=ctx.guild.icon)
    embed.add_field(
        name=f"Average amount of points",
        value=
        f"The average amount of points for {ctx.guild.name} is {average} points.",
        inline=False)
    embed.add_field(
        name=f"Standard Deviation",
        value=
        f"The standard deviation of points for {ctx.guild.name} is {standard_deviation_approx(people)} points.",
        inline=False)
    await ctx.send(embed=embed)


@commands.guild_only()
@stats.command(name='points_distribution', aliases=["pd"])
async def _pd(ctx):
    """
    Rounds points to nearest 100 and then displays data in bar graph
    """
    async with ctx.typing():
        people = get_points(ctx)
        distrib = {}
        for person in people:
            distrib[person // 100 * 100] = distrib.get(person // 100 * 100, 0) + 1

        fig = plt.figure(figsize=(10, 5))
        plt.locator_params(axis="both", integer=True, tight=True)

        plt.bar(list(distrib.keys()), list(distrib.values()), color='green', width=20)

        plt.xlabel("Points rounded down to the nearest 100")
        plt.ylabel("Number of people")
        plt.title("Points Distribution")
        plt.savefig('assets/image.png')

    await ctx.send(file=discord.File("assets/image.png"))


@commands.guild_only()
@stats.command(name='percentile', aliases=["pc"])
async def _pc(ctx, user: typing.Optional[discord.Member]):
    """
    Shows global percentiles

    :param user: Where is [subject] on the percentile chart? defaults to you
    :type user: discord.Member, optional
    """
    if user is None:
        user = ctx.author

    async with ctx.typing():
        people = get_points(ctx, True)
        nparr = np.array(people)

        fig = plt.figure(figsize=(10, 5))
        plt.locator_params(axis="both", integer=True, tight=True)

        x = list(range(1, 101))
        y = [float(np.percentile(nparr, i)) for i in x]

        plt.plot(x, y, color='green')
        mypercent = scistats.percentileofscore(people, ctx.bot.getpoints(str(user.id)))
        plt.plot(mypercent, round((np.percentile(nparr, mypercent)), 2), "ro")

        plt.xlabel("Percentile")
        plt.ylabel("Number")
        plt.title("Percentiles")
        plt.savefig('assets/image.png')

    await ctx.send(file=discord.File("assets/image.png"))
