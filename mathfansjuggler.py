import discord
import os
import configparser
from datetime import datetime
from discord.ext import commands
from pathlib import Path, PureWindowsPath

client = commands.Bot(command_prefix='!')

# Read config files
config = configparser.ConfigParser()
config.read('config.ini')
token = config.get('DEFAULT', 'Token')
instructor = int(config.get('DEFAULT', 'Instructor'))
current_voice_channel = int(config.get('DEFAULT', 'CurrentVoiceChannel'))
question_mode = config.get('DEFAULT', 'QuestionMode')


# New Data Class To Handle Student Attendance
class Student:
    def __init__(self, s_name):
        self.name = s_name
        self.timein = ''
        self.timeout = ''

    def timein(self, in_string):
        self.timein = in_string

    def timeout(self, in_string):
        self.timeout = in_string


# Default values
user_queue = []
lesson_mode = None
attendance_list = []


def get_channel(channel_str):
    for guild in client.guilds:
        for channel in guild.channels:
            if channel.name == channel_str:
                return channel


def get_guild(guild_str):
    for guild in client.guilds:
        if guild.name == guild_str:
            return guild


# Subroutine to change lesson_mode
def change_lesson_mode(bool):
    global lesson_mode
    lesson_mode = bool


# Subroutine to change question_mode
def change_question_mode(str):
    global question_mode
    question_mode = str


# Bot activity + load up notifier
@client.event
async def on_ready():
    await client.change_presence(
        activity=discord.Activity(
            name='with Numbers', type=discord.ActivityType.playing))
    print('Bot is ready.')


# command to close bot
@client.command()
async def botstop(ctx):
    if ctx.message.author.id != instructor:
        await ctx.send('Nice Try')
        return
    await ctx.send('Bye Bye')
    await client.logout()


# change active voice channel
@client.command()
async def changechannel(ctx, channel_id):
    global attendance_list
    global current_voice_channel
    if ctx.message.author.id != instructor:
        await ctx.send('Missing Permissions. Please check !help')
        return
    else:
        current_voice_channel = int(channel_id)
        attendance_list.clear()
        await ctx.message.delete(delay=5.0)
        await ctx.send(f'Current voice channel set to {channel_id}', delete_after=5.0)


# update instructor id
@client.command()
async def changeinstructor(ctx, id):
    global instructor
    if ctx.message.author.id != instructor:
        await ctx.send('Missing Permissions. Please check !help')
        return
    else:
        instructor = int(id)
        await ctx.send(f'Instuctor ID set to {id}')

# Checks for new member join and mutes them.
@client.event
async def on_voice_state_update(member, before, after):
    guild_obj = get_guild(member.guild.name)
    # checks if in lesson mode
    if lesson_mode:
        if before.channel is None and after.channel is not None:
            if member.id != instructor:
                await guild_obj.get_member(member.id).edit(mute=True)


# sub routine for done/forcedone to prompt next user
@client.command()
async def next(ctx):
    guild_obj = get_guild(ctx.guild.name)
    # checks user permissions
    if ctx.message.author.id != instructor:
        await ctx.send('Missing Permissions. Please check !help')
        return
    # checks if queue has Users
    if not user_queue:
        await ctx.send('Queue Empty')
        return
    member = guild_obj.get_member(user_queue[0].id)
    # unmute user in voice channel
    if member in guild_obj.get_channel(current_voice_channel).members:
        print(member.voice.mute)
        if not member.voice.mute:
            await forcedone(ctx)
        if lesson_mode == 'auto':
            return
        if not user_queue:
            await ctx.send('Queue Empty')
            return
        member = guild_obj.get_member(user_queue[0].id)
        await guild_obj.get_member(member.id).edit(mute=False)
        await ctx.send(f'{member.display_name} speak permissions set to True')
        await ctx.send(f'{member.display_name} is now asking his/her question')
        return
    # if member is not found, pop and retry
    else:
        user_queue.pop(0)
        await ctx.send(
            f'Unable to find {member.display_name} in voice channel, skipping to next user')
        await next(ctx)
        return


# auto next bypass instructor checks
@client.command()
async def forcenext(ctx):
    guild_obj = get_guild(ctx.guild.name)
    # checks if queue has Users
    if not user_queue:
        await ctx.send('Queue Empty')
        return
    member = guild_obj.get_member(user_queue[0].id)
    # unmute user in voice channel
    if member in guild_obj.get_channel(current_voice_channel).members:
        print(member.voice.mute)
        if not member.voice.mute:
            await forcedone(ctx)
        if lesson_mode == 'auto':
            return
        if not user_queue:
            await ctx.send('Queue Empty')
            return
        member = guild_obj.get_member(user_queue[0].id)
        await guild_obj.get_member(member.id).edit(mute=False)
        await ctx.send(f'{member.display_name} speak permissions set to True')
        await ctx.send(f'{member.display_name} is now asking his/her question')
        return
    # if member is not found, pop and retry
    else:
        user_queue.pop(0)
        await ctx.send(
            f'Unable to find {member.display_name} in voice channel, skipping to next user')
        await forcenext(ctx)
        return


# commands to change question_mode
@client.command()
async def qauto(ctx):
    # checks user permissions
    if ctx.message.author.id != instructor:
        await ctx.send('Missing Permissions. Please check !help')
        return
    global question_mode
    question_mode = 'auto'
    await ctx.message.add_reaction("✅")


@client.command()
async def qsingle(ctx):
    # checks user permissions
    if ctx.message.author.id != instructor:
        await ctx.send('Missing Permissions. Please check !help')
        return
    global question_mode
    question_mode = 'single'
    await ctx.message.add_reaction("✅")


# allows current user to end their question
@client.command()
async def done(ctx):
    guild_obj = get_guild(ctx.guild.name)
    if not lesson_mode:
        await ctx.send('Class is not in session.')
        return

    # if user queue empty
    if not user_queue:
        await ctx.send('No math fans in line!')
    # if user who is currently talking wants to stop
    elif ctx.message.author == user_queue[0]:
        user_popped = user_queue.pop(0)
        member = guild_obj.get_member(user_popped.id)
        # if user in voice channel, mute
        if ctx.author in guild_obj.get_channel(current_voice_channel).members:
            await guild_obj.get_member(member.id).edit(mute=True)
            await ctx.send(f'{member.display_name} muted')
        await ctx.author.edit(mute=True)
        await ctx.send(
            f'{user_popped.display_name} is no longer in line and is now muted.')
        await ctx.send(
            f'There are {len(user_queue)} math fans in line.')
        # [Auto Mode] next user into their question
        if question_mode == 'auto':
            await forcenext(ctx)
    # if user isnt currently the person talking
    else:
        await ctx.send('You are not currently talking')


# allows instructor to toggle next user
@client.command()
async def forcedone(ctx):
    guild_obj = get_guild(ctx.guild.name)
    if ctx.message.author.id != instructor:
        await ctx.send('Missing Permissions. Please check !help')
        return

    if not user_queue:
        await ctx.send('No math fans in line!')
    else:
        user_popped = user_queue.pop(0)
        member = guild_obj.get_member(user_popped.id)
        # if user in voice channel, unmute
        if member in guild_obj.get_channel(current_voice_channel).members:
            await guild_obj.get_member(member.id).edit(mute=True)
            await ctx.send(f'{member.display_name} muted')
        await ctx.send(
            f'{user_popped.display_name} is no longer in line and is now muted.')
        await ctx.send(
            f'There are {len(user_queue)} math fans in line.')


# shows queue
@client.command()
async def queue(ctx):
    if user_queue:
        for member in user_queue:
            queuelist = []
            queuelist.append(member.name)
        await ctx.send(f'Current Queue: {queuelist}')
    else:
        await ctx.send('Queue is empty!')


# queues user to ask a question
@client.command()
async def talk(ctx):
    guild_obj = get_guild(ctx.guild.name)
    if not lesson_mode:
        await ctx.send('Class is not in session.')
        return
    # dynamically fetch guild object and member
    member = guild_obj.get_member(ctx.author.id)

    # if user already in line, do nothing
    if ctx.author in user_queue:
        await ctx.send(f'{ctx.author.display_name} already in line')
        return

    # if user queue empty
    if not user_queue:
        user_queue.append(ctx.author)
        await ctx.send(f'{ctx.author.display_name} has been added to the queue')
        if question_mode == 'auto':
            # unmute member if in the voice channel, unmute
            if member in guild_obj.get_channel(current_voice_channel).members:
                await guild_obj.get_member(member.id).edit(mute=False)
                await ctx.send(f'{member.display_name} unmuted')
            await ctx.send(f'No math fans in line. {ctx.author.display_name} unmuted.')
    else:
        user_queue.append(ctx.author)
        await ctx.send(
            f'{ctx.author.display_name} there are {len(user_queue) - 1} math fans ahead of you in line.')


# starts class
@client.command()
async def start(ctx):
    if current_voice_channel == 0:
        await ctx.send('Please set current voice channel')
        return
    guild_obj = get_guild(ctx.guild.name)
    if ctx.message.author.id != instructor:
        await ctx.send('Missing Permissions. Please check !help')
        return

    # sets lesson mode
    change_lesson_mode(True)

    # mute all members in the voice channel
    for member in guild_obj.get_channel(current_voice_channel).members:
        if member.id != instructor:
            await guild_obj.get_member(member.id).edit(mute=True)

    await ctx.send('Lesson Started! All users muted. Hello Math Fans!')


# ends class
@client.command()
async def end(ctx):
    guild_obj = get_guild(ctx.guild.name)
    if ctx.message.author.id != instructor:
        await ctx.send('Missing Permissions. Please check !help')
        return

    # sets lesson mode
    change_lesson_mode(False)

    # unmute all members in the voice channel
    for member in guild_obj.get_channel(current_voice_channel).members:
        await guild_obj.get_member(member.id).edit(mute=False)

    # signing students off
    time_now = datetime.now()
    for x in attendance_list:
        if x.timeout == '':
            x.timeout = f"{time_now.strftime('%X')} [*]"

    # flush attendance list

    await flushattendance(ctx)
    await ctx.send('All users unmuted.  That\'s all for now!')


# command to count attendance
@client.command()
async def attendance(ctx, *, name: str = None):
    global attendance_list
    if lesson_mode is None or lesson_mode is False:
        await ctx.send('Class is not in session, please wait for the instructor to start class!')
        return
    normpath = os.path.normpath(os.getcwd())
    data_folder = Path(normpath)
    attendance_path = data_folder / 'Attendance' / f'attendance_{ctx.guild.name}_{datetime.now().date()}.txt'
    attendance_path = PureWindowsPath(attendance_path)
    for x in attendance_list:
        if x.name == ctx.author.display_name:
            await ctx.send('You are already signed in!')
            return
    attendance_list.append(Student(ctx.author.display_name))
    time_now = datetime.now()
    for x in attendance_list:
        if x.name == ctx.author.display_name:
            x.timein = time_now.strftime("%X")
    if not os.path.exists(attendance_path):
        attendance_file = open(attendance_path, 'a')
        attendance_file.write('Name | Time In | Time Out\n')
    attendance_file = open(attendance_path, 'a')
    attendance_file.write(f'{ctx.author.display_name} | {time_now.strftime("%X")} | \n')
    attendance_file.close()
    await ctx.message.add_reaction("✅")


# alternate command phrase for attendance
@client.command()
async def join(ctx):
    await attendance(ctx)


# end of class Student
@client.command()
async def leave(ctx):
    global attendance_list
    time_now = datetime.now()
    if lesson_mode is None or lesson_mode is False:
        await ctx.send('Class is not in session! Please wait for the instructor to start class.')
        return
    for x in attendance_list:
        if x.name == ctx.author.display_name:
            if x.timeout != '':
                await ctx.send('You have already signed out!')
                return
            x.timeout = time_now.strftime("%X")
            await flushattendance(ctx)
            await ctx.message.add_reaction("✅")
            return
    await ctx.send('Student did not sign in!')


# alternative to leave
@client.command()
async def goodbye(ctx):
    await leave(ctx)


# get attendance list
@client.command()
async def flushattendance(ctx):
    global attendance_list
    normpath = os.path.normpath(os.getcwd())
    data_folder = Path(normpath)
    attendance_path = data_folder / 'Attendance' / f'attendance_{ctx.guild.name}_{datetime.now().date()}.txt'
    attendance_path = PureWindowsPath(attendance_path)
    attendance_file = open(attendance_path, 'w')
    attendance_file.write('Name | Time In | Time Out \n')
    for x in attendance_list:
        attendance_file.write(f'{x.name} | {x.timein} | {x.timeout}\n')
    attendance_file.close()


# poll command for creating new polls
@client.command()
async def poll(ctx, *, input_string):

    input_list = input_string.split('? ')
    if len(input_list) != 2:
        await ctx.send('Formatting for polls should be: `!poll <question>? <option1>:<option2>`')
        return
    input_question = input_list[0] + '?'
    answers = input_list[1].split(':')
    emoji_list = ["🐌", "🐇", "🐘", "🐖", "🐏", "🐍", "🐬"]
    output_list = [f"Poll: {input_question} [By: {ctx.author.display_name}]\n"]
    if len(answers) > 7:
        await ctx.send('Too many answers, please reduce the number of answers.')
        return
    for indx, val in enumerate(answers):
        output_list.append(emoji_list[indx] + f" - {val}\n")
    output_string = ''.join([str(elem) for elem in output_list])
    msg = await ctx.send(output_string)
    for indx, val in enumerate(answers):
        await msg.add_reaction(emoji_list[indx])
    await ctx.message.delete()


# change default help commands
client.remove_command('help')
@client.command()
async def help(ctx):
    await bothelp(ctx)

# clears user queue for questions
@client.command()
async def clearqueue(ctx):
    guild_obj = get_guild(ctx.guild.name)
    if ctx.message.author.id != instructor:
        await ctx.send('Missing Permissions. Please check !help')
        return
    global user_queue
    user_queue = []
    await ctx.send('Queue has been cleared.')

    # mutes everyone if cleared while unmuted
    for member in guild_obj.get_channel(current_voice_channel).members:
        if member.id != instructor:
            await guild_obj.get_member(member.id).edit(mute=True)


# bothelp command with refrence for users
@client.command()
async def bothelp(ctx):
    if ctx.message.author.id == instructor:
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

        await ctx.send(embed=instructor_embed)

    else:
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

        await ctx.send(embed=embed)

client.run(token)
