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
import discord
import docstring_parser

intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix=".", intents=intents)

type_emojis = {
    "int": ":1234: integer",
    "discord.Member": ":person_standing: Discord User",
    "str": ":abc: string"
}


async def setup(bot):
    bot.help_command = MyHelp()


class MyHelp(commands.HelpCommand):

    async def send_bot_help(self, mapping):
        destination = self.get_destination()
        await destination.send('send_bot_help got called')

    async def send_command_help(self, command):
        dstr = docstring_parser.parse(command.help)

        embed = discord.Embed(title="Scibowlbot help", color=discord.Color.green())
        embed.add_field(name=f"`{self.get_command_signature(command)}`", value=dstr.short_description + (
            f"\n\n{dstr.long_description}" if dstr.long_description else ""), inline=False)

        args = ""
        for arg in dstr.params:
            args += f"{arg.arg_name} {'= ' + arg.default if arg.default else ''} " \
                    f"({type_emojis.get(arg.type_name, arg.type_name)}" \
                    f"{', optional' if arg.is_optional else ''})\n> {arg.description}\n\n"
        embed.add_field(name="Arguments", value=(args if args else "This command requires no arguments!"), inline=False)

        destination = self.get_destination()
        await destination.send(embed=embed)

    async def send_group_help(self, group):
        destination = self.get_destination()
        await destination.send('send_group_help got called')

    async def send_error_message(self, error):
        await self.context.bot.on_command_error(self.context, error)


intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='!', help_command=MyHelp(), intents=intents)
