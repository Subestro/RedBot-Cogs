import discord
from redbot.core import Config, commands, tasks
from redbot.core.data_manager import cog_data_path
import requests
import json

class rTrakt(commands.Cog):
    """Shows your Trakt scrobbler status in the bot's rich presence."""

    # The interval at which to update the presence (in seconds)
    update_presence_interval = 60

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1010011010)
        default_global = {
            "client_id": None,
            "client_secret": None,
            "access_token": None,
            "refresh_token": None
        }
        self.config.register_global(**default_global)
        self.authorization_task = None

        # Start the presence update task
        self.presence_update = tasks.loop(self.update_presence_interval, self.set_presence)
        self.presence_update.start()

    def __unload(self):
        """Stops the presence update task."""
        self.presence_update.cancel()

    async def set_presence(self):
        """Sets the bot's rich presence."""
        # Get the user's currently playing media from the Trakt API
        url = "https://api.trakt.tv/users/me/watched/progress/all"
        headers = {"Content-Type": "application/json", "trakt-api-version": "2", "trakt-api-key": await self.config.client_id(), "Authorization": f"Bearer {await self.config.access_token()}"}
        async with self.bot.session.get(url, headers=headers) as response:
            # Check if the request was successful
            if response.status != 200:
                return

            # Get the response data
            data = await response.json()

            # Set the media data
            media = data[0] if data else None
            media_title = media["show"]["title"] if media["type"] == "show" else media["movie"]["title"]
            media_type = media["type"]
            media_progress = media["progress"]
            media_duration = media["show"]["aired_episodes"] if media_type == "show" else media["movie"]["runtime"]
            media_runtime = f"{media_progress}/{media_duration} {media_type}"

        # Set the presence data
        presence_data = {
            "state": f"Watching {media_title}",
            "details": media_runtime,
            "large_image_key": "trakt_logo",
            "small_image_key": "play",
            "small_image_text": "Playing"
        }

        # Set the presence
        presence = discord.Game(**presence_data)
        await self.bot.change_presence(activity=presence)

    @commands.command(name="displaycode")
    async def display_code(self, ctx):
        """Displays the authorization link and code for the Trakt API."""
        # Get the client ID and client secret
        client_id = await self.config.client_id()
        client_secret = await self.config.client_secret()

        if not client_id or not client_secret:
            return await ctx.send("The client ID and client secret have not been set. Use the `trakt set` command to set them.")

        # Set the authorization URL
        authorization_url = f"https://trakt.tv/oauth/authorize?response_type=code&client_id={client_id}&redirect_uri=urn:ietf:wg:oauth:2.0:oob"

        # Send the authorization request
        await ctx.send(f"To authorize the Trakt API for your account, visit the following URL and enter the authorization code:\n{authorization_url}\n\nOnce you have the authorization code, use the `trakt auth` command to complete the authorization process.")

    @commands.command(name="auth")
    async def poll_for_authorization(self, ctx, code: str):
        """Polls for authorization of the Trakt API."""
        # Get the client ID, client secret, and redirect URI
        client_id = await self.config.client_id()
        client_secret = await self.config.client_secret()
        redirect_uri = "urn:ietf:wg:oauth:2.0:oob"

        if not client_id or not client_secret:
            return await ctx.send("The client ID and client secret have not been set. Use the `trakt set` command to set them.")

        # Set the URL and headers for the API request
        url = "https://api.trakt.tv/oauth/token"
        headers = {"Content-Type": "application/json", "trakt-api-version": "2", "trakt-api-key": client_id}
        data = {"code": code, "client_id": client_id, "client_secret": client_secret, "redirect_uri": redirect_uri, "grant_type": "authorization_code"}

        # Send the API request
        async with self.bot.session.post(url, headers=headers, json=data) as response:
            # Check if the request was successful
            if response.status != 200:
                return await ctx.send("Failed to authorize the Trakt API. Please ensure that you have entered the correct authorization code and try again.")

            # Get the response data
            data = await response.json()

            # Set the access token and refresh token
            access_token = data["access_token"]
            refresh_token = data["refresh_token"]
            await self.config.access_token.set(access_token)
            await self.config.refresh_token.set(refresh_token)

        # Send the success message
        await ctx.send("Successfully authorized the Trakt API for your account.")
        # Set the interval for updating the presence
        interval = 30  # Update the presence every 30 seconds

        # Start the presence update task
        self.presence_update.start(interval)

    @tasks.loop(seconds=30)
    async def presence_update(self):
        """Updates the bot's rich presence with the user's currently playing media."""
        # Get the access token
        access_token = await self.config.access_token()

        if not access_token:
            return

        # Set the headers for the API request
        headers = {"Authorization": f"Bearer {access_token}", "trakt-api-version": "2", "trakt-api-key": self.client_id}

        # Send the API request to get the user's currently playing media
        async with self.bot.session.get("https://api.trakt.tv/sync/playback", headers=headers) as response:
            # Check if the request was successful
            if response.status != 200:
                return

            # Get the response data
            data = await response.json()

            # Check if there is currently playing media
            if not data:
                return

            # Get the media type and title
            media_type = data["type"]
            title = data["movie"]["title"] if media_type == "movie" else data["show"]["title"]
            episode = data["episode"]["title"] if media_type == "episode" else None

            # Set the presence
            if media_type == "movie":
                presence = f"Watching {title}"
            elif media_type == "episode":
                presence = f"Watching {title} - {episode}"
            else:
                presence = f"Listening to {title}"

            # Update the presence
            await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=presence))
