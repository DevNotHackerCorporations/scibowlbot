#!/usr/bin/python -tt
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

import discord
from discord.ext import commands
from discord.ext.commands import MissingRequiredArgument, DisabledCommand, MemberNotFound, GuildNotFound, UserNotFound, BadUnionArgument, ExtensionNotLoaded, ExtensionAlreadyLoaded, ExtensionNotLoaded, BadArgument, CommandNotFound

import asyncio
from datetime import datetime
from flask import Flask, send_file
import json
import logging
import os
import time
import pyrebase
import traceback

dev = 0

alertdev_err = [
    MissingRequiredArgument, DisabledCommand, MemberNotFound, GuildNotFound,
    UserNotFound, BadUnionArgument, ExtensionNotLoaded, ExtensionAlreadyLoaded,
    ExtensionNotLoaded, BadArgument
]

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


class Sbb(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True

        super().__init__(
            command_prefix=".",
            description="The best way to do science on discord!",
            owner_id=728297793646624819,  # Andrew
            case_insensitive=True,
            intents=intents,
        )

        config = {
            "apiKey": os.environ['API_key'],
            "authDomain": "https://scibowlbot-6226d.firebaseapp.com",
            "projectId": "scibowlbot-6226d",
            "storageBucket": "https://scibowlbot-6226d.appspot.com",
            "messagingSenderId": "845301907304",
            "databaseURL":
            "https://scibowlbot-6226d-default-rtdb.firebaseio.com/",
            "appId": "1:845301907304:web:542d9a100ffac52576a0dd",
            "measurementId": "G-17XY9EN63J"
        }
        self.db = pyrebase.initialize_app(config).database()

    async def setup_hook(self):
        await self.load_extension('commands.constants')
        await client.load_extension('commands.question2')
        await self.load_extension('commands.profile')
        await self.load_extension('commands.serverstats')
        await self.load_extension('commands.dev')
        await self.load_extension('commands.gift')
        await self.load_extension('commands.leaderboard')

    async def on_ready(self):
        print('Logged in as {0.user} in {1} servers at {2} (UTC)'.format(
            client, len(client.guilds),
            datetime.now().strftime("%B %d, %Y %H:%M:%S")))
        await client.change_presence(status=discord.Status.online,
                                     activity=discord.Game(
                                         name=(".help"),
                                         type=discord.ActivityType.listening,
                                         start=datetime(2021, 12, 2, 16)))
        global dev
        dev = client.get_user(728297793646624819)
        client.devs = [dev]

    async def on_message(self, message):
        if message.author == client.user:
            return
        await self.invoke(await super().get_context(message))

        if client.user.mention in message.content:
            await message.channel.send(
                "Hi there! I'm active and ready to serve up questions. For help, type "
                + ".help")

    async def on_command_error(self, ctx, err):
        if isinstance(err, CommandNotFound):
            return
        
        alert_dev = not any([isinstance(err, b) for b in alertdev_err])
        embed = discord.Embed(
            title=f":warning: Warning! :warning:",
            description=
            "While processing this request, we ran into an unexpected error",
            color=0xFFFF00)
        
        embed.set_author(name=ctx.author.display_name,
            url="",
            icon_url=ctx.author.avatar)
        
        embed.add_field(name=f'The error',
            value="```\n" + str(err) +"\n```")
        
        if alert_dev:
            embed.set_footer(text="The dev has been notified",
            icon_url=dev.avatar)
        else:
            embed.set_footer(text="The dev has blacklisted this error", icon_url=dev.avatar)
        
        await ctx.channel.send(embed=embed)
        
        if alert_dev:
            raise err

        if alert_dev:
            embed = discord.Embed(
                title=f":warning: Dev Alert! :warning:",
                description="While processing a request, we ran into an error",
                color=0xFFFF00)
            embed.set_author(name=ctx.author.display_name,
                             url="",
                             icon_url=ctx.author.avatar)
            embed.add_field(name="Message Sender",
                            value=f"{ctx.author} ({ctx.author.id})",
                            inline=False)
            embed.add_field(name="Message ID",
                            value=f"{ctx.message.id}",
                            inline=False)
            if ctx.guild:
                embed.add_field(name="Message Guild",
                                value=f"{ctx.guild.name} ({ctx.guild.id})",
                                inline=False)
            embed.add_field(name="Contex",
                            value="```\n" + ctx.message.content + "\n```",
                            inline=False)
            embed.add_field(name=f'Error!',
                            value="```\n" + str(err) + "\n```",
                            inline=False)
            embed.add_field(name=f'Jump Link',
                            value=ctx.message.jump_url,
                            inline=False)
            await dev.send(embed=embed)


def update_data_from_firebase():
    global client
    while True:
        open("points.json", "w").write(json.dumps(client.db.get().val()))
        time.sleep(5 * 60)


app = Flask("app")


@app.route("/")
def home():
    return open("website/index.html", "r").read()


from threading import Thread


@app.route("/style.css")
def cssfile():
    return open("website/style.css", "r").read(), 200, {
        'Content-Type': 'text/css; charset=utf-8'
    }


@app.route("/atom.png")
def logopng():
    return send_file("website/atom.png", mimetype='image/png')


@app.route("/LICENSE.txt")
def license():
    return open("LICENSE.txt", "r").read(), 200, {
        'Content-Type': 'text/plain; charset=utf-8'
    }


@app.route("/api")
def api():
    return open("points.json", "r").read(), 200, {
        'Content-Type': 'text/json; charset=utf-8'
    }


Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()
Thread(target=update_data_from_firebase).start()
client = Sbb()
client.run(os.getenv('TOKEN'))
