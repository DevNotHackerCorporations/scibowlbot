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

category_emojis = {
    "Profile": "🧍",
    "Utility": "🛠️",
    "Currency": "🪙",
    "Jishaku": "👨‍💻",
    "Homepage": "🏠",
    "Miscellaneous": "⭐"
}


async def setup(bot):
    bot.help_command = MyHelp()


class MyHelp(commands.HelpCommand):
    def help_embed(self):
        embed = discord.Embed(
            title="Scibowlbot help",
            color=discord.Color.blue(),
            description="The best way to train and play Science Bowl in your own Discord Server.")
        embed.add_field(name="How to use this guide", value="Use `.help category` for info on a category.\nUse "
                                                            "`.help command` for more info on a command.",
                        inline=False)
        embed.add_field(
            name='What is Scibowlbot?',
            value="Scibowlbot is an open-source science bot made by Actinium#6072 et al with discord.py 2.0.0a. "
                  "It is licensed under the [GNU General Public License v3](https://github.com/DevNotHackerCorporations/scibowlbot/blob/main/LICENSE.txt). "
                  "Scibowlbot has many features like serving questions, a points system, profiles, achievements, and much more!",
            inline=False)
        return embed

    async def send_bot_help(self, mapping):
        view = HelpView(self.context, self)
        view.add_categories(dict(mapping), "Homepage")

        destination = self.get_destination()
        await destination.send(embed=self.help_embed(), view=view)

    async def send_command_help(self, command):
        dstr = docstring_parser.parse(command.help)

        embed = discord.Embed(title="Scibowlbot help", color=discord.Color.blurple())
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

    def get_cog_embed(self, cog, name=None):
        embed = discord.Embed(
            title="Scibowlbot help",
            color=discord.Color.brand_green(),
            description=f"{category_emojis.get(name or cog.qualified_name, '⚙️')} {name or cog.qualified_name}")
        body = ""
        if isinstance(cog, discord.ext.commands.Cog):
            cog = cog.get_commands()

        for command in cog:
            body += f"`{self.get_command_signature(command)}` - {docstring_parser.parse(command.help).short_description}\n"

        embed.add_field(name="Commands", value=body)
        return embed

    async def send_cog_help(self, cog):
        destination = self.get_destination()
        await destination.send(embed=self.get_cog_embed(cog))


class HelpView(discord.ui.View):
    def __init__(self, ctx, source):
        self.selectMenu = None
        self.ctx = ctx
        self.help = source
        self.mapping = None
        self.current = None
        super().__init__(timeout=30.0)

    def cogName(self, cog):
        if cog is None:
            return "Miscellaneous"
        if isinstance(cog, discord.ext.commands.Cog):
            return cog.qualified_name
        return str(cog)

    def add_categories(self, mapping: dict, current: str = "Homepage"):
        self.clear_items()
        self.mapping = mapping
        self.current = current
        self.selectMenu = HelpSelect()
        self.selectMenu.add_options(["Homepage"] + list(map(self.cogName, mapping.keys())), current)
        self.add_item(self.selectMenu)

    async def rebind(self, cog, interaction: discord.Interaction, name=None):
        self.selectMenu.add_options(["Homepage"] + list(map(self.cogName, self.help.get_bot_mapping().keys())), name)
        await interaction.response.edit_message(embed=(self.help.get_cog_embed(cog, name) if cog else self.help.help_embed()), view=self)

    async def on_timeout(self) -> None:
        self.clear_items()
        await self.ctx.message.edit(view=self)


class HelpSelect(discord.ui.Select):
    def __init__(self):
        super().__init__(placeholder="What category do you want to check out?")

    def add_options(self, subjects, default):
        self.options = [
            discord.SelectOption(
                label=subject,
                value=subject,
                default=(subject == default),
                emoji=category_emojis[subject])
            for subject in subjects
        ]

    async def callback(self, interaction):
        if self.values[0] == "Homepage":
            await self.view.rebind(None, interaction, "Homepage")
        elif self.values[0] == "Miscellaneous":
            await self.view.rebind(self.view.help.get_bot_mapping()[None], interaction, "Miscellaneous")
        else:
            await self.view.rebind(self.view.ctx.bot.get_cog(self.values[0]), interaction, self.values[0])


intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='!', help_command=MyHelp(), intents=intents)
