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

import time
from discord.ext import commands
import discord

from utils.func import Competition

intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix=".", intents=intents)


async def setup(bot):
    bot.add_command(competition)


@commands.guild_only()
@commands.hybrid_group(fallback=None, invoke_without_command=True, pass_context=True, aliases=["comp", "co"])
async def competition(ctx):
    """
    Challenge your friends and enemies in a competition!
    """
    await info(ctx)


@commands.guild_only()
@competition.command(name="info")
async def info(ctx):
    """
    Instructions
    """
    help_command = ctx.bot.help_command
    await help_command.prepare_help_command(ctx)
    help_command.context = ctx
    help_command.get_destination = lambda: ctx
    await help_command.command_callback(ctx, command="competition")


@commands.guild_only()
@competition.command(name="new")
async def new(ctx: commands.Context):
    """
    Create a new competition
    """
    #if ctx.author.id in ctx.bot.in_comp:
    #    return await ctx.send("You are already in a competition! You may not create another.", ephemeral=True)
    embed = discord.Embed(title="New Competition", color=discord.Color.none())
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar)
    comp = Competition(ctx)
    view = NewComp(ctx, embed, comp)
    await view.run()


class NewComp(discord.ui.View):
    def __init__(self, ctx: commands.Context, embed: discord.Embed, comp: Competition):
        self.ctx = ctx
        self.embed = embed
        self.comp = comp
        self.message = None
        self.embed.add_field(name="Participants", value="Nothing here yet!", inline=False)
        self.embed.add_field(name="Queue", value="Nothing here yet!", inline=False)
        self.embed.add_field(name="Declined Participants", value="Nothing here yet!", inline=False)

        super().__init__(timeout=1800.0)

    async def update_data(self, interaction = None):
        self.embed.set_field_at(0, name="Participants",
                                value=("\n".join(map(lambda id: f"<@{id}>", self.comp.participants)) or "Nothing here yet!"),
                                inline=False)
        self.embed.set_field_at(1, name="Queue",
                                value=("\n".join(map(lambda id: f"<@{id}>", self.comp.queue)) or "Nothing here yet!"),
                                inline=False)
        self.embed.set_field_at(2, name="Declined Participants",
                                value=("\n".join(map(lambda id: f"<@{id}>", self.comp.declined)) or "Nothing here yet!"),
                                inline=False)
        if interaction:
            await interaction.response.edit_message(embed=self.embed)
        else:
            await self.message.edit(embed=self.embed)

    @discord.ui.button(label="Join", style=discord.ButtonStyle.green)
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        #if interaction.user.id in self.ctx.bot.in_comp and self.ctx.bot.in_comp[self.ctx.author.id] != self.comp.contest_id:
        #    return await interaction.response.send_message("You are already in another competition! You may not join this one.", ephemeral=True)
        if interaction.user.id in self.comp.participants or interaction.user.id in self.comp.queue:
            return await interaction.response.send_message("You already signed up!", ephemeral=True)

        self.ctx.bot.in_comp[interaction.user.id] = self.id
        self.comp.queue.append(interaction.user.id)
        await self.update_data()
        await interaction.response.defer()

    @discord.ui.button(label="Leave", style=discord.ButtonStyle.red)
    async def leave(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id in self.comp.participants:
            self.comp.participants.remove(interaction.user.id)
            self.comp.scoreboard.pop(interaction.user.id)
            if interaction.user.id != self.comp.creator.id:
                self.ctx.bot.in_comp.pop(interaction.user.id)
            await self.update_data()
        if interaction.user.id in self.comp.queue:
            self.comp.queue.remove(interaction.user.id)
            if interaction.user.id != self.comp.creator.id:
                self.ctx.bot.in_comp.pop(interaction.user.id)
            await self.update_data()
        if interaction.user.id in self.comp.declined:
            self.comp.declined.remove(interaction.user.id)
            if interaction.user.id != self.comp.creator.id:
                self.ctx.bot.in_comp.pop(interaction.user.id)
            await self.update_data()
        await interaction.response.defer()

    @discord.ui.button(label="Cancel Competition", style=discord.ButtonStyle.red, row=1)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.comp.creator.id:
            return await interaction.response.send_message("You are not the contest host!", ephemeral=True)
        self.stop()
        for child in self.children:
            child.disabled = True
        await self.comp.purge()

        self.embed.add_field(name="Competition **Canceled**", value=f"The host canceled the competition <t:{round(time.time())}:R>. Thank you for your understanding")
        await interaction.response.edit_message(view=self, embed=self.embed)

    @discord.ui.button(label="Approve Participants", style=discord.ButtonStyle.gray, row=1)
    async def approve(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.comp.creator.id:
            return await interaction.response.send_message("You did not start this.", ephemeral=True)
        view = Approve(timeout=180.0)
        await view.run(interaction, self.comp, self)

    @discord.ui.button(label="Start", style=discord.ButtonStyle.gray, row=1)
    async def start(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.comp.creator.id:
            return await interaction.response.send_message("You are not the contest host!", ephemeral=True)
        if len(self.comp.participants) < 2:
            return await interaction.response.send_message("There must be at least 2 participants to start", ephemeral=True)

        for child in self.children:
            child.disabled = True

        for person in self.comp.queue:
            self.ctx.bot.in_comp.pop(person)
        await interaction.response.edit_message(view=self)
        await self.comp.send_question(interaction)

    async def run(self):
        self.message = await self.ctx.send(embed=self.embed, view=self)

    async def on_timeout(self) -> None:
        for child in self.children:
            child.disabled = True
        await self.message.edit(view=self)


class Approve(discord.ui.View):
    async def run(self, interaction: discord.Interaction, comp: Competition, parent: NewComp):
        self.comp = comp
        self.parent = parent
        if not len(self.comp.queue):
            return await interaction.response.send_message("No participants to approve yet!", ephemeral=True)

        await interaction.response.send_message(f"Approve <@{self.comp.queue[0]}>?", view=self, ephemeral=True)

    async def delete(self, interaction):
        self.clear_items()
        await interaction.response.edit_message(content="Great! We're done with member approving. Feel free to hit the blue `Dismiss Message` button below", view=self)

    @discord.ui.button(label="Approve", style=discord.ButtonStyle.green)
    async def approve(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.comp.scoreboard[self.comp.queue[0]] = [0, 0]
        self.comp.participants.add(self.comp.queue.pop(0))
        await self.parent.update_data()
        if not len(self.comp.queue):
            return await self.delete(interaction)
        await interaction.response.edit_message(content=f"Approve <@{self.comp.queue[0]}>?")

    @discord.ui.button(label="Don't Approve", style=discord.ButtonStyle.red)
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.comp.declined.append(self.comp.queue.pop(0))
        await self.parent.update_data()
        if not len(self.comp.queue):
            return await self.delete(interaction)
        self.parent.ctx.bot.in_comp.pop(interaction.user.id)
        await interaction.response.edit_message(content=f"Approve <@{self.comp.queue[0]}>?")
