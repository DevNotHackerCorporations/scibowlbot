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

intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix=".", intents=intents)


async def setup(bot):
    bot.add_command(_server_stats)


def standard_deviation_approx(arr):
    top = 0
    average = sum(arr) / len(arr)
    for val in arr:
        top += (val - average)**2
    top = int(top // len(arr))
    return math.isqrt(top)


@commands.hybrid_command(name="serverstats")
async def _server_stats(message):
    """
    View the statistics for this server!

    Statistics include:
        - Average points in server
        - Standard Deviation of points in server
    """
    memberlist = set()
    for member in message.guild.members:
        memberlist.add(str(member.id))
    points = json.loads(open("points.json", "r").read()).get("points")
    people = []
    for k in points:
        if str(k) in memberlist:
            people.append(points[k])

    average = round(sum(people) / len(people), 2)

    embed = discord.Embed(title=f"Server stats of **{message.guild.name}**",
                          color=0xFF5733)
    embed.set_author(name=message.author.display_name,
                     url="",
                     icon_url=message.author.avatar)
    embed.set_thumbnail(url=message.guild.icon)
    embed.add_field(
        name=f"Average amount of points",
        value=
        f"The average amount of points for {message.guild.name} is {average} points.",
        inline=False)
    embed.add_field(
        name=f"Standard Deviation",
        value=
        f"The standard deviation of points for {message.guild.name} is {standard_deviation_approx(people)} points.",
        inline=False)
    await message.send(embed=embed)
