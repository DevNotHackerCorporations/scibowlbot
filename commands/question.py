import difflib
import readtime
import requests
import asyncio
import json
import re
import discord
import random
from discord.ext import commands
from discord_components import DiscordComponents, Button, ActionRow



client = commands.Bot(command_prefix=".")
DiscordComponents(client)

valid = ["PHY", "GEN", "ENERGY", "EAS", "CHEM", "BIO", "ASTRO", "MATH", "CS", "ES", "WEIRD", "CRAZY", "ALL"]

async def setup(bot):
	bot.add_command(_q)
	bot.add_command(_a)

# CONSTANT VARIABLES
yay_reactions = [
	"\N{Thumbs Up Sign}", 
	"\N{White Heavy Check Mark}", 
	"\N{Brain}", 
	"\N{Hundred Points Symbol}", 
	"\N{Direct Hit}", 
	"\N{Clapping Hands Sign}", 
	"\N{Trophy}", 
	"\N{Slightly Smiling Face}", 
	"\N{Party popper}"
]
aw_reactions = [
	"\N{Crying Face}", 
	"\N{White Question Mark Ornament}", 
	"\N{Slightly Frowning Face}", 
	"\N{Worried Face}", 
	"\N{Thumbs Down Sign}", 
	"\N{Loudly Crying Face}", 
	"\N{Cross Mark}", 
	"\N{Face with No Good Gesture}"
]

# UTILITY FUNCTIONS

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

def color(correct, mine, current):
	if current == correct:
		return 3
	if mine == -1:
		return 4
	if current == mine:
		return 4
	return 1

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
# END



@client.command(name="q")
async def _q(message, subject):
	"""
	Generate a new scibowl question!

	Valid subjects include:
	GEN
	ENERGY
	EAS
	CHEM
	BIO
	ASTRO
	MATH
	CS
	ES
	WEIRD
	CRAZY
	ALL 
	"""
	subject = subject.upper()

	if subject not in valid:
		embed = discord.Embed(title=f":warning: Error :warning:", description="While processing this request, we ran into an error", color=0xFFFF00)
		embed.set_author(name=message.author.display_name, url="", icon_url=message.author.avatar)
		embed.add_field(name=f'"{subject}" is not a valid subject', value="We only support the following subjects```"+"\n".join(valid)+"```")
		await message.channel.send(embed=embed)
		return
	
	# FUNCTIONS
	def validate(msg): 
		if str(msg.author.display_name) == responder and ".a" not in msg.content:
			asyncio.create_task(msg.reply("Once again, to answer write `.a ANSWER` with `ANSWER` being your answer."))
		if str(msg.author.display_name) == responder and ".a" in msg.content:
			return True
		return False

	def validatebtn(msg):
		return str(msg.custom_id) == str(message.channel.id)


	def validate_mc(msg):
		if msg.custom_id[:3] == "niu":
			asyncio.create_task(msg.send("This question already ended ¯\_(ツ)_/¯"))
		if str(msg.author.display_name) == responder and re.match("mc_(w|x|y|z)([0-9]+)",str(msg.custom_id)):
			return True
		asyncio.create_task(msg.send("This question is not yours!"))
		return False

	def check_override(msg):
		if str(msg.author.display_name) == responder and str(msg.custom_id) == msg_id:
			return True
		asyncio.create_task(msg.send(f"You never answered this question. \n\n DEBUG DATA:\n Expected responder: `{str(msg.author.display_name)}` Got: `{responder}`\nExpected ID: `{msg.custom_id}` Got: {msg_id}"))
		return False

	# END FUNCTIONS

	isweird = subject == "WEIRD"
	iscrazy = subject == "CRAZY"
	

	if message.channel.id in message.bot.hasQuestion:
		await message.reply(f"**There already is another question in this channel.**", mention_author=False)
		return
	message.bot.hasQuestion.add(message.channel.id)
	if isweird:
		question_json = random.choice(json.loads(open("probs.json", "r").read()))
	elif iscrazy:
		question_json = random.choice(json.loads(open("crazy.json", "r").read()))
	else:
		question_json = requests.post("https://scibowldb.com/api/questions/random", json={
			"categories":message.bot.apprev[subject]
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
		waitfor = await message.bot.wait_for(
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
			await waitfor.send("It's your turn to answer! You have 10 seconds plus an estimated and type time.")
			try: 
				user_answer = await message.bot.wait_for(
					"message",
					timeout=10+type_time,
					check=validate
				)
			except (asyncio.TimeoutError):
				message.bot.changepoints(responderid,  -1)
				await message.reply(f"Incorrect **{responder}**, you ran out of time. The answer was `{correct_answer}`. You now have **{message.bot.getpoints(responderid)}** (-1) points ", mention_author=False)
				message.bot.hasQuestion.remove(message.channel.id)
				return
			user_ans = user_answer.content
		else:

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
				mcButtonClick = await message.bot.wait_for(
					"button_click",
					timeout=6,
					check=validate_mc
				)
			except (asyncio.TimeoutError):
				message.bot.changepoints(responderid,  -1)
				await message.reply(f"Incorrect **{responder}**, you ran out of time. The answer was `{correct_answer}`. You now have **{message.bot.getpoints(responderid)}** (-1) points ", mention_author=False)
				message.bot.hasQuestion.remove(message.channel.id)
				await mcbuttons.add_reaction(random.choice(aw_reactions))
				await mcbuttons.edit("**"+responder+"** chose: **DID NOT CHOOSE**", components = ActionRow([
					Button(label = "W) "+answers[0], custom_id="niu1", style=color(correct_answer, -1, "W")),
					Button(label = "X) "+answers[1], custom_id="niu2", style=color(correct_answer, -1, "X")),
					Button(label = "Y) "+answers[2], custom_id="niu3", style=color(correct_answer, -1, "Y")),
					Button(label = "Z) "+answers[3], custom_id="niu4", style=color(correct_answer, -1, "Z"))
				]))
				return
			user_ans = ".a "+mcButtonClick.custom_id[3]
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
			message.bot.changepoints(responderid, 1)
			await message.reply(f"Correct **{responder}** You now have **{message.bot.getpoints(responderid)}** (+1) points (This is a *weird* question, so you get a point.)", mention_author=False)
		elif u_answer in test_cases and iscrazy:
			message.bot.changepoints(responderid, 0)
			await message.reply(f"Correct **{responder}** You now have **{message.bot.getpoints(responderid)}** (+0) points (This is a *crazy* question, so you get no points, you may get some kicks though?)", mention_author=False)
		elif u_answer in test_cases:
			message.bot.changepoints(responderid,  2)
			pointtest = message.bot.getpoints(responderid)
			await message.reply(f"Correct **{responder}** You now have **{message.bot.getpoints(responderid)}** (+2) points", mention_author=False)
			if (not mc):
				await user_answer.add_reaction(random.choice(yay_reactions))
			else:
				await mcbuttons.add_reaction(random.choice(yay_reactions))
		elif algorithm_correct:
			message.bot.hasQuestion.remove(message.channel.id)
			message.bot.changepoints(responderid, 1)
			msg_id = "_ov_"+str(user_answer.channel.id)+str(user_answer.author.id)+str(random.randint(1, 100))
			override_close_enough = await message.reply(
				f"You may be correct **{responder}**. Our algorithm marked it was \"close enough.\" (Your answer got a score of **{percent}**) The answer is `{correct_answer}`. You now have **{message.bot.getpoints(responderid)}** (+1) points", mention_author=False, 
				components = [
					Button(
						label = "Override, I was incorrect", 
						custom_id=msg_id, 
						style=1
					)
				]
			)
			my_emoji = random.choice(yay_reactions)
			if (not mc):
				await user_answer.add_reaction(my_emoji)
			else:
				await mcbuttons.add_reaction(my_emoji)
			try:
				waiting_honest = await message.bot.wait_for("button_click", timeout=30, check=check_override)
			except (asyncio.TimeoutError):
				await override_close_enough.edit(
					content=f"You may be correct **{responder}**. Our algorithm marked it was \"close enough.\" (Your answer got a score of **{percent}**) The answer is `{correct_answer}`. You now have **{message.bot.getpoints(responderid)}** (+1) points", mention_author=False, 
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
				message.bot.changepoints(responderid, -2)
				await override_close_enough.edit(
					content=f"Let's give **{responder}** a round of applause :clap: for being honest! Our algorithm thought their answer was \"close enough,\" but **{responder}** was honest and overrode it. The answer is `{correct_answer}`. **{responder}** now has **{message.bot.getpoints(responderid)}** (-1) points", mention_author=False, 
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
			message.bot.changepoints(responderid,  -1)
			await message.reply(f"Incorrect **{responder}**, the answer was `{correct_answer}`. You now have **{message.bot.getpoints(responderid)}** (-1) points", mention_author=False)
			if (not mc):
				await user_answer.add_reaction(random.choice(aw_reactions))
			else:
				await mcbuttons.add_reaction(random.choice(aw_reactions))
		message.bot.hasQuestion.remove(message.channel.id)			

	else:
		await message.reply("The answer was `"+correct_answer+"`", mention_author=False)			
		await sentmsg.edit(content=question, components = [
			Button(label = "Time's up. No one answered", disabled=True)
		])
		message.bot.hasQuestion.remove(message.channel.id)

@client.command(name="a")
async def _a(message, response):
	"""
	Answer a science bowl question.

	Can only be used with .q
	"""
	pass