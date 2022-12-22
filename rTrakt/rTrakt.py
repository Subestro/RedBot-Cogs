import requests
import discord
from redbot.core import commands

# Your API key and secret
API_KEY = "your_api_key"
API_SECRET = "your_api_secret"

class rTrakt(commands.Cog):
    @commands.command()
    async def update_rich_presence(self, ctx):
        # Fetch the current playback details from the trakt API
        response = requests.get(
            "https://api.trakt.tv/sync/playback",
            headers={
                "Content-Type": "application/json",
                "trakt-api-key": API_KEY,
                "trakt-api-version": "2",
            },
            auth=(API_KEY, API_SECRET),
        )

        # Extract the show or movie title and current episode or scene
        title = response["item"]["title"]
        details = f"{response['progress']} of {response['item']['episode']['title']}"

        # Create a rich presence activity
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name=title,
            details=details,
        )

        # Update the bot's presence
        await ctx.bot.change_presence(activity=activity)

def setup(bot):
    bot.add_cog(rTrakt())