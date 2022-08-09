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

import difflib
import readtime
import requests
import json
import re
import discord
import random
from discord.ext import commands
from discord.ext.commands import BadArgument

intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix=".", intents=intents)


async def setup(bot):
    bot.add_command(q)


@commands.hybrid_command(name="q")
async def q(ctx, subject):
    """
    Generate a new scibowl question!

    Valid subjects include:
    PHY    (Physics)
    GEN    (General Science)
    ENERGY (Energy)
    EAS    (Earth and Space)
    CHEM   (Chemistry)
    BIO    (Biology)
    ASTRO  (Astronomy)
    MATH   (Mathematics)
    CS     (Computer Science)
    ES     (Earth Science)
    ALL    (All Subjects Above)
    WEIRD  (Our own questions)
    CRAZY  (Our own non-science questions)
    """
    try:
        obj = Question(ctx, subject.upper())
        await obj.run()
    except Exception as err:
        raise err  # Raise error as discord.ext.commands error instead of normal console error that displays in shell


@q.autocomplete('subject')
async def q_autocomplete(interaction, current):
    choices = {
        "Physics": 'PHY',
        "General Science": 'GEN',
        "Energy": 'ENERGY',
        "Earth and Space": 'EAS',
        "Chemistry": 'CHEM',
        "Biology": 'BIO',
        "Astronomy": 'ASTRO',
        "Math": 'MATH',
        "Computer Science": 'CS',
        "Earth Science": 'ES',
        "Weird": 'WEIRD',
        "Crazy": 'CRAZY',
        "All": 'ALL'
    }

    return [
        discord.app_commands.Choice(name=subject, value=value)
        for subject, value in choices.items()
        if current.lower() in subject.lower()
    ]


class Question(discord.ui.View):
    def __init__(self, ctx, subject: str):
        super().__init__(timeout=15.0)
        self.ctx = ctx
        self.yay_reactions = [
            "\N{Thumbs Up Sign}", "\N{White Heavy Check Mark}", "\N{Brain}",
            "\N{Hundred Points Symbol}", "\N{Direct Hit}",
            "\N{Clapping Hands Sign}", "\N{Trophy}",
            "\N{Slightly Smiling Face}", "\N{Party popper}"
        ]
        self.aw_reactions = [
            "\N{Crying Face}", "\N{White Question Mark Ornament}",
            "\N{Slightly Frowning Face}", "\N{Worried Face}",
            "\N{Thumbs Down Sign}", "\N{Loudly Crying Face}", "\N{Cross Mark}",
            "\N{Face with No Good Gesture}"
        ]
        self.wspace = {" ,": ", ", "  ": " "}
        self.valid = [
            "PHY", "GEN", "ENERGY", "EAS", "CHEM", "BIO", "ASTRO", "MATH",
            "CS", "ES", "WEIRD", "CRAZY", "ALL"
        ]
        self.achiev = self.ctx.bot.Achievements
        self.subject = subject
        self.isweird = subject == "WEIRD"
        self.iscrazy = subject == "CRAZY"
        self.author = ctx.author.id
        self.timedout = False
        self.buzzed = False
        self.postedBtns = False
        self.graded = False
        self.buzzer = None
        self.embed = discord.Embed(title=f"Question",
                                   color=discord.Colour.blue())
        self.embed.set_author(name="Unattempted", url="")

        self.mc_timeout = 6.0
        self.override = False
        self.override_timeout = 15.0

    def extra_whitespace(self, string):
        string = string.strip()
        for before, after in self.wspace.items():
            string = string.replace(before, after)
        return string

    def generate_answers(self, answer):
        res = [answer]
        regexs = [
            "\(ACCEPT\s*:*\s*([^)]+)\s*\)",  # Deal with accepts (alternate answers)
            "\((.*)\)",  # A more generic accept
            "(.*) OR (.*)"  # Deal with "answer1 OR answer2"
        ]

        # Generalized regexps
        for reg in regexs:
            reg_res = re.findall(reg, answer)
            if reg_res:
                if isinstance(reg_res[0], tuple):
                    reg_res = list(reg_res[0])
                res.extend(reg_res)

        # Specific operations
        res.append(self.extra_whitespace(re.sub(regexs[1], "", answer)))

        return res

    async def run(self):
        # Checks
        if self.subject not in self.valid:
            raise BadArgument(
                f'"{self.subject}" is not a valid subject. Run `.help q` for a list of subjects'
            )

        if self.ctx.channel.id in self.ctx.bot.hasQuestion:
            raise BadArgument(
                f"There is already a question being served in this channel\n\nThink this is a mistake? Try running `.clear`"
            )

        self.ctx.bot.hasQuestion.add(self.ctx.channel.id)

        # Get Question
        if self.isweird:
            question_json = random.choice(
                json.loads(open("probs.json", "r").read()))
        elif self.iscrazy:
            question_json = random.choice(
                json.loads(open("crazy.json", "r").read()))
        else:
            question_json = requests.post(
                "https://scibowldb.com/api/questions/random",
                json={
                    "categories": self.ctx.bot.apprev[self.subject]
                }).json()

        self.question_json = question_json
        self.question_header = "**" + question_json["question"][
            "category"] + " " + question_json["question"][
                "tossup_format"] + " (Source: " + question_json["question"][
                    "source"] + ")\n**"
        self.question = question_json["question"]["tossup_question"]
        self.mc = question_json["question"][
            "tossup_format"] == "Multiple Choice"
        self.algorithm_correct = False

        self.timeout = self.calc_timeout(self.question)

        # Regexp fetching all the metadata hidden in the problem text

        if self.mc:
            self.correct_answer = (
                question_json["question"]["tossup_answer"])[0].upper()
            self.answers = []
            if "(W)" in self.question:
                regstring = "\(W\)(.*)\(X\)(.*)\(Y\)(.*)\(Z\)(.*)"
            else:
                regstring = "(\(|)W\)(.*)(\(|)X\)(.*)(\(|)Y\)(.*)(\(|)Z\)(.*)"
            if re.search(regstring,
                         self.question.replace("\n", ""),
                         flags=re.DOTALL | re.MULTILINE):
                for i in list(
                        re.search(regstring,
                                  self.question.replace("\n", ""),
                                  flags=re.DOTALL | re.MULTILINE).groups()):
                    if i != "":
                        i = i.strip()
                        if len(i) < 70:
                            self.answers.append(i)
                        else:
                            self.answers.append(i[:70] + "...")
            else:
                self.answers = ["", "", "", ""]
        else:
            self.correct_answer = question_json["question"][
                "tossup_answer"].upper()

        self.answer_list = self.generate_answers(self.correct_answer)

        self.embed.add_field(name=self.question_header,
                             value=self.question,
                             inline=False)
        self.message = await self.ctx.send(embed=self.embed, view=self)

    @discord.ui.button(label="Buzz!", style=discord.ButtonStyle.green)
    async def buzz(self, interaction, button):
        self.responder = interaction.user
        self.author = self.responder.id
        self.embed.set_author(name=self.responder.display_name,
                              url="",
                              icon_url=self.responder.avatar)
        await self.message.edit(embed=self.embed)
        self.buzzed = True
        self.children[0].disabled = True
        self.children[0].style = discord.ButtonStyle.gray
        if self.mc:
            self.add_item(
                MCOption(self.ctx, "W)", self.answers[0], self.author))
            self.add_item(
                MCOption(self.ctx, "X)", self.answers[1], self.author))
            self.add_item(
                MCOption(self.ctx, "Y)", self.answers[2], self.author))
            self.add_item(
                MCOption(self.ctx, "Z)", self.answers[3], self.author))
            await interaction.response.edit_message(view=self)
            self.timeout = self.mc_timeout
        else:
            self.children[0].disabled = True
            await self.message.edit(view=self)
            await interaction.response.send_modal(
                GetResponse(self, self.calc_timeout(self.answer_list[0]),
                            self.author))

    def remove_id(self):
        if self.ctx.channel.id in self.ctx.bot.hasQuestion:
            self.ctx.bot.hasQuestion.remove(self.ctx.channel.id)
        self.add_item(
            AfterButton(self.ctx,
                        f"New {self.subject} question",
                        value=self.subject,
                        style=discord.ButtonStyle.blurple))
        self.add_item(
            AfterButton(self.ctx,
                        f"New question (Any Subject)",
                        value="ALL",
                        style=discord.ButtonStyle.blurple))
        self.postedBtns = True
        self.timeout = 15

    async def on_timeout(self, element=False):
        if self.postedBtns:
            for item in self.children:
                item.disabled = True
            self.postedBtns = False 

        if self.buzzed and not self.graded:

            for item in self.children:
                item.disabled = True
                if self.mc:
                    if item.label[0] == self.answer_list[0][0]:
                        item.style = discord.ButtonStyle.green
                    elif item.label == "Buzz!":
                        item.style = discord.ButtonStyle.gray
                    elif item.label[0] != self.answer_list[0][0]:
                        item.style = discord.ButtonStyle.red
                item.disabled = True

            self.changepoints(self.author, -1)

            self.embed.add_field(
                name="Question Timed Out",
                value=
                f"Incorrect **{self.responder.display_name}**, you ran out of time. The answer was `{self.answer_list[0]}`. You now have **{self.ctx.bot.getpoints(self.author)}** (-1) points"
            )

            await self.message.add_reaction(random.choice(self.aw_reactions))

            self.remove_id()
            self.graded = True

        if not self.buzzed and not self.graded:
            for item in self.children:
                item.disabled = True
            self.embed.add_field(
                name="Timeout",
                value=
                f"No one has buzzed. The answer was `{self.answer_list[0]}`")
            self.remove_id()

        if self.override:
            self.children[-1].disabled = True

        await self.message.edit(view=self, embed=self.embed)

    def changepoints(self, author, amount):
        # Deal with achievements
        user = self.achiev(author)
        res = ""
        curPoints = self.ctx.bot.changepoints(author, amount)

        checks = {
            self.achiev.pts50(): curPoints >= 50,
            self.achiev.pts100(): curPoints >= 100,
            self.achiev.pts200(): curPoints >= 200,
            self.achiev.pts500(): curPoints >= 500,
            self.achiev.pts1000(): curPoints >= 1000,
        }

        for name, check in checks.items():
            if check:
                data = user.set(name)
                if data:
                    res += f"{data['emoji']} {data['name']} - {data['description']}\n"

        if res:
            self.embed.add_field(name="Achievement(s) Unlocked!",
                                 value=res,
                                 inline=False)

        return curPoints

    def compare(self, str1, str2):
        return difflib.SequenceMatcher(None, str1, str2).ratio() * 100

    def calc_timeout(self, string):
        return 5 + readtime.of_text(string).seconds

    async def validate(self, answer):
        self.embed.add_field(name="The answer recieved",
                             value=f"`{answer}`",
                             inline=False)
        answer = answer.upper()

        # Decide Verdict
        self.correct = True
        self.answer_list = list(map(lambda x: x.upper(), self.answer_list))
        accuracy = [self.compare(case, answer) for case in self.answer_list]
        responder = self.responder.display_name
        algorithm_correct = False
        percent = max(accuracy)
        if 75 <= percent <= 100 and not self.mc:
            algorithm_correct = True

        if answer in self.answer_list and self.isweird:
            verdict = f"Correct **{responder}** You now have **{self.changepoints(self.author, 1)}** (+1) points (This is a *weird* question, so you get a point.)"
            await self.message.add_reaction(random.choice(self.yay_reactions))

        elif answer in self.answer_list and self.iscrazy:
            verdict = f"Correct **{responder}** You now have **{self.changepoints(self.author, 0)}** (+0) points (This is a *crazy* question, so you get no points, you may get some kicks though?)"
            await self.message.add_reaction(random.choice(self.yay_reactions))

        elif answer in self.answer_list:
            verdict = f"Correct **{responder}** You now have **{self.changepoints(self.author, 2)}** (+2) points"
            await self.message.add_reaction(random.choice(self.yay_reactions))

        elif algorithm_correct:
            verdict = f"You may be correct **{responder}**. Our algorithm marked it was \"close enough.\" (Your answer got a score of **{round(percent, 3)}**) The answer is `{self.correct_answer}`. You now have **{self.changepoints(self.author, 2 if not self.iscrazy else 0)}** (+{2 if not self.iscrazy else 0}) points"
            self.add_item(
                Override(self.ctx,
                         self.author,
                         change=(False if self.iscrazy else True)))
            await self.message.add_reaction(random.choice(self.yay_reactions))
            self.override = True
            self.timeout = self.override_timeout

        else:
            self.correct = False
            verdict = f"Incorrect **{responder}**, the answer was `{self.correct_answer}`. You now have **{self.changepoints(self.author, -1)}** (-1) points"
            await self.message.add_reaction(random.choice(self.aw_reactions))

        self.embed.add_field(name="Verdict", value=verdict, inline=False)
        self.graded = True
        if self.mc:
            for item in self.children:
                if item.label[0] == self.answer_list[0][0]:
                    item.style = discord.ButtonStyle.green
                elif item.label == "Buzz!":
                    item.style = discord.ButtonStyle.gray
                elif item.label[0] != self.answer_list[0][0]:
                    item.style = (discord.ButtonStyle.gray
                                  if self.correct else discord.ButtonStyle.red)
                item.disabled = True
        self.remove_id()
        await self.message.edit(view=self, embed=self.embed)


class GetResponse(discord.ui.Modal, title="Short Response"):
    answer = discord.ui.TextInput(label='Answer',
                                  style=discord.TextStyle.short,
                                  placeholder="Quick! Your answer")

    def __init__(self, view, timeout, author):
        super().__init__(timeout=timeout)
        self.view = view
        self.a = author
        self.timeouted = False

    async def on_submit(self, interaction: discord.Interaction):
        if interaction.user.id != self.a:
            return await interaction.response.send_message(
                "I have no idea how in the world you managed to circumvent our buzzer disable and answer another person's question, but you did it. (We have a check here, so your submit didn't do anything)",
                ephemeral=True)
        if not self.timeouted:
            await self.view.validate(self.answer.value)
        await interaction.response.defer()

    async def on_timeout(self):
        self.timeouted = True
        await self.view.on_timeout(True)
        self.stop()


class MCOption(discord.ui.Button):
    def __init__(self, ctx, label, opt, author):
        self.val = label
        self.ctx = ctx
        self.author = author
        super().__init__(style=discord.ButtonStyle.blurple,
                         label=f"{label} {opt}",
                         row=2)

    async def callback(self, interaction):
        if interaction.user.id != self.author:
            return await interaction.response.send_message(
                "Sorry, this button is not controlled by you! Maybe buzz next round?",
                ephemeral=True)

        await self.view.validate(self.val[0])
        await interaction.response.edit_message(view=self.view)


class Override(discord.ui.Button):
    def __init__(self, ctx, author, change=True):
        self.ctx = ctx
        self.author = author
        self.change = change
        super().__init__(style=discord.ButtonStyle.blurple,
                         label=f"Override",
                         row=0)

    async def callback(self, interaction):
        if interaction.user.id != self.author:
            return await interaction.response.send_message(
                "Sorry, this button is not controlled by you! Maybe buzz next round?",
                ephemeral=True)

        self.style = discord.ButtonStyle.green
        self.disabled = True
        self.view.embed.add_field(
            name="Override",
            value=
            f"The verdict has been overriden by **{interaction.user.display_name}**. They now have **{self.view.changepoints(interaction.user.id, -3 if self.change else 0)}** {'(-1 from original) points.' if self.change else '(No Change)'}"
        )
        await interaction.response.edit_message(embed=self.view.embed,
                                                view=self.view)

        await self.view.message.add_reaction(
            random.choice(self.view.aw_reactions))


class AfterButton(discord.ui.Button):
    def __init__(self, ctx, label, value, style):
        self.ctx = ctx
        self.value = value
        super().__init__(style=style, label=label, row=0)

    async def callback(self, interaction):
        for item in self.view.children:
            item.disabled = True

        await interaction.response.edit_message(view=self.view)

        obj = Question(self.ctx, self.value.upper())
        await obj.run()
