import discord
import asyncio
import youtube_dl

from discord.ext import commands
from discord.utils import get

# Initialize the Discord client and the command prefix
client = commands.Bot(command_prefix='/')

# Define a list to store the queued songs for each guild
queues = {}

# Define a dictionary to store the playlists for each user
playlists = {}

# Define the options for the youtube_dl downloader
ytdl_opts = {
    'format': 'bestaudio/best',
    'quiet': True,
    'extractaudio': True,
    'audioformat': 'mp3',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'source_address': '0.0.0.0'
}

# Define a function to download a song from a Youtube URL and return the filename
def download_song(url):
    with youtube_dl.YoutubeDL(ytdl_opts) as ytdl:
        info = ytdl.extract_info(url, download=True)
        filename = ytdl.prepare_filename(info)
    return filename

# Define a function to add a song to the queue
def add_to_queue(ctx, song):
    guild = ctx.guild
    if guild not in queues:
        queues[guild] = []
    queues[guild].append(song)

# Define a function to play the next song in the queue
async def play_next_song(ctx):
    guild = ctx.guild
    if guild in queues and len(queues[guild]) > 0:
        filename = download_song(queues[guild][0])
        voice_channel = get(guild.voice_channels, name='Music')
        if voice_channel is not None:
            voice_client = await voice_channel.connect()
            voice_client.play(discord.FFmpegPCMAudio(filename), after=lambda e: asyncio.run_coroutine_threadsafe(play_next_song(ctx), client.loop))
            queues[guild].pop(0)
        else:
            await ctx.send('You need to be in the Music voice channel to play music!')
    else:
        await ctx.send('The queue is empty!')

# Define a function to create a playlist for a user
def create_playlist(user):
    if user not in playlists:
        playlists[user] = []

# Define a command to add a song to the queue
@client.command()
async def play(ctx, url):
    add_to_queue(ctx, url)
    await ctx.send('Song added to the queue!')
    if not ctx.voice_client.is_playing():
        await play_next_song(ctx)

# Define a command to skip the current song
@client.command()
async def skip(ctx):
    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send('Song skipped!')
        await play_next_song(ctx)
    else:
        await ctx.send('No song is currently playing!')

# Define a command to show the current queue
@client.command()
async def queue(ctx):
    if ctx.guild in queues and len(queues[ctx.guild]) > 0:
        queue_str = 'Current queue:\n'
        for i, song in enumerate(queues[ctx.guild]):
            queue_str += f'{i + 1}. {song}\n'
        await ctx.send(queue_str)
    else:
        await ctx.send('The queue is empty!')

# Define a command to create a playlist
@client.command()
async def create(ctx):
    user = ctx.author
    create_playlist(user)
    await ctx.send('Playlist created!')

# Define a command to add a song to a playlist
@client.command()