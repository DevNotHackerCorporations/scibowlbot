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
import json
import os


async def setup(client):
    client.apprev = {
        "PHY": ["PHYSICS"],
        "GEN": ["GENERAL SCIENCE"],
        "ENERGY": ["ENERGY"],
        "EAS": ["EARTH AND SPACE"],
        "CHEM": ["CHEMISTRY"],
        "BIO": ["BIOLOGY"],
        "ASTRO": ["ASTRONOMY"],
        "MATH": ["MATH"],
        "CS": ["COMPUTER SCIENCE"],
        "ES": ["EARTH SCIENCE"],
        "WEIRD": ["WEIRD PROBLEMS"],
        "CRAZY": ["CRAZY PROBLEMS"],
        "ALL": [
            "PHYSICS", "GENERAL SCIENCE", "ENERGY", "EARTH AND SPACE",
            "EARTH SCIENCE", "CHEMISTRY", "BIOLOGY", "ASTRONOMY", "MATH",
            "COMPUTER SCIENCE"
        ],
        "EVERYTHING": [
            "PHYSICS", "GENERAL SCIENCE", "ENERGY", "EARTH AND SPACE",
            "EARTH SCIENCE", "CHEMISTRY", "BIOLOGY", "ASTRONOMY", "MATH",
            "COMPUTER SCIENCE", "WEIRD PROBLEMS", "CRAZY PROBLEMS"
        ]
    }

    client.comps = {}

    client.in_comp = {}

    client.scibowl_subjects = ["BIO", "CHEM", "EAS", "ASTRO", "MATH", "PHY", "ES"]

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

    discord.Color.none = lambda: 0x2f3136

    def changepoints(user, point):
        user = str(user)
        points = json.loads(open("assets/points.json", "r").read())
        points["points"][user] = points.get("points").get(user, 0) + point
        open("assets/points.json", "w").write(json.dumps(points))
        client.db.set(points)
        return points["points"][user]

    def getpoints(user):
        user = str(user)
        points = json.loads(open("assets/points.json", "r").read())
        return points.get("points").get(user, 0)

    def changeprofile(user, good=None, bad=None, bio=None):
        user = str(user)
        points = json.loads(open("assets/points.json", "r").read())
        if not points["profile"].get(user):
            points["profile"][user] = [[], [], ""]
        if good:
            points["profile"][user][0] = good
        if bad:
            points["profile"][user][1] = bad
        if bio:
            points["profile"][user][2] = bio
        open("assets/points.json", "w").write(json.dumps(points))
        client.db.set(points)

    def getprofile(user):
        user = str(user)
        points = json.loads(open("assets/points.json", "r").read())
        return points.get("profile").get(user, [[], [], ""])

    def t_string(seconds: int) -> str:
        day = seconds // (24 * 3600)
        seconds = seconds % (24 * 3600)
        hour = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60
        seconds = seconds
        return ("%d days, %d hours, %d minutes, and %d seconds!" %
                (day, hour, minutes, seconds))

    class Achievements:
        def __init__(self, id: str):
            self.desc = [
                {
                    "name": "Intern Scientist",
                    "description": "Reach 50 or more points!",
                    "earned": False,
                    "emoji": client.get_emoji(1003734599714754682)
                },
                {
                    "name": "100% Awesome",
                    "description": "Reach 100 or more points!",
                    "earned": False,
                    "emoji": ":100:"
                },
                {
                    "name": "Junior Scientist",
                    "description": "Reach 200 or more points!",
                    "earned": False,
                    "emoji": client.get_emoji(1003739000055529588)
                },
                {
                    "name": "Experienced Scientist",
                    "description": "Reach 500 or more points!",
                    "earned": False,
                    "emoji": client.get_emoji(1003739001200586904)
                },
                {
                    "name": "Senior Scientist",
                    "description": "Reach 1000 or more points!",
                    "earned": False,
                    "emoji": client.get_emoji(1003739002404343849)
                },
            ]
            self.id = str(id)

            raw = json.loads(open("assets/points.json",
                                  "r").read())['achiev'].get(self.id, 0)
            self.progress = list(
                map(lambda x: bool(int(x)), list(bin(raw)[2:])))

            self.parse()

        def parse(self):
            self.progress.extend(
                [False for _ in range(len(self.desc) - len(self.progress))])
            for earned, acheiv in zip(self.progress, self.desc):
                acheiv['earned'] = earned

        def set(self, index: int) -> bool:
            if self.desc[index]['earned']:
                return False
            self.desc[index]['earned'] = True

            binary = int(
                "".join([str(int(achiev['earned'])) for achiev in self.desc]),
                2)

            raw = json.loads(open("assets/points.json", "r").read())
            raw['achiev'][self.id] = binary
            open("assets/points.json", "w").write(json.dumps(raw))
            client.db.set(raw)

            return self.desc[index]

        # Enumeration
        @staticmethod
        def pts50():
            return 0

        @staticmethod
        def pts100():
            return 1

        @staticmethod
        def pts200():
            return 2

        @staticmethod
        def pts500():
            return 3

        @staticmethod
        def pts1000():
            return 4

    client.changepoints = changepoints
    client.getpoints = getpoints
    client.changeprofile = changeprofile
    client.getprofile = getprofile
    client.hasQuestion = set()
    client.Achievements = Achievements
