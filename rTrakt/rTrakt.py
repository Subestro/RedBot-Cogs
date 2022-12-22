import asyncio
import requests
import discord
from discord.ext import commands
from redbot.core import Config

class rTrakt(commands.Cog):
    async def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=3393734173)
        default_global = {"api_key": None}
        self.config.register_global(**default_global)
        self.trakt_api_key = self.config.api_key()
        self.update_presence()
        self.loop_task = self.bot.loop.create_task(self.loop())

    async def update_presence(self):
        # Make a request to the Trakt API to retrieve the current scrobbler status
        headers = {
            "Content-Type": "application/json",
            "trakt-api-key": self.trakt_api_key,
        }
        response = requests.get("https://api.trakt.tv/users/me/watching", headers=headers)
        data = response.json()

        # If we're currently watching something, create an activity object and update the rich presence
        if data["watching"]:
            show = data["watching"]["show"]
            episode = data["watching"]["episode"]
            activity = discord.Activity(
                name=f"{show['title']} - {episode['title']}",
                type=discord.ActivityType.watching,
            )
            await self.bot.change_presence(activity=activity)

    async def loop(self):
        while True:
            self.update_presence()
            await asyncio.sleep(30)

    @commands.command()
    async def setapikey(self, ctx, api_key: str):
        await self.config.api_key.set(api_key)
        self.trakt_api_key = api_key
        await ctx.send("Successfully set Trakt API key!")

def setup(bot):
    bot.add_cog(rTrakt(bot))
