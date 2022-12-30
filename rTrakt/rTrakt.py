import discord
import aiohttp
from discord.ext import commands
from redbot.core import Config, checks
from redbot.core.bot import Red


class rTrakt(commands.Cog):
    def __init__(self, bot: Red):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1010011010, force_registration=True)

        default_global = {
            "client_id": None,
            "client_secret": None,
            "access_token": None,
            "refresh_token": None,
        }
        self.config.register_global(**default_global)

    @commands.group()
    @checks.is_owner()
    async def _trakt(self, ctx: commands.Context):
        """Trakt scrobbler commands."""
        pass

    @_trakt.command(name="generatecodes")
    async def _generatecodes(self, ctx: commands.Context):
        """Generates a new client ID and client secret for the Trakt API."""
        # Generate a new client ID and client secret here
        client_id = "your_generated_client_id"
        client_secret = "your_generated_client_secret"

        # Update the cog's configuration with the new client ID and client secret
        await self.config.client_id.set(client_id)
        await self.config.client_secret.set(client_secret)

        await ctx.send(
            f"Generated new client ID and client secret for the Trakt API:\nClient ID: {client_id}\nClient secret: {client_secret}"
        )

    @_trakt.command(name="setcodes")
    async def _setcodes(self, ctx: commands.Context, client_id: str, client_secret: str):
        """Sets the client ID and client secret for the Trakt API."""
        # Update the cog's configuration with the new client ID and client secret
        await self.config.client_id.set(client_id)
        await self.config.client_secret.set(client_secret)
        await ctx.send("Successfully set the client ID and client secret for the Trakt API.")

    @_trakt.command(name="displaycode")
    async def _displaycode(self, ctx: commands.Context):
        """Displays the authorization link for the Trakt API."""
        # Get the client ID and redirect URL from the cog's configuration
        client_id = await self.config.client_id()
        redirect_url = "urn:ietf:wg:oauth:2.0:oob"

        # Construct the authorization link
        authorization_url = f"https://trakt.tv/oauth/authorize?response_type=code&client_id={client_id}&redirect_uri={redirect_url}"

        await ctx.send(f"To authorize the Trakt API, visit the following link and enter the authorization code:\n{authorization_url}")

    @_trakt.command(name="pollauth")
    async def _pollauth(self, ctx: commands.Context):
        """Polls for authorization of the Trakt API."""
        # Get the client ID, client secret, and authorization code from the cog's configuration
        client_id = await self.config.client_id()
        client_secret = await self.config.client_secret()
        authorization_code = await self.config.authorization_code()

        # Construct the authorization URL
        authorization_url = "https://api.trakt.tv/oauth/token"

        # Construct the request payload
        payload = {
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": "urn:ietf:wg:oauth:2.0:oob",
            "code": authorization_code,
            "grant_type": "authorization_code",
        }

        # Send the authorization request
        async with aiohttp.ClientSession() as session:
            async with session.post(authorization_url, data=payload) as resp:
                if resp.status == 200:
                    response_json = await resp.json()
                    access_token = response_json["access_token"]
                    refresh_token = response_json["refresh_token"]

                    # Update the cog's configuration with the new access and refresh tokens
                    await self.config.access_token.set(access_token)
                    await self.config.refresh_token.set(refresh_token)
                    await ctx.send("Successfully authorized the Trakt API.")
                else:
                    await ctx.send("Failed to authorize the Trakt API. Please check your authorization code and try again.")

    @_trakt.command(name="successauth")
    async def _successauth(self, ctx: commands.Context):
        """Displays a success message if the Trakt API has been successfully authorized."""
        access_token = await self.config.access_token()
        if access_token:
            await ctx.send("The Trakt API has been successfully authorized.")
        else:
            await ctx.send("The Trakt API has not yet been authorized. Please use the `[p]trakt pollauth` command to poll for authorization.")

    @commands.Cog.listener()
    async def on_ready(self):
        # Get the access token from the cog's configuration
        access_token = await self.config.access_token()

        # Construct the headers for the request
        headers = {
            "Content-Type": "application/json",
            "trakt-api-key": "{client_id}",
            "trakt-api-version": "2",
            "Authorization": f"Bearer {access_token}",
        }

        # Send a request to the Trakt API to get the user's currently playing media
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.trakt.tv/sync/playback", headers=headers) as resp:
                if resp.status == 200:
                    response_json = await resp.json()
                    # Get the user's currently playing media from the response
                    media = response_json[0]["movie"] or response_json[0]["episode"]

                    # Construct the rich presence message
                    if media["type"] == "movie":
                        presence_message = f"Watching {media['title']} ({media['year']})"
                    else:
                        presence_message = f"Watching {media['show']['title']} S{media['season']:02d}E{media['number']:02d} - {media['title']}"

                    # Set the rich presence message
                    presence = discord.Activity(name=presence_message, type=discord.ActivityType.watching)
                    await self.bot.change_presence(activity=presence)
                else:
                    # If the request fails, clear the rich presence message
                    await self.bot.change_presence(activity=None)

def setup(bot: Red):
    bot.add_cog(rTrakt(bot))

