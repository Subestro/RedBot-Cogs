import aiohttp
import asyncio
import discord
from discord.ext import commands, tasks
from redbot.core import Config
from redbot.core.bot import Red
from redbot.core import commands
from redbot.core.utils.chat_formatting import pagify
from redbot.core.utils.menus import menu, DEFAULT_CONTROLS
from redbot.core import checks
from redbot.core.utils.predicates import MessagePredicate
from urllib.parse import urlencode

class rTrakt(commands.Cog):
    update_presence_interval = 60
    """Shows your Trakt scrobbler status in the bot's rich presence."""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1010011010)

        default_global = {"client_id": None, "client_secret": None, "access_token": None, "refresh_token": None}
        self.config.register_global(**default_global)

        self.presence_update = tasks.loop(self.update_presence_interval, self.set_presence)

    def cog_unload(self):
        self.update_presence.cancel()

    @tasks.loop(minutes=1.0)
    async def update_presence(self):
        """Updates the bot's rich presence with the user's currently playing media."""
        # Get the access token from the cog's configuration
        access_token = await self.config.access_token()

        # Check if the access token is set
        if access_token is None:
            return

        # Set the headers for the API request
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        # Make the API request to get the user's currently playing media
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.trakt.tv/sync/playback", headers=headers) as resp:
                # Check if the request was successful
                if resp.status != 200:
                    return

                # Get the response data
                data = await resp.json()

                # Get the currently playing media
                media = data[0]["progress"]

                # Check if there is currently playing media
                if media == 0:
                    return

                # Set the media information
                show_name = data[0]["show"]["title"]
                season_number = data[0]["episode"]["season"]
                episode_number = data[0]["episode"]["number"]
                episode_name = data[0]["episode"]["title"]
                runtime = data[0]["show"]["runtime"]

                # Set the presence
                presence = discord.Game(f"{show_name} S{season_number:02d}E{episode_number:02d} - {episode_name} ({runtime}m)")
                await self.bot.change_presence(activity=presence)

    @commands.command(name="generatecodes")
    @commands.guild_only()
    async def generate_codes(self, ctx):
        """Generates authorization codes for the Trakt API."""
        # Get the client ID and secret from the cog's configuration
        client_id = await self.config.client_id()
        client_secret = await self.config.client_secret()

        # Check if the client ID and secret are set
        if client_secret is None:
            return await ctx.send("The client ID or secret is not set. Set them using the `trakt set` command.")

        # Set the authorization URL
        auth_url = (
            f"https://trakt.tv/oauth/authorize?response_type=code&client_id={client_id}&redirect_uri=urn:ietf:wg:oauth:2.0:oob"
        )

        # Send the authorization request
        await ctx.send(f"Authorization link: {auth_url}\nEnter the authorization code below to exchange it for an access token.")

        # Wait for the authorization code
        pred = MessagePredicate.valid_int()
        try:
            code = await self.bot.wait_for("message", check=pred, timeout=60)
        except asyncio.TimeoutError:
            return await ctx.send("Timed out waiting for authorization code.")

        # Set the data for the API request
        data = {
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": "urn:ietf:wg:oauth:2.0:oob",
            "grant_type": "authorization_code",
        }

        # Set the headers for the API request
        headers = {
            "Content-Type": "application/json",
        }

        # Make the API request to exchange the code for an access token
        async with aiohttp.ClientSession() as session:
            async with session.post("https://api.trakt.tv/oauth/token", json=data, headers=headers) as resp:
                # Check if the request was successful
                if resp.status != 200:
                    return await ctx.send("Failed to exchange code for access token.")

                # Get the response data
                data = await resp.json()

                # Set the access and refresh tokens in the cog's configuration
                await self.config.access_token.set(data["access_token"])
                await self.config.refresh_token.set(data["refresh_token"])

                # Confirm the access and refresh tokens were set
                await ctx.send("Successfully exchanged code for access token and refresh token.")

    @commands.command(name="displaycode")
    @commands.guild_only()
    async def display_code(self, ctx):
        """Displays the client ID and secret."""
        # Get the client ID and secret from the cog's configuration
        client_id = await self.config.client_id()
        client_secret = await self.config.client_secret()

        # Check if the client ID and secret are set
        if client_id is None or client_secret is None:
            return await ctx.send("The client ID or secret is not set. Set them using the `trakt set` command.")

        # Send the client ID and secret
        await ctx.send(f"Client ID: {client_id}\nClient secret: {client_secret}")

    @commands.command(name="trakt")
    @commands.guild_only()
    async def trakt(self, ctx, *, subcommand: str):
        """Manages the Trakt API integration."""
        # Split the subcommand into the command and arguments
        parts = subcommand.split()
        command = parts[0]
        args = parts[1:]

        # Check which command was used
        if command == "generatecodes":
            return await self.generate_codes(ctx)
        elif command == "set":
            return await self.set_codes(ctx, *args)
        elif command == "poll":
            return await self.poll_authorization(ctx)
        elif command == "authorize":
            return await self.authorize(ctx, *args)

    async def generate_codes(self, ctx):
        """Generates the client ID and secret."""
        # Set the authorization URL
        url = "https://trakt.tv/oauth/authorize"
        redirect_url = "urn:ietf:wg:oauth:2.0:oob"
        client_id = "1010011010"

        # Build the authorization URL
        authorization_url = f"{url}?response_type=code&client_id={client_id}&redirect_uri={redirect_url}"

        # Send the authorization URL
        await ctx.send(f"To generate the client ID and secret, visit the following URL and authorize the application:\n\n{authorization_url}")

    async def set_codes(self, ctx, *args):
        """Sets the client ID and secret."""
        # Check if the correct number of arguments was given
        if len(args) != 2:
            return await ctx.send("Invalid number of arguments. Use `trakt set [client_id] [client_secret]`.")

        # Set the client ID and secret
        await self.config.client_id.set(args[0])
        await self.config.client_secret.set(args[1])

        await ctx.send("The client ID and secret have been set.")

    async def poll_authorization(self, ctx):
        """Polls for authorization."""
        # Set the URL and headers for the API request
        url = "https://api.trakt.tv/oauth/device/code"
        headers = {"Content-Type": "application/json", "trakt-api-version": "2", "trakt-api-key": await self.config.client_id()}

        # Set the payload for the API request
        payload = {"client_id": await self.config.client_id(), "redirect_uri": "urn:ietf:wg:oauth:2.0:oob"}

        # Send the API request
        async with self.bot.session.post(url, headers=headers, json=payload) as response:
            # Check if the request was successful
            if response.status != 200:
                return await ctx.send("An error occurred while generating the authorization code.")

            # Get the response data
            data = await response.json()

            # Set the authorization data in the cog's configuration
            await self.config.authorization_code.set(data["device_code"])
            await self.config.authorization_verification_url.set(data["verification_url"])
            await self.config.authorization_expires_in.set(data["expires_in"])
            await self.config.authorization_interval.set(data["interval"])

        # Send the authorization instructions
        await ctx.send(f"To authorize the application, visit the following URL:\n\n{data['verification_url']}\n\nThen enter the following code:\n\n{data['user_code']}")

        # Start the authorization polling task
        self.authorization_task = self.bot.loop.create_task(self.poll_authorization_task())

    async def poll_authorization_task(self):
        """Polls for authorization."""
        # Set the URL and headers for the API request
        url = "https://api.trakt.tv/oauth/device/token"
        headers = {"Content-Type": "application/json", "trakt-api-version": "2", "trakt-api-key": await self.config.client_id()}

        # Set the payload for the API request
        payload = {"client_id": await self.config.client_id(), "client_secret": await self.config.client_secret(), "code": await self.config.authorization_code()}

        # Get the authorization interval
        interval = await self.config.authorization_interval()

        # Poll for authorization
        while True:
            # Send the API request
            async with self.bot.session.post(url, headers=headers, json=payload) as response:
                # Check if the request was successful
                if response.status != 200:
                    continue

                # Get the response data
                data = await response.json()

                # Set the access token in the cog's configuration
                await self.config.access_token.set(data["access_token"])
                await self.config.refresh_token.set(data["refresh_token"])

                # Break out of the loop
                break
            await asyncio.sleep(interval)

        # Set the authorization task to None
        self.authorization_task = None

        # Send a success message
        await ctx.send("Successfully authorized the Trakt API.")
        
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

