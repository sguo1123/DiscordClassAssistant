# Partially sourced from https://github.com/Isklar/WolfBot - Used for pattern + intro to api access etc.
import sys
import string
import wolframalpha
import pprint
import discord
import asyncio
import configparser
from discord.ext import commands

# Wolfram Alpha credentials and client session
config = configparser.ConfigParser()
config.read('config.ini')
app_id = config.get('DEFAULT', 'WolframID')
waclient = wolframalpha.Client(app_id)

# Globals for message removal
messageHistory = set()
computemessageHistory = set()

# Fun strings for invalid queries
invalidQueryStrings = ["Nobody knows.", "It's a mystery.", "I have no idea.", "No clue, sorry!", "I'm afraid I can't let you do that.", "Maybe another time.", "Ask someone else.", "That is anybody's guess.", "Beats me.", "I haven't the faintest idea."]

# formatting for graph Pods
def graphEmbed(dict):
    results = 0
    graphs = 0
    result_value = []
    graph_value = []
    solution_id = ['Result', 'Solution', 'SymbolicSolution', 'ComplexSolution']
    graph_id = ['SurfacePlot', 'RootPlot', 'Plot']
    for pod in list(dict['pod']):
        if pod['@id'] == 'Input':
            input_value = pod['subpod']['img']['@title']
        elif pod['@id'] in solution_id and results == 0:
            if int(pod['@numsubpods']) > 1:
                for item in pod['subpod']:
                    result_value.append(item['img']['@title'])
            else:
                result_value.append(pod['subpod']['img']['@title'])
            results = 1
        elif pod['@id'] in graph_id and graphs == 0:
            if int(pod['@numsubpods']) > 1:
                for item in pod['subpod']:
                    graph_value.append(item['img']['@src'])
            else:
                graph_value.append(pod['subpod']['img']['@src'])
            graphs = 1
    if results == 0 and graphs == 0:
        result_value.append('Unknown?')
    print_embed = discord.Embed(
        title='Results',
        description='Wolfram|Alpha',
        color=discord.Colour.purple()
        )
    print_embed.set_thumbnail(url='https://i.imgur.com/cXwo5bz.png')
    print_embed.add_field(name='Input:', value=input_value, inline=False)
    print_embed.add_field(name='Result:', value=result_value, inline=False)
    if graphs == 1:
        print_embed.set_image(url=str(graph_value[0]))
    return print_embed


# formatting for Pods
def computeEmbed(dict):
    results = 0
    for pod in list(dict['pod']):
        if pod['@id'] == 'Input':
            input_value = pod['subpod']['img']['@title']
        elif pod['@id'] == 'Result':
            result_value = pod['subpod']['img']['@title']
            results = 1
        elif pod['@id'] == 'DecimalApproximation' and results == 0:
            result_value = pod['subpod']['img']['@title']
            results = 1
        elif results == 0:
            result_value = pod['subpod']['img']['@title']
    print_embed = discord.Embed(
        title='Results',
        description='Wolfram|Alpha',
        color=discord.Colour.purple()
        )
    print_embed.set_thumbnail(url='https://i.imgur.com/cXwo5bz.png')
    print_embed.add_field(name='Input:', value=input_value, inline=False)
    print_embed.add_field(name='Result:', value=result_value, inline=False)
    return print_embed

class Wolfram(commands.Cog):

    def __init__(self, client):
        self.client = client

    # Graph Wolfram Response
    @commands.command()
    async def graphwolf(self, ctx, *, query):
        queryComputeMessage = await ctx.send(":wolf: Computing '" + query + "' :computer: :thought_balloon: ...")
        res = waclient.query(query, format='plantext,image')
        res_dict=dict(res)
        if res_dict['@error'] == 'true':
            await ctx.send(random.choice(invalidQueryStrings))
            return
        await ctx.send(embed=graphEmbed(res_dict))
        await ctx.send("Finished! " + ctx.author.mention + " :checkered_flag:")

    # Compute Wolfram Response
    @commands.command()
    async def computewolf(self, ctx, *, query):
        queryComputeMessage = await ctx.send(":wolf: Computing '" + query + "' :computer: :thought_balloon: ...")
        res = waclient.query(query, format='plantext,image')
        res_dict=dict(res)
        if res_dict['@error'] == 'true':
            await ctx.send(random.choice(invalidQueryStrings))
            return
        await ctx.send(embed=computeEmbed(res_dict))
        await ctx.send("Finished! " + ctx.author.mention + " :checkered_flag:")

def setup(client):
    client.add_cog(Wolfram(client))
