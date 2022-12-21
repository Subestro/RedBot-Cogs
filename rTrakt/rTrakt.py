import os
import requests

import discord
from discord.ext import commands

class rTrakt(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def scrobbler(self, ctx):
        # Request authorization code
        auth_response = requests.post(
            "https://api.trakt.tv/oauth/device/code",
            headers={"Content-Type": "application/json", "trakt-api-key": os.environ["TRAKT_CLIENT_ID"], "trakt-api-version": 2},
            json={"client_id": os.environ["TRAKT_CLIENT_ID"]}
        )

        # Extract authorization code from response
        auth_code = auth_response.json()["user_code"]

        # Display authorization code in embed
        embed = discord.Embed(title="Trakt Scrobbler", description=f"Enter the following code to authorize the bot: `{auth_code}`")
        await ctx.send(embed=embed)

        # Wait for user to enter code and authorize bot
        auth_response = requests.post(
            "https://api.trakt.tv/oauth/device/token",
            headers={"Content-Type": "application/json", "trakt-api-key": os.environ["TRAKT_CLIENT_ID"], "trakt-api-version": 2},
            json={"client_id": os.environ["TRAKT_CLIENT_ID"], "client_secret": os.environ["TRAKT_CLIENT_SECRET"], "code": auth_code}
        )

        # Extract access token from response
        access_token = auth_response.json()["access_token"]

        # Use access token to retrieve scrobbler status
        scrobbler_response = requests.get(
            "https://api.trakt.tv/sync/playback/scrobble",
            headers={"Content-Type": "application/json", "trakt-api-key": os.environ["TRAKT_CLIENT_ID"], "trakt-api-version": 2, "Authorization": f"Bearer {access_token}"}
        )

        # Extract scrobbler status from response
        scrobbler_status = scrobbler_response.json()["status"]

        # Set bot's rich presence
        await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=scrobbler_status))

def setup(bot):
    bot.add_cog(rTrakt(bot))
