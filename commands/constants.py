import discord
import json
import os

async def setup(client):
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

	client.emoj = {
		"phy": "🍎",
		"gen": "🧪",
		"energy": "⚡",
		"eas": "🌃",
		"chem": "⚛",
		"bio": "🧬",
		"astro": "🪐",
		"math": "🔢",
		"es": "🌎",
		"cs": "💻",
	}
	
	
	def changepoints(user, point):
		points = json.loads(open("points.json", "r").read())
		points["points"][user] = points.get("points").get(user, 0) + point
		open("points.json", "w").write(json.dumps(points))
		client.db.set(points)
	
	
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
		client.db.set(points)
	
	
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
	client.hasQuestion = set()
	
	#client.status_webhook = [discord.Webhook.from_url(os.getenv("WEBHOOKURL"), adapter=discord.RequestsWebhookAdapter()), discord.Webhook.from_url(os.getenv("SECONDARYWEBHOOK"), adapter=discord.RequestsWebhookAdapter())]
	#for webhook in client.status_webhook:
	#	webhook.send("Sbb starting up")