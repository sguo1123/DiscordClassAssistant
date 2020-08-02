import discord
import re
from discord.ext import commands

# url formatter
def urlify(string):
    # Replace all runs of whitespace with a single dash
    string = re.sub(r"\s+", '&space;', string)
    string.replace("\\", "\\\\")
    string = string[1:-1]
    return string

class Equation(commands.Cog):

    def __init__(self, client):
        self.client = client

    # equation render
    @commands.command()
    async def equation(self, ctx, *, equation):
        await ctx.send('test1')
        equation = urlify(equation)
        await ctx.send('test2')
        equ_url = f'https://latex.codecogs.com/png.latex?\\dpi{{200}}&space;\\bg_white&space;{equation}'
        print(equ_url)
        equ = discord.Embed()
        equ.set_image(url= equ_url)

        await ctx.message.delete()
        await ctx.send(embed=equ)

def setup(client):
    client.add_cog(Equation(client))
