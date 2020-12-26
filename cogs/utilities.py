import discord
from cogs.youtube_api import youtube_api
from discord.ext import commands
from discord.ext.commands import Context
from discord import Embed

import time
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
        message = await ctx.send('pong. `DWSPz latency: ' + str(round(ctx.bot.latency * 1000)) + 'ms`')
        end_time = time.time()
        await message.edit(content='pong. `DWSP latency: ' + str(round(ctx.bot.latency * 1000)) + 'ms` ' +
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
    async def add(self, ctx: Context, yt_link: str):
        """
        Adds a song to the playlist
        """
        # Split up yotube link into video ID and shortened clickable link
        parsed = urlparse(yt_link)
        yt_link_id = parse_qs(parsed.query)['v'][0]
        yt_link_short = yt_link.split('&')[0]

        playlistId ='PLXfw-OhAIheRIwSuBzbva5nzRxCMftKz1'

        # Calls request to add video to playlist and gets information from video
        request = youtube_api.add_video(playlistId=playlistId, videoId=yt_link_id)
        video_thumbnail = request['snippet']['thumbnails']['default']['url']
        video_name = request['snippet']['title']
        playlist_name = youtube_api.find_playlist(request['snippet']['playlistId'])['items'][0]['snippet']['localized']['title']

        # Creates Embed to send to discord with information on song
        embed = Embed(title='Song Added!', colour=discord.Colour.red())
        embed.set_thumbnail(url=f'{video_thumbnail}')
        embed.add_field(name='Song', value=f'{video_name}\nLink: {yt_link_short}', inline=False)
        embed.add_field(name='Playlist', value=f'{playlist_name}', inline=False)
        embed.set_footer(icon_url=ctx.author.avatar_url, text= f'Added by {ctx.author.display_name}')
        await ctx.send(embed=embed)