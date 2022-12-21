import discord
import pytrakt
import requests
import trakt
import urllib.parse
from redbot.core import commands

class rTrakt(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def watching(self, ctx, access_token=None):
        # Check if the OAuth access token is present
        if access_token is None:
            # Build the authorize URL with the necessary parameters
            params = {
                "client_id": "your_client_id_here",
                "redirect_uri": "your_redirect_uri_here",
                "response_type": "code",
                "state": "random_string_here"
            }
            authorize_url = "https://trakt.tv/oauth/authorize?" + urllib.parse.urlencode(params)

            # Send a message to the user with a link to the authorize URL
            embed = discord.Embed(
                title="Authorization Required",
                description=f"To use this command, you must authorize this app to access your Trakt account. Click [here]({authorize_url}) to begin the authorization process.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        # Create a new Client object and authenticate using the OAuth access token
        client = pytrakt.Client(access_token=access_token)

        # Get the user's current activity
        activity = client.activity.watching()

        # Create a new Game object with the user's current activity as the name
        game = discord.Game(name=activity)

        # Update the bot's rich presence with the new Game object
        await self.bot.change_presence(activity=game)
