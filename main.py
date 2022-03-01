import discord
from discord_components import DiscordComponents, Button, ActionRow, Select, SelectOption
import os
import asyncio
import readtime
import requests
import re
import json
import random
#import pyrebase
import difflib
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

def attempt_do_not_accept(accepted_answer):
	a = accepted_answer
	try:
		a=a.split('DO NOT ACCEPT: ',1)[0]
	except:
		a=a
	return a
def mc_mistaken_for_short(accepted_answer):
	also_accepted_answer = ""
	if "W)" in accepted_answer:
		also_accepted_answer = "W"
	if "X)" in accepted_answer:
		also_accepted_answer = "X"
	if "Y)" in accepted_answer:
		also_accepted_answer = "Y"
	if "Z)" in accepted_answer:
		also_accepted_answer = "Z"
	return also_accepted_answer

	
def mc_mistaken_for_short_2(accepted_answer):
	also_accepted_answer_2 = ""
	if "W)" in accepted_answer:
		also_accepted_answer_2 = accepted_answer.split("W) ")
	if "X)" in accepted_answer:
		also_accepted_answer_2 = accepted_answer.split("X) ")
	if "Y)" in accepted_answer:
		also_accepted_answer_2 = accepted_answer.split("Y) ")
	if "Z)" in accepted_answer:
		also_accepted_answer_2 = accepted_answer.split("Z) ")
	return also_accepted_answer_2
	
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
	subject = re.match("\\"+prefix+"Q (PHY|GEN|ENERGY|EAS|ES|CHEM|BIO|ASTRO|MATH|CS|ALL|WEIRD|CRAZY)", message.content.upper())
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
		]
	}
	if subject:
		isweird = subject.group(1) == "WEIRD"
		iscrazy = subject.group(1) == "CRAZY"
		

		# 	message.channel.send("scibowlbot is currently rate-limited by Discord for some reason. In other words, scibowlbot is down. Thanks for being patient.")
		# return

		if message.channel.id in hasQuestion:
			await message.reply(f"**There already is another question in this channel.**", mention_author=False)
			return
		hasQuestion.add(message.channel.id)
		if isweird:
			question_json = random.choice(json.loads(open("probs.json", "r").read()))
		elif iscrazy:
			question_json = random.choice(json.loads(open("crazy.json", "r").read()))
		else:
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
		else:
			correct_answer = question_json["question"]["tossup_answer"].upper()
			answer_accept_bypass = re.sub("(\(.*\))", "", question_json["question"]["tossup_answer"].upper()).strip().replace("  ", " ")
			try:
				correct_answer = question_json["question"]["tossup_answer"].upper()
				accepted_answer = question_json["question"]["tossup_answer"].upper().split('(ACCEPT: ',1)[1]
				accepted_answer = accepted_answer.split(')', 1)[0]
				accepted_answer = attempt_do_not_accept(accepted_answer)
				accepted_answer_2 = mc_mistaken_for_short(accepted_answer)
				accepted_answer_3 = mc_mistaken_for_short_2(accepted_answer)
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
				type_time = len(accepted_answer)/100
				#time.sleep(2)
				await waitfor.send("It's your turn to answer! You have 10 seconds plus an estimated and type time.")
				try: 
					user_answer = await client.wait_for(
						"message",
						timeout=10+type_time,
						check=validate
					)
			#t = 11
			#e = 0
			#global t
			#while e == 0:
			#if t > 3:
				#t -= 1
				#time.sleep(1)
			#else:
				#await message.channel.send("Three seconds")
				#break
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
			u_answer = user_ans.strip()[3:].upper()
			test_cases = [correct_answer, answer_accept_bypass, accepted_answer, """accepted_answer_2, accepted_answer_3"""]
			algorithm_correct = False
			accuracy = [compare(case, u_answer) for case in test_cases]
			for percent in accuracy:
				if 75 <= percent <= 100 and question_json["question"]["tossup_format"] != "Multiple Choice":
					algorithm_correct = True
					break
			if u_answer in test_cases and isweird:
				changepoints(responderid, 1)
				await message.reply(f"Correct **{responder}** You now have **{getpoints(responderid)}** (+1) points (This is a *weird* question, so you get a point.)", mention_author=False)
			elif u_answer in test_cases and iscrazy:
				changepoints(responderid, 0)
				await message.reply(f"Correct **{responder}** You now have **{getpoints(responderid)}** (+0) points (This is a *crazy* question, so you get no points, you may get some kicks though?)", mention_author=False)
			elif u_answer in test_cases:
				changepoints(responderid,  2)
				pointtest = getpoints(responderid)
				await message.reply(f"Correct **{responder}** You now have **{getpoints(responderid)}** (+2) points", mention_author=False)
				if (not mc):
					await user_answer.add_reaction(random.choice(yay_reactions))
				else:
					await mcbuttons.add_reaction(random.choice(yay_reactions))
			elif algorithm_correct:
				hasQuestion.remove(message.channel.id)
				changepoints(responderid, 1)
				msg_id = "_ov_"+str(user_answer.channel.id)+str(user_answer.author.id)+str(random.randint(1, 100))
				override_close_enough = await message.reply(
					f"You may be correct **{responder}**. Our algorithm marked it was \"close enough.\" (Your answer got a score of **{percent}**) The answer is `{correct_answer}`. You now have **{getpoints(responderid)}** (+1) points", mention_author=False, 
					components = [
						Button(
							label = "Override, I was incorrect", 
							custom_id=msg_id, 
							style=1
						)
					]
				)
				def check_override(msg):
					if str(msg.author.display_name) == responder and str(msg.custom_id) == msg_id:
						return True
					asyncio.create_task(msg.send(f"You never answered this question. \n\n DEBUG DATA:\n Expected responder: `{str(msg.author.display_name)}` Got: `{responder}`\nExpected ID: `{msg.custom_id}` Got: {msg_id}"))
					return False
				my_emoji = random.choice(yay_reactions)
				if (not mc):
					await user_answer.add_reaction(my_emoji)
				else:
					await mcbuttons.add_reaction(my_emoji)
				try:
					waiting_honest = await client.wait_for("button_click", timeout=30, check=check_override)
				except (asyncio.TimeoutError):
					await override_close_enough.edit(
						content=f"You may be correct **{responder}**. Our algorithm marked it was \"close enough.\" (Your answer got a score of **{percent}**) The answer is `{correct_answer}`. You now have **{getpoints(responderid)}** (+1) points", mention_author=False, 
						components = [
							Button(
								label = "Override, I was incorrect", 
								custom_id=msg_id, 
								style=1,
								disabled=True
							)
						]
					)
				else:
					await waiting_honest.send("Thanks for being honest :slight_smile: You lost two points")
					changepoints(responderid, -2)
					await override_close_enough.edit(
						content=f"Let's give **{responder}** a round of applause :clap: for being honest! Our algorithm thought their answer was \"close enough,\" but **{responder}** was honest and overrode it. The answer is `{correct_answer}`. **{responder}** now has **{getpoints(responderid)}** (-1) points", mention_author=False, 
						components = [
							Button(
								label = "Override, I was incorrect", 
								custom_id=msg_id, 
								style=3,
								disabled=True
							)
						]
					)
					await user_answer.remove_reaction(my_emoji, client.user)
					await user_answer.add_reaction(random.choice(aw_reactions))

				
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
		helptxt = f"""
**Scibowlbot**
*a bot to help run science bowl rounds*
I have been serving quesitons for **{t_string(time.time() - 1638489600)}** (Since <t:1638489600>)

**How to obtain and answer a question**
Scibowlbot is a bot built by AndrewC10#6072 et al. as an alternative to womogenes's scibowlbot (https://github.com/womogenes/ScibowlBot). To start a round, simply type `"""+prefix+"""q SUBJECT`, with Subject being one of the below:

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
:interrobang: WEIRD (Our own custom questions that are related)
:exploding_head: CRAZY (Our own questions that are unrelated)

After you type in the command, a question and a big "Answer" button will be generated. You will be given 5 seconds plus an estimated read time to click the button. First person to click the button gets to answer the question. To answer, simply type `"""+prefix+"""a ANSWER`.(please only type the letter for multiple choice). You will be given 10 seconds to do so.

**Other features**
To view the server leaderboard, type `"""+prefix+"""leaderboard`.
To view your profile you have, type `"""+prefix+"""profile`.
To view someone else's profiles type `"""+prefix+"""profile @MENTION` or `"""+prefix+"""profile USER_ID`.
To change your profile, type `"""+prefix+"""change_profile`
To view the server statistics, type `"""+prefix+"""serverstats`.
To gift someone points, type `"""+prefix+"""gift AMOUNT USER` With user either being a ping, or the user's id.
==split==
**FAQ's**
Q: How can I invite scibowlbot?
A: Under <@!"""+str(client.user.id)+""">'s profile (You can get there by clicking that mention) there is a big "Add to Server" button under the bot's name. If that somehow doesn't show up, then use this link: <https://tinyurl.com/sbbv2invite>.

Q: What can I do when the bot is down?
A: You can DM or ping one of the devs, preferabaly `AndrewC10#6072`

Q: I have a question, how can I ask it?
A: You can DM one of the devs, but it is prefered that you send us an email at devnothackercorporations@gmail.com

Q: What if the bot says "There already is another question in this channel." when there clearly is not?
A: Run the `"""+prefix+"""dev_clear` command and everything should be fixed.

**This bot is open source!**
This bot is open source! Help us improve it here: <https://github.com/DevNotHackerCorporations/scibowlbot> You are allowed to use this code under the conditions of the license: <https://devnothackercorporations.github.io/scibowlbot/LICENSE.txt>
		"""
		await message.add_reaction("\N{White Heavy Check Mark}")
		await message.author.send(helptxt.split("==split==")[0])
		await message.author.send(helptxt.split("==split==")[1])


	if re.match("\\"+prefix+"profile <@!([0-9]+)>", message.content.strip()) or message.content.strip() == prefix+"profile" or re.match("\\"+prefix+"profile ([0-9]+)", message.content.strip()):
		if re.match("\\"+prefix+"profile <@!([0-9]+)>", message.content.strip()):
			id = int(re.match("\\"+prefix+"profile <@!([0-9]+)>", message.content.strip()).group(1))
		elif message.content.strip() == prefix+"profile":
			id = int(message.author.id)
		else:
			id = int(re.match("\\"+prefix+"profile ([0-9]+)", message.content.strip()).group(1))
		try:
			member = await message.guild.fetch_member(id)
		except:
			await message.reply("No user with that id has been found in this server.")
			return

		embed = discord.Embed(title=f"{member.display_name}'s profile", description="What they are good at, their points, etc.", color=0xFF5733)
		embed.set_author(name=member.display_name, url="", icon_url=member.avatar_url)
		embed.set_thumbnail(url=member.avatar_url)
		embed.add_field(name=f"{member}'s point count", value=f"**{str(member.display_name)}** has **{str(getpoints(str(member.id)))}** point(s)", inline=False)
		good_at = ", ".join(list(map(lambda x: apprev[x.upper()][0].lower(), getprofile(member.id)[0])))
		if not good_at:
			good_at = "*Nothing*"
		bad_at = ", ".join(list(map(lambda x: apprev[x.upper()][0].lower(), getprofile(member.id)[1])))
		if not bad_at:
			bad_at = "*Nothing*"
		embed.add_field(name=f"What {member} is is good at", value=f"{str(member.display_name)} is good at {good_at}", inline=False)
		embed.add_field(name=f"What {member} is is not so good at", value=f"{str(member.display_name)} is not so good at {bad_at}", inline=False)
		await message.channel.send(embed=embed)

	if message.content.startswith(prefix+"leaderboard"):
		if not message.guild:
			await message.channel.send("You can't view leaderboard in a DM")
			return
		maxx = 3
		if re.match("\\"+prefix+"leaderboard ([0-9]+)", message.content.strip()):
			maxx = int(re.match("\\"+prefix+"leaderboard ([0-9]+)", message.content.strip()).group(1))
			if maxx > 30 or maxx < 3:
				await message.reply("Please enter a number between 3 and 30.", mention_author=False)
				return

		points = json.loads(open("points.json", "r").read()).get("points")
		points = {k: v for k, v in sorted(points.items(), key=lambda item: item[1], reverse=True)}
		numusers = 0
		# Setting up embed
		embed = discord.Embed(title=f"The points leaderboard for **{message.guild.name}**", description=f"Top {maxx} people", color=0xFF5733)
		embed.set_author(name=message.author.display_name, url="", icon_url=message.author.avatar_url)
		embed.set_thumbnail(url=message.guild.icon_url)
		# end set up
		memberlist = set()
		for member in message.guild.members:
			memberlist.add(str(member.id))
		whatplace = {
			1: ":first_place: ",
			2: ":second_place: ",
			3: ":third_place: ",
		}
		prev = float("-inf")
		result = ""
		my_id = int(message.author.id)
		place = f"You're not among the top {maxx} people."
		
		for k in points:
			if str(k) in memberlist:
				if points[k] != prev:
					numusers += 1
				prev = points[k]
				if numusers > maxx:
					break
				if my_id == int(k):
					place = f"You occupy place #{numusers}!"
				member = message.guild.get_member(int(k))
				if numusers > 3:
					emoji = ":medal: "
				else:
					emoji = whatplace[numusers]
				result += (emoji+" **"+str(member.display_name)+"** ("+str(points[k])+"pt)\n")
				if len(result) >= 800:
					embed.add_field(name=f"The people and their scores", value=result, inline=False)
					await message.channel.send(embed=embed)	
					embed = discord.Embed(title=f"Overflow", description="We went over 1024 chars so we had to split it into two messages", color=0xFF5733)
					result = ""

		embed.add_field(name=f"The people and their scores", value=result, inline=False)
		embed.add_field(name=f"What place am I?", value=place, inline=False)
		await message.channel.send(embed=embed)	
					


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
		
	if message.content.startswith(prefix+"serverstats"):
		memberlist = set()
		for member in message.guild.members:
			memberlist.add(str(member.id))
		points = json.loads(open("points.json", "r").read()).get("points")
		average = 0
		num_pep = 0
		for k in points:
			if str(k) in memberlist:
				average += points[k]
				num_pep += 1 
		if num_pep == 0:
			num_pep = 1
		average = round(average / num_pep, 2)
		# Setting up embed
		embed = discord.Embed(title=f"Server stats of **{message.guild.name}**", color=0xFF5733)
		embed.set_author(name=message.author.display_name, url="", icon_url=message.author.avatar_url)
		embed.set_thumbnail(url=message.guild.icon_url)
		embed.add_field(name=f"Average amount of points", value=f"The average amount of points for {message.guild.name} is {average} points.", inline=False)
		await message.channel.send(embed=embed)
		# end set up

		
	if message.content.strip() == prefix+"dev_servers":
		await message.channel.send("I am currently in "+str(len(client.guilds))+" servers!")

	if message.content.strip() == prefix+"dev_clear":
		if message.channel.id in hasQuestion:
			hasQuestion.remove(message.channel.id)
		await message.reply("Done!", mention_author=False)

	if message.content.strip() == prefix+"change_profile":
		good_at, bad_at, bio = getprofile(int(message.author.id))
		select_id = str(message.channel.id)+str(message.author.id)+str(random.randint(1, 100))
		orig_msg = await message.channel.send(f"**{str(message.author.display_name)}**, change your profile here!", components = [
			Select(
				placeholder="The subjects you are good at!",
				max_values=10, 
				id = select_id + "1",
				options=[
					SelectOption(label="Physics", value="phy", default=("phy" in good_at), emoji="\N{Red Apple}"),
					SelectOption(label="General Science", value="gen", default=("" in good_at), emoji="\N{Test Tube}"),
					SelectOption(label="Energy", value="energy", default=("energy" in good_at), emoji="\N{High Voltage Sign}"),
					SelectOption(label="Earth and Space", value="eas", default=("eas" in good_at), emoji="\N{Night with Stars}"),
					SelectOption(label="Chemistry", value="chem", default=("chem" in good_at), emoji="\N{Atom Symbol}"),
					SelectOption(label="Biology", value="bio", default=("bio" in good_at), emoji="\N{DNA Double Helix}"),
					SelectOption(label="Astronomy", value="astro", default=("astro" in good_at), emoji="\N{Ringed Planet}"),
					SelectOption(label="Math", value="math", default=("math" in good_at), emoji="\N{Input Symbol for Numbers}"),
					SelectOption(label="Earth Science", value="es", default=("es" in good_at), emoji="\N{Earth Globe Americas}"),
					SelectOption(label="Computer Science", value="cs",default=("cs" in good_at), emoji="\N{Personal Computer}")
				]
			),
			Select(
				placeholder="The subjects you are bad at",
				max_values=10, 
				id = select_id + "2",
				options=[
					SelectOption(label="Physics", value="phy", default=("phy" in bad_at), emoji="\N{Red Apple}"),
					SelectOption(label="General Science", value="gen", default=("" in bad_at), emoji="\N{Test Tube}"),
					SelectOption(label="Energy", value="energy", default=("energy" in bad_at), emoji="\N{High Voltage Sign}"),
					SelectOption(label="Earth and Space", value="eas", default=("eas" in bad_at), emoji="\N{Night with Stars}"),
					SelectOption(label="Chemistry", value="chem", default=("chem" in bad_at), emoji="\N{Atom Symbol}"),
					SelectOption(label="Biology", value="bio", default=("bio" in bad_at), emoji="\N{DNA Double Helix}"),
					SelectOption(label="Astronomy", value="astro", default=("astro" in bad_at), emoji="\N{Ringed Planet}"),
					SelectOption(label="Math", value="math", default=("math" in bad_at), emoji="\N{Input Symbol for Numbers}"),
					SelectOption(label="Earth Science", value="es", default=("es" in bad_at), emoji="\N{Earth Globe Americas}"),
					SelectOption(label="Computer Science", value="cs",default=("cs" in bad_at), emoji="\N{Personal Computer}")
				]
			),
		])
		select_author = int(message.author.id)
		def profile_check(interaction):
			if interaction.custom_id[:-1] == select_id and select_author == int(interaction.author.id):
				return True
			asyncio.create_task(interaction.send("This isn't your profile"))
			return False

		while True:
			try:
				select_op = await client.wait_for("select_option", timeout=15, check=profile_check)
			except asyncio.TimeoutError:
				await orig_msg.edit(content=f"**{str(message.author.display_name)}**, change your profile here!", components = [
					Select(
						placeholder="The subjects you are good at!",
						max_values=10, 
						disabled=True,
						id = "niu1",
						options=[
							SelectOption(label="Physics", value="phy", default=("phy" in good_at), emoji="\N{Red Apple}"),
							SelectOption(label="General Science", value="gen", default=("" in good_at), emoji="\N{Test Tube}"),
							SelectOption(label="Energy", value="energy", default=("energy" in good_at), emoji="\N{High Voltage Sign}"),
							SelectOption(label="Earth and Space", value="eas", default=("eas" in good_at), emoji="\N{Night with Stars}"),
							SelectOption(label="Chemistry", value="chem", default=("chem" in good_at), emoji="\N{Atom Symbol}"),
							SelectOption(label="Biology", value="bio", default=("bio" in good_at), emoji="\N{DNA Double Helix}"),
							SelectOption(label="Astronomy", value="astro", default=("astro" in good_at), emoji="\N{Ringed Planet}"),
							SelectOption(label="Math", value="math", default=("math" in good_at), emoji="\N{Input Symbol for Numbers}"),
							SelectOption(label="Earth Science", value="es", default=("es" in good_at), emoji="\N{Earth Globe Americas}"),
							SelectOption(label="Computer Science", value="cs",default=("cs" in good_at), emoji="\N{Personal Computer}")
						]
					),
					Select(
						placeholder="The subjects you are bad at",
						max_values=10, 
						id = "niu2",
						disabled=True,
						options=[
							SelectOption(label="Physics", value="phy", default=("phy" in bad_at), emoji="\N{Red Apple}"),
							SelectOption(label="General Science", value="gen", default=("" in bad_at), emoji="\N{Test Tube}"),
							SelectOption(label="Energy", value="energy", default=("energy" in bad_at), emoji="\N{High Voltage Sign}"),
							SelectOption(label="Earth and Space", value="eas", default=("eas" in bad_at), emoji="\N{Night with Stars}"),
							SelectOption(label="Chemistry", value="chem", default=("chem" in bad_at), emoji="\N{Atom Symbol}"),
							SelectOption(label="Biology", value="bio", default=("bio" in bad_at), emoji="\N{DNA Double Helix}"),
							SelectOption(label="Astronomy", value="astro", default=("astro" in bad_at), emoji="\N{Ringed Planet}"),
							SelectOption(label="Math", value="math", default=("math" in bad_at), emoji="\N{Input Symbol for Numbers}"),
							SelectOption(label="Earth Science", value="es", default=("es" in bad_at), emoji="\N{Earth Globe Americas}"),
							SelectOption(label="Computer Science", value="cs",default=("cs" in bad_at), emoji="\N{Personal Computer}")
						]
					),
				])
				break
			inter_number = select_op.custom_id[-1]
			if inter_number == "1":
				changeprofile(select_author, good=select_op.values)
			if inter_number == "2":
				changeprofile(select_author, bad=select_op.values)
			await select_op.send("Updated your profile")

	elif re.match(".gift ([0-9]+) <@!([0-9]+)>", message.content) or re.match(".gift ([0-9]+) ([0-9]+)", message.content):
		if re.match(".gift ([0-9]+) <@!([0-9]+)>", message.content):
			amount = int(re.match(".gift ([0-9]+) <@!([0-9]+)>", message.content).group(1))
			to = re.match(".gift ([0-9]+) <@!([0-9]+)>", message.content).group(2) 
		else:
			amount = int(re.match(".gift ([0-9]+) ([0-9]+)", message.content).group(1))
			to = re.match(".gift ([0-9]+) ([0-9]+)", message.content).group(2) 

		# Setup
		embed = discord.Embed(title=f"Some points were just gifted!", description=f"{message.author.display_name} just tried to gift {amount} points.", color=0xFF5733)
		embed.set_author(name=message.author.display_name, url="", icon_url=message.author.avatar_url)
		embed.set_thumbnail(url=message.author.avatar_url)
		# calculations
		if not message.guild:
			embed.add_field(name="Error", value="You can't gift points outside of a server.")
			await message.channel.send(embed=embed)
			return
		user = str(message.author.id)
		user_money = int(getpoints(user))
		
		to_user = await message.guild.fetch_member(int(to))
		embed.set_thumbnail(url=to_user.avatar_url)
		#if amount < 0:
		#	embed.add_field(name="Error", value="It's not like your going to gain money from this...")
		#	return
		if amount > user_money:
			embed.add_field(name="Error", value=f"This goes over your current balance of {user_money}")
		elif to_user.bot:
			embed.add_field(name="Error", value="You can't give points to a bot...")
		else:
			changepoints(user, -1*amount)
			changepoints(to, amount)
			embed.add_field(name=f"{message.author.display_name} now has", value=f"{getpoints(user)} points. (-{amount})")
			embed.add_field(name=f"{to_user.display_name} now has", value=f"{getpoints(to)} points. (+{amount})")
			await to_user.send(f"**{message.author.display_name}** just sent you **{amount}** coins!") 
		await message.reply(embed=embed)

	
	elif "<@!"+str(client.user.id)+">" in message.content:
		await message.channel.send("Hi there! I'm active and ready to serve up questions. For help, type "+prefix+"help")

@client.event
async def on_button_click(interaction):
	if interaction.custom_id[:3] == "niu":
		await interaction.respond(content="This button is not in use anymore.")
		return

"""@bot.slash(name="points", description="See someone's point's!")
async def points(ctx, target: discord.Member = None):
	if target and target != discord.Member:
		return
	if not target:
		target = ctx.author
	await ctx.send(content=f"**{str(target.display_name)}**, you have **{str(getpoints(str(target.id)))}** point(s)")"""

# Compares two strings and returns a percentage based on how similar they are. 
# The algorithm is not perfect, but it should work
def compare(str1: str, str2: str) -> float:
	"""
	str_one_letters = {}
	for letter in str1:
		str_one_letters[letter] = str_one_letters.get(letter, 0) + 1
	for letter in str2:
		str_one_letters[letter] = abs(str_one_letters.get(letter, 0) - 1)
	return round((1-((sum(str_one_letters.values()))/len(str1)))*100, 2)
	"""
	return difflib.SequenceMatcher(None, str1, str2).ratio()*100

def t_string(seconds: int) -> str:
	day = seconds // (24 * 3600)
	seconds = seconds % (24 * 3600)
	hour = seconds // 3600
	seconds %= 3600
	minutes = seconds // 60
	seconds %= 60
	seconds = seconds
	return ("%d days, %d hours, %d minutes, and %d seconds!" % (day, hour, minutes, seconds))

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
