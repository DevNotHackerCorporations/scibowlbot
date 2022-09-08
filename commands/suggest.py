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

if message.content.startswith(".suggest"):
        channel_entry = 1016869552707084378
        y = message.content
        z = y.replace(".suggest", "", 1)
        channel = client.get_channel(channel_entry)
        embed=discord.Embed(title=message.author, description=z, color=0x91FA46)
        await channel.send(embed=embed)
