import discord
import os
from datetime import datetime
import pyrebase
from discord.ext import commands
from discord.ext.commands import *
from discord_components import DiscordComponents, Button, ActionRow, ButtonStyle
from flask import Flask, send_file
import json
import time

# === SETUP ===
prefix = "."
dev = 0
alertdev_err = [MissingRequiredArgument, DisabledCommand, MemberNotFound, GuildNotFound, UserNotFound, BadUnionArgument, ExtensionNotLoaded, ExtensionAlreadyLoaded, ExtensionNotLoaded, BadArgument]

intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix=prefix, intents=intents)
DiscordComponents(client)
client.hasQuestion = set()


config = {
	"apiKey": os.environ['API_key'],
	"authDomain": "https://scibowlbot-6226d.firebaseapp.com",
	"projectId": "scibowlbot-6226d",
	"storageBucket": "https://scibowlbot-6226d.appspot.com",
	"messagingSenderId": "845301907304",
	"databaseURL": "https://scibowlbot-6226d-default-rtdb.firebaseio.com/",
	"appId": "1:845301907304:web:542d9a100ffac52576a0dd",
	"measurementId": "G-17XY9EN63J"
}
firebase = pyrebase.initialize_app(config)
client.db = firebase.database()



# This gets rid of the flask messages
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
# End

# Commands
client.load_extension('commands.constants')
client.load_extension('commands.question')
client.load_extension('commands.profile')
client.load_extension('commands.serverstats')
client.load_extension('commands.dev')
client.load_extension('commands.gift')
client.load_extension('commands.leaderboard')
# End

	
@client.event
async def on_ready():
	print('Logged in as {0.user} in {1} servers at {2} (UTC)'.format(client, len(client.guilds), datetime.now().strftime("%B %d, %Y %H:%M:%S")))
	await client.change_presence(status=discord.Status.online, activity=discord.Game(name=(prefix+"help"), type=discord.ActivityType.listening, start=datetime(2021, 12, 2, 16)))
	global dev
	dev = client.get_user(728297793646624819)
	client.devs = [dev]
	for webhook in client.status_webhook:
		webhook.send("Sbb ready to serve up questions")

@client.event
async def on_disconnect():
	for webhook in client.status_webhook:
		webhook.send("Sbb has disconnected")

@client.event
async def on_message(message):
	if message.author == client.user:
		return
	await client.process_commands(message)

	if "<@!"+str(client.user.id)+">" in message.content:
		await message.channel.send("Hi there! I'm active and ready to serve up questions. For help, type "+prefix+"help")

@client.event
async def on_button_click(interaction):
	if interaction.custom_id[:3] == "niu":
		await interaction.respond(content="This button is not in use anymore.")
		return

@client.event
async def on_command_error(ctx, err):
	if isinstance(err, CommandNotFound):
		return

	alert_dev = not any([isinstance(err, b) for b in alertdev_err])
	embed = discord.Embed(title=f":warning: Warning! :warning:", description="While processing this request, we ran into an unexpected error", color=0xFFFF00)
	embed.set_author(name=ctx.author.display_name, url="", icon_url=ctx.author.avatar_url)
	embed.add_field(name=f'The error', value="```\n"+str(err)+"\n```")
	if alert_dev:
		embed.set_footer(text="The dev has been notified", icon_url=dev.avatar_url)
	else:
		embed.set_footer(text="The dev has blacklisted this error", icon_url=dev.avatar_url)
	await ctx.channel.send(embed=embed)

	if alert_dev:
		embed = discord.Embed(title=f":warning: Dev Alert! :warning:", description="While processing a request, we ran into an error", color=0xFFFF00)
		embed.set_author(name=ctx.author.display_name, url="", icon_url=ctx.author.avatar_url)
		embed.add_field(name="Message Sender", value=f"{ctx.author} ({ctx.author.id})", inline=False)
		embed.add_field(name="Message ID", value=f"{ctx.message.id}", inline=False)
		if ctx.guild:
			embed.add_field(name="Message Guild", value=f"{ctx.guild.name} ({ctx.guild.id})", inline=False)
		embed.add_field(name="Contex", value="```\n"+ctx.message.content+"\n```", inline=False)
		embed.add_field(name=f'Error!', value="```\n"+str(err)+"\n```", inline=False)
		await dev.send(
			embed=embed, 
			components = [
				Button(
					style=ButtonStyle.URL,
					url=ctx.message.jump_url,
					label = "Take me there!",
				)
			]
		)


def update_data_from_firebase():
	while True:
		open("points.json", "w").write(json.dumps(client.db.get().val()))
		time.sleep(5*60)


app = Flask("app")
@app.route("/")
def home():
	return open("index.html", "r").read()
from threading import Thread


@app.route("/style.css")
def cssfile():
	return open("style.css", "r").read(), 200, {'Content-Type': 'text/css; charset=utf-8'}

@app.route("/atom.png")
def logopng():
	return send_file("atom.png", mimetype='image/png')

@app.route("/LICENSE.txt")
def license():
	return open("LICENSE.txt", "r").read(), 200, {'Content-Type': 'text/plain; charset=utf-8'}


Thread(target=lambda:app.run(host='0.0.0.0', port=8080)).start()
Thread(target=update_data_from_firebase).start()
client.run(os.getenv("TOKEN"))
