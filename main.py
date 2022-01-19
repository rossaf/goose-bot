import discord
import os
client = discord.Client()
import crypto
import music
from discord.ext import commands
from discord.utils import get
from dotenv import load_dotenv
import chessdriver

client = commands.Bot(command_prefix='!', help_command=None)

load_dotenv()
key = os.getenv("DISCORD_KEY")

@client.command()
async def help(ctx):
    embed=discord.Embed(title="Help Menu")
    embed.add_field(name="Chess Commands:", value="!chess challenge {@player} \n !chess accept {gameid} \n !chess move {to} {from} {gameid} \n !chess concede {gameid} \n !chess list {@player} \n !chess view {game_id}", inline=False)
    embed.add_field(name="Music Commands:", value="!yt join \n !yt play {yt url} \n !yt stop", inline=False)
    embed.add_field(name="Crypto Commands:", value="!coin get {coin} {compared to(USD, ETH, etc.)} {period (3m, 1d, 1w)} \n !coin top", inline=False)
    await ctx.send(embed=embed)

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.command()
async def yt(ctx, command, *args):
    if command == 'play':
        await music.play(ctx, client, *args)
    elif command == 'pause':
        music.play()
    elif command == 'stop':
        music.stop()
    elif command == 'queue':
        music.queue()
    else:
        await music.join(ctx, client)
@yt.error
async def yt_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('**You need to specify a command argument...** (ex. play, pause, stop, queue)')
    else:
        await ctx.send(str(err))

@client.command()
async def coin(ctx, *args):
    async with ctx.typing():
        response = crypto.getCrypto(args)
        await sendChat(response, ctx)

@client.command()
async def chess(ctx, command, *args):
    async with ctx.typing():
        if command == 'challenge':
            await chessdriver.challenge(ctx, client, *args)
        if command == 'accept':
            await chessdriver.accept(ctx, client, *args)
        if command == 'view':
            await chessdriver.view(ctx, client, *args)
        if command == 'concede':
            await chessdriver.concede(ctx, *args)
        if command == 'move':
            await chessdriver.move(ctx, client, *args)
        if command == 'list':
            await chessdriver.list(ctx, client, *args)


async def sendChat(response, ctx):
    for x in response:
        if x[0] != '~':
            await ctx.send(x)
        elif x[0] == '~':
            comm, expr = x.split('~', 1)
            await ctx.send(file = eval(expr))
        elif x[0] == '>':
            comm, expr = x.split('>', 1)
            await eval(expr)
            
client.run(key)

