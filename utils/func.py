import discord
import json


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
