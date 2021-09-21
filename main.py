from discord.ext import commands
import discord
import youtube_dl
import youtube_search
import queue
import logging

logging.basicConfig(level=logging.INFO)


# Fields


client = commands.Bot(command_prefix = '*')
client.remove_command('help')
client.activity = discord.Activity(type=discord.ActivityType.listening, name="*help")
playlist = queue.Queue()
naruto_trap = 'https://www.youtube.com/watch?v=WmsNDyzfYkw'

#======================================================================================================
# Helper functions
#======================================================================================================


def valid_url(url):
    extractors = youtube_dl.extractor.gen_extractors()
    for e in extractors:
        if e.suitable(url) and e.IE_NAME != 'generic':
            return True
    return False

def next_in_queue(e, ctx):
    voice_bot = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if not playlist.empty():
        voice_bot.play(discord.FFmpegPCMAudio(playlist.get()), after=lambda e: next_in_queue(e, ctx))

#======================================================================================================
# Bot Functionality
#======================================================================================================


@client.event
async def on_ready():
    print("Ready :()()()")


@client.command()
async def help(ctx):
    embed = discord.Embed(title='Commands :()()()()()', colour=discord.Colour.blue())
    embed.add_field(name='*yt', value='Plays the given youtube video. You can pass a youtube URL or multiple search phrases and the most matching video will be played.')
    embed.add_field(name='*play', value='Plays the given mp3 sound file. You just need to pass the file name.')
    embed.add_field(name='*skip', value='Stops the current video/sound file and continues with the successor in the queue if there is one.')
    embed.add_field(name='*stop', value='Stops the current video/sound file and deletes the queue content.')
    embed.add_field(name='*pause', value='Pauses the current video/sound file.')
    embed.add_field(name='*resume', value='Resumes the paused video/sound file.')
    embed.add_field(name='*dc', value='Disconnects the bot :(')
    await ctx.send(embed=embed)


@client.command()
async def play(ctx, soundfile):
    voice = ctx.author.voice
    voice_bot = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice:
        channel = voice.channel
        if not voice_bot:
            await channel.connect()
        voice_bot = discord.utils.get(client.voice_clients, guild=ctx.guild)
        if not voice_bot.is_playing():
            voice_bot.play(discord.FFmpegPCMAudio("sound_files/" + soundfile + ".mp3"), after=lambda e: next_in_queue(e, ctx))
        else:
            playlist.put("sound_files/" + soundfile + ".mp3")
            await ctx.send("Queued @" + str(ctx.author) + ", size of Queue: " + str(playlist.qsize()) + " :()")

    else:
        await ctx.send("You must be in a voice channel to run this command :()")

@client.command()
async def dc(ctx):
    voice_bot = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice_bot:
        if voice_bot.is_playing():
            voice_bot.stop()
            playlist.empty()
        await voice_bot.disconnect()
    else: 
        await ctx.send("I am not in a voice channel :()")

@client.command()
async def yt(ctx, *args):
    voice = ctx.author.voice
    voice_bot = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice:
        channel = voice.channel
        if not voice_bot:
            await channel.connect()
        voice_bot = discord.utils.get(client.voice_clients, guild=ctx.guild)
        YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True', 'defaultsearch':'ytsearch'}
        if len(args) == 1 and valid_url(args[0]):
            with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(args[0], download=False)
        else:
            arg = ""
            for s in args:
                arg += s + " "
            url_suff = youtube_search.YoutubeSearch(arg, max_results=1).to_dict()[0]['url_suffix']
            with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info('https://www.youtube.com' + str(url_suff), download=False)
        url = info['formats'][0]['url']
        if not voice_bot.is_playing():
            voice_bot.play(discord.FFmpegPCMAudio(url), after=lambda e: next_in_queue(e, ctx))
        else:
            playlist.put(url)
            await ctx.send("Queued @" + str(ctx.author) + ", size of Queue: " + str(playlist.qsize()) + " :()")
    else:
        await ctx.send("You must be in a voice channel to run this command :()")

@client.command()
async def skip(ctx):
    voice_bot = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice_bot:
        if voice_bot.is_playing():
            voice_bot.stop()
            if not playlist.empty():
                voice_bot.play(discord.FFmpegPCMAudio(playlist.get()), after=lambda e: next_in_queue(e, ctx))
                await ctx.send("Playing next url, new size of Queue: " + str(playlist.qsize()) + " :()")
        else:
            await ctx.send("I am not playing anything :()")
    else:
        await ctx.send("I am not in a voice channel :()")

@client.command()
async def stop(ctx):
    voice_bot = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice_bot:
        if voice_bot.is_playing():
            voice_bot.stop()
            playlist.empty()
            await ctx.send("Stopped and removed queued urls :()")
        else:
            await ctx.send("I am not playing anything :()")
    else:
        await ctx.send("I am not in a voice channel :()")

@client.command()
async def pause(ctx):
    voice_bot = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice_bot:
        if voice_bot.is_playing():
            voice_bot.pause()
            await ctx.send("Paused current track :()")
        else:
            await ctx.send("I am not playing anything :()")
    else:
        await ctx.send("I am not in a voice channel :()")

@client.command()
async def resume(ctx):
    voice_bot = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice_bot:
        if not voice_bot.is_playing():
            voice_bot.resume()
            await ctx.send("Resumed current track :()")
        else:
            await ctx.send("I am already playing something at the moment :()")
    else:
        await ctx.send("I am not in a voice channel :()")

#======================================================================================================
# Debugging command
#======================================================================================================

@client.command()
async def test(ctx, link):
    print("debugging message: test was called :()")
    await ctx.send("Only used for debugging purposes :()")
   
#======================================================================================================
# Run Bot
#======================================================================================================

token = ""
with open("bot_token.txt", 'r') as file:
    token = file.read().replace('\n', '')

client.run(token)
        