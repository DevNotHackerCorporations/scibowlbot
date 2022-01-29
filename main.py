import discord
from discord_components import DiscordComponents, Button, ActionRow
import os
import asyncio
import readtime
import requests
import re
import json
import random
#import pyrebase
import time
from datetime import datetime

# setting up firebase
"""config = {
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
#auth = firebase.auth()
#user = auth.sign_in_with_email_and_password("devnothackercorporations@gmail.com", os.environ['email_psw'])
#user = auth.refresh(user['refreshToken'])
db = firebase.database()"""

# This gets rid of the flask messages
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
# End


intents = discord.Intents.default()
intents.members = True

client = discord.Client(intents=intents)
#bot = SlashCommand(client, sync_commands=True)
DiscordComponents(client)
prefix = "."
hasQuestion = set()

yay_reactions = ["\N{Thumbs Up Sign}", "\N{White Heavy Check Mark}", "\N{Brain}", "\N{Hundred Points Symbol}", "\N{Direct Hit}", "\N{Clapping Hands Sign}", "\N{Trophy}", "\N{Slightly Smiling Face}", "\N{Party popper}"]
aw_reactions = ["\N{Crying Face}", "\N{White Question Mark Ornament}", "\N{Slightly Frowning Face}", "\N{Worried Face}", "\N{Thumbs Down Sign}", "\N{Loudly Crying Face}", "\N{Cross Mark}", "\N{Face with No Good Gesture}"]
def changepoints(user, point):
	points = json.loads(open("points.json", "r").read())
	points[user] = points.get(user, 0) + point
	open("points.json", "w").write(json.dumps(points))
	# db.set(points)


def getpoints(user):
	points = json.loads(open("points.json", "r").read())
	return points.get(user, 0)


@client.event
async def on_ready():
	print('Logged in as {0.user} in {1} servers at {2} (UTC)'.format(client, len(client.guilds), datetime.now().strftime("%B %d, %Y %H:%M:%S")))
	await client.change_presence(status=discord.Status.online, activity=discord.Game(name=(prefix+"help"), type=discord.ActivityType.listening))


@client.event
async def on_message(message):
	if message.author == client.user:
		return

	def validate(msg): 
		if str(msg.author.display_name) == responder and prefix+"a" not in msg.content:
			asyncio.create_task(msg.reply("Once again, to answer write `.a ANSWER` with `ANSWER` being your answer."))
		if str(msg.author.display_name) == responder and prefix+"a" in msg.content:
			return True
		return False

	def validatebtn(msg):
		return str(msg.custom_id) == str(message.channel.id)
	subject = re.match("\\"+prefix+"Q (PHY|GEN|ENERGY|EAS|ES|CHEM|BIO|ASTRO|MATH|CS|ALL)", message.content.upper())
	apprev = {
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
		]
	}
	if subject:

		# 	message.channel.send("scibowlbot is currently rate-limited by Discord for some reason. In other words, scibowlbot is down. Thanks for being patient.")
		# return

		if message.channel.id in hasQuestion:
			await message.reply(f"**There already is another question in this channel.**", mention_author=False)
			return
		hasQuestion.add(message.channel.id)
		question_json = requests.post("https://scibowldb.com/api/questions/random", json={
			"categories":apprev[subject.group(1)]
		}).json()
		question_header = "**"+question_json["question"]["category"]+" "+question_json["question"]["tossup_format"]+" (Source: "+question_json["question"]["source"]+")\n**"
		question = question_header+question_json["question"]["tossup_question"]
		mc = True
		if question_json["question"]["tossup_format"] == "Multiple Choice":
			correct_answer = (question_json["question"]["tossup_answer"])[0].upper()
			answers = []
			if ("(W)" in question):
				regstring = "\(W\)(.*)\(X\)(.*)\(Y\)(.*)\(Z\)(.*)"
			else:
				regstring = "(\(|)W\)(.*)(\(|)X\)(.*)(\(|)Y\)(.*)(\(|)Z\)(.*)"
			if re.search(regstring, question.replace("\n", ""), flags=re.DOTALL | re.MULTILINE):
				for i in list(re.search(regstring, question.replace("\n", ""), flags=re.DOTALL | re.MULTILINE).groups()):
					if i != "":
						i = i.strip()
						if len(i) < 70:
							answers.append(i)
						else:
							answers.append(i[:70]+"...")
			else:
				answers = ["", "", "", ""]
			answer_accept_bypass = correct_answer		
			accepted_answer = correct_answer	
			answer_solution_bypass = correct_answer
		else:
			correct_answer = question_json["question"]["tossup_answer"].upper()
			answer_accept_bypass = re.sub("(\(.*\))", "", question_json["question"]["tossup_answer"].upper()).strip().replace("  ", " ")
			try:
				correct_answer = question_json["question"]["tossup_answer"].upper()
				accepted_answer = question_json["question"]["tossup_answer"].upper().split(' (*ACCEPT: ',1)[1]
				accepted_answer = accepted_answer.split('DO NOT ACCEPT: ')[0]
				accepted_answer = accepted_answer.split(')')[0]
				answer_solution_bypass = question_json["question"]["tossup_answer"].upper().split(' (*SOLUTION:',1)[0]
			except BaseException: 
				accepted_answer = correct_answer
			mc = False


		sentmsg = await message.channel.send(
			question,
			components = [
				Button(label = "Answer!", custom_id=message.channel.id)
			]
		)

		clicked = True

		try: 
			waitfor = await client.wait_for(
        		"button_click",
				timeout=5+(readtime.of_text(question).seconds),
				check=validatebtn
    		)
		except (asyncio.TimeoutError):
			clicked = False
		
		if clicked:
			responder = str(waitfor.author.display_name)
			responderid = str(waitfor.author.id)
			await sentmsg.edit(content=question, components = [
				Button(label = f"Answered by {responder}!", disabled=True)
			])
			if not mc:
				#time.sleep(2)
				await waitfor.send("It's your turn to answer! You have 10 seconds.")
				try: 
					user_answer = await client.wait_for(
        				"message",
						timeout=10,
						check=validate
    				)
				except (asyncio.TimeoutError):
					changepoints(responderid,  -1)
					await message.reply(f"Incorrect **{responder}**, you ran out of time. The answer was `{correct_answer}`. You now have **{getpoints(responderid)}** (-1) points ", mention_author=False)
					#await user_answer.add_reaction(random.choice(aw_reactions))
					hasQuestion.remove(message.channel.id)
					return
				user_ans = user_answer.content
			else:
				def color(correct, mine, current):
					if current == correct:
						return 3
					if mine == -1:
						return 4
					if current == mine:
						return 4
					return 1

				def validate_mc(msg):
					if msg.custom_id[:3] == "niu":
						asyncio.create_task(msg.send("This question already ended ¯\_(ツ)_/¯"))
					if str(msg.author.display_name) == responder and re.match("mc_(w|x|y|z)([0-9]+)",str(msg.custom_id)):
						return True
					asyncio.create_task(msg.send("This question is not yours!"))
					return False

				#time.sleep(2)

				await waitfor.send("You're on! click the buttons below to answer. (You have 6 seconds in total)")
				mcbuttons = await message.channel.send(
					"The answer to the question is ___",
					components = ActionRow([
						Button(label = "W) "+answers[0], custom_id="mc_w"+str(message.channel.id), style=1),
						Button(label = "X) "+answers[1], custom_id="mc_x"+str(message.channel.id), style=1),
						Button(label = "Y) "+answers[2], custom_id="mc_y"+str(message.channel.id), style=1),
						Button(label = "Z) "+answers[3], custom_id="mc_z"+str(message.channel.id), style=1)
					])
				)
				try:
					mcButtonClick = await client.wait_for(
        				"button_click",
						timeout=6,
						check=validate_mc
    				)
				except (asyncio.TimeoutError):
					changepoints(responderid,  -1)
					await message.reply(f"Incorrect **{responder}**, you ran out of time. The answer was `{correct_answer}`. You now have **{getpoints(responderid)}** (-1) points ", mention_author=False)
					hasQuestion.remove(message.channel.id)
					await mcbuttons.add_reaction(random.choice(aw_reactions))
					await mcbuttons.edit("**"+responder+"** chose: **DID NOT CHOOSE**", components = ActionRow([
						Button(label = "W) "+answers[0], custom_id="niu1", style=color(correct_answer, -1, "W")),
						Button(label = "X) "+answers[1], custom_id="niu2", style=color(correct_answer, -1, "X")),
						Button(label = "Y) "+answers[2], custom_id="niu3", style=color(correct_answer, -1, "Y")),
						Button(label = "Z) "+answers[3], custom_id="niu4", style=color(correct_answer, -1, "Z"))
					]))
					return
				user_ans = prefix+"a "+mcButtonClick.custom_id[3]
				await mcButtonClick.send("Success! Your answer was recorded")
				await mcbuttons.edit("**"+responder+"** chose: **"+mcButtonClick.custom_id[3].upper()+"**", components = ActionRow([
					Button(label = "W) "+answers[0], custom_id="niu1", style=color(correct_answer, mcButtonClick.custom_id[3].upper(), "W")),
					Button(label = "X) "+answers[1], custom_id="niu2", style=color(correct_answer, mcButtonClick.custom_id[3].upper(), "X")),
					Button(label = "Y) "+answers[2], custom_id="niu3", style=color(correct_answer, mcButtonClick.custom_id[3].upper(), "Y")),
					Button(label = "Z) "+answers[3], custom_id="niu4", style=color(correct_answer, mcButtonClick.custom_id[3].upper(), "Z"))
				]))


			if user_ans.strip()[3:].upper() in [correct_answer, answer_accept_bypass, accepted_answer]:
				changepoints(responderid,  2)
				await message.reply(f"Correct **{responder}** You now have **{getpoints(responderid)}** (+2) points", mention_author=False)
				if (not mc):
					await user_answer.add_reaction(random.choice(yay_reactions))
				else:
					await mcbuttons.add_reaction(random.choice(yay_reactions))
			else:
				changepoints(responderid,  -1)
				await message.reply(f"Incorrect **{responder}**, the answer was `{correct_answer}`. You now have **{getpoints(responderid)}** (-1) points", mention_author=False)
				if (not mc):
					await user_answer.add_reaction(random.choice(aw_reactions))
				else:
					await mcbuttons.add_reaction(random.choice(aw_reactions))
			hasQuestion.remove(message.channel.id)			

		else:
			await message.reply("The answer was `"+correct_answer+"`", mention_author=False)			
			await sentmsg.edit(content=question, components = [
				Button(label = "Time's up. No one answered", disabled=True)
			])
			hasQuestion.remove(message.channel.id)

	if message.content.strip() == prefix+"help":
		helptxt = """
**Scibowlbot**
*a bot to help run science bowl rounds*

**How to obtain and answer a question**
Scibowlbot is a bot built by AndrewC10#6072 et al. as an alternative to womogenes's scibowlbot (https://github.com/womogenes/ScibowlBot). To start a round, simply type `"""+prefix+"""SUBJECT`, with Subject being one of the below:

:apple: PHY (**Phy**sics)
:test_tube: GEN (**Gen**eral Science)
:zap:  ENERGY (**Energy**)
:night_with_stars:  EAS (**E**arth **a**nd **S**pace)
:atom:  CHEM (**Chem**istry)
:dna:  BIO (**Bio**logy)
:ringed_planet:  ASTRO (**Astro**nomy)
:1234:  MATH (**Math**ematics)
:desktop:  CS (**C**omputer **S**cience)
:earth_americas:  ES (**E**arth **S**cience)
:microscope:  ALL (**All** categories stated above)

After you type in the command, a question and a big "Answer" button will be generated. You will be given 5 seconds plus an estimated read time to click the button. First person to click the button gets to answer the question. To answer, simply type `"""+prefix+"""a ANSWER`.(please only type the letter for multiple choice). You will be given 10 seconds to do so.

**Other features**
To view the server leaderboard, type `"""+prefix+"""leaderboard`.
To view how many points you have, type `"""+prefix+"""points`.
(Not supported anymore)To view the server statistics, type `"""+prefix+"""stats`.
==split==
**FAQ's**
Q: How can I invite scibowlbot?
A: Under <@!"""+str(client.user.id)+""">'s profile (You can get there by clicking that mention) there is a big "Add to Server" button under the bot's name. If that somehow doesn't show up, then use this link: <https://tinyurl.com/sbbv2invite>.

Q: What can I do when the bot is down?
A: You can DM or ping one of the devs, preferabaly `AndrewC10#6072`

Q: I have a question, how can I ask it?
A: You can DM one of the devs, but it is prefered that you send us an email at devnothackercorporations@gmail.com

**This bot is open source!**
This bot is open source! Help us improve it here: <https://github.com/DevNotHackerCorporations/scibowlbot> You are allowed to use this code under the conditions of the license: <https://devnothackercorporations.github.io/scibowlbot/LICENSE.txt>
		"""
		await message.add_reaction("\N{White Heavy Check Mark}")
		await message.author.send(helptxt.split("==split==")[0])
		await message.author.send(helptxt.split("==split==")[1])

	if message.content.strip() == prefix+"points":
		await message.channel.send(f"**{str(message.author.display_name)}**, you have **{str(getpoints(str(message.author.id)))}** point(s)")

	if re.match("\\"+prefix+"points <@!([0-9]+)>", message.content.strip()):
		member = await message.guild.fetch_member(int(re.match("\\"+prefix+"points <@!([0-9]+)>", message.content.strip()).group(1)))
		await message.channel.send(f"**{str(member.display_name)}** has **{str(getpoints(str(member.id)))}** point(s)")

	if message.content.startswith(prefix+"leaderboard"):
		if not message.guild:
			await message.channel.send("You can't view leaderboard in a DM")
			return
		maxx = 3
		if re.match("\\"+prefix+"leaderboard ([0-9]+)", message.content.strip()):
			maxx = int(re.match("\\"+prefix+"leaderboard ([0-9]+)", message.content.strip()).group(1))
			if maxx > 15 or maxx < 3:
				await message.reply("Please enter a number between 3 and 15.", mention_author=False)
				return

		points = json.loads(open("points.json", "r").read())
		points = {k: v for k, v in sorted(points.items(), key=lambda item: item[1], reverse=True)}
		numusers = 0
		result = f"The points leaderboard for **{message.guild.name}** (top {maxx})\n"
		memberlist = set()
		for member in message.guild.members:
			memberlist.add(str(member.id))
		whatplace = {
			1: ":first_place: ",
			2: ":second_place: ",
			3: ":third_place: ",
		}
		for k in points:
			if str(k) in memberlist:
				numusers += 1
				if numusers > maxx:
					break

				member = message.guild.get_member(int(k))
				if numusers > 3:
					emoji = ":medal: "
				else:
					emoji = whatplace[numusers]
				result += (emoji+" **"+str(member.display_name)+"** ("+str(points[k])+"pt)\n")
		await message.channel.send(result)	

	if message.content.startswith(prefix+"stats"):
		await message.channel.send("Terribly sorry--we (the dev team) are temporarily closing the stats command as it is interfering with the deployment of scibowlbot's website, which is crucial for keeping the bot online 24/7. Thanks for your understanding.")
		"""msgToEdit = await message.channel.send("Generating statistics--please wait.")
		memberlist = set()
		for member in message.guild.members:
			memberlist.add(str(member.id))
		points = json.loads(open("points.json", "r").read())
		values = []
		for k in points:
			if str(k) in memberlist:
				values.append(points.get(k))

		plt.xlabel('Number of points')
		plt.ylabel('Number of users')
		plt.hist(values)
		plt.savefig("tempstats.png")
		await message.channel.send(f"The statistics for **{message.guild.name}**\n", file=discord.File(open("tempstats.png", "rb"), 'stats.png'))
		await msgToEdit.delete()
		os.remove("tempstats.png")		
		plt.clf()"""

	if message.content.strip() == prefix+"dev_servers":
		await message.channel.send("I am currently in "+str(len(client.guilds))+" servers!")

	if message.content.strip() == prefix+"dev_clear":
		if message.channel.id in hasQuestion:
			hasQuestion.remove(message.channel.id)
		await message.reply("Done!", mention_author=False)

	elif "<@!"+str(client.user.id)+">" in message.content:
		await message.channel.send("Hi there! I'm active and ready to serve up questions. For help, type "+prefix+"help")

"""@bot.slash(name="points", description="See someone's point's!")
async def points(ctx, target: discord.Member = None):
	if target and target != discord.Member:
		return
	if not target:
		target = ctx.author
	await ctx.send(content=f"**{str(target.display_name)}**, you have **{str(getpoints(str(target.id)))}** point(s)")"""


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
