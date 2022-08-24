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

intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix=".", intents=intents)


async def setup(bot):
    bot.add_cog(Currency())


class Currency(commands.Cog):
    """
    Commands that relate to scibowlbot currency (aka. points)
    """
    @commands.hybrid_command(name="leaderboard")
    async def _leaderboard(self, message, max_people: int = 3):
        """
        View the server leaderboard (and your place in it)

        :param max_people: How many people should we show on the leaderboard? Must be between 3 and 30, inclusive.
        :type max_people: int
        """
        if not message.guild:
            embed = discord.Embed(
                title=f":warning: Error :warning:",
                description="While processing this request, we ran into an error",
                color=0xFFFF00)
            embed.set_author(name=message.author.display_name,
                             url="",
                             icon_url=message.author.avatar)
            embed.add_field(name=f'Invalid enviorment',
                            value="Leaderboards don't work in a DM")
            await message.channel.send(embed=embed)
            return
        if max_people > 30 or max_people < 3:
            embed = discord.Embed(
                title=f":warning: Error :warning:",
                description="While processing this request, we ran into an error",
                color=0xFFFF00)
            embed.set_author(name=message.author.display_name,
                             url="",
                             icon_url=message.author.avatar)
            embed.add_field(
                name=f'Invalid range "{max_people}"',
                value="Please enter a number between 3 and 30 (inclusive)")
            await message.channel.send(embed=embed)
            return

        points = json.loads(open("points.json", "r").read()).get("points")
        points = {
            k: v
            for k, v in sorted(
                points.items(), key=lambda item: item[1], reverse=True)
        }
        numusers = 0
        # Setting up embed
        embed = discord.Embed(
            title=f"The points leaderboard for **{message.guild.name}**",
            description=f"Top {max_people} people",
            color=0xFF5733)
        embed.set_author(name=message.author.display_name,
                         url="",
                         icon_url=message.author.avatar)
        embed.set_thumbnail(url=message.guild.icon)
        # end set up
        memberlist = set()
        for member in message.guild.members:
            memberlist.add(str(member.id))
        whatplace = {
            1: ":first_place: ",
            2: ":second_place: ",
            3: ":third_place: ",
        }
        prev = float("-inf")
        result = ""
        my_id = int(message.author.id)
        place = f"You're not among the top {max_people} people."

        for k in points:
            if str(k) in memberlist:
                if points[k] != prev:
                    numusers += 1
                prev = points[k]
                if numusers > max_people:
                    break
                if my_id == int(k):
                    place = f"You occupy place #{numusers}!"
                member = message.guild.get_member(int(k))
                if numusers > 3:
                    emoji = ":medal: "
                else:
                    emoji = whatplace[numusers]
                result += (emoji + " **" + str(member.display_name) + "** (" +
                           str(points[k]) + "pt)\n")
                if len(result) >= 800:
                    embed.add_field(name=f"The people and their scores",
                                    value=result,
                                    inline=False)
                    await message.send(embed=embed)
                    embed = discord.Embed(
                        title=f"Overflow",
                        description=
                        "We went over 1024 chars so we had to split it into two messages",
                        color=0xFF5733)
                    result = ""

        embed.add_field(name=f"The people and their scores",
                        value=result,
                        inline=False)
        embed.add_field(name=f"What place am I?", value=place, inline=False)
        await message.send(embed=embed)

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
