import discord
import pytrakt
import requests
import trakt
import urllib.parse
from redbot.core import commands

import requests

@commands.command()
async def watching(self, ctx, access_token=None):
    # Check if the OAuth access token is present
    if access_token is None:
        # Send a message to the user with instructions on how to obtain the access token
        embed = discord.Embed(
            title="Access Token Required",
            description="To use this command, you must provide a valid OAuth access token. You can obtain a token by visiting the following URL and following the instructions: https://trakt.tv/oauth/applications",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    # Make a GET request to the /sync/playback endpoint
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    response = requests.get("https://api.trakt.tv/sync/playback", headers=headers)

    # Check the response status code
    if response.status_code == 200:
        # Parse the response data
        data = response.json()

        # Get the user's current activity
        activity = data["item"]["title"]

        # Create a new Game object with the user's current activity as the name
        game = discord.Game(name=activity)

        # Update the bot's rich presence with the new Game object
        await self.bot.change_presence(activity=game)
    else:
        # If the request fails, send a message to the user
        embed = discord.Embed(
            title="Error",
            description=f"An error occurred while trying to get your current playback activity. The status code was {response.status_code}.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
