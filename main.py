import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import youtube_dl
import asyncio

load_dotenv(dotenv_path="config")
bot = commands.Bot(command_prefix="µ")


@bot.event
async def on_ready():
    print("He's alive !")


@bot.command(name="hello")
async def hello(ctx):
    await ctx.channel.send('Hello ! Je suis Potat et je joue de la musique')


@bot.command(name="command")
async def command(ctx):
    await ctx.channel.send('Mon préfix est µ et mes commandes sont :')
    await ctx.channel.send('hello')
    await ctx.channel.send('command')
    await ctx.channel.send('join (pour me faire rejoindre un voc)')
    await ctx.channel.send('leave (pour me faire quitter un voc)')
    await ctx.channel.send('play (pour me faire jouer une chanson)')
    await ctx.channel.send('pause (pour mettre en pause une chanson)')
    await ctx.channel.send('resume (pour continuer une chanson)')
    await ctx.channel.send('stop (pour arreter une chanson)')


youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = ""

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
        filename = data['title'] if stream else ytdl.prepare_filename(data)
        return filename


@bot.command(name='join')
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send("{}, rejoint un voc d'abord. ".format(ctx.message.author.name))
        return
    else:
        channel = ctx.message.author.voice.channel
    await channel.connect()


@bot.command(name='leave')
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected():
        await voice_client.disconnect()


@bot.command(name='play')
async def play(ctx, url):
    try:
        server = ctx.message.guild
        voice_channel = server.voice_client
        async with ctx.typing():
            filename = await YTDLSource.from_url(url, loop=bot.loop)
            voice_channel.play(discord.FFmpegPCMAudio(executable="ffmpeg.exe", source=filename))
        await ctx.send('**Chanson:** {}'.format(filename))
    except:
        await ctx.send("Je ne suis pas dans un voc -_- ")


@bot.command(name='pause')
async def pause(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.pause()
    else:
        await ctx.send("Je ne suis pas entrain de jouer une chanson -_-")


@bot.command(name='resume', help='Resumes the song')
async def resume(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_paused():
        await voice_client.resume()
    else:
        await ctx.send("Je ne suis pas entrain de jouer une chanson -_-")


@bot.command(name='stop', help='Stops the song')
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.stop()
    else:
        await ctx.send("Je ne suis pas entrain de jouer une chanson -_-")
bot.run(os.getenv("TOKEN"))
