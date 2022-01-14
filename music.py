from youtube_dl import YoutubeDL
from discord import FFmpegPCMAudio
from discord import TextChannel
from discord.utils import get
import discord

async def join(ctx, client):
    channel = ctx.message.author.voice.channel
    voice = get(client.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()


async def play(ctx, client, *url):
    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn', 'executable': "C:/ffmpeg/bin/ffmpeg.exe"}
    voice = get(client.voice_clients, guild=ctx.guild)

    if not voice.is_playing() and url:
        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
        URL = info['url']
        voice.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))
        voice.is_playing()
        await ctx.send('Bot is playing')
    elif not voice.is_playing():
        voice.resume()
        await ctx.send('Bot is resuming')
    else:
        await ctx.send('Bot is already playing')
        return

# command to pause voice if it is playing
async def pause(ctx, client):
    voice = get(client.voice_clients, guild=ctx.guild)

    if voice.is_playing():
        voice.pause()
        await ctx.send('Bot has been paused')


# command to stop voice
async def stop(ctx, client):
    voice = get(client.voice_clients, guild=ctx.guild)

    if voice.is_playing():
        voice.stop()
        await ctx.send('Stopping...')
