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
from discord import app_commands
import discord
import docstring_parser
from utils.menu import Menu

intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix=".", intents=intents)

type_emojis = {
    "int": ":1234: Integer",
    "discord.Member": ":person_standing: Discord User",
    "str": ":abc: String",
    "bool": "<:binary:1020904671017177108> Binary"
}

category_emojis = {
    "Profile": "🧍",
    "Utility": "🛠️",
    "Currency": "🪙",
    "Jishaku": "👨‍💻",
    "Homepage": "🏠",
    "Miscellaneous": "⭐"
}


async def setup(bot: commands.Bot):
    bot.help_command = MyHelp()


class MyHelp(commands.HelpCommand):
    def help_embed(self):
        embed = discord.Embed(
            title="Scibowlbot help",
            color=discord.Color.blue(),
            description="The best way to train and play Science Bowl in your own Discord Server.")

        body = commands.Paginator(prefix="", suffix="", max_size=1024 - 10 - len(embed.title) - len(embed.description),
                                  linesep="\n\n")

        body.add_line("**How to use this guide**\n"
                      + "Use `.help category` for info on a category.\nUse `.help command` for more info on a command.")

        body.add_line('**What is Scibowlbot?**\n'
                      + "Scibowlbot is an open-source science bot made with discord.py 2.0.0a. that trains you for Science Bowl."
                        "It is licensed under the [GNU General Public License v3](https://github.com/DevNotHackerCorporations/scibowlbot/blob/main/LICENSE.txt). "
                        "Scibowlbot has many features like serving questions, a points system, profiles, achievements, and much more!")

        body.add_line('**Credits**\n'
                      "Scibowlbot is made by `Actinium#6072` with help from `hi-person#8594`, `goodbye#5213`, and `pulsar|not|black_hole#5039`. "
                      "Special thanks to `Fyssion#5985`, `ilovetocode#9113`, and `Streakwind#5347` for their support "
                      "helping troubleshoot and figure out discord.py. Questions are sourced from [CQCumbers's scibowldb](https://github.com/CQCumbers/scibowldb).")
        body.add_line("**Changelog**\n")
        for line in open("Changelog.md", "r").read().split("\n[END]\n"):
            body.add_line(line)

        return embed, body

    async def send_bot_help(self, mapping):
        view = Menu(self.context, self)
        view.add_categories(dict(mapping), "Homepage")

        destination = self.get_destination()
        embed, body = self.help_embed()

        view.body = body
        view.embed = embed
        await view.goto(0, edit=False)
        view.message = await destination.send(embed=view.embed, view=view)

    def get_command_embed(self, command):
        dstr = docstring_parser.parse(command.help)

        embed = discord.Embed(title="Scibowlbot help", color=discord.Color.blurple())

        body = commands.Paginator(prefix="", suffix="", max_size=1024 - 10 - len(embed.title),
                                  linesep="\n\n")

        body.add_line(self.get_command_signature(command)),
        body.add_line(((dstr.short_description or "") + (dstr.long_description or '')) or "Strangely, there's nothing "
                                                                                          "here...")

        args = ""
        for arg in dstr.params:
            args += f"{arg.arg_name} {'= ' + arg.default if arg.default else ''} " \
                    f"({type_emojis.get(arg.type_name, arg.type_name)}" \
                    f"{', optional' if arg.is_optional else ''})\n> {arg.description}\n\n"
        body.add_line("**Arguments**\n" + (args if args else "This command requires no arguments!"))
        return embed, body

    async def send_command_help(self, command):
        view = Menu(self.context, self)

        destination = self.get_destination()
        embed, body = self.get_command_embed(command)

        view.body = body
        view.embed = embed
        await view.goto(0, edit=False)
        view.message = await destination.send(embed=view.embed, view=view)

    async def send_group_help(self, group: commands.Group):
        destination = self.get_destination()
        embed = discord.Embed(
            title="Scibowlbot help",
            color=discord.Color.purple(),
            description=f"{group.qualified_name} - {group.short_doc}")

        body = commands.Paginator(prefix="", suffix="", max_size=1024 - 10 - len(embed.title) - len(embed.description),
                                  linesep="\n")

        for command in group.commands:
            body.add_line(
                f"`{self.get_command_signature(command)}` - {docstring_parser.parse(command.help).short_description}\n")
        if not group.commands:
            body.add_line("No commands here yet....")

        view = Menu(self.context, self)
        view.body = body
        view.embed = embed
        await view.goto(0, edit=False)
        view.message = await destination.send(embed=view.embed, view=view)

    async def send_error_message(self, error):
        await self.context.bot.on_command_error(self.context, error)

    def get_cog_embed(self, cog, name=None):
        embed = discord.Embed(
            title="Scibowlbot help",
            color=discord.Color.brand_green(),
            description=f"{category_emojis.get(name or cog.qualified_name, '⚙️')} {name or cog.qualified_name}")
        body = commands.Paginator(prefix="", suffix="", max_size=1024 - 10 - len(embed.title) - len(embed.description),
                                  linesep="\n")
        if isinstance(cog, discord.ext.commands.Cog):
            cog = cog.get_commands()

        for command in cog:
            body.add_line(
                f"`{self.get_command_signature(command)}` - {docstring_parser.parse(command.help).short_description}\n")

        return embed, body

    async def send_cog_help(self, cog):
        view = Menu(self.context, self)

        destination = self.get_destination()
        embed, body = self.get_cog_embed(cog)

        view.body = body
        view.embed = embed
        await view.goto(0, edit=False)
        view.message = await destination.send(embed=view.embed, view=view)


intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='!', help_command=MyHelp(), intents=intents)
