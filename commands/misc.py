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
                      "Scibowlbot is made by `Actinium#6072` with help from `hi-person#8594` and `goodbye#5213`. "
                      "Special thanks to `Fyssion#5985`, `ilovetocode#9113`, and `Streakwind#5347` for their support "
                      "helping troubleshoot and figure out discord.py. Questions are sourced from [CQCumbers's scibowldb](https://github.com/CQCumbers/scibowldb).")
        body.add_line("**Changelog**\n" + open("Changelog.md", "r").read())

        return embed, body

    async def send_bot_help(self, mapping):
        view = HelpView(self.context, self)
        view.add_categories(dict(mapping), "Homepage")

        destination = self.get_destination()
        embed, body = self.help_embed()

        view.body = body
        view.embed = embed
        await view.goto(0, edit=False)
        view.message = await destination.send(embed=view.embed, view=view)

    async def get_command_embed(self, command):
        dstr = docstring_parser.parse(command.help)

        embed = discord.Embed(title="Scibowlbot help", color=discord.Color.blurple())
        embed.add_field(name=f"`{self.get_command_signature(command)}`", value=((dstr.short_description or "") + (
            f"\n\n{dstr.long_description or ''}") or "Strangely, there's nothing here..."), inline=False)

        args = ""
        for arg in dstr.params:
            args += f"{arg.arg_name} {'= ' + arg.default if arg.default else ''} " \
                    f"({type_emojis.get(arg.type_name, arg.type_name)}" \
                    f"{', optional' if arg.is_optional else ''})\n> {arg.description}\n\n"
        embed.add_field(name="Arguments", value=(args if args else "This command requires no arguments!"), inline=False)
        return embed

    async def send_command_help(self, command):
        destination = self.get_destination()
        await destination.send(embed=await self.get_command_embed(command))

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

        view = HelpView(self.context, self)
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
        view = HelpView(self.context, self)

        destination = self.get_destination()
        embed, body = self.get_cog_embed(cog)

        view.body = body
        view.embed = embed
        await view.goto(0, edit=False)
        view.message = await destination.send(embed=view.embed, view=view)


class HelpView(discord.ui.View):
    def __init__(self, ctx, source):
        self.selectMenu = None
        self.ctx = ctx
        self.help = source
        self.message = None
        self.mapping = None
        self.embed = None
        self.body = None
        self.current = None
        self.curPage = 0
        super().__init__(timeout=30.0)

    def cogName(self, cog):
        if cog is None:
            return "Miscellaneous"
        if isinstance(cog, discord.ext.commands.Cog):
            return cog.qualified_name
        return str(cog)

    def add_categories(self, mapping: dict, current: str = "Homepage"):
        self.mapping = mapping
        self.current = current
        self.selectMenu = HelpSelect()
        self.selectMenu.add_options(["Homepage"] + list(map(self.cogName, mapping.keys())), current)
        self.add_item(self.selectMenu)

    async def rebind(self, cog, interaction: discord.Interaction, name=None):
        self.selectMenu.add_options(["Homepage"] + list(map(self.cogName, self.help.get_bot_mapping().keys())), name)
        self.embed, self.body = self.help.get_cog_embed(cog, name) if cog else self.help.help_embed()
        await self.goto(0, interaction.response)

    async def goto(self, pagenum=0, interaction: discord.Interaction = None, edit=True):
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("This is not your command!", ephemeral=True)
        self.embed.clear_fields()
        self.embed.add_field(name=f"Page {pagenum + 1}/{len(self.body.pages)}", value=self.body.pages[pagenum],
                             inline=True)
        for child in self.children:
            if child.custom_id in ["btnBack", "btnPrev"]:
                child.disabled = pagenum == 0
            if child.custom_id in ["btnNext", "btnForward"]:
                child.disabled = pagenum == len(self.body.pages) - 1

        self.curPage = pagenum
        if edit:
            if interaction.response:
                await interaction.response.edit_message(embed=self.embed, view=self)
            else:
                await self.message.edit(embed=self.embed, view=self)

    @discord.ui.button(label="<<", style=discord.ButtonStyle.gray, row=1, custom_id="btnBack")
    async def leftBtnCallback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.goto(0, interaction)

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.blurple, row=1, custom_id="btnPrev")
    async def prevBtnCallback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.goto(self.curPage - 1, interaction)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.blurple, row=1, custom_id="btnNext")
    async def nextBtnCallback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.goto(self.curPage + 1, interaction)

    @discord.ui.button(label=">>", style=discord.ButtonStyle.gray, row=1, custom_id="btnForward")
    async def rightBtnCallback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.goto(max(len(self.body.pages) - 1, 0), interaction)

    @discord.ui.button(label="Quit", style=discord.ButtonStyle.red, row=1)
    async def quitBtnCallback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.on_timeout()
        self.stop()

    async def on_timeout(self) -> None:
        self.clear_items()
        # THANK YOU ilovetocode#9113
        await self.message.edit(view=self)


class HelpSelect(discord.ui.Select):
    def __init__(self):
        super().__init__(placeholder="What category do you want to check out?", row=0)

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
