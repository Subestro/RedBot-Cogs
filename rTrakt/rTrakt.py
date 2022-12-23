import aiohttp
import discord
import json
import urllib.parse
from discord.ext import commands
from redbot.core import Config

class rTrakt(commands.Cog):
    """Show the scrobbler status in the bot's rich presence"""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=9811198108111121, force_registration=True)
        self.config.register_global(client_id=None, client_secret=None, redirect_uri=None, access_token=None, refresh_token=None, access_token_expiry=None)
        self.session = aiohttp.ClientSession(loop=bot.loop)
        self.auth_url = None

    @commands.command()
    async def traktauth(self, ctx):
        """Initiate the OAuth authentication process"""
        # Get the client ID and redirect URI from the config
        client_id = await self.config.client_id()
        redirect_uri = await self.config.redirect_uri()

        # Generate the authorization URL
        self.auth_url = f"https://trakt.tv/oauth/authorize?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}"

        # Send a message with the authorization URL to the user who invoked the command
        await ctx.send(f"To authenticate with the Trakt API, visit this URL: {self.auth_url}")

    @commands.command()
    async def traktauthcomplete(self, ctx, authorization_code: str):
        """Exchange the authorization code for an access token"""
        # Get the client ID, client secret, and redirect URI from the config
        client_id = await self.config.client_id()
        client_secret = await self.config.client_secret()
        redirect_uri = await self.config.redirect_uri()

        # Build the request body
        data = {
            "grant_type": "authorization_code",
            "code": authorization_code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri
        }

        # Send a request to the Trakt API to exchange the authorization code for an access token
        async with self.session.post("https://api.trakt.tv/oauth/token", data=data) as resp:
            # Check if the request was successful
            if resp.status != 200:
                return await ctx.send("Failed to exchange authorization code for an access token. Please try again.")

            # Get the access token and refresh token from the response
            tokens = json.loads(await resp.text())
            access_token = tokens["access_token"]
            refresh_token = tokens["refresh_token"]
            access_token_expiry = tokens["expires_in"]

            # Save the access token, refresh token, and access token expiry in the config
            
            await self.config.access_token.set(access_token)
            await self.config.refresh_token.set(refresh_token)
            await self.config.access_token_expiry.set(access_token_expiry)

            # Send a message to confirm that the authorization process is complete
            await ctx.send("Authorization process complete. You can now use the `traktstatus` command to get your scrobbler status.")
def setup(bot):
    bot.add_cog(rTrakt(bot))
