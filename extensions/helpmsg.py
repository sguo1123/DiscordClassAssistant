import discord
import asyncio
import configparser
from discord.ext import commands

config = configparser.ConfigParser()
config.read('config.ini')
instructor = int(config.get('DEFAULT', 'Instructor'))

instructor_embed = discord.Embed(
    title='Instructor Comands',
    description='Commands for Instructors',
    color=discord.Colour.purple()
    )
instructor_embed.set_thumbnail(url='https://i.imgur.com/v8CwNn0.png')
instructor_embed.add_field(name='!start', value='start class, will mute users in voice chat', inline=False)
instructor_embed.add_field(name='!end', value='ends class, will unmutes all users in voice chat', inline=False)
instructor_embed.add_field(name='!qauto', value='changes questions to cycle automatically', inline=False)
instructor_embed.add_field(name='!qsingle', value='changes questions to cycle one at a time', inline=False)
instructor_embed.add_field(name='!next', value='cycles to the next student in line', inline=False)
instructor_embed.add_field(name='!clearqueue', value='clears voice queue for questions', inline=False)
instructor_embed.add_field(name='!changechannel <channel_id>', value='changes current voice channel', inline=False)
instructor_embed.add_field(name='!changeinstructor <instructor_id>', value='changes current instructor', inline=False)
instructor_embed.add_field(name='!setgroup <num>', value='creates new group room category and creates "num" of rooms for Students', inline=False)
instructor_embed.add_field(name='!group', value='moves students from main room to group rooms - unmutes', inline=False)
instructor_embed.add_field(name='!regroup', value='moves students back into main room - mutes', inline=False)
instructor_embed.add_field(name='!points <tag_user> <points>', value='adds points for tagged user', inline=False)
instructor_embed.add_field(name='!removepoints <tag_user> <points>', value='removes points for tagged user - min is 0', inline=False)

embed = discord.Embed(
    title='Student Commands',
    description='Commands for Students',
    color=discord.Colour.blue()
    )
embed.set_thumbnail(url='https://i.imgur.com/v8CwNn0.png')
embed.add_field(name='!attendance or !join', value='logs the student to the attendance log', inline=False)
embed.add_field(name='!leave or !goodbye', value='logs the student leaving the attendance log')
embed.add_field(name='!talk', value='adds the user to the voice queue', inline=False)
embed.add_field(name='!done', value='removes the user from the voice queue', inline=False)
embed.add_field(name='!queue', value='shows current queue to ask questions', inline=False)
embed.add_field(name='!poll', value='creates a reaction poll with format [`!poll <question>? <option1>:<option2>`]', inline=False)
embed.add_field(name='!equation `LaTeX_Equation`', value='renders LaTeX equation as an image in chat', inline=False)
embed.add_field(name='!mypoints', value='returns number of points tied to your account', inline=False)
embed.add_field(name='!pointslist', value='returns list of all points in class', inline=False)

class Help(commands.Cog):

    def __init__(self, client):
        self.client = client

    # bothelp command with refrence for users
    @commands.command()
    async def help(self, ctx):
        if ctx.message.author.id == instructor:
            await ctx.send(embed=instructor_embed)
        else:
            await ctx.send(embed=embed)

def setup(client):
    client.remove_command('help')
    client.add_cog(Help(client))
