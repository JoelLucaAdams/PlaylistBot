import discord
from cogs.youtube_api import youtube_api
from cogs.youtube_api import Playlists
from discord.ext import commands
from discord.ext.commands import Context
from discord import Embed

import time
import re
from datetime import datetime
from urllib.parse import urlparse
from urllib.parse import parse_qs


class Utilities(commands.Cog):
    """
    General Utilities
    """

    @commands.command()
    async def ping(self, ctx: Context):
        """
        Status check
        """
        start_time = time.time()
        message = await ctx.send('🏓 pong. `DWSPz latency: ' + str(round(ctx.bot.latency * 1000)) + 'ms`')
        end_time = time.time()
        await message.edit(content='🏓 pong. `DWSP latency: ' + str(round(ctx.bot.latency * 1000)) + 'ms` ' +
                                   '`Response time: ' + str(int((end_time - start_time) * 1000)) + 'ms`')

    @commands.command()
    async def source(self, ctx: Context):
        """
        Print a link to the source code
        """
        await ctx.send(content='Created by `Joel Adams`\n'
                               'https://github.com/JoelLucaAdams/ManPageBot')

class Youtube(commands.Cog):
    """
    Youtube commands
    """

    @commands.command()
    async def add(self, ctx: Context, playlist_index: int, yt_link: str):
        """
        Adds a song to the playlist
        """
        # delete previous message to avoid duplication
        await ctx.message.delete()

        # Split up yotube link into video ID and shortened clickable link
        parsed = urlparse(yt_link)
        if yt_link.__contains__('https://www.youtube.com/'):
            yt_link_id = parse_qs(parsed.query)['v'][0]
            yt_link_short = yt_link.split('&')[0]
        elif yt_link.__contains__('https://youtu.be/'):
            yt_link_id = parsed.path.split('/')[1]
            yt_link_short = yt_link
        else:
            await ctx.send('Invalid url passed...')
            raise Exception(commands.errors.BadArgument)

        playlistId = Playlists[youtube_api.get_local_playlist_key(playlist_index)]

        # Calls request to add video to playlist and gets information from video
        video_added_to_playlist = youtube_api.add_video(playlistId=playlistId, videoId=yt_link_id)

        request = youtube_api.find_video(videoId=yt_link_id)
        video_thumbnail = request['items'][0]['snippet']['thumbnails']['maxres']['url']
        video_name = request['items'][0]['snippet']['title']
        video_duration = request['items'][0]['contentDetails']['duration']
        video_channel = request['items'][0]['snippet']['channelTitle']

        playlist_name = youtube_api.find_playlist(video_added_to_playlist['snippet']['playlistId'])['items'][0]['snippet']['localized']['title']
        playlist_url = f'https://www.youtube.com/playlist?list={playlistId}'

        playlist_length = youtube_api.get_playlist_length(playlistId)

        #formats the video duration
        hours_pattern = re.compile(r'(\d+)H')
        minutes_pattern = re.compile(r'(\d+)M')
        seconds_pattern = re.compile(r'(\d+)S')

        hours = hours_pattern.search(video_duration)
        minutes = minutes_pattern.search(video_duration)
        seconds = seconds_pattern.search(video_duration)

        hours = int(hours.group(1)) if hours else 0
        minutes = int(minutes.group(1)) if minutes else 0
        seconds = int(seconds.group(1)) if seconds else 0

        if hours != 0:
            formatted_video_time = f'{hours}:{minutes}:{seconds}'
        else:
            formatted_video_time = f'{minutes}:{seconds}'

        # Creates Embed to send to discord with information on song
        embed = Embed(title='Song Added!', colour=discord.Colour.from_rgb(255, 0, 0), timestamp=datetime.utcnow())
        embed.set_thumbnail(url=f'{video_thumbnail}')
        embed.add_field(name='🎶 Song', value=f'{video_name} - [link]({yt_link_short})', inline=False)
        embed.add_field(name='⏱️ Song Length', value=f'{formatted_video_time}', inline=True)
        embed.add_field(name='📋 Channel Name', value=f'{video_channel}', inline=True)
        embed.add_field(name='📼 Playlist', value=f'{playlist_name} - [link]({playlist_url})', inline=False)
        embed.add_field(name='⏱️ Playlist Length', value=f'{playlist_length}', inline=True)
        embed.set_footer(icon_url=ctx.author.avatar_url, text= f'Added by {ctx.author.display_name}')
        await ctx.send(embed=embed)

    @commands.command()
    async def playlists(self, ctx: Context):
        """
        Prints a list of all playlists
        """
        
        embed = Embed(title='🎧 Playlists available', colour=discord.Colour.green())
        i = 0
        for item in Playlists:
            embed.add_field(name=f'{i} - {item}', value=f'[link](https://www.youtube.com/playlist?list={Playlists[item]})', inline=False)
            i += 1
        await ctx.send(embed=embed)