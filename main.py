import discord
import os
client = discord.Client()
import crypto
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("DISCORD_KEY")
    
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    command, *args = message.content.split(" ", 5)
    response = []
    print(command)
    print(args)
    if message.content.startswith('!'):
        match command:
            case '!help':
                f = open("goosebot-main\help.txt", "r")
                response = f.read()
                f.close
            case '!coin':
                response = crypto.getCrypto(args)
            case _:
                response = ["**ERROR:** Unrecognized command _(Try using !help)_"]

        for x in response:
            if x[0] != '~':
                await message.channel.send(x)
            else:
                comm, expr = x.split('~')
                await message.channel.send(file = eval(expr))
    
client.run(key)

