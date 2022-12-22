import requests
import discord
from redbot.core import commands
from redbot.core.bot import Red

class rTrakt(commands.Cog):
    def __init__(self, bot: Red):
        self.bot = bot
        self.api_key = None
        self.api_secret = None

    @commands.is_owner()
    @commands.command()
    async def set_api_credentials(self, ctx, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        await ctx.send("API credentials set successfully")

    @commands.command()
    async def update_rich_presence(self, ctx):
        # Fetch the current playback details from the trakt API
        response = requests.get(
            "https://api.trakt.tv/sync/playback",
            headers={
                "Content-Type": "application/json",
                "trakt-api-key": self.api_key,
                "trakt-api-version": "2",
            },
            auth=(self.api_key, self.api_secret),
        )

        # Extract the show or movie title and current episode or scene
        data = response.json()
        title = data["item"]["title"]
        details = f"{data['progress']} of {data['item']['episode']['title']}"

        # Create a rich presence activity
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name=title,
            details=details,
        )

        # Update the bot's presence
        await self.bot.change_presence(activity=activity)

def setup(bot):
    bot.add_cog(rTrakt(bot))
