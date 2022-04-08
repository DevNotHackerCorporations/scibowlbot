import discord
import os
import json
from datetime import datetime
from discord.ext import commands
from discord.ext.commands import *
from discord_components import DiscordComponents, Button, ActionRow, ButtonStyle



# === SETUP ===
intents = discord.Intents.default()
intents.members = True
#client = discord.Client(intents=intents)
prefix = "."
client = commands.Bot(command_prefix=prefix, intents=intents)
DiscordComponents(client)
client.hasQuestion = set()
alertdev_err = [MissingRequiredArgument, DisabledCommand, MemberNotFound, GuildNotFound, UserNotFound, BadUnionArgument, ExtensionNotLoaded, ExtensionAlreadyLoaded]
dev = 0



# This gets rid of the flask messages
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
# End

# Commands
client.load_extension('commands.question')
client.load_extension('commands.profile')
client.load_extension('commands.serverstats')
client.load_extension('commands.dev')
client.load_extension('commands.gift')
client.load_extension('commands.leaderboard')
client.load_extension('commands.change_profile')
# End

client.apprev = {
	"PHY":["PHYSICS"],
	"GEN":["GENERAL SCIENCE"],
	"ENERGY":["ENERGY"],
	"EAS":["EARTH AND SPACE"],
	"CHEM":["CHEMISTRY"],
	"BIO":["BIOLOGY"],
	"ASTRO":["ASTRONOMY"],
	"MATH":["MATH"],
	"CS":["COMPUTER SCIENCE"],
	"ES":["EARTH SCIENCE"],
	"WEIRD":["WEIRD PROBLEMS"],
	"CRAZY":["CRAZY PROBLEMS"],
	"ALL":[
		"PHYSICS",
		"GENERAL SCIENCE",
		"ENERGY",
		"EARTH AND SPACE",
		"EARTH SCIENCE",
		"CHEMISTRY",
		"BIOLOGY",
		"ASTRONOMY",
		"MATH",
		"COMPUTER SCIENCE"
	],
	"EVERYTHING":[
		"PHYSICS",
		"GENERAL SCIENCE",
		"ENERGY",
		"EARTH AND SPACE",
		"EARTH SCIENCE",
		"CHEMISTRY",
		"BIOLOGY",
		"ASTRONOMY",
		"MATH",
		"COMPUTER SCIENCE",
		"WEIRD PROBLEMS",
		"CRAZY PROBLEMS"
	]
}


def changepoints(user, point):
	points = json.loads(open("points.json", "r").read())
	points["points"][user] = points.get("points").get(user, 0) + point
	open("points.json", "w").write(json.dumps(points))
	# db.set(points)


def getpoints(user):
	points = json.loads(open("points.json", "r").read())
	return points.get("points").get(user, 0)

def changeprofile(user, good=None, bad=None, bio=None):
	user = str(user)
	points = json.loads(open("points.json", "r").read())
	if not points["profile"].get(user):
		points["profile"][user] = [[], [], ""]
	if good:
		points["profile"][user][0] = good
	if bad:
		points["profile"][user][1] = bad
	if bio:
		points["profile"][user][2] = bio
	open("points.json", "w").write(json.dumps(points))
	# db.set(points)


def getprofile(user):
	user = str(user)
	points = json.loads(open("points.json", "r").read())
	return points.get("profile").get(user, [[], [], ""])

def t_string(seconds: int) -> str:
	day = seconds // (24 * 3600)
	seconds = seconds % (24 * 3600)
	hour = seconds // 3600
	seconds %= 3600
	minutes = seconds // 60
	seconds %= 60
	seconds = seconds
	return ("%d days, %d hours, %d minutes, and %d seconds!" % (day, hour, minutes, seconds))

client.changepoints = changepoints
client.getpoints = getpoints
client.changeprofile = changeprofile
client.getprofile = getprofile


	
@client.event
async def on_ready():
	print('Logged in as {0.user} in {1} servers at {2} (UTC)'.format(client, len(client.guilds), datetime.now().strftime("%B %d, %Y %H:%M:%S")))
	await client.change_presence(status=discord.Status.online, activity=discord.Game(name=(prefix+"help"), type=discord.ActivityType.listening))
	global dev
	dev = client.get_user(728297793646624819)
	client.devs = [dev]

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

from flask import Flask, send_file

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
#Thread(target=update_data_from_firebase).start()
client.run(os.getenv("TOKEN"))
