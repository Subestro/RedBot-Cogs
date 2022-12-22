import discord
import aiohttp
import asyncio
import os

from discord.ext import commands
from redbot.core import Config, checks, commands

class rTrakt(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890)
        default_global = {
            "api_key": None,
        }
        self.config.register_global(**default_global)

    @commands.command()
    @checks.is_owner()
    async def setapikey(self, ctx, api_key: str):
        """Set the API key for the Trakt API"""
        await self.config.api_key.set(api_key)
        await ctx.send("API key set successfully.")

    async def update_rich_presence(self):
        """Update the bot's rich presence with the scrobbler status"""
        api_key = await self.config.api_key()
        if api_key is None:
            return

        # Use the Trakt API to retrieve the scrobbler status
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.trakt.tv/sync/playback", headers={
                "Content-Type": "application/json",
                "trakt-api-key": api_key,
                "trakt-api-version": "2",
            }) as resp:
                if resp.status != 200:
                    return
                data = await resp.json()

        # Update the bot's rich presence with the scrobbler status
        if data["type"] == "episode":
            activity = discord.Activity(
                name=data["episode"]["title"],
                type=discord.ActivityType.watching,
                details=data["show"]["title"],
                state=f"Season {data['episode']['season']} Episode {data['episode']['number']}",
            )
        elif data["type"] == "movie":
            activity = discord.Activity(
                name=data["movie"]["title"],
                type=discord.ActivityType.watching,
                details=data["movie"]["title"],
            )
        await self.bot.change_presence(activity=activity)

    async def on_ready(self):
        """Start updating the rich presence with the scrobbler status"""
        api_key = await self.config.api_key()
        if api_key is None:
            return

        # Start updating the rich presence in a loop
        self.task = self.bot.loop.create_task(self.update_rich_presence_loop())

    async def update_rich_presence_loop(self):
        """Update the rich presence in a loop"""
        while True:
            await self.update_rich_presence()
            await asyncio.sleep(60)

def setup(bot):
    bot.add_cog(rTrakt(bot))

