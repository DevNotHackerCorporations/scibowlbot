import discord
from discord.ext import commands
import json
import random
import string
from utils.menu import Menu


async def setup(bot):
    pass


def generate_id(char_list = string.ascii_uppercase + string.digits, length=5):
    return "".join([random.choice(char_list) for _ in range(length)])


def get_points(ctx, global_=False, returnDict=False):
    if not ctx.guild:
        return [ctx.bot.getpoints(str(ctx.author.id))]
    memberlist = {str(member.id) for member in ctx.guild.members}
    points = json.loads(open("points.json", "r").read()).get("points")
    people = [] if not returnDict else {}
    for k in points:
        if str(k) in memberlist or global_:
            if returnDict:
                people[str(k)] = points[k]
            else:
                people.append(points[k])
    return people


class Competition:
    def __init__(self, context):
        self.ctx = context
        self.creator = self.ctx.author
        self.participants = set()
        self.queue = []
        self.declined = []
        self.question = 1
        self.scoreboard = {}
        self.max_question = 23
        self.contest_id = generate_id()
        while self.contest_id in self.ctx.bot.comps.keys():
            self.contest_id = generate_id()
        self.ctx.bot.in_comp[self.creator.id] = self.contest_id
        self.ctx.bot.comps[self.contest_id] = self.creator.id

    def get_title(self):
        return f"Question {self.question}/{self.max_question}"

    async def after_question(self):
        self.question += 1

    async def send_question(self, interaction: discord.Interaction = None):
        if self.question > self.max_question:
            return await self.end()

        from commands.question2 import Question
        obj = Question(self.ctx, random.choice(self.ctx.bot.scibowl_subjects), self)
        await obj.run()

    async def purge(self):
        for person in self.queue:
            self.ctx.bot.in_comp.pop(person)
        for person in self.participants:
            self.ctx.bot.in_comp.pop(person)
        if self.creator.id in self.ctx.bot.in_comp:
            self.ctx.bot.in_comp.pop(self.creator.id)
        if self.contest_id in self.ctx.bot.comps:
            self.ctx.bot.comps.pop(self.contest_id)

    async def end(self):
        await self.purge()
        standingEmojis = {
            1: ":first_place: ",
            2: ":second_place: ",
            3: ":third_place: ",
        }
        embed = discord.Embed(
            title=f"The host has ended the contest!",
            description=f"Standings for Competition `{self.contest_id}`",
            color=0xFF5733)
        embed.set_author(name=self.ctx.author.display_name,
                         url="",
                         icon_url=self.ctx.author.avatar)

        embed.set_thumbnail(
            url=f"https://raw.githubusercontent.com/DevNotHackerCorporations/scibowlbot/main/website/trophy.png")

        body = commands.Paginator(prefix="",
                                  suffix="",
                                  max_size=1024 - 10 - len(embed.title) - len(embed.description),
                                  linesep="\n")

        self.scoreboard = {k: v for k, v in sorted(self.scoreboard.items(), reverse=True, key=lambda x: x[1][0] - x[1][1])}

        for index, (id, points) in enumerate(self.scoreboard.items()):
            name = self.ctx.guild.get_member(int(id)).display_name

            emoji = standingEmojis.get(index + 1, ":medal:")
            body.add_line(f"{emoji} **{name}** ({points[0]} Right, {points[1]} Wrong)")

        view = Menu(self.ctx, self)

        view.body = body
        view.embed = embed
        await view.goto(0, edit=False)
        view.message = await self.ctx.send(embed=view.embed, view=view)
