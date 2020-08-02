import discord
import json
from discord.ext import commands

# New global dictionary to store points - flushes to points.json
ptsDatabase = {}

class Points(commands.Cog):

    def __init__(self, client):
        self.client = client

    # user points section
    @commands.command(aliases=['ptstop'])
    async def pointstop(self, ctx):
        global ptsDatabase
        with open('points.json') as f:
            ptsDatabase = json.load(f)
        if not ptsDatabase:
            await ctx.send('No Data Found.')
            return
        output_str = "```Class Points\nStudent Name - Number of Points\n"
        student_keys = []
        for key in list(ptsDatabase.keys()):
            student_keys.append(key)
        student_keys.sort()
        for student in student_keys:
            student_name =  student.ljust(12).capitalize()
            student_pts = ptsDatabase[student]
            output_str += f'{student_name} - {student_pts}\n'
        output_str += "```"
        await ctx.send(output_str)
        await ctx.message.add_reaction("✅")

    # add points to students
    @commands.command(aliases=['pts', 'addpts'])
    async def points(self, ctx, tagged_member : discord.Member, *, pts=1):
        global ptsDatabase
        if tagged_member.display_name in list(ptsDatabase.keys()):
            ptsDatabase[tagged_member.display_name] += pts
        else:
            ptsDatabase[tagged_member.display_name] = pts
        with open('points.json', 'w') as json_file:
            json.dump(ptsDatabase, json_file)
        await ctx.message.add_reaction("✅")

    # remove points from students
    @commands.command()
    async def removepoints(self, ctx, tagged_member : discord.Member, *, pts=1):
        global ptsDatabase
        if tagged_member.display_name in list(ptsDatabase.keys()):
            if ptsDatabase[tagged_member.display_name] > pts:
                ptsDatabase[tagged_member.display_name] -= pts
            else:
                ptsDatabase[tagged_member.display_name] = 0
        else:
            ptsDatabase[tagged_member.display_name] = 0
        with open('points.json', 'w') as json_file:
            json.dump(ptsDatabase, json_file)
        await ctx.message.add_reaction("✅")

    # check personal points
    @commands.command(aliases=['mypts'])
    async def mypoints(self, ctx):
        global ptsDatabase
        with open('points.json') as f:
            ptsDatabase = json.load(f)
        if ctx.message.author.display_name in list(ptsDatabase.keys()):
            await ctx.send(f'You currently have {ptsDatabase[ctx.message.author.display_name]} points.')
        else:
            await ctx.send(f"It doesn't look like you have points yet.")
        await ctx.message.add_reaction("✅")

def setup(client):
    client.add_cog(Points(client))
