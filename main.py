import discord
from discord_components import DiscordComponents, Button
import os
import asyncio
import readtime
import requests
import re
import json

# This gets rid of the flask messages
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
# End


intents = discord.Intents.default()
intents.members = True

client = discord.Client(intents=intents)
DiscordComponents(client)
prefix = "-"
hasQuestion = set()

def changepoints(user, point):
	points = json.loads(open("points.json", "r").read())
	points[user] = points.get(user, 0) + point
	open("points.json", "w").write(json.dumps(points))
def getpoints(user):
	points = json.loads(open("points.json", "r").read())
	return points.get(user, 0)

@client.event
async def on_ready():
	print('Logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
	if message.author == client.user:
		return
	

	def validate(msg): 
		if str(msg.author) == responder and prefix+"a" in msg.content:
			return True
		return False

	def validatebtn(msg):
		return int(msg.custom_id) == int(message.channel.id)
	subject = re.match(prefix+"Q (PHY|GEN|ENERGY|EAS|ES|CHEM|BIO|ASTRO|MATH|CS|ALL)", message.content.upper())
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
		if message.channel.id in hasQuestion:
			await message.reply(f"**There already is another question in this channel.**", mention_author=False)
			return
		hasQuestion.add(message.channel.id)
		question_json = requests.post("https://scibowldb.com/api/questions/random", json={
			"categories":apprev[subject.group(1)]
		}).json()
		question_header = "**"+question_json["question"]["category"]+" "+question_json["question"]["tossup_format"]+" (Source: "+question_json["question"]["source"]+")\n**"
		question = question_header+question_json["question"]["tossup_question"]
		if question_json["question"]["tossup_format"] == "Multiple Choice":
			correct_answer = (question_json["question"]["tossup_answer"])[0].upper()
		else:
			correct_answer = question_json["question"]["tossup_answer"].upper()


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
			responder = str(waitfor.author)
			responderid = str(waitfor.author.id)
			await waitfor.send("It's your turn to answer! You have 10 seconds.")
			await sentmsg.edit(content=question, components = [
				Button(label = f"Answered by {responder}!", disabled=True)
			])
			try: 
				user_answer = await client.wait_for(
        			"message",
					timeout=10,
					check=validate
    			)
			except (asyncio.TimeoutError):
				changepoints(responderid,  -1)
				await message.reply(f"Incorrect **{responder}**, you ran out of time. The answer was `{correct_answer}`. You now have **{getpoints(responderid)}** (-1) points ", mention_author=False)
				hasQuestion.remove(message.channel.id)
				return


			if user_answer.content.strip()[3:].upper() == correct_answer:
				changepoints(responderid,  2)
				await message.reply(f"Correct **{user_answer.author}** You now have **{getpoints(responderid)}** (+2) points", mention_author=False)
			else:
				changepoints(responderid,  -1)
				await message.reply(f"Incorrect **{responder}**, the answer was `{correct_answer}`. You now have **{getpoints(responderid)}** (-1) points", mention_author=False)
			hasQuestion.remove(message.channel.id)			

		else:
			await message.reply("The answer was `"+correct_answer+"`", mention_author=False)			
			await sentmsg.edit(content=question, components = [
				Button(label = "Time's up. No one answered", disabled=True)
			])
			hasQuestion.remove(message.channel.id)

	if message.content.strip() == prefix+"help":
		helptxt = """
**SciBowlBot**
*a bot to help run science bowl rounds*

Scibowlbot is a bot built by AndrewC10#6072 et al. as an alternative to womogenes's scibowlbot (https://github.com/womogenes/ScibowlBot). To start a round, simply type `-q SUBJECT`, with Subject being one of the below:
```
PHY
GEN
ENERGY
EAS
CHEM
BIO
ASTRO
MATH
CS
ES
ALL
```
After you type in the command, a question and a big "Answer" button will be generated. You will be given 5 seconds plus an estimated read time to click the button. First person to click the button gets to answer the question. To answer, simply type `-a ANSWER` (please only type the letter for multiple choice). You will be given 10 seconds to do so.
		"""
		await message.channel.send(helptxt)

	if message.content.strip() == prefix+"points":
		await message.channel.send(f"**{str(message.author)}**, you have **{str(getpoints(str(message.author.id)))}** point(s)")

	if message.content.strip() == prefix+"leaderboard":
		points = json.loads(open("points.json", "r").read())
		points = {k: v for k, v in sorted(points.items(), key=lambda item: item[1], reverse=True)}
		numusers = 0
		result = f"The points leaderboard for **{message.guild.name}**\n"
		memberlist = set()
		for member in message.guild.members:
			memberlist.add(str(member.id))
		whatplace = {1:":first_place: ",2:":second_place: ",3:":third_place: "}
		for k in points:
			if str(k) in memberlist:
				numusers += 1
				if numusers > 3:
					break

				member = message.guild.get_member(int(k))
				result += (whatplace[numusers]+" **"+(member.name+"#"+member.discriminator)+"** ("+str(points[k])+"pt)\n")
		await message.channel.send(result)	




from threading import Thread
from flask import Flask

app = Flask("app")
@app.route("/")
def home():
    return "Hello World"

def start_flask():
	app.run(host='0.0.0.0', port=8080)

Thread(target=start_flask).start()
client.run(os.getenv("TOKEN"))