import discord
from redbot.core import commands, checks, Config

class rTrakt(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890)  # Replace with a unique identifier
        self.config.register_global(activity="")

    @commands.Cog.listener()
    async def on_ready(self):
        activity = await self.config.activity()
        if activity:
            await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=activity))

    @commands.command()
    @checks.is_owner()
    async def setactivity(self, ctx, *, activity: str):
        await self.config.activity.set(activity)
        await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=activity))
        await ctx.send(f"Activity set to: {activity}")

def setup(bot):
    bot.add_cog(rTrakt(bot))
