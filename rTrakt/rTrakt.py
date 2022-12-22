import aiohttp
import datetime
import json
import os
import requests

import discord
from redbot.core import Config, commands

class rTrakt(commands.Cog):
    """Show the scrobbler status in the bot's rich presence"""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=9811198108111121, force_registration=True)
        self.config.register_global(client_id=None, client_secret=None, redirect_uri=None, access_token=None, refresh_token=None, access_token_expiry=None)
        self.session = aiohttp.ClientSession(loop=bot.loop)
        self.auth_url = None  # Add this line to define auth_url as an attribute of the rTrakt cog

    async def setup(self, bot):
        """Set up the cog"""
        self.bot = bot
        self.session = aiohttp.ClientSession(loop=bot.loop)

        # Get the client ID, client secret, and redirect URI from the config
        client_id = await self.config.client_id()
        client_secret = await self.config.client_secret()
        redirect_uri = await self.config.redirect_uri()

        # Initiate the OAuth authentication process
        self.auth_url = f"https://trakt.tv/oauth/authorize?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}" 

    @commands.command()
    async def traktauth(self, ctx):
        """Get the authorization URL for the Trakt API"""
        await ctx.send(self.auth_url)

    @commands.command()
    async def traktauthcomplete(self, ctx, code: str):
        """Complete the OAuth authentication process"""
        # Get the client ID, client secret, and redirect URI from the config
        client_id = await self.config.client_id()
        client_secret = await self.config.client_secret()
        redirect_uri = await self.config.redirect_uri()

        # Exchange the authorization code for an access token
        response = requests.post("https://api.trakt.tv/oauth/token", headers={
            "Content-Type": "application/json",
        }, data=json.dumps({
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "code": code,
            "grant_type": "authorization_code",
        }))
        response.raise_for_status()
        token_response = response.json()

        # Save the access token, refresh token, and access token expiry in the config
        await self.config.access_token.set(token_response["access_token"])
        await self.config.refresh_token.set(token_response["refresh_token"])
        expires_in = token_response["expires_in"]
        access_token_expiry = datetime.datetime.utcnow() + datetime.timedelta(seconds=expires_in)

    @commands.Cog.listener()
    async def on_ready(self):
        """Update the bot's rich presence when the bot is ready"""
        await self.update_rich_presence()

    async def update_rich_presence(self):
        """Update the bot's rich presence with the scrobbler status"""
        # Check if the access token has expired
        if datetime.datetime.utcnow() > self.access_token_expiry:
            # Refresh the access token
            async with self.session.post("https://api.trakt.tv/oauth/token", headers={
                "Content-Type": "application/json",
            }, data=json.dumps({
                "client_id": await self.config.client_id(),
                "client_secret": await self.config.client_secret(),
                "redirect_uri": await self.config.redirect_uri(),
                "refresh_token": await self.config.refresh_token(),
                "grant_type": "refresh_token",
            })) as response:
                response.raise_for_status()
                token_response = await response.json()

                # Save the new access token and access token expiry in the config
                await self.config.access_token.set(token_response["access_token"])
                expires_in = token_response["expires_in"]
                self.access_token_expiry = datetime.datetime.utcnow() + datetime.timedelta(seconds=expires_in)

        # Get the access token from the config
        access_token = await self.config.access_token()

        # Get the scrobbler status from the Trakt API
        async with self.session.get("https://api.trakt.tv/sync/playback", headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
            "trakt-api-version": "2",
            "trakt-api-key": await self.config.client_id(),
        }) as response:
            response.raise_for_status()
            scrobbler_status = await response.json()

        # Update the bot's rich presence
        if scrobbler_status:
            if scrobbler_status["movie"]:
                movie = scrobbler_status["movie"]
                movie_title = movie["title"]
                movie_year = movie["year"]
                movie_time = datetime.timedelta(seconds=int(scrobbler_status["progress"]))
                movie_duration = datetime.timedelta(seconds=movie["runtime"])
                movie_progress = f"{movie_time}/{movie_duration}"
                await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{movie_title} ({movie_year}) - {movie_progress}"))
            elif scrobbler_status["episode"]:
                episode = scrobbler_status["episode"]
                show_title = episode["show"]["title"]
                episode_title = episode["title"]
                episode_season = episode["season"]
                episode_number = episode["number"]
                episode_time = datetime.timedelta(seconds=int(scrobbler_status["progress"]))
                episode_duration = datetime.timedelta(seconds=episode["runtime"])
                episode_progress = f"{episode_time}/{episode_duration}"
                await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{show_title} S{episode_season:02d}E{episode_number:02d} - {episode_title} - {episode_progress}"))
        else:
            await self.bot.change_presence(activity=None)

def setup(bot):
    """Set up the cog"""
    bot.add_cog(rTrakt(bot))