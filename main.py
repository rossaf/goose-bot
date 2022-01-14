import discord
import os
client = discord.Client()
import crypto
import music
from discord.ext import commands
from discord.utils import get
from dotenv import load_dotenv
import chessdriver

client = commands.Bot(command_prefix='!')

load_dotenv()
key = os.getenv("DISCORD_KEY")
    
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

@client.command()
async def coin(ctx, *args):
    response = crypto.getCrypto(args)
    await sendChat(response, ctx)

@client.command()
async def chess(ctx, command, *args):
    if command == 'challenge':
        response = chessdriver.challenge(ctx, *args)
    if command == 'accept':
        response = chessdriver.accept(*args)
    if command == 'view':
        response = chessdriver.view(*args)
    if command == 'move':
        response = chessdriver.move(ctx, *args)
    await sendChat(response, ctx)


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

