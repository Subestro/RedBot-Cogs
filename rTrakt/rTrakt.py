import aiohttp
import asyncio
import discord
from discord.ext import commands
from redbot.core import Config
from redbot.core.bot import Red
from redbot.core import commands
from redbot.core.utils.chat_formatting import pagify
from redbot.core.utils.menus import menu, DEFAULT_CONTROLS
from redbot.core import checks
from redbot.core.utils.predicates import MessagePredicate

# Add this import
from redbot.core.tasks import tasks


class rTrakt(commands.Cog):
    def __init__(self, bot: Red):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1010011010, force_registration=True)
        self.config.register_global(
            client_id=None, client_secret=None, authorization_code=None,
            access_token=None, refresh_token=None,
        )

    @commands.group()
    @checks.is_owner()
    async def rTrakt(self, ctx: commands.Context):
        """Trakt scrobbler commands."""
        pass

    @rTrakt.command(name="generatecodes")
    async def rTrakt_generatecodes(self, ctx: commands.Context):
        """Generates a new client ID and client secret for the Trakt API."""
        async with aiohttp.ClientSession() as session:
            async with session.post("https://api.trakt.tv/oauth/client/new", json={"name": "RedBot"}) as resp:
                if resp.status == 200:
                    response_json = await resp.json()
                    client_id = response_json["client_id"]
                    client_secret = response_json["client_secret"]
                    await ctx.send(f"Client ID: {client_id}\nClient secret: {client_secret}")
                else:
                    await ctx.send("Failed to generate a new client ID and client secret for the Trakt API.")
                    
    @rTrakt.command(name="setcodes")
    async def rTrakt_setcodes(self, ctx: commands.Context, client_id: str, client_secret: str):
        """Sets the client ID and client secret for the Trakt API."""
        # Update the cog's configuration with the new client ID and client secret
        await self.config.client_id.set(client_id)
        await self.config.client_secret.set(client_secret)
        await ctx.send("The client ID and client secret have been set.")

    @rTrakt.command(name="displaycode")
    async def rTrakt_displaycode(self, ctx: commands.Context):
        """Displays the authorization link for the Trakt API."""
        # Get the client ID and client secret from the cog's configuration
        client_id = await self.config.client_id()
        client_secret = await self.config.client_secret()

        if client_id is None or client_secret is None:
            await ctx.send("The client ID or client secret has not been set. Please use the `[p]rTrakt setcodes` command to set them.")
        else:
            # Construct the authorization link
            authorization_url = "https://api.trakt.tv/oauth/authorize"
            params = {
                "response_type": "code",
                "client_id": client_id,
                "redirect_uri": "urn:ietf:wg:oauth:2.0:oob",
            }
            authorization_link = f"{authorization_url}?{urlencode(params)}"

            await ctx.send(f"Authorization link: {authorization_link}")

    @rTrakt.command(name="pollauth")
    async def rTrakt_pollauth(self, ctx: commands.Context, authorization_code: str):
        """Polls for authorization of the Trakt API."""
        # Get the client ID and client secret from the cog's configuration
        client_id = await self.config.client_id()
        client_secret = await self.config.client_secret()

        # Construct the authorization request payload
        authorization_url = "https://api.trakt.tv/oauth/token"
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
                    # Save the access token and refresh token in the cog's configuration
                    await self.config.access_token.set(response_json["access_token"])
                    await self.config.refresh_token.set(response_json["refresh_token"])
                    await ctx.send("Successfully authorized the Trakt API.")
                else:
                    await ctx.send("Failed to authorize the Trakt API.")

    @rTrakt.command(name="refreshauth")
    async def rTrakt_refreshauth(self, ctx: commands.Context):
        """Refreshes the authorization for the Trakt API."""
        # Get the client ID and client secret from the cog's configuration
        client_id = await self.config.client_id()
        client_secret = await self.config.client_secret()

        # Get the refresh token from the cog's configuration
        refresh_token = await self.config.refresh_token()

        if refresh_token is None:
            await ctx.send("No refresh token found. Please use the `[p]rTrakt pollauth` command to obtain an access token and refresh token.")
        else:
            # Construct the refresh request payload
            refresh_url = "https://api.trakt.tv/oauth/token"
            payload = {
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uri": "urn:ietf:wg:oauth:2.0:oob",
                "refresh_token": refresh_token,
                "grant_type": "refresh_token",
            }

            # Send the refresh request
            async with aiohttp.ClientSession() as session:
                async with session.post(refresh_url, data=payload) as resp:
                    if resp.status == 200:
                        response_json = await resp.json()
                        # Save the new access token in the cog's configuration
                        await self.config.access_token.set(response_json["access_token"])
                        await ctx.send("Successfully refreshed the Trakt API authorization.")
                    else:
                        await ctx.send("Failed to refresh the Trakt API authorization.")

    @rTrakt.command(name="checkauth")
    async def rTrakt_checkauth(self, ctx: commands.Context):
        """Checks the authorization status for the Trakt API."""
        access_token = await self.config.access_token()
        if access_token is None:
            await ctx.send("The Trakt API is not authorized. Please use the `[p]rTrakt auth` command to authorize it.")
        else:
            await ctx.send("The Trakt API is authorized.")

    @rTrakt.command(name="rOMDB")
    async def rTrakt_rOMDB(self, ctx: commands.Context, api_key: str):
        """Sets the OMDB API key."""
        # Update the cog's configuration with the new OMDB API key
        await self.config.omdb_api_key.set(api_key)
        await ctx.send("The OMDB API key has been set.")

    @rTrakt.command(name="set")
    async def rTrakt_set(self, ctx: commands.Context, *, presence: str):
        """Sets the bot's rich presence."""
        # Update the cog's configuration with the new rich presence
        await self.config.presence.set(presence)
        await ctx.send("The rich presence has been set.")

    @rTrakt.command(name="unset")
    async def rTrakt_unset(self, ctx: commands.Context):
        """Unsets the bot's rich presence."""
        # Clear the cog's rich presence configuration
        await self.config.presence.clear()
        await ctx.send("The rich presence has been unset.")

    @tasks.loop(seconds=30)
    async def update_presence(self):
        """Updates the bot's rich presence with the user's currently playing media."""
        # Get the access token and rich presence from the cog's configuration
        access_token = await self.config.access_token()
        presence = await self.config.presence()

        if access_token is None:
            return

        # Construct the request headers with the access token
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
            "trakt-api-version": "2",
            "trakt-api-key": self.client_id,
        }

        # Send the request to the Trakt API to get the user's currently playing media
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.trakt.tv/sync/playback/active", headers=headers) as resp:
                if resp.status == 200:
                    response_json = await resp.json()
                    media_type = response_json["type"]
                    # Check if the media is a movie or TV show
                    if media_type == "movie":
                        # Get the movie's title and year
                        title = response_json["movie"]["title"]
                        year = response_json["movie"]["year"]
                        # Set the presence to "Watching a movie"
                        presence = f"Watching a movie: {title} ({year})"
                    elif media_type == "episode":
                        # Get the TV show's title and episode information
                        title = response_json["show"]["title"]
                        season = response_json["episode"]["season"]
                        number = response_json["episode"]["number"]
                        # Set the presence to "Watching a TV show"
                        presence = f"Watching TV: {title} S{season:02d}E{number:02d}"

                    # Update the bot's presence
                    activity = discord.Game(name=presence)
                    await self.bot.change_presence(activity=activity)
                else:
                    # If the request fails, clear the presence
                    await self.bot.change_presence(activity=None)

def setup(bot):
    bot.add_cog(rTrakt(bot))

