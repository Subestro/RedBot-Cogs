import discord
from discord.ext import commands, tasks
from redbot.core import checks, commands, Config
from rTrakt.Trakt import Trakt
import asyncio

class rTrakt(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.trakt_user = "Subestro"  # Replace with your Trakt username
        self.activity_task.start()

    def cog_unload(self):
        self.activity_task.cancel()

    @tasks.loop(seconds=10)
    async def activity_task(self):
        await self.bot.wait_until_ready()
        trakt_activity = await Trakt.users(self.trakt_user).activity()
        # Parse the Trakt activity and extract the relevant information
        # You can customize how the activity is displayed in Discord
        activity_text = f"Currently watching: {trakt_activity[0].type} {trakt_activity[0].show.title}"
        await self.bot.change_presence(activity=discord.Game(name=activity_text))

def setup(bot):
    Trakt.configuration.defaults.client(
        id='4129a600893f2b057301ef356e96277f0bf2898c205ff02e6dcfdeecef899b42',
        secret='be487ee7080112b005cd8008157eceb022a14740e7f10bbc6c571803893dbda5'
    )
    bot.add_cog(rTrakt(bot))
